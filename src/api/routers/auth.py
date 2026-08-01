"""Đăng nhập và thông tin phiên."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.deps import CurrentUser, DbSession
from src.api.errors import ApiError
from src.api.serializers import user_dict
from src.db.seed_data import DEMO_PASSWORD, USERS
from src.models.schemas import LoginRequest, LoginResponse
from src.services.auth import AuthError, authenticate, create_token, permission_matrix

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, session: DbSession) -> dict:
    """Đăng nhập bằng email + mật khẩu."""
    try:
        user = authenticate(session, payload.email, payload.password)
    except AuthError as exc:
        raise ApiError(401, exc.code, exc.message_vi) from exc

    return {
        "token": create_token(user),
        "user": user_dict(session, user),
        "permissions": permission_matrix(user),
    }


@router.get("/me")
def me(user: CurrentUser, session: DbSession) -> dict:
    """Thông tin người đang đăng nhập kèm ma trận quyền."""
    return {"user": user_dict(session, user), "permissions": permission_matrix(user)}


@router.get("/demo-accounts")
def demo_accounts() -> dict:
    """Ba nút "vào thẳng" trên màn đăng nhập.

    Trả mật khẩu ra ngoài là có chủ đích: đây là **tài khoản demo dùng dữ liệu
    mô phỏng**, và người chấm cần đăng nhập được cả ba vai trò.
    """
    mo_ta = {
        "resident": "Hỏi phân loại, đặt lịch thu gom, xem yêu cầu của mình",
        "cleaner": "Xem tuyến hôm nay, đánh dấu đã thu, xác nhận nhãn nghi ngờ",
        "manager": "Duyệt 3 hàng đợi HITL, xem vận hành và chất lượng AI",
    }
    return {
        "password": DEMO_PASSWORD,
        "accounts": [
            {
                "email": u["email"],
                "full_name": u["full_name"],
                "role": u["role"],
                "unit": u["unit_code"],
                "description": mo_ta.get(u["role"], ""),
            }
            for u in USERS
            if u["email"] in {"resident@demo.vn", "cleaner@demo.vn", "manager@demo.vn"}
        ],
        "notice": (
            "Hệ thống demo dùng dữ liệu mô phỏng và dữ liệu công khai. Ảnh tải lên được tự động "
            "xoá thông tin vị trí và làm mờ khuôn mặt trước khi xử lý."
        ),
    }
