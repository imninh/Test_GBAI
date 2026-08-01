"""Provider dùng giao thức tương thích OpenAI: OpenAI, OpenRouter, NVIDIA NIM.

Ba nhà cung cấp này cùng một khuôn ``POST /chat/completions`` nên dùng chung
một lớp; chỉ khác ``base_url``, key và tên model. Gọi thẳng bằng ``httpx`` thay
vì SDK để không phải gánh thêm phụ thuộc và không bị khoá vào một nhà cung cấp.
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

_TIMEOUT_SECONDS = 60.0


class OpenAICompatibleClient:
    """Gọi model qua endpoint kiểu OpenAI."""

    def __init__(self, provider_name: str, base_url: str, api_key: str) -> None:
        self.provider_name = provider_name
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    # --- API công khai ---------------------------------------------------

    def classify_image(self, image_bytes: bytes, categories: list[CategoryOption], model: str) -> VisionResult:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        content = [
            {"type": "text", "text": build_image_prompt(categories)},
            {
                "type": "image_url",
                # detail=low đủ cho ảnh 512px và rẻ hơn nhiều; con số token thật
                # đo được ghi vào RunNodeMetric để đối chiếu với detail=high.
                "image_url": {"url": f"data:image/jpeg;base64,{encoded}", "detail": "low"},
            },
        ]
        return self._call(model, content, categories)

    def classify_text(self, text: str, categories: list[CategoryOption], model: str) -> VisionResult:
        content = [{"type": "text", "text": build_text_prompt(text, categories)}]
        return self._call(model, content, categories)

    def generate_text(self, prompt: str, model: str, max_tokens: int = 500) -> tuple[str, Usage]:
        """Sinh văn bản thuần (dùng cho node advise). Trả về ``(text, usage)``."""
        body = self._post(
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": max_tokens,
            }
        )
        try:
            text = body["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise VisionUnavailableError("Model trả về khuôn dữ liệu lạ.", code="VISION-502") from exc

        usage_block = body.get("usage") or {}
        tokens_in = int(usage_block.get("prompt_tokens", 0) or 0)
        tokens_out = int(usage_block.get("completion_tokens", 0) or 0)
        cost, price_known = estimate_cost(model, tokens_in, tokens_out)
        return text, Usage(tokens_in=tokens_in, tokens_out=tokens_out, cost_usd=cost, price_known=price_known)

    def embed(self, texts: list[str], model: str) -> list[list[float]]:
        """Sinh embedding cho kho tri thức. Trả về rỗng nếu không gọi được."""
        if not self._api_key or not texts:
            return []
        try:
            with httpx.Client(timeout=_TIMEOUT_SECONDS) as client:
                response = client.post(
                    f"{self._base_url}/embeddings",
                    json={"model": model, "input": texts},
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        return [item.get("embedding", []) for item in response.json().get("data", [])]

    # --- Nội bộ ----------------------------------------------------------

    def _post(self, payload: dict) -> dict:
        """Gửi một yêu cầu tới ``/chat/completions`` và trả về JSON."""
        if not self._api_key:
            raise VisionUnavailableError(
                f"Chưa cấu hình API key cho {self.provider_name}. Điền vào .env rồi thử lại.",
                code="VISION-401",
            )
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        if self.provider_name == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/greenbin-ai"
            headers["X-Title"] = "GreenBin AI"

        try:
            with httpx.Client(timeout=_TIMEOUT_SECONDS) as client:
                response = client.post(f"{self._base_url}/chat/completions", json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise VisionUnavailableError(
                "Không kết nối được tới máy chủ model. Ảnh của bạn vẫn được giữ lại.",
                code="VISION-503",
            ) from exc

        if response.status_code == 429:
            raise VisionUnavailableError("Model đang quá tải (rate limit). Thử lại sau ít phút.", code="VISION-429")
        if response.status_code >= 400:
            raise VisionUnavailableError(
                f"Model trả về lỗi {response.status_code}. Kiểm tra tên model và API key trong .env.",
                code=f"VISION-{response.status_code}",
            )
        return response.json()

    def _call(self, model: str, content: list[dict], categories: list[CategoryOption]) -> VisionResult:
        body = self._post(
            {
                "model": model,
                "messages": [{"role": "user", "content": content}],
                "temperature": 0.1,
                "max_tokens": 700,
                "response_format": {"type": "json_object"},
            }
        )
        try:
            text = body["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise VisionUnavailableError("Model trả về khuôn dữ liệu lạ.", code="VISION-502") from exc

        usage_block = body.get("usage") or {}
        tokens_in = int(usage_block.get("prompt_tokens", 0) or 0)
        tokens_out = int(usage_block.get("completion_tokens", 0) or 0)
        cost, price_known = estimate_cost(model, tokens_in, tokens_out)
        usage = Usage(
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            # Nhà cung cấp gộp token ảnh vào prompt_tokens; tách ra được thì tách.
            image_tokens=int((usage_block.get("prompt_tokens_details") or {}).get("image_tokens", 0) or 0),
            cost_usd=cost,
            price_known=price_known,
        )

        data = parse_model_json(text, {c.code for c in categories})
        return result_from_json(data, model=model, provider=self.provider_name, usage=usage, raw_text=text)


def build_openai_compatible_client(provider: str) -> OpenAICompatibleClient:
    settings = get_settings()
    keys = {
        "openai": settings.openai_api_key,
        "openrouter": settings.openrouter_api_key,
        "nvidia": settings.nvidia_api_key,
        "deepseek": settings.deepseek_api_key,
    }
    from src.config import OPENAI_COMPATIBLE_BASE_URLS

    base_url = OPENAI_COMPATIBLE_BASE_URLS.get(provider, "")
    if not base_url:
        raise VisionUnavailableError(f"Không biết nhà cung cấp '{provider}'.", code="VISION-400")
    return OpenAICompatibleClient(provider, base_url, keys.get(provider, ""))
