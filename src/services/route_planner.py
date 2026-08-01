"""Gộp yêu cầu thu gom thành tuyến — HITL #3.

Nguyên tắc bất di bất dịch: **agent không được tự đổi lịch làm việc của con
người.** Tuyến do agent gộp luôn ở trạng thái ``proposed`` cho tới khi đội
trưởng bấm duyệt.

Cách gộp (P0, cố ý không dùng VRP đầy đủ — xem CLAUDE.md mục 3): nhóm theo
**cùng ngày + cùng khung giờ + cụm toà gần nhau**, giới hạn bởi tải trọng xe.
Kèm theo tuyến là khối "vì sao gộp thế này" liệt kê tiêu chí, các yêu cầu bị
loại và lý do, cùng phần tiết kiệm so với đi lẻ. Khối đó quan trọng bằng chính
cái tuyến: người duyệt phải hiểu logic mới dám duyệt.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import get_settings
from src.db.models import (
    Building,
    Notification,
    PickupEvent,
    PickupRequest,
    PickupRoute,
    RouteStop,
    Unit,
    User,
)

# Hai toà cách nhau dưới ngưỡng này thì coi là cùng cụm, gộp được một chuyến.
CLUSTER_RADIUS_KM = 0.8

STOP_ISSUES: list[dict[str, str]] = [
    {"code": "khong_co_nguoi", "label_vi": "Không có người"},
    {"code": "khoi_luong_khac", "label_vi": "Khối lượng khác dự kiến"},
    {"code": "co_rac_nguy_hai", "label_vi": "Có rác nguy hại lẫn vào"},
    {"code": "khong_tiep_can", "label_vi": "Không tiếp cận được"},
    {"code": "khac", "label_vi": "Khác"},
]
STOP_ISSUE_CODES = {i["code"] for i in STOP_ISSUES}


@dataclass
class Candidate:
    """Một yêu cầu đang chờ xếp tuyến, kèm thông tin toà để tính quãng đường."""

    request: PickupRequest
    building: Building | None
    unit_code: str

    @property
    def weight_kg(self) -> float:
        # Xếp tuyến theo cận TRÊN của khoảng: thà xe còn chỗ trống còn hơn quá tải.
        return self.request.weight_max_kg or self.request.est_weight_kg


def _so(value: float) -> str:
    """Định dạng số theo quy ước tiếng Việt: dấu phẩy là dấu thập phân."""
    text = f"{value:g}"
    return text.replace(".", ",")


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Khoảng cách đường chim bay giữa hai điểm, tính bằng km."""
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def _distance_between(a: Building | None, b: Building | None) -> float:
    if a is None or b is None or a.id == b.id:
        return 0.0
    if None in (a.lat, a.lng, b.lat, b.lng):
        return 0.3  # hai toà khác nhau, chưa có toạ độ — ước lượng tối thiểu
    return haversine_km(a.lat, a.lng, b.lat, b.lng)


def estimate_route_km(candidates: list[Candidate]) -> float:
    """Quãng đường ước tính của tuyến: đi qua các toà theo thứ tự, rồi quay về.

    Đây là **ước lượng đường chim bay**, không phải quãng đường thực tế theo
    đường đi. Con số hiển thị trên UI ghi rõ là ước tính.
    """
    if not candidates:
        return 0.0
    total = 0.0
    for previous, current in zip(candidates, candidates[1:], strict=False):
        total += _distance_between(previous.building, current.building)
    # Chặng đi và chặng về từ khu tập kết: cộng một lượng cố định nhỏ.
    return round(total + 1.2, 2)


def _load_candidates(session: Session, service_date: date, window: str) -> tuple[list[Candidate], list[Candidate]]:
    """Trả về ``(hợp lệ, bị loại)`` cho một ngày và khung giờ.

    Bị loại = đã duyệt, chờ xếp tuyến, nhưng lệch ngày hoặc lệch khung giờ.
    Danh sách này lên thẳng khối "vì sao gộp thế này" — người duyệt cần thấy
    agent đã cân nhắc gì rồi mới bỏ ra.
    """
    rows = session.execute(
        select(PickupRequest, Unit, Building)
        .join(Unit, PickupRequest.unit_id == Unit.id)
        .join(Building, Unit.building_id == Building.id)
        .where(PickupRequest.status == "approved")
        .order_by(PickupRequest.created_at)
    ).all()

    matched: list[Candidate] = []
    excluded: list[Candidate] = []
    for request, unit, building in rows:
        candidate = Candidate(request=request, building=building, unit_code=unit.code)
        if request.preferred_date == service_date and (not window or request.preferred_window == window):
            matched.append(candidate)
        else:
            excluded.append(candidate)
    return matched, excluded


def propose_route(
    session: Session,
    *,
    service_date: date,
    window: str,
    team_id: int | None = None,
    capacity_kg: float | None = None,
    run_id: int | None = None,
) -> PickupRoute:
    """Agent đề xuất một tuyến gộp. Kết quả luôn ở trạng thái ``proposed``.

    Raises:
        ValueError: khi không có yêu cầu nào đã duyệt cho ngày/khung giờ đó.
    """
    settings = get_settings()
    capacity = capacity_kg or settings.vehicle_capacity_kg
    matched, excluded = _load_candidates(session, service_date, window)
    if not matched:
        raise ValueError("Không có yêu cầu nào đã duyệt cho ngày và khung giờ này")

    # Gộp theo cụm toà: bắt đầu từ toà của yêu cầu đầu tiên, thêm dần các yêu
    # cầu ở toà nằm trong bán kính cụm, dừng khi chạm tải trọng.
    anchor = matched[0].building
    selected: list[Candidate] = []
    over_capacity: list[Candidate] = []
    too_far: list[Candidate] = []
    total_weight = 0.0

    for candidate in matched:
        if _distance_between(anchor, candidate.building) > CLUSTER_RADIUS_KM:
            too_far.append(candidate)
            continue
        if total_weight + candidate.weight_kg > capacity:
            over_capacity.append(candidate)
            continue
        selected.append(candidate)
        total_weight += candidate.weight_kg

    if not selected:  # tất cả đều quá tải — vẫn xếp yêu cầu đầu để người duyệt xử lý
        selected = [matched[0]]
        over_capacity = [c for c in matched[1:]]
        total_weight = selected[0].weight_kg

    # Sắp xếp điểm dừng: gom các điểm cùng toà cạnh nhau, toà gần khu tập kết trước.
    selected.sort(key=lambda c: (c.building.code if c.building else "", c.unit_code))

    est_km = estimate_route_km(selected)
    baseline_km = round(len(selected) * settings.baseline_km_per_standalone_trip, 2)
    building_names = sorted({c.building.code for c in selected if c.building})

    criteria = [
        f"Cùng ngày {service_date.strftime('%d/%m/%Y')}" + (f" và khung giờ {window}" if window else ""),
        f"Cùng cụm toà {', '.join(building_names)} (bán kính {_so(CLUSTER_RADIUS_KM)} km)",
        f"Tổng {total_weight:.0f} kg — trong tải trọng {capacity:.0f} kg của xe",
    ]

    excluded_notes: list[dict[str, str]] = []
    for candidate in excluded:
        ly_do = []
        if candidate.request.preferred_date != service_date:
            ly_do.append(f"lệch ngày ({candidate.request.preferred_date})")
        elif candidate.request.preferred_window != window:
            ly_do.append(f"lệch khung giờ ({candidate.request.preferred_window})")
        excluded_notes.append(
            {
                "request_id": str(candidate.request.id),
                "unit": candidate.unit_code,
                "ly_do": " · ".join(ly_do) or "không khớp điều kiện",
            }
        )
    for candidate in too_far:
        excluded_notes.append(
            {
                "request_id": str(candidate.request.id),
                "unit": candidate.unit_code,
                "ly_do": f"toà {candidate.building.code if candidate.building else '?'} nằm ngoài cụm",
            }
        )
    for candidate in over_capacity:
        excluded_notes.append(
            {
                "request_id": str(candidate.request.id),
                "unit": candidate.unit_code,
                "ly_do": f"vượt tải trọng còn lại của xe ({_so(capacity)} kg)",
            }
        )

    route = PickupRoute(
        service_date=service_date,
        window=window,
        team_id=team_id,
        status="proposed",
        total_weight_kg=round(total_weight, 1),
        est_distance_km=est_km,
        run_id=run_id,
        reasoning={
            "criteria": criteria,
            "excluded": excluded_notes,
            "baseline_km": baseline_km,
            "saved_km": round(max(0.0, baseline_km - est_km), 2),
            "saved_trips": max(0, len(selected) - 1),
            "capacity_kg": capacity,
            "note": "Quãng đường là ước tính theo đường chim bay giữa các toà, không phải quãng đường thực tế.",
        },
        proposed_stop_order=[c.request.id for c in selected],
    )
    session.add(route)
    session.flush()

    for index, candidate in enumerate(selected, start=1):
        session.add(RouteStop(route_id=route.id, request_id=candidate.request.id, seq=index))
    session.flush()
    return route


def review_route(
    session: Session,
    *,
    route: PickupRoute,
    actor: User,
    action: str,
    stop_order: list[int] | None = None,
    removed_stops: list[int] | None = None,
) -> PickupRoute:
    """HITL #3 — đội trưởng duyệt / sửa rồi duyệt / đề xuất lại / huỷ tuyến.

    Args:
        action: ``approve`` · ``approve_with_changes`` · ``cancel``.
            ``regenerate`` do lớp API xử lý vì nó tạo tuyến mới.
        stop_order: danh sách ``request_id`` theo thứ tự người duyệt sắp lại.
        removed_stops: các ``request_id`` bị bỏ khỏi tuyến, quay về nhóm chờ xếp.

    Raises:
        ValueError: khi hành động không hợp lệ hoặc tuyến đã chốt.
    """
    if action not in {"approve", "approve_with_changes", "cancel"}:
        raise ValueError(f"Hành động không hợp lệ: {action}")
    if route.status not in {"proposed", "approved"}:
        raise ValueError(f"Tuyến đang ở trạng thái '{route.status}', không duyệt lại được")

    if action == "cancel":
        for stop in route.stops:
            request = session.get(PickupRequest, stop.request_id)
            if request is not None and request.status == "scheduled":
                request.status = "approved"
        route.status = "cancelled"
        session.flush()
        return route

    if action == "approve_with_changes":
        removed = set(removed_stops or [])
        for stop in list(route.stops):
            if stop.request_id in removed:
                request = session.get(PickupRequest, stop.request_id)
                if request is not None:
                    request.status = "approved"
                    session.add(
                        PickupEvent(
                            request_id=request.id,
                            kind="routed",
                            label_vi="Bị bỏ khỏi tuyến khi ban quản lý duyệt — chờ xếp chuyến khác",
                            actor_id=actor.id,
                        )
                    )
                # Gỡ khỏi quan hệ để collection trong bộ nhớ khớp với CSDL ngay;
                # cascade delete-orphan lo phần xoá bản ghi.
                route.stops.remove(stop)
        session.flush()

        if stop_order:
            position = {request_id: index for index, request_id in enumerate(stop_order, start=1)}
            for stop in route.stops:
                stop.seq = position.get(stop.request_id, stop.seq)
        session.flush()
        _recalculate_totals(session, route)

    route.status = "approved"
    route.approved_by = actor.id
    route.approved_at = datetime.now()
    session.flush()

    for stop in sorted(route.stops, key=lambda s: s.seq):
        request = session.get(PickupRequest, stop.request_id)
        if request is None:
            continue
        request.status = "scheduled"
        session.add(
            PickupEvent(
                request_id=request.id,
                kind="routed",
                label_vi=(
                    f"Đã xếp vào chuyến {route.window or ''} ngày "
                    f"{route.service_date.strftime('%d/%m')} cùng {len(route.stops) - 1} hộ khác"
                ).strip(),
                actor_id=actor.id,
                detail={"route_id": route.id, "seq": stop.seq},
            )
        )
        session.add(
            Notification(
                user_id=request.resident_id,
                title="Yêu cầu của bạn đã được xếp lịch thu gom",
                body=(
                    f"Chuyến {route.window} ngày {route.service_date.strftime('%d/%m/%Y')}. "
                    f"Đi cùng chuyến với {max(0, len(route.stops) - 1)} hộ khác trong toà — giảm "
                    f"{route.reasoning.get('saved_trips', 0)} chuyến xe."
                ),
                entity="pickup_route",
                entity_id=str(route.id),
            )
        )
    if route.team_id:
        session.add(
            Notification(
                user_id=route.team_id,
                title="Có tuyến mới đã được duyệt",
                body=f"{len(route.stops)} điểm dừng · {route.total_weight_kg:.0f} kg",
                entity="pickup_route",
                entity_id=str(route.id),
            )
        )
    session.flush()
    return route


def _recalculate_totals(session: Session, route: PickupRoute) -> None:
    """Tính lại khối lượng và quãng đường sau khi người duyệt sửa tuyến."""
    candidates: list[Candidate] = []
    for stop in sorted(route.stops, key=lambda s: s.seq):
        request = session.get(PickupRequest, stop.request_id)
        if request is None:
            continue
        unit = session.get(Unit, request.unit_id)
        building = session.get(Building, unit.building_id) if unit else None
        candidates.append(Candidate(request=request, building=building, unit_code=unit.code if unit else ""))

    route.total_weight_kg = round(sum(c.weight_kg for c in candidates), 1)
    route.est_distance_km = estimate_route_km(candidates)
    baseline = round(len(candidates) * get_settings().baseline_km_per_standalone_trip, 2)
    reasoning = dict(route.reasoning or {})
    reasoning["baseline_km"] = baseline
    reasoning["saved_km"] = round(max(0.0, baseline - route.est_distance_km), 2)
    reasoning["saved_trips"] = max(0, len(candidates) - 1)
    reasoning["edited_by_human"] = True
    route.reasoning = reasoning


def route_diff(route: PickupRoute) -> dict[str, Any]:
    """So sánh bản AI đề xuất với bản người duyệt đã sửa.

    Phần diff này rất đáng giá khi demo: nó cho thấy người vẫn là người chốt.
    """
    proposed = list(route.proposed_stop_order or [])
    current = [s.request_id for s in sorted(route.stops, key=lambda s: s.seq)]
    return {
        "proposed": proposed,
        "final": current,
        "removed": [r for r in proposed if r not in current],
        "reordered": proposed != current and sorted(proposed) == sorted(current),
        "changed": proposed != current,
    }


def complete_stop(
    session: Session,
    *,
    stop: RouteStop,
    actor: User,
    issue: str = "",
    issue_note: str = "",
    actual_weight_kg: float | None = None,
) -> RouteStop:
    """Đội vệ sinh đánh dấu đã thu tại một điểm dừng.

    Raises:
        ValueError: khi mã sự cố nằm ngoài danh sách cố định.
    """
    if issue and issue not in STOP_ISSUE_CODES:
        raise ValueError(f"Mã sự cố '{issue}' không nằm trong danh sách cố định")

    stop.done_at = datetime.now()
    stop.issue = issue
    stop.issue_note = issue_note
    stop.actual_weight_kg = actual_weight_kg

    request = session.get(PickupRequest, stop.request_id)
    if request is not None:
        request.status = "done"
        session.add(
            PickupEvent(
                request_id=request.id,
                kind="done",
                label_vi="Đội vệ sinh đã thu gom",
                actor_id=actor.id,
                detail={"issue": issue, "note": issue_note},
            )
        )

    route = session.get(PickupRoute, stop.route_id)
    if route is not None:
        if all(s.done_at is not None for s in route.stops):
            route.status = "done"
        elif route.status == "approved":
            route.status = "in_progress"
    session.flush()
    return stop
