"""Test yêu cầu thu gom (HITL #1) và gộp tuyến (HITL #3)."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.orm import Session

from src.db.models import Building, Notification, PickupEvent, PickupRequest, Unit, User
from src.services import pickup, route_planner


@pytest.fixture
def toa_nha(db_session: Session) -> dict[str, object]:
    """Ba toà: S1 và S2 gần nhau (cùng cụm), S3 ở xa."""
    s1 = Building(code="S1", name="Toà S1", lat=10.7769, lng=106.7009)
    s2 = Building(code="S2", name="Toà S2", lat=10.7782, lng=106.7021)
    s3 = Building(code="S3", name="Toà S3", lat=10.8200, lng=106.7500)
    db_session.add_all([s1, s2, s3])
    db_session.flush()

    units = {}
    for building, codes in ((s1, ["S1-1203", "S1-0805"]), (s2, ["S2-0501"]), (s3, ["S3-0710"])):
        for code in codes:
            unit = Unit(building_id=building.id, code=code)
            db_session.add(unit)
            db_session.flush()
            units[code] = unit

    manager = User(email="m@demo.vn", full_name="Trần Minh Đức", role="manager", password_hash="x")
    cleaner = User(email="c@demo.vn", full_name="Lê Văn Hùng", role="cleaner", password_hash="x")
    db_session.add_all([manager, cleaner])
    db_session.flush()

    residents = {}
    for index, code in enumerate(units, start=1):
        resident = User(
            email=f"r{index}@demo.vn",
            full_name=f"Cư dân {index}",
            role="resident",
            password_hash="x",
            unit_id=units[code].id,
        )
        db_session.add(resident)
        db_session.flush()
        residents[code] = resident

    db_session.commit()
    return {"units": units, "residents": residents, "manager": manager, "cleaner": cleaner}


def _tao_yeu_cau(
    db_session,
    toa_nha,
    unit_code: str,
    weight: float,
    ngay: date,
    khung: str = "08:00-10:00",
    duyet_luon: bool = False,
):
    """Tạo yêu cầu; mặc định cho ban quản lý duyệt luôn nếu nó vượt ngưỡng.

    Chỉ yêu cầu đã duyệt mới vào được bộ gộp tuyến, nên test tuyến cần bước này.
    """
    yeu_cau = pickup.create_pickup_request(
        db_session,
        resident=toa_nha["residents"][unit_code],
        items=[{"name": "Tủ gỗ cũ", "category_code": "bulky", "qty": 1}],
        est_weight_kg=weight,
        preferred_date=ngay,
        preferred_window=khung,
    )
    if duyet_luon and yeu_cau.status == "pending":
        pickup.review_pickup(db_session, request=yeu_cau, actor=toa_nha["manager"], action="approve")
    return yeu_cau


# --- HITL #1: ngưỡng duyệt ----------------------------------------------


def test_duoi_nguong_thi_tu_dong_duyet(db_session: Session, toa_nha) -> None:
    yeu_cau = _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=10, ngay=date(2026, 8, 6))

    assert yeu_cau.requires_hitl is False
    assert yeu_cau.status == "approved"
    assert yeu_cau.threshold_hit == []


def test_vuot_nguong_khoi_luong_thi_cho_duyet_va_noi_ro_con_so(db_session: Session, toa_nha) -> None:
    yeu_cau = _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=40, ngay=date(2026, 8, 6))

    assert yeu_cau.requires_hitl is True
    assert yeu_cau.status == "pending"
    hit = yeu_cau.threshold_hit[0]
    assert hit["rule"] == "vuot_khoi_luong"
    assert hit["threshold"] == 30.0
    assert hit["value"] == yeu_cau.weight_max_kg


def test_nguong_so_voi_can_tren_cua_khoang_khoi_luong(db_session: Session, toa_nha) -> None:
    """ADR-0003: sai số ước lượng phải nghiêng về phía cần người duyệt."""
    # 25 kg ước lượng → khoảng 15–35 kg → cận trên vượt ngưỡng 30 kg.
    yeu_cau = _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=25, ngay=date(2026, 8, 6))

    assert yeu_cau.weight_min_kg == 15.0
    assert yeu_cau.weight_max_kg == 35.0
    assert yeu_cau.requires_hitl is True, "Cận trên vượt ngưỡng mà vẫn tự động cho qua là sai"


def test_co_mon_nguy_hai_thi_luon_can_duyet_du_nhe(db_session: Session, toa_nha) -> None:
    yeu_cau = pickup.create_pickup_request(
        db_session,
        resident=toa_nha["residents"]["S1-1203"],
        items=[{"name": "Hộp pin cũ", "category_code": "hazardous", "qty": 1}],
        est_weight_kg=1.0,
        preferred_date=date(2026, 8, 6),
    )

    assert yeu_cau.requires_hitl is True
    assert any(h["rule"] == "co_mon_nguy_hai" for h in yeu_cau.threshold_hit)


def test_tu_choi_bat_buoc_chon_ly_do_trong_danh_sach(db_session: Session, toa_nha) -> None:
    yeu_cau = _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=40, ngay=date(2026, 8, 6))

    with pytest.raises(ValueError, match="phải kèm lý do"):
        pickup.review_pickup(db_session, request=yeu_cau, actor=toa_nha["manager"], action="reject")

    with pytest.raises(ValueError, match="không nằm trong danh sách cố định"):
        pickup.review_pickup(
            db_session, request=yeu_cau, actor=toa_nha["manager"], action="reject", reason="tại vì tôi thích"
        )


def test_duyet_thi_ghi_timeline_va_bao_cho_cu_dan(db_session: Session, toa_nha) -> None:
    yeu_cau = _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=40, ngay=date(2026, 8, 6))

    pickup.review_pickup(db_session, request=yeu_cau, actor=toa_nha["manager"], action="approve")
    db_session.commit()

    assert yeu_cau.status == "approved"
    assert yeu_cau.approved_by == toa_nha["manager"].id
    moc = db_session.query(PickupEvent).filter_by(request_id=yeu_cau.id).all()
    assert {m.kind for m in moc} == {"created", "threshold", "reviewed"}
    assert db_session.query(Notification).filter_by(user_id=yeu_cau.resident_id).count() == 1


def test_boi_canh_quyet_dinh_tinh_bang_sql(db_session: Session, toa_nha) -> None:
    _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=5, ngay=date(2026, 8, 5))
    yeu_cau = _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=40, ngay=date(2026, 8, 6))
    db_session.commit()

    boi_canh = pickup.decision_context(db_session, yeu_cau)

    assert boi_canh["resident_history"]["so_yeu_cau_truoc"] == 1
    assert boi_canh["building_context"]["so_yeu_cau"] >= 2
    assert boi_canh["capacity_context"]["tai_trong_xe_kg"] == 200.0


def test_da_xep_tuyen_thi_khong_huy_duoc(db_session: Session, toa_nha) -> None:
    yeu_cau = _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=5, ngay=date(2026, 8, 6))
    yeu_cau.status = "scheduled"

    with pytest.raises(ValueError, match="đã được xếp vào tuyến"):
        pickup.cancel_pickup(db_session, request=yeu_cau, actor=toa_nha["residents"]["S1-1203"])


# --- HITL #3: gộp tuyến --------------------------------------------------


def test_gop_cac_yeu_cau_cung_ngay_cung_khung_gio_cung_cum(db_session: Session, toa_nha) -> None:
    ngay = date(2026, 8, 6)
    _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=20, ngay=ngay)
    _tao_yeu_cau(db_session, toa_nha, "S1-0805", weight=15, ngay=ngay)
    _tao_yeu_cau(db_session, toa_nha, "S2-0501", weight=10, ngay=ngay)
    _tao_yeu_cau(db_session, toa_nha, "S3-0710", weight=10, ngay=ngay, khung="14:00-16:00")
    db_session.commit()

    tuyen = route_planner.propose_route(db_session, service_date=ngay, window="08:00-10:00")

    assert tuyen.status == "proposed", "Agent không được tự chốt lịch của người"
    assert len(tuyen.stops) == 3
    assert tuyen.reasoning["saved_trips"] == 2
    assert tuyen.reasoning["saved_km"] > 0
    ly_do_loai = " ".join(e["ly_do"] for e in tuyen.reasoning["excluded"])
    assert "lệch khung giờ" in ly_do_loai, "Phải nói rõ vì sao yêu cầu kia không được gộp"


def test_khong_gop_qua_tai_trong_xe(db_session: Session, toa_nha) -> None:
    ngay = date(2026, 8, 6)
    _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=100, ngay=ngay, duyet_luon=True)
    _tao_yeu_cau(db_session, toa_nha, "S1-0805", weight=100, ngay=ngay, duyet_luon=True)
    _tao_yeu_cau(db_session, toa_nha, "S2-0501", weight=100, ngay=ngay, duyet_luon=True)
    db_session.commit()

    tuyen = route_planner.propose_route(db_session, service_date=ngay, window="08:00-10:00", capacity_kg=200)

    assert tuyen.total_weight_kg <= 200
    assert any("tải trọng" in e["ly_do"] for e in tuyen.reasoning["excluded"])


def test_khong_co_yeu_cau_nao_thi_bao_loi_ro_rang(db_session: Session, toa_nha) -> None:
    with pytest.raises(ValueError, match="Không có yêu cầu nào đã duyệt"):
        route_planner.propose_route(db_session, service_date=date(2026, 12, 25), window="08:00-10:00")


def test_duyet_tuyen_thi_moi_yeu_cau_chuyen_sang_da_xep_lich(db_session: Session, toa_nha) -> None:
    ngay = date(2026, 8, 6)
    _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=20, ngay=ngay)
    _tao_yeu_cau(db_session, toa_nha, "S1-0805", weight=15, ngay=ngay)
    db_session.commit()
    tuyen = route_planner.propose_route(db_session, service_date=ngay, window="08:00-10:00", team_id=toa_nha["cleaner"].id)

    route_planner.review_route(db_session, route=tuyen, actor=toa_nha["manager"], action="approve")
    db_session.commit()

    assert tuyen.status == "approved"
    trang_thai = {db_session.get(PickupRequest, s.request_id).status for s in tuyen.stops}
    assert trang_thai == {"scheduled"}
    assert db_session.query(Notification).count() >= 3  # 2 cư dân + 1 đội vệ sinh


def test_sua_roi_duyet_thi_hien_duoc_diff_so_voi_ban_ai_de_xuat(db_session: Session, toa_nha) -> None:
    ngay = date(2026, 8, 6)
    a = _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=20, ngay=ngay)
    b = _tao_yeu_cau(db_session, toa_nha, "S1-0805", weight=15, ngay=ngay)
    c = _tao_yeu_cau(db_session, toa_nha, "S2-0501", weight=10, ngay=ngay)
    db_session.commit()
    tuyen = route_planner.propose_route(db_session, service_date=ngay, window="08:00-10:00")
    ban_ai = list(tuyen.proposed_stop_order)

    route_planner.review_route(
        db_session,
        route=tuyen,
        actor=toa_nha["manager"],
        action="approve_with_changes",
        removed_stops=[c.id],
        stop_order=[b.id, a.id],
    )
    db_session.commit()

    diff = route_planner.route_diff(tuyen)
    assert diff["changed"] is True
    assert c.id in diff["removed"]
    assert diff["proposed"] == ban_ai
    assert db_session.get(PickupRequest, c.id).status == "approved", "Điểm bị bỏ phải quay về nhóm chờ xếp tuyến"


def test_bo_diem_khoi_tuyen_thi_tinh_lai_quang_duong(db_session: Session, toa_nha) -> None:
    ngay = date(2026, 8, 6)
    a = _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=20, ngay=ngay)
    _tao_yeu_cau(db_session, toa_nha, "S1-0805", weight=15, ngay=ngay)
    db_session.commit()
    tuyen = route_planner.propose_route(db_session, service_date=ngay, window="08:00-10:00")
    khoi_luong_truoc = tuyen.total_weight_kg

    route_planner.review_route(
        db_session, route=tuyen, actor=toa_nha["manager"], action="approve_with_changes", removed_stops=[a.id]
    )

    assert tuyen.total_weight_kg < khoi_luong_truoc
    assert tuyen.reasoning["edited_by_human"] is True


def test_danh_dau_da_thu_va_bao_su_co(db_session: Session, toa_nha) -> None:
    ngay = date(2026, 8, 6)
    _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=20, ngay=ngay)
    _tao_yeu_cau(db_session, toa_nha, "S1-0805", weight=15, ngay=ngay)
    db_session.commit()
    tuyen = route_planner.propose_route(db_session, service_date=ngay, window="08:00-10:00")
    route_planner.review_route(db_session, route=tuyen, actor=toa_nha["manager"], action="approve")

    diem_dau, diem_sau = sorted(tuyen.stops, key=lambda s: s.seq)
    route_planner.complete_stop(db_session, stop=diem_dau, actor=toa_nha["cleaner"])
    assert tuyen.status == "in_progress"

    route_planner.complete_stop(
        db_session, stop=diem_sau, actor=toa_nha["cleaner"], issue="co_rac_nguy_hai", issue_note="Có pin lẫn trong thùng"
    )
    db_session.commit()

    assert tuyen.status == "done"
    assert diem_sau.issue == "co_rac_nguy_hai"


def test_ma_su_co_ngoai_danh_sach_thi_bao_loi(db_session: Session, toa_nha) -> None:
    ngay = date(2026, 8, 6)
    _tao_yeu_cau(db_session, toa_nha, "S1-1203", weight=20, ngay=ngay)
    db_session.commit()
    tuyen = route_planner.propose_route(db_session, service_date=ngay, window="08:00-10:00")

    with pytest.raises(ValueError, match="không nằm trong danh sách cố định"):
        route_planner.complete_stop(
            db_session, stop=tuyen.stops[0], actor=toa_nha["cleaner"], issue="tự nghĩ ra"
        )
