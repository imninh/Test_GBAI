"""Schema cơ sở dữ liệu cho GreenBin AI (VHR-17).

Nguyên tắc thiết kế:

* ``Media`` tách khỏi ``Classification``: ảnh có vòng đời riêng (hạn lưu trữ,
  cờ đã tước EXIF, cờ đã làm mờ khuôn mặt) và là nơi chịu trách nhiệm về
  quyền riêng tư. Hai cờ đó hiển thị được lên UI làm bằng chứng tuân thủ.
* ``Classification`` ghi lại ``tier`` và ``model`` của từng lần phân loại —
  đây là dữ liệu để chứng minh việc định tuyến model 3 tầng có hiệu quả.
* ``AgentRun`` / ``RunNodeMetric`` có mặt từ đầu vì yêu cầu chương trình bắt
  buộc theo dõi độ trễ, lỗi, chi phí và trace được chuỗi xử lý.
* Mọi hành động rủi ro (duyệt thu gom lớn, chốt tuyến, xem ảnh gốc) đều phải
  ghi ``AuditLog``.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


# --- Người dùng và địa điểm ---------------------------------------------


class User(Base):
    """Người dùng hệ thống.

    Ba vai trò, trong đó ``resident`` và ``manager`` là hai vai trò bắt buộc
    theo yêu cầu tối thiểu của chương trình; ``cleaner`` là đội vệ sinh.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20), index=True)  # resident | cleaner | manager
    password_hash: Mapped[str] = mapped_column(String(255))
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    green_points: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Building(Base):
    """Toà nhà. Quy định phân loại và lịch thu gom khác nhau giữa các toà."""

    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str] = mapped_column(String(300), default="")
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Unit(Base):
    """Căn hộ."""

    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)
    code: Mapped[str] = mapped_column(String(30))

    building: Mapped[Building] = relationship()


# --- Danh mục rác --------------------------------------------------------


class WasteCategory(Base):
    """Danh mục loại rác và hướng dẫn xử lý.

    ``is_hazardous`` quyết định ngưỡng an toàn: nhóm nguy hại dùng ngưỡng
    confidence cao hơn và luôn kèm cảnh báo cố định, không để LLM tự sinh.
    """

    __tablename__ = "waste_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    parent_code: Mapped[str] = mapped_column(String(40), default="")
    is_hazardous: Mapped[bool] = mapped_column(default=False, index=True)
    # Ngưỡng confidence tối thiểu để hệ thống dám tự trả lời cho nhóm này.
    min_confidence: Mapped[float] = mapped_column(Float, default=0.6)
    bin_color: Mapped[str] = mapped_column(String(30), default="")
    handling_note: Mapped[str] = mapped_column(Text, default="")
    safety_warning: Mapped[str] = mapped_column(Text, default="")
    # Gợi ý icon cho UI. Màu KHÔNG được là kênh thông tin duy nhất (spec 2.2).
    icon: Mapped[str] = mapped_column(String(16), default="")
    sort_order: Mapped[int] = mapped_column(default=0)
    # Nhãn tiếng Anh dùng cho CLIP zero-shot ở tầng T0.5, phân cách bằng "|".
    clip_prompts: Mapped[str] = mapped_column(Text, default="")


# --- Ảnh và phân loại ----------------------------------------------------


class Media(Base):
    """Ảnh do cư dân tải lên. Chịu trách nhiệm về quyền riêng tư.

    Ảnh gốc KHÔNG bao giờ được gửi tới API khi chưa qua tiền xử lý: tước EXIF
    (chứa toạ độ GPS), làm mờ khuôn mặt, nén về 512px.
    """

    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    uploader_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    stored_path: Mapped[str] = mapped_column(String(400))
    # Ảnh gốc chưa xử lý. Chỉ BQL được mở, và mỗi lần mở đều ghi AuditLog.
    original_path: Mapped[str] = mapped_column(String(400), default="")
    # Băm tri giác — dùng làm cache tầng 0, ảnh trùng/gần trùng không gọi lại API.
    phash: Mapped[str] = mapped_column(String(32), index=True, default="")
    width: Mapped[int] = mapped_column(default=0)
    height: Mapped[int] = mapped_column(default=0)
    bytes_size: Mapped[int] = mapped_column(default=0)
    original_width: Mapped[int] = mapped_column(default=0)
    original_height: Mapped[int] = mapped_column(default=0)
    original_bytes_size: Mapped[int] = mapped_column(default=0)

    exif_stripped: Mapped[bool] = mapped_column(default=False)
    faces_blurred: Mapped[int] = mapped_column(default=0)  # số khuôn mặt đã làm mờ
    # Các trường metadata đã bị xoá, dạng [{field, value_before}] — đây là dữ
    # liệu cho màn "Ảnh của tôi đã được xử lý thế nào" (spec 4.5).
    removed_fields: Mapped[list] = mapped_column(JSON, default=list)
    # Hạn lưu trữ. Job dọn dẹp xoá ảnh quá hạn; ảnh dùng cho eval tách riêng.
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    kept_for_eval: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Classification(Base):
    """Một lần phân loại rác — từ ảnh hoặc từ mô tả bằng chữ."""

    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"), nullable=True, index=True)
    text_query: Mapped[str] = mapped_column(Text, default="")
    input_type: Mapped[str] = mapped_column(String(10), default="image")  # image | text
    asker_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    building_id: Mapped[int | None] = mapped_column(ForeignKey("buildings.id"), nullable=True)
    item_name: Mapped[str] = mapped_column(String(200), default="")  # tên món AI nhận ra
    # Khi ảnh có nhiều món: [{name, category_code, confidence}] (spec 4.3 ⑦).
    items: Mapped[list] = mapped_column(JSON, default=list)

    predicted_category_id: Mapped[int | None] = mapped_column(ForeignKey("waste_categories.id"), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    # t0_cache | t1_mini | t2_full | local — chứng minh hiệu quả định tuyến 3 tầng.
    tier: Mapped[str] = mapped_column(String(20), default="", index=True)
    model: Mapped[str] = mapped_column(String(60), default="")
    prompt_version: Mapped[str] = mapped_column(String(20), default="")

    # Hệ thống từ chối trả lời khi dưới ngưỡng an toàn — ghi lại để đo tỉ lệ.
    refused: Mapped[bool] = mapped_column(default=False)
    refusal_reason: Mapped[str] = mapped_column(String(120), default="")
    escalated_to_human: Mapped[bool] = mapped_column(default=False)
    # Vì sao phải leo từ T1 lên T2: "confidence thấp" hoặc "nghi rác nguy hại".
    escalation_reason: Mapped[str] = mapped_column(String(160), default="")
    # Suy giảm một phần: nhận ra món rác nhưng node advise lỗi (spec mục 6.4).
    degraded: Mapped[bool] = mapped_column(default=False)
    degraded_note: Mapped[str] = mapped_column(String(200), default="")

    # Nhãn đúng do người xác nhận. Nguồn dữ liệu cho eval và cải tiến.
    human_label_id: Mapped[int | None] = mapped_column(ForeignKey("waste_categories.id"), nullable=True)
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    advice: Mapped[str] = mapped_column(Text, default="")
    advice_sources: Mapped[list] = mapped_column(JSON, default=list)  # id các chunk đã trích dẫn

    latency_ms: Mapped[int] = mapped_column(default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    run_id: Mapped[int | None] = mapped_column(ForeignKey("agent_runs.id"), nullable=True)
    # Bản ghi mô phỏng để trang Vận hành / Chất lượng AI có hình dạng lúc demo.
    # UI BẮT BUỘC hiện nhãn "dữ liệu demo mô phỏng" cho các bản ghi này.
    is_seed: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class ClassificationFeedback(Base):
    """Phản hồi 👍/👎 của người dùng về một lần phân loại.

    Bấm 👎 sẽ đẩy ca đó vào hàng đợi xác nhận nhãn của BQL (HITL #2) và chảy
    ngược vào tập cải tiến (PLO 7).
    """

    __tablename__ = "classification_feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    classification_id: Mapped[int] = mapped_column(ForeignKey("classifications.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_correct: Mapped[bool] = mapped_column(default=True)
    suggested_category_code: Mapped[str] = mapped_column(String(40), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


# --- Kho tri thức (RAG) --------------------------------------------------


class KnowledgeDoc(Base):
    """Tài liệu nguồn: quy định pháp luật, nội quy toà nhà, lịch thu gom."""

    __tablename__ = "knowledge_docs"

    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int | None] = mapped_column(ForeignKey("buildings.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    source: Mapped[str] = mapped_column(String(300), default="")
    doc_type: Mapped[str] = mapped_column(String(40), default="")  # law | building_rule | schedule | hazard
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class KnowledgeChunk(Base):
    """Đoạn văn bản đã cắt để truy hồi.

    ``embedding`` lưu dạng JSON list cho SQLite. Khi chuyển sang PostgreSQL
    thì đổi sang kiểu ``vector`` của pgvector, phần còn lại giữ nguyên.
    """

    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    doc_id: Mapped[int] = mapped_column(ForeignKey("knowledge_docs.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    section: Mapped[str] = mapped_column(String(200), default="")
    embedding: Mapped[list] = mapped_column(JSON, default=list)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)


# --- Thu gom -------------------------------------------------------------


class PickupRequest(Base):
    """Yêu cầu thu gom đồ cồng kềnh / rác tái chế khối lượng lớn.

    Vượt ngưỡng khối lượng hoặc số món thì ``requires_hitl=True`` và phải được
    BQL/đội vệ sinh xác nhận trước khi lên lịch — đúng ràng buộc của đề.
    """

    __tablename__ = "pickup_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    resident_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), index=True)
    items: Mapped[list] = mapped_column(JSON, default=list)  # [{name, category_code, qty, media_id}]
    # Khối lượng lưu thành KHOẢNG (ADR-0003): vision ước lượng kg từ ảnh sai
    # vài lần là bình thường, nên ngưỡng HITL so với ``weight_max_kg`` —
    # sai số phải nghiêng về phía cần người duyệt.
    weight_min_kg: Mapped[float] = mapped_column(Float, default=0.0)
    weight_max_kg: Mapped[float] = mapped_column(Float, default=0.0)
    # Giữ lại để tương thích code cũ; bằng trung điểm của khoảng.
    est_weight_kg: Mapped[float] = mapped_column(Float, default=0.0)
    preferred_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    preferred_window: Mapped[str] = mapped_column(String(30), default="")
    note: Mapped[str] = mapped_column(Text, default="")

    requires_hitl: Mapped[bool] = mapped_column(default=False, index=True)
    # Các ngưỡng đã kích hoạt: [{rule, value, threshold, label_vi}] — màn duyệt
    # BẮT BUỘC hiển thị khối này, hàng đợi không nói lý do là hàng đợi vô nghĩa.
    threshold_hit: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    # pending | approved | rejected | scheduled | done | cancelled
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reject_reason: Mapped[str] = mapped_column(String(80), default="")
    review_note: Mapped[str] = mapped_column(Text, default="")

    is_seed: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class PickupEvent(Base):
    """Một mốc trên timeline của yêu cầu thu gom (spec 4.8).

    Timeline là nơi HITL hiện ra với người dùng cuối, nên phải ghi thành bản
    ghi thật chứ không dựng lại từ trạng thái hiện tại.
    """

    __tablename__ = "pickup_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("pickup_requests.id"), index=True)
    kind: Mapped[str] = mapped_column(String(40))  # created | threshold | reviewed | routed | done | cancelled
    label_vi: Mapped[str] = mapped_column(String(200))
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class PickupRoute(Base):
    """Một chuyến thu gom do agent gộp lịch đề xuất, người duyệt mới chốt."""

    __tablename__ = "pickup_routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_date: Mapped[date] = mapped_column(Date, index=True)
    window: Mapped[str] = mapped_column(String(30), default="")
    team_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="proposed", index=True)
    # proposed | approved | in_progress | done
    total_weight_kg: Mapped[float] = mapped_column(Float, default=0.0)
    est_distance_km: Mapped[float] = mapped_column(Float, default=0.0)
    # Khối "Vì sao gộp thế này" (spec 4.12) — quan trọng bằng chính cái tuyến:
    # {criteria[], excluded[], baseline_km, saved_km, capacity_kg}.
    reasoning: Mapped[dict] = mapped_column(JSON, default=dict)
    # Bản AI đề xuất ban đầu, giữ nguyên để hiện diff khi người duyệt sửa tay.
    proposed_stop_order: Mapped[list] = mapped_column(JSON, default=list)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    run_id: Mapped[int | None] = mapped_column(ForeignKey("agent_runs.id"), nullable=True)
    is_seed: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    stops: Mapped[list[RouteStop]] = relationship(back_populates="route", cascade="all, delete-orphan")


class RouteStop(Base):
    """Một điểm dừng trong chuyến thu gom."""

    __tablename__ = "route_stops"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("pickup_routes.id"), index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("pickup_requests.id"), index=True)
    seq: Mapped[int] = mapped_column(default=0)
    done_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # Đội vệ sinh báo phát sinh tại điểm dừng (spec 4.9).
    issue: Mapped[str] = mapped_column(String(80), default="")
    issue_note: Mapped[str] = mapped_column(Text, default="")
    actual_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    route: Mapped[PickupRoute] = relationship(back_populates="stops")


# --- Vận hành và kiểm toán ----------------------------------------------


class AgentRun(Base):
    """Một lần chạy pipeline agent. Gốc của màn Agent Run / Trace trên UI."""

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(40), default="classify")  # classify | schedule | batch_eval
    trigger: Mapped[str] = mapped_column(String(30), default="manual")
    status: Mapped[str] = mapped_column(String(20), default="running", index=True)
    items_processed: Mapped[int] = mapped_column(default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    duration_ms: Mapped[int] = mapped_column(default=0)
    error: Mapped[str] = mapped_column(Text, default="")
    is_seed: Mapped[bool] = mapped_column(default=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    nodes: Mapped[list[RunNodeMetric]] = relationship(back_populates="run", cascade="all, delete-orphan")


class RunNodeMetric(Base):
    """Số liệu một node trong một lần chạy: độ trễ, lỗi, chi phí."""

    __tablename__ = "run_node_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("agent_runs.id"), index=True)
    node: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(20), default="ok")
    duration_ms: Mapped[int] = mapped_column(default=0)
    tokens_in: Mapped[int] = mapped_column(default=0)
    tokens_out: Mapped[int] = mapped_column(default=0)
    image_tokens: Mapped[int] = mapped_column(default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    cache_hits: Mapped[int] = mapped_column(default=0)
    llm_calls: Mapped[int] = mapped_column(default=0)
    retries: Mapped[int] = mapped_column(default=0)
    error_type: Mapped[str] = mapped_column(String(80), default="")
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    run: Mapped[AgentRun] = relationship(back_populates="nodes")


class AuditLog(Base):
    """Nhật ký kiểm toán cho mọi hành động rủi ro hoặc chạm dữ liệu nhạy cảm."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(60), index=True)
    entity: Mapped[str] = mapped_column(String(60))
    entity_id: Mapped[str] = mapped_column(String(60), default="")
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


# --- Lịch thu gom, cảnh báo, thông báo -----------------------------------


class CollectionSchedule(Base):
    """Lịch thu gom theo nhóm rác của từng toà.

    Hướng dẫn "bỏ ở đâu, thu gom lúc nào" chỉ đúng với toà đang chọn — đây là
    bảng làm cho câu đó đúng, và là dữ liệu cho màn Lịch xem được offline.
    """

    __tablename__ = "collection_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)
    category_code: Mapped[str] = mapped_column(String(40), index=True)
    weekdays: Mapped[list] = mapped_column(JSON, default=list)  # 0=Thứ 2 … 6=Chủ nhật
    window: Mapped[str] = mapped_column(String(30), default="")  # "18:00-20:00"
    location: Mapped[str] = mapped_column(String(200), default="")


class Alert(Base):
    """Cảnh báo hiện trên dải đầu màn Tổng quan của BQL."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    severity: Mapped[str] = mapped_column(String(20), default="info", index=True)  # critical | warning | info
    title: Mapped[str] = mapped_column(String(300))
    building_id: Mapped[int | None] = mapped_column(ForeignKey("buildings.id"), nullable=True, index=True)
    entity: Mapped[str] = mapped_column(String(60), default="")
    entity_id: Mapped[str] = mapped_column(String(60), default="")
    threshold: Mapped[str] = mapped_column(String(120), default="")
    ack: Mapped[bool] = mapped_column(default=False, index=True)
    ack_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_seed: Mapped[bool] = mapped_column(default=False, index=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class Notification(Base):
    """Thông báo gửi cho cư dân / đội vệ sinh khi có quyết định của người duyệt."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, default="")
    entity: Mapped[str] = mapped_column(String(60), default="")
    entity_id: Mapped[str] = mapped_column(String(60), default="")
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


# --- Eval ----------------------------------------------------------------


class EvalRun(Base):
    """Một lần chạy eval trên tập test giữ riêng.

    Tách ``by_dataset`` công khai / tự chụp vì chênh lệch giữa hai bộ là một
    phát hiện đáng đưa vào báo cáo (CLAUDE.md mục 6).
    """

    __tablename__ = "eval_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset: Mapped[str] = mapped_column(String(30), default="public")  # public | own | mixed
    test_size: Mapped[int] = mapped_column(default=0)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    macro_f1: Mapped[float] = mapped_column(Float, default=0.0)
    hazard_recall: Mapped[float] = mapped_column(Float, default=0.0)
    # Chỉ số an toàn cốt lõi: rác nguy hại bị phân loại thành rác thường.
    hazard_missed_count: Mapped[int] = mapped_column(default=0)
    retrieval_precision_at_5: Mapped[float] = mapped_column(Float, default=0.0)
    confusion_matrix: Mapped[dict] = mapped_column(JSON, default=dict)
    prompt_version: Mapped[str] = mapped_column(String(20), default="")
    model: Mapped[str] = mapped_column(String(60), default="")
    avg_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    p95_latency_ms: Mapped[int] = mapped_column(default=0)
    is_seed: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class FailureCase(Base):
    """Một ca AI nhận sai, kèm phân loại nguyên nhân.

    Đây là lợi thế demo lớn nhất của đề: trình chiếu được ảnh thật bị nhận sai.
    """

    __tablename__ = "failure_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    eval_run_id: Mapped[int | None] = mapped_column(ForeignKey("eval_runs.id"), nullable=True, index=True)
    classification_id: Mapped[int | None] = mapped_column(ForeignKey("classifications.id"), nullable=True)
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    item_name: Mapped[str] = mapped_column(String(200), default="")
    true_category_code: Mapped[str] = mapped_column(String(40), default="")
    predicted_category_code: Mapped[str] = mapped_column(String(40), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    # ảnh tối | nhiều vật | vật bị che | chất liệu hỗn hợp | góc chụp lạ
    cause: Mapped[str] = mapped_column(String(40), default="")
    resolved: Mapped[bool] = mapped_column(default=False)
    is_seed: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
