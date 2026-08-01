"""Tầng T0.5 — CLIP zero-shot chạy offline trên CPU.

Vì sao zero-shot mà không fine-tune: nhóm chưa có bộ ảnh tự chụp đủ lớn, mà
``docs/research/sota-model-nhe-phan-loai-rac.md`` đã chỉ ra model fine-tune trên
dataset công khai rớt từ 94% xuống 41% trên ảnh rác thật. Zero-shot không hứa
hẹn gì về accuracy, nên nó được dùng đúng vai trò của mình: **một cổng chặn rẻ
đứng trước API trả phí**, chỉ chốt khi rất chắc.

Hai ràng buộc an toàn cứng:

* dưới ``clip_accept_confidence`` thì không kết luận, đẩy lên T1;
* **không bao giờ được chốt nhãn cho nhóm nguy hại** — dù điểm số cao tới đâu.
  Sai ở nhóm đó gây hại thật, và một model 350MB không có khả năng đọc nhãn
  chai hoá chất (CLAUDE.md mục 5).

Model tải một lần (~350MB) về cache HuggingFace rồi chạy hoàn toàn offline.
"""

from __future__ import annotations

import io
import logging

from PIL import Image

from src.config import get_settings
from src.services.vision.base import CategoryOption, Usage, VisionResult

logger = logging.getLogger(__name__)

_model = None
_processor = None
_load_failed = False


def _load() -> tuple[object, object] | None:
    """Nạp CLIP một lần. Trả về ``None`` nếu không nạp được.

    Không nạp được thì hệ thống bỏ qua tầng T0.5 và đi thẳng T1 — mất một tầng
    tiết kiệm chi phí, nhưng không ai bị chặn.
    """
    global _model, _processor, _load_failed
    if _load_failed:
        return None
    if _model is not None and _processor is not None:
        return _model, _processor

    try:
        import torch  # noqa: F401  (kiểm tra có sẵn trước khi nạp transformers)
        from transformers import CLIPModel, CLIPProcessor
    except ImportError:
        logger.warning("Chưa cài torch/transformers — bỏ qua tầng T0.5 model local.")
        _load_failed = True
        return None

    name = get_settings().clip_model_name
    try:
        _model = CLIPModel.from_pretrained(name)
        _processor = CLIPProcessor.from_pretrained(name)
        _model.eval()
    except (OSError, ValueError) as exc:
        logger.warning("Không nạp được model local '%s': %s. Bỏ qua tầng T0.5.", name, exc)
        _load_failed = True
        return None

    logger.info("Đã nạp model local T0.5: %s", name)
    return _model, _processor


def is_loaded() -> bool:
    """Model đã nạp sẵn trong bộ nhớ chưa — **không kích hoạt việc tải model**.

    Trang Vận hành dùng hàm này. Dùng nhầm hàm có tác dụng phụ ở một endpoint
    chỉ đọc sẽ khiến request đầu tiên treo vài phút để tải 350MB.
    """
    return _model is not None and _processor is not None


def warm_up() -> bool:
    """Nạp model ngay (tải về nếu chưa có). Gọi chủ động khi khởi động server."""
    return get_settings().local_model_enabled and _load() is not None


def _prompts_for(category: CategoryOption) -> list[str]:
    """Sinh các câu mô tả tiếng Anh để CLIP chấm độ khớp với ảnh."""
    if category.hint:
        return [p.strip() for p in category.hint.split("|") if p.strip()]
    return [f"a photo of {category.name}"]


def classify_image_local(image_bytes: bytes, categories: list[CategoryOption]) -> VisionResult | None:
    """Chấm ảnh bằng CLIP. Trả về ``None`` khi không dùng được model local.

    Kết quả trả về vẫn có thể có ``confidence`` thấp — người gọi
    (:mod:`src.services.classifier`) là nơi quyết định chấp nhận hay leo tầng.
    """
    settings = get_settings()
    if not settings.local_model_enabled:
        return None

    loaded = _load()
    if loaded is None:
        return None
    model, processor = loaded

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except (OSError, ValueError):
        return None

    prompts: list[str] = []
    owner: list[CategoryOption] = []
    for category in categories:
        for prompt in _prompts_for(category):
            prompts.append(prompt)
            owner.append(category)
    if not prompts:
        return None

    import torch

    inputs = processor(text=prompts, images=image, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)[0]

    # Gộp điểm của các câu mô tả cùng một nhóm: lấy điểm cao nhất trong nhóm.
    best_by_code: dict[str, float] = {}
    for prob, category in zip(probs.tolist(), owner, strict=True):
        best_by_code[category.code] = max(best_by_code.get(category.code, 0.0), float(prob))
    if not best_by_code:
        return None

    top_code = max(best_by_code, key=lambda c: best_by_code[c])
    top_category = next(c for c in categories if c.code == top_code)
    confidence = best_by_code[top_code]

    suspect_hazardous = any(
        best_by_code.get(c.code, 0.0) > 0.15 for c in categories if c.is_hazardous
    ) or top_category.is_hazardous

    return VisionResult(
        item_name=top_category.name,
        category_code=top_code,
        confidence=confidence,
        reason=f"Model local CLIP khớp cao nhất với nhóm {top_category.name}",
        quality_issue="",
        suspect_hazardous=suspect_hazardous,
        model=get_settings().clip_model_name,
        provider="local_clip",
        # Chạy trên máy mình nên chi phí bằng 0, và đây là con số ĐO ĐƯỢC
        # chứ không phải ước tính — khác với các model free tier.
        usage=Usage(cost_usd=0.0, price_known=True),
        raw_text="",
    )
