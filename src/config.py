"""Cấu hình toàn hệ thống GreenBin AI.

Nguyên tắc: **đổi nhà cung cấp model chỉ bằng sửa ``.env``, không sửa code.**
Nhóm chưa có API key OpenAI nên tầng T1/T2 tạm chạy trên Gemini / OpenRouter /
NVIDIA NIM; khi có key OpenAI thì đổi ``VISION_PROVIDER=openai`` là xong, kiến
trúc định tuyến 3 tầng ở ``CLAUDE.md`` mục 4 giữ nguyên.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

VisionProvider = Literal["gemini", "openai", "openrouter", "nvidia", "local_only"]

# Điểm cuối của các nhà cung cấp dùng giao thức tương thích OpenAI.
OPENAI_COMPATIBLE_BASE_URLS: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "nvidia": "https://integrate.api.nvidia.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
}

# Giá tham chiếu USD / 1 triệu token, dùng để ước tính chi phí khi nhà cung cấp
# không trả về giá. Con số thật vẫn lấy từ ``usage`` của API — xem
# ``src/services/vision/base.py``. Model không có trong bảng coi như $0
# (free tier) và được đánh dấu ``price_known=False`` để không đưa nhầm lên slide.
MODEL_PRICES_USD_PER_MTOK: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "openai/gpt-4o-mini": (0.15, 0.60),
    "openai/gpt-4o": (2.50, 10.00),
    "text-embedding-3-small": (0.02, 0.0),
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App -------------------------------------------------------------
    app_name: str = "GreenBin AI"
    app_env: Literal["development", "production", "test"] = "development"
    app_port: int = Field(default=8000, ge=1, le=65535)
    app_host: str = "0.0.0.0"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    # ``https://localhost`` và ``capacitor://localhost`` là origin mà app Android
    # đóng gói bằng Capacitor tự dùng khi phục vụ giao diện từ trong máy. Thiếu
    # hai dòng này thì app cài về gọi API bị CORS chặn.
    cors_origins: str = (
        "http://localhost:3000,http://localhost:3001,https://localhost,capacitor://localhost"
    )

    # Máy chủ tự nạp dữ liệu nền khi khởi động. Bật trên Render vì ở đó không có
    # chỗ chạy tay ``scripts/seed.py``; để tắt khi dev cho khỏi bất ngờ.
    seed_on_start: bool = False
    # Kèm dữ liệu demo mô phỏng (mọi bản ghi đều gắn cờ ``is_seed``) để trang
    # Vận hành / Chất lượng AI của bản deploy không trống trơn.
    seed_demo_on_start: bool = True

    # --- Xác thực --------------------------------------------------------
    # Hệ thống demo tự làm auth thay vì Supabase — xem ADR-0004.
    jwt_secret: str = "greenbin-dev-secret-doi-truoc-khi-deploy"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = Field(default=60 * 12, ge=5)

    # --- Nhà cung cấp model vision ---------------------------------------
    vision_provider: VisionProvider = "gemini"

    openai_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_api_key: str = ""
    nvidia_api_key: str = ""
    deepseek_api_key: str = ""

    # Tên model từng tầng. Mặc định điền theo provider trong ``resolve_models``
    # nếu để trống, nên thường không cần đụng tới.
    vision_model_t1: str = ""
    vision_model_t2: str = ""
    text_model: str = ""

    # Giữ tên cũ để code/template cũ không gãy.
    model_name: str = "gpt-4o-mini"
    model_fast: str = "gpt-4o-mini"
    model_smart: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    llm_temperature: float = Field(default=0.2, ge=0.0, le=2.0)

    prompt_version: str = "v1"

    # --- Tầng T0.5: model local chạy offline trên CPU ---------------------
    local_model_enabled: bool = True
    # CLIP zero-shot: không cần train, không cần dữ liệu gán nhãn. Tải một lần
    # (~350MB) rồi chạy hoàn toàn offline.
    clip_model_name: str = "openai/clip-vit-base-patch32"
    # Dưới ngưỡng này thì T0.5 không dám kết luận và đẩy lên T1.
    clip_accept_confidence: float = Field(default=0.82, ge=0.0, le=1.0)
    # Nhóm nguy hại không bao giờ được chốt bởi model local — luôn đẩy lên
    # tầng có khả năng suy luận. Xem CLAUDE.md mục 5.
    local_never_decides_hazardous: bool = True

    # --- Tầng T0: cache pHash --------------------------------------------
    # Khoảng cách Hamming tối đa giữa 2 pHash để coi là cùng một món rác.
    phash_max_distance: int = Field(default=6, ge=0, le=64)

    # --- Ngưỡng an toàn và HITL ------------------------------------------
    # So với cận TRÊN của khoảng khối lượng (ADR-0003): sai số nghiêng về phía
    # cần người duyệt.
    hitl_weight_threshold_kg: float = Field(default=30.0, gt=0)
    hitl_item_count_threshold: int = Field(default=3, gt=0)
    # Ngưỡng mặc định khi nhóm rác chưa khai báo ``min_confidence`` riêng.
    default_min_confidence: float = Field(default=0.60, ge=0.0, le=1.0)
    hazardous_min_confidence: float = Field(default=0.80, ge=0.0, le=1.0)

    # --- Điều phối tuyến --------------------------------------------------
    vehicle_capacity_kg: float = Field(default=200.0, gt=0)
    # Quãng đường ước tính cho một chuyến đi lẻ tới một điểm, dùng làm baseline
    # để tính phần tiết kiệm. Con số minh hoạ, có ghi rõ trên UI.
    baseline_km_per_standalone_trip: float = Field(default=3.6, gt=0)

    # --- Ảnh và quyền riêng tư -------------------------------------------
    media_dir: str = "./data/media"
    media_max_edge_px: int = Field(default=512, ge=128)
    media_retention_days: int = Field(default=30, ge=1)
    face_blur_enabled: bool = True

    # --- Kiểm soát chi phí ------------------------------------------------
    llm_batch_size: int = Field(default=25, ge=1, le=100)
    budget_limit_usd: float = Field(default=25.0, gt=0)
    llm_cache_dir: str = "./data/cache"

    # --- Database ---------------------------------------------------------
    database_url: str = "sqlite:///./data/app.db"
    chroma_persist_dir: str = "./data/chroma"

    # --- Tiện ích ---------------------------------------------------------

    @property
    def is_openai_compatible(self) -> bool:
        """Provider hiện tại có dùng giao thức OpenAI không."""
        return self.vision_provider in OPENAI_COMPATIBLE_BASE_URLS

    @property
    def provider_base_url(self) -> str:
        return OPENAI_COMPATIBLE_BASE_URLS.get(self.vision_provider, "")

    @property
    def provider_api_key(self) -> str:
        keys = {
            "openai": self.openai_api_key,
            "openrouter": self.openrouter_api_key,
            "nvidia": self.nvidia_api_key,
            "gemini": self.gemini_api_key,
            "local_only": "",
        }
        return keys.get(self.vision_provider, "")

    def resolve_models(self) -> tuple[str, str, str]:
        """Trả về ``(model_t1, model_t2, model_text)`` cho provider đang chọn.

        Cho phép ghi đè từng cái qua ``.env``; phần để trống thì lấy mặc định
        hợp lý của provider đó.
        """
        defaults: dict[str, tuple[str, str, str]] = {
            "openai": ("gpt-4o-mini", "gpt-4o", "gpt-4o-mini"),
            "openrouter": ("openai/gpt-4o-mini", "openai/gpt-4o", "openai/gpt-4o-mini"),
            "nvidia": (
                "meta/llama-3.2-11b-vision-instruct",
                "meta/llama-3.2-90b-vision-instruct",
                "meta/llama-3.1-8b-instruct",
            ),
            # Google đã đóng ``gemini-2.5-flash`` và ``gemini-2.5-pro`` với key
            # tạo mới ("no longer available to new users", HTTP 404) — chúng vẫn
            # hiện trong danh sách ``/models`` nên chỉ lộ ra lúc gọi thật. Bí
            # danh ``*-latest`` không bị khoá và tự trỏ sang bản mới nhất.
            # Đo ngày 01/08/2026: `pro-latest` và `2.0-flash` trả 429 ngay từ
            # lần gọi đầu trên free tier, nên T2 dùng `flash-latest`.
            # Model sinh hướng dẫn dùng bản `lite`: hạn free tier của
            # `gemini-flash-latest` (hiện trỏ tới gemini-3.6-flash) chỉ **20
            # request**, cạn sau vài phút thử. Bước advise chạy sau MỌI lần phân
            # loại thành công nên nó là chỗ tiêu quota nhanh nhất — để nó ở model
            # đắt là hết quota giữa buổi demo.
            "gemini": ("gemini-flash-lite-latest", "gemini-flash-latest", "gemini-flash-lite-latest"),
            "local_only": ("", "", ""),
        }
        t1, t2, text = defaults.get(self.vision_provider, ("", "", ""))
        return (
            self.vision_model_t1 or t1,
            self.vision_model_t2 or t2,
            self.text_model or text,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    """Xoá cache cấu hình. Dùng trong test khi đổi biến môi trường."""
    get_settings.cache_clear()
