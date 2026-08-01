"""Định tuyến model 4 tầng cho việc phân loại rác.

| Tầng | Dùng khi | Chi phí |
|---|---|---|
| ``t0_cache`` | ảnh trùng/gần trùng đã phân loại (pHash) | $0 |
| ``t0_5_local`` | CLIP zero-shot chạy trên CPU, rất chắc và không phải nhóm nguy hại | $0 |
| ``t1_mini`` | model vision rẻ — phần lớn lưu lượng | thấp |
| ``t2_full`` | confidence thấp **hoặc nghi rác nguy hại** | cao |

Module này chỉ lo *chọn tầng nào và có dám trả lời không*. Việc tra quy định
của toà nằm ở :mod:`src.services.rag`, việc ghi bản ghi nằm ở lớp API.

Mọi bước đều sinh một :class:`NodeMetric` để màn Agent Run (spec 4.15) và trang
Vận hành (4.16) có số liệu thật, không phải số ước.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import get_settings
from src.db.models import Classification, Media, WasteCategory
from src.services import safety
from src.services.image import phash_distance
from src.services.safety import HardBlockRule, RefusalReason
from src.services.vision import (
    CategoryOption,
    VisionResult,
    VisionUnavailableError,
    classify_image_local,
    get_tier_models,
    get_vision_client,
)

TIER_T0_CACHE = "t0_cache"
TIER_T05_LOCAL = "t0_5_local"
TIER_T1 = "t1_mini"
TIER_T2 = "t2_full"

TIER_LABELS_VI: dict[str, str] = {
    TIER_T0_CACHE: "Đã biết câu trả lời",
    TIER_T05_LOCAL: "Nhận ra ngay trên máy",
    TIER_T1: "",
    TIER_T2: "Đã kiểm tra kỹ",
}


@dataclass
class NodeMetric:
    """Số liệu một bước xử lý — map thẳng vào bảng ``run_node_metrics``."""

    node: str
    status: str = "ok"
    duration_ms: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    image_tokens: int = 0
    cost_usd: float = 0.0
    cache_hits: int = 0
    llm_calls: int = 0
    retries: int = 0
    error_type: str = ""
    meta: dict = field(default_factory=dict)


@dataclass
class ClassifyOutcome:
    """Kết quả trọn vẹn của một lần phân loại."""

    item_name: str = ""
    category: WasteCategory | None = None
    confidence: float = 0.0
    min_confidence: float = 0.0
    confidence_level: str = "duoi_nguong"
    tier: str = ""
    model: str = ""
    provider: str = ""
    prompt_version: str = "v1"

    refused: bool = False
    refusal_reason: str = ""
    refusal_label_vi: str = ""
    refusal_headline_vi: str = ""
    guess_item_name: str = ""
    guess_category_code: str = ""

    hard_block: HardBlockRule | None = None
    escalation_reason: str = ""
    suspect_hazardous: bool = False
    safety_warning: str = ""
    items: list[dict] = field(default_factory=list)

    latency_ms: int = 0
    cost_usd: float = 0.0
    price_known: bool = True
    cache_source_id: int | None = None
    nodes: list[NodeMetric] = field(default_factory=list)

    @property
    def category_code(self) -> str:
        return self.category.code if self.category else ""


def load_category_options(session: Session) -> list[CategoryOption]:
    """Đọc danh mục rác từ CSDL thành danh sách lựa chọn đưa vào prompt."""
    rows = session.scalars(select(WasteCategory).order_by(WasteCategory.sort_order)).all()
    return [
        CategoryOption(code=c.code, name=c.name, is_hazardous=c.is_hazardous, hint=c.clip_prompts)
        for c in rows
    ]


def _category_by_code(session: Session, code: str) -> WasteCategory | None:
    if not code:
        return None
    return session.scalar(select(WasteCategory).where(WasteCategory.code == code))


def _refuse(
    outcome: ClassifyOutcome,
    reason: RefusalReason,
    *,
    headline: str = "",
) -> ClassifyOutcome:
    """Đánh dấu từ chối trả lời, giữ lại phỏng đoán để hiện trên màn 4.4.

    Phỏng đoán **vẫn hiện** nhưng dán nhãn rõ là phỏng đoán và không kèm hướng
    dẫn xử lý — đó là điểm khác nhau giữa "thận trọng" và "vô dụng".
    """
    outcome.refused = True
    outcome.refusal_reason = str(reason)
    outcome.refusal_label_vi = safety.REFUSAL_LABELS_VI[reason]
    outcome.refusal_headline_vi = headline or safety.REFUSAL_HEADLINE_VI
    outcome.guess_item_name = outcome.guess_item_name or outcome.item_name
    outcome.guess_category_code = outcome.guess_category_code or outcome.category_code
    # Từ chối thì không chốt nhãn, và tuyệt đối không kèm hướng dẫn xử lý.
    outcome.category = None
    outcome.item_name = ""
    outcome.safety_warning = ""
    return outcome


def _quality_refusal_reason(quality_issue: str) -> RefusalReason | None:
    mapping = {
        "anh_toi": RefusalReason.ANH_TOI,
        "mo": RefusalReason.ANH_MO,
        "vat_bi_che": RefusalReason.VAT_BI_CHE,
        "nhieu_vat": RefusalReason.NHIEU_VAT,
    }
    return mapping.get(quality_issue)


def _lookup_phash_cache(session: Session, phash: str) -> tuple[Classification, int] | None:
    """Tìm lần phân loại trước của ảnh trùng hoặc gần trùng.

    Trong chung cư, cùng một loại vỏ hộp được chụp lại rất nhiều lần — đây là
    tầng rẻ nhất và cũng là tầng hay trúng nhất.
    """
    if not phash:
        return None
    max_distance = get_settings().phash_max_distance

    rows = session.execute(
        select(Classification, Media)
        .join(Media, Classification.media_id == Media.id)
        .where(
            Media.phash != "",
            Classification.refused.is_(False),
            Classification.predicted_category_id.is_not(None),
        )
        .order_by(Classification.created_at.desc())
        .limit(300)
    ).all()

    best: tuple[Classification, int] | None = None
    for classification, media in rows:
        distance = phash_distance(phash, media.phash)
        if distance <= max_distance and (best is None or distance < best[1]):
            best = (classification, distance)
            if distance == 0:
                break
    return best


def _apply_vision_result(
    session: Session,
    outcome: ClassifyOutcome,
    result: VisionResult,
    tier: str,
) -> ClassifyOutcome:
    """Ghi kết quả model vào outcome và tính ngưỡng của nhóm tương ứng."""
    outcome.tier = tier
    outcome.model = result.model
    outcome.provider = result.provider
    outcome.item_name = result.item_name
    outcome.confidence = result.confidence
    outcome.items = result.items
    outcome.suspect_hazardous = result.suspect_hazardous
    outcome.category = _category_by_code(session, result.category_code)
    outcome.min_confidence = safety.min_confidence_for(outcome.category)
    outcome.confidence_level = safety.confidence_level(outcome.confidence, outcome.min_confidence)
    outcome.safety_warning = safety.safety_warning_for(outcome.category)
    return outcome


def classify_waste(
    session: Session,
    *,
    image_bytes: bytes | None = None,
    image_phash: str = "",
    text_query: str = "",
) -> ClassifyOutcome:
    """Chạy trọn định tuyến 4 tầng cho một món rác.

    Args:
        session: phiên CSDL để đọc danh mục và cache.
        image_bytes: ảnh **đã qua tiền xử lý** (:func:`src.services.image.preprocess_image`).
            Không bao giờ truyền ảnh gốc vào đây.
        image_phash: pHash của ảnh đã xử lý, dùng cho cache tầng T0.
        text_query: câu mô tả bằng chữ, dùng khi không có ảnh.

    Returns:
        :class:`ClassifyOutcome` — có thể ở trạng thái từ chối trả lời, và đó là
        một kết quả hợp lệ chứ không phải lỗi.
    """
    settings = get_settings()
    outcome = ClassifyOutcome(prompt_version=settings.prompt_version)
    started = time.perf_counter()

    # --- Bước 1: chặn cứng theo câu chữ người dùng, trước mọi lệnh gọi model ---
    step = time.perf_counter()
    rule = safety.check_hard_block(text_query)
    outcome.nodes.append(
        NodeMetric(
            node="safety_precheck",
            duration_ms=int((time.perf_counter() - step) * 1000),
            meta={"hard_block": rule.code if rule else ""},
        )
    )
    if rule is not None:
        outcome.hard_block = rule
        outcome.guess_item_name = rule.label_vi
        _refuse(outcome, RefusalReason.CHAN_CUNG, headline=safety.REFUSAL_HARD_BLOCK_VI)
        outcome.latency_ms = int((time.perf_counter() - started) * 1000)
        return outcome

    categories = load_category_options(session)

    # --- Bước 2: T0 — cache pHash ---
    if image_bytes is not None and image_phash:
        step = time.perf_counter()
        hit = _lookup_phash_cache(session, image_phash)
        duration = int((time.perf_counter() - step) * 1000)
        if hit is not None:
            previous, distance = hit
            outcome.nodes.append(
                NodeMetric(
                    node="cache_lookup",
                    duration_ms=duration,
                    cache_hits=1,
                    meta={"phash_distance": distance, "source_classification_id": previous.id},
                )
            )
            outcome.tier = TIER_T0_CACHE
            outcome.model = "cache"
            outcome.provider = "cache"
            outcome.item_name = previous.item_name
            outcome.confidence = previous.confidence
            outcome.category = session.get(WasteCategory, previous.predicted_category_id)
            outcome.min_confidence = safety.min_confidence_for(outcome.category)
            outcome.confidence_level = safety.confidence_level(outcome.confidence, outcome.min_confidence)
            outcome.safety_warning = safety.safety_warning_for(outcome.category)
            outcome.cache_source_id = previous.id
            outcome.latency_ms = int((time.perf_counter() - started) * 1000)
            return outcome
        outcome.nodes.append(NodeMetric(node="cache_lookup", duration_ms=duration, meta={"hit": False}))

    # --- Bước 3: T0.5 — model local, chỉ chốt khi rất chắc và không nguy hại ---
    if image_bytes is not None and settings.local_model_enabled:
        step = time.perf_counter()
        local = classify_image_local(image_bytes, categories)
        duration = int((time.perf_counter() - step) * 1000)
        if local is None:
            outcome.nodes.append(
                NodeMetric(node="local_model", status="skipped", duration_ms=duration, meta={"reason": "khong_san_sang"})
            )
        else:
            category = _category_by_code(session, local.category_code)
            is_hazard_related = local.suspect_hazardous or bool(category and category.is_hazardous)
            blocked_by_policy = is_hazard_related and settings.local_never_decides_hazardous
            accepted = local.confidence >= settings.clip_accept_confidence and not blocked_by_policy
            outcome.nodes.append(
                NodeMetric(
                    node="local_model",
                    duration_ms=duration,
                    meta={
                        "confidence": round(local.confidence, 4),
                        "nguong_chap_nhan": settings.clip_accept_confidence,
                        "chot_nhan": accepted,
                        "chan_vi_nghi_nguy_hai": blocked_by_policy,
                    },
                )
            )
            if accepted:
                _apply_vision_result(session, outcome, local, TIER_T05_LOCAL)
                outcome.latency_ms = int((time.perf_counter() - started) * 1000)
                return _finalize(outcome, text_query)

    # --- Bước 4: T1 → (nếu cần) T2 ---
    model_t1, model_t2, model_text = get_tier_models()
    try:
        client = get_vision_client()
    except VisionUnavailableError as exc:
        outcome.nodes.append(NodeMetric(node="classify_waste", status="error", error_type=exc.code))
        outcome.latency_ms = int((time.perf_counter() - started) * 1000)
        return _refuse(outcome, RefusalReason.MODEL_LOI, headline=exc.message_vi)

    step = time.perf_counter()
    try:
        if image_bytes is not None:
            result = client.classify_image(image_bytes, categories, model_t1)
        else:
            result = client.classify_text(text_query, categories, model_text or model_t1)
    except (VisionUnavailableError, ValueError) as exc:
        code = getattr(exc, "code", "VISION-500")
        outcome.nodes.append(
            NodeMetric(
                node="classify_waste",
                status="error",
                duration_ms=int((time.perf_counter() - step) * 1000),
                llm_calls=1,
                error_type=code,
            )
        )
        outcome.latency_ms = int((time.perf_counter() - started) * 1000)
        message = getattr(exc, "message_vi", "Hệ thống nhận diện đang gặp sự cố.")
        return _refuse(outcome, RefusalReason.MODEL_LOI, headline=message)

    _apply_vision_result(session, outcome, result, TIER_T1)
    outcome.cost_usd += result.usage.cost_usd
    outcome.price_known = outcome.price_known and result.usage.price_known
    outcome.nodes.append(
        NodeMetric(
            node="classify_waste",
            duration_ms=int((time.perf_counter() - step) * 1000),
            tokens_in=result.usage.tokens_in,
            tokens_out=result.usage.tokens_out,
            image_tokens=result.usage.image_tokens,
            cost_usd=result.usage.cost_usd,
            llm_calls=1,
            meta={
                "tier": TIER_T1,
                "model": result.model,
                "confidence": round(result.confidence, 4),
                "nguong_nhom": round(outcome.min_confidence, 4),
            },
        )
    )

    escalation = safety.should_escalate_to_t2(
        outcome.confidence, outcome.min_confidence, result.suspect_hazardous
    )
    if escalation and model_t2 and model_t2 != model_t1:
        outcome.escalation_reason = escalation
        step = time.perf_counter()
        try:
            if image_bytes is not None:
                result_t2 = client.classify_image(image_bytes, categories, model_t2)
            else:
                result_t2 = client.classify_text(text_query, categories, model_t2)
        except (VisionUnavailableError, ValueError) as exc:
            # T2 lỗi thì giữ kết quả T1 và để bước kiểm ngưỡng bên dưới quyết
            # định — không được im lặng nâng cấp độ tin cậy.
            outcome.nodes.append(
                NodeMetric(
                    node="classify_waste_t2",
                    status="error",
                    duration_ms=int((time.perf_counter() - step) * 1000),
                    llm_calls=1,
                    error_type=getattr(exc, "code", "VISION-500"),
                )
            )
        else:
            _apply_vision_result(session, outcome, result_t2, TIER_T2)
            outcome.cost_usd += result_t2.usage.cost_usd
            outcome.price_known = outcome.price_known and result_t2.usage.price_known
            outcome.nodes.append(
                NodeMetric(
                    node="classify_waste_t2",
                    duration_ms=int((time.perf_counter() - step) * 1000),
                    tokens_in=result_t2.usage.tokens_in,
                    tokens_out=result_t2.usage.tokens_out,
                    image_tokens=result_t2.usage.image_tokens,
                    cost_usd=result_t2.usage.cost_usd,
                    llm_calls=1,
                    meta={
                        "tier": TIER_T2,
                        "model": result_t2.model,
                        "ly_do_escalate": escalation,
                        "confidence": round(result_t2.confidence, 4),
                    },
                )
            )
        outcome.suspect_hazardous = outcome.suspect_hazardous or result.suspect_hazardous

    outcome.latency_ms = int((time.perf_counter() - started) * 1000)
    return _finalize(outcome, text_query, quality_issue=result.quality_issue)


def _finalize(outcome: ClassifyOutcome, text_query: str, quality_issue: str = "") -> ClassifyOutcome:
    """Kiểm tra an toàn lần cuối trước khi dám trả lời.

    Thứ tự ưu tiên: chặn cứng → chất lượng ảnh → ngưỡng của nhóm. Chặn cứng
    đứng trước vì nó **bỏ qua confidence** hoàn toàn.
    """
    step = time.perf_counter()
    rule = safety.check_hard_block(outcome.item_name, text_query)
    outcome.nodes.append(
        NodeMetric(
            node="safety_check",
            duration_ms=int((time.perf_counter() - step) * 1000),
            meta={"hard_block": rule.code if rule else "", "danh_sach_chan_cung": len(safety.HARD_BLOCK_RULES)},
        )
    )
    if rule is not None:
        outcome.hard_block = rule
        return _refuse(outcome, RefusalReason.CHAN_CUNG, headline=safety.REFUSAL_HARD_BLOCK_VI)

    if not outcome.category:
        return _refuse(outcome, RefusalReason.KHONG_NHAN_RA)

    if outcome.confidence < outcome.min_confidence:
        quality_reason = _quality_refusal_reason(quality_issue)
        if quality_reason is not None:
            return _refuse(outcome, quality_reason)
        if outcome.category.is_hazardous or outcome.suspect_hazardous:
            return _refuse(outcome, RefusalReason.NGHI_NGUY_HAI, headline=safety.REFUSAL_HAZARD_VI)
        return _refuse(outcome, RefusalReason.DUOI_NGUONG)

    return outcome
