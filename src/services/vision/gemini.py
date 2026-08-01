"""Provider Gemini — mặc định của dự án khi chưa có API key OpenAI.

Gọi thẳng REST ``generativelanguage.googleapis.com`` bằng ``httpx``, không dùng
SDK, để giữ danh sách phụ thuộc gọn và để việc đổi sang OpenAI về sau chỉ là
đổi một dòng trong ``.env``.
"""

from __future__ import annotations

import base64

import httpx

from src.config import get_settings
from src.services.vision.base import (
    CategoryOption,
    Usage,
    VisionResult,
    VisionUnavailableError,
    build_image_prompt,
    build_text_prompt,
    estimate_cost,
    parse_model_json,
    result_from_json,
)

_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
_TIMEOUT_SECONDS = 60.0

# Mức "suy nghĩ" thấp nhất mà `gemini-flash-latest` và `gemini-flash-lite-latest`
# chấp nhận (đo 01/08/2026 — đặt 0 thì API trả 400). Xem chú thích ở ``_call``.
_THINKING_BUDGET = 128


class GeminiClient:
    """Gọi model Gemini qua REST."""

    provider_name = "gemini"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def classify_image(self, image_bytes: bytes, categories: list[CategoryOption], model: str) -> VisionResult:
        parts = [
            {"text": build_image_prompt(categories)},
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(image_bytes).decode("ascii"),
                }
            },
        ]
        return self._call(model, parts, categories)

    def classify_text(self, text: str, categories: list[CategoryOption], model: str) -> VisionResult:
        return self._call(model, [{"text": build_text_prompt(text, categories)}], categories)

    def generate_text(self, prompt: str, model: str, max_tokens: int = 500) -> tuple[str, Usage]:
        """Sinh văn bản thuần (dùng cho node advise). Trả về ``(text, usage)``."""
        if not self._api_key:
            raise VisionUnavailableError("Chưa cấu hình GEMINI_API_KEY trong .env.", code="VISION-401")

        url = f"{_BASE_URL}/models/{model}:generateContent?key={self._api_key}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": max_tokens},
        }
        try:
            with httpx.Client(timeout=_TIMEOUT_SECONDS) as client:
                response = client.post(url, json=payload)
        except httpx.HTTPError as exc:
            raise VisionUnavailableError("Không kết nối được tới máy chủ model.", code="VISION-503") from exc
        if response.status_code >= 400:
            raise VisionUnavailableError(f"Gemini trả về lỗi {response.status_code}.", code=f"VISION-{response.status_code}")

        body = response.json()
        candidates = body.get("candidates") or []
        text = "".join(p.get("text", "") for p in (candidates[0].get("content") or {}).get("parts", [])) if candidates else ""

        meta = body.get("usageMetadata") or {}
        tokens_in = int(meta.get("promptTokenCount", 0) or 0)
        tokens_out = int(meta.get("candidatesTokenCount", 0) or 0)
        cost, price_known = estimate_cost(model, tokens_in, tokens_out)
        return text, Usage(tokens_in=tokens_in, tokens_out=tokens_out, cost_usd=cost, price_known=price_known)

    def embed(self, texts: list[str], model: str = "text-embedding-004") -> list[list[float]]:
        """Sinh embedding cho kho tri thức RAG.

        Trả về danh sách rỗng nếu chưa có key — RAG sẽ tự lui về xếp hạng từ
        khoá thay vì làm hỏng cả luồng.
        """
        if not self._api_key or not texts:
            return []
        url = f"{_BASE_URL}/models/{model}:batchEmbedContents?key={self._api_key}"
        payload = {
            "requests": [
                {"model": f"models/{model}", "content": {"parts": [{"text": t}]}} for t in texts
            ]
        }
        try:
            with httpx.Client(timeout=_TIMEOUT_SECONDS) as client:
                response = client.post(url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        embeddings = response.json().get("embeddings") or []
        return [e.get("values", []) for e in embeddings]

    # --- Nội bộ ----------------------------------------------------------

    def _call(self, model: str, parts: list[dict], categories: list[CategoryOption]) -> VisionResult:
        if not self._api_key:
            raise VisionUnavailableError(
                "Chưa cấu hình GEMINI_API_KEY trong .env.",
                code="VISION-401",
            )

        url = f"{_BASE_URL}/models/{model}:generateContent?key={self._api_key}"
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 900,
                "responseMimeType": "application/json",
                # Các model Gemini đời mới bật "suy nghĩ" mặc định, và token suy
                # nghĩ TÍNH VÀO maxOutputTokens. Đo ngày 01/08/2026 trên
                # `gemini-flash-latest`: 672 token suy nghĩ / 900, còn 24 token
                # cho câu trả lời → JSON bị cắt giữa chừng, `finishReason`
                # MAX_TOKENS. Phân loại rác là bài trích xuất có cấu trúc, không
                # cần suy luận nhiều bước nên ghìm xuống mức thấp nhất dùng được.
                # (``thinkingBudget: 0`` bị hai model này từ chối bằng lỗi 400.)
                "thinkingConfig": {"thinkingBudget": _THINKING_BUDGET},
            },
        }

        try:
            with httpx.Client(timeout=_TIMEOUT_SECONDS) as client:
                response = client.post(url, json=payload)
                # Danh mục model Gemini đổi liên tục và không phải model nào cũng
                # nhận ``thinkingConfig``. Thử lại một lần không kèm tham số đó,
                # thay vì để cả luồng chết vì một tuỳ chọn tối ưu.
                if response.status_code == 400:
                    payload["generationConfig"].pop("thinkingConfig", None)
                    response = client.post(url, json=payload)
        except httpx.HTTPError as exc:
            raise VisionUnavailableError(
                "Không kết nối được tới máy chủ model. Ảnh của bạn vẫn được giữ lại.",
                code="VISION-503",
            ) from exc

        if response.status_code == 429:
            raise VisionUnavailableError("Model đang quá tải (rate limit). Thử lại sau ít phút.", code="VISION-429")
        if response.status_code >= 400:
            raise VisionUnavailableError(
                f"Gemini trả về lỗi {response.status_code}. Kiểm tra tên model và GEMINI_API_KEY trong .env.",
                code=f"VISION-{response.status_code}",
            )

        body = response.json()
        candidates = body.get("candidates") or []
        if not candidates:
            raise VisionUnavailableError("Model không trả về nội dung (có thể bị chặn bởi bộ lọc).", code="VISION-502")

        text = "".join(p.get("text", "") for p in (candidates[0].get("content") or {}).get("parts", []))

        meta = body.get("usageMetadata") or {}
        tokens_in = int(meta.get("promptTokenCount", 0) or 0)
        tokens_out = int(meta.get("candidatesTokenCount", 0) or 0)
        cost, price_known = estimate_cost(model, tokens_in, tokens_out)
        usage = Usage(tokens_in=tokens_in, tokens_out=tokens_out, cost_usd=cost, price_known=price_known)

        data = parse_model_json(text, {c.code for c in categories})
        return result_from_json(data, model=model, provider=self.provider_name, usage=usage, raw_text=text)


def build_gemini_client() -> GeminiClient:
    return GeminiClient(get_settings().gemini_api_key)
