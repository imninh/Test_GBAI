"""Điểm vào ứng dụng FastAPI của GreenBin AI."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from src.api.errors import ApiError, api_error_handler, http_error_handler, unhandled_error_handler
from src.api.routes import router
from src.config import get_settings
from src.db.session import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    # Slice 0 tạo bảng trực tiếp; chuyển sang Alembic khi schema ổn định.
    init_db()
    if settings.seed_on_start:
        _nap_du_lieu_nen(demo=settings.seed_demo_on_start)
    logger.info("GreenBin AI khởi động — môi trường %s, provider %s", settings.app_env, settings.vision_provider)
    yield
    logger.info("GreenBin AI đã dừng")


def _nap_du_lieu_nen(*, demo: bool) -> None:
    """Nạp danh mục, toà, tài khoản demo ngay lúc khởi động.

    Dùng cho môi trường deploy (Render), nơi không có chỗ chạy tay
    ``scripts/seed.py``. ``bootstrap`` gọi lại nhiều lần vô hại nên restart
    không sinh dữ liệu trùng. Nhập trong hàm để lần khởi động bình thường
    không phải nạp cả module seed.
    """
    from scripts.seed import bootstrap
    from src.db.session import session_scope

    try:
        with session_scope() as session:
            ket_qua = bootstrap(session, demo=demo)
        logger.info("Đã nạp dữ liệu nền lúc khởi động: %s", ket_qua)
    except SQLAlchemyError:
        # Không nạp được dữ liệu nền thì vẫn phải để máy chủ lên — trang lỗi
        # còn đọc được, hơn là cả service chết.
        logger.exception("Nạp dữ liệu nền lúc khởi động thất bại")


app = FastAPI(
    title="GreenBin AI",
    description=(
        "Agent phân loại rác và điều phối thu gom tái chế cho toà chung cư (VHR-17). "
        "Mọi ảnh đều được tước EXIF và làm mờ khuôn mặt trước khi xử lý."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khuôn lỗi thống nhất {error:{code, message_vi, detail}} cho mọi loại lỗi.
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
def health() -> dict:
    return {"status": "ok", "env": settings.app_env}
