"""Lớp truy cập model vision, tách rời khỏi phần còn lại của hệ thống.

Dùng như sau::

    from src.services.vision import get_vision_client, get_tier_models

    client = get_vision_client()
    result = client.classify_image(image_bytes, categories, model=get_tier_models()[0])
"""

from __future__ import annotations

from src.config import get_settings
from src.services.vision.base import (
    PROMPT_VERSION,
    CategoryOption,
    Usage,
    VisionClient,
    VisionResult,
    VisionUnavailableError,
)
from src.services.vision.gemini import GeminiClient, build_gemini_client
from src.services.vision.local_clip import (
    classify_image_local,
)
from src.services.vision.local_clip import (
    is_loaded as local_model_loaded,
)
from src.services.vision.local_clip import (
    warm_up as warm_up_local_model,
)
from src.services.vision.openai_compat import OpenAICompatibleClient, build_openai_compatible_client

__all__ = [
    "PROMPT_VERSION",
    "CategoryOption",
    "GeminiClient",
    "OpenAICompatibleClient",
    "Usage",
    "VisionClient",
    "VisionResult",
    "VisionUnavailableError",
    "classify_image_local",
    "get_tier_models",
    "get_vision_client",
    "local_model_loaded",
    "provider_status",
    "warm_up_local_model",
]


def get_vision_client() -> VisionClient:
    """Trả về client theo ``VISION_PROVIDER`` trong ``.env``.

    Raises:
        VisionUnavailableError: khi provider là ``local_only`` (không có model
            đám mây nào để gọi) hoặc tên provider không hợp lệ.
    """
    provider = get_settings().vision_provider
    if provider == "gemini":
        return build_gemini_client()
    if provider in {"openai", "openrouter", "nvidia"}:
        return build_openai_compatible_client(provider)
    if provider == "local_only":
        raise VisionUnavailableError(
            "Đang chạy ở chế độ chỉ dùng model local, không gọi model đám mây.",
            code="VISION-LOCAL",
        )
    raise VisionUnavailableError(f"VISION_PROVIDER='{provider}' không hợp lệ.", code="VISION-400")


def get_tier_models() -> tuple[str, str, str]:
    """``(model_T1, model_T2, model_text)`` của provider đang chọn."""
    return get_settings().resolve_models()


def provider_status() -> dict[str, object]:
    """Tóm tắt cấu hình model để hiện trên trang Vận hành.

    Có key hay không là thông tin vận hành cần thiết; **giá trị key không bao
    giờ được trả ra ngoài**.
    """
    settings = get_settings()
    t1, t2, text = settings.resolve_models()
    return {
        "provider": settings.vision_provider,
        "has_api_key": bool(settings.provider_api_key),
        "model_t1": t1,
        "model_t2": t2,
        "model_text": text,
        "local_model_enabled": settings.local_model_enabled,
        "local_model_name": settings.clip_model_name if settings.local_model_enabled else "",
        "prompt_version": settings.prompt_version,
    }
