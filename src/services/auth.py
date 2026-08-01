"""Xác thực và phân quyền.

Nhóm tự làm auth thay vì dùng Supabase như thẻ đề gợi ý — xem ADR-0004. Lý do
gọn: hệ thống chỉ cần ba vai trò cố định và tài khoản demo, mà phần đắt giá của
đề nằm ở AI chứ không ở quản lý danh tính; thêm một dịch vụ ngoài là thêm một
điểm hỏng khi demo.

Ma trận quyền ở :data:`PERMISSIONS` là bản chép lại của bảng trong
``docs/FRONTEND_SPEC.md`` mục 1. Sửa một bên thì sửa cả hai.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import get_settings
from src.db.models import AuditLog, User
from src.services.security import verify_password

ROLES = ("resident", "cleaner", "manager")

# Quyền → các vai trò được phép. Vai trò không có quyền thì UI **hiện mờ kèm
# tooltip giải thích**, không ẩn hẳn, để ranh giới phân quyền nhìn thấy được.
PERMISSIONS: dict[str, tuple[str, ...]] = {
    "classify": ("resident", "cleaner", "manager"),
    "view_schedule": ("resident", "cleaner", "manager"),
    "create_pickup": ("resident", "manager"),
    "view_own_pickups": ("resident", "cleaner", "manager"),
    "view_all_pickups": ("cleaner", "manager"),
    "review_pickup": ("manager",),
    "verify_label": ("cleaner", "manager"),
    "review_route": ("manager",),
    "complete_stop": ("cleaner", "manager"),
    "edit_catalog": ("manager",),
    "view_original_media": ("manager",),
    "view_ops": ("manager",),
    "view_eval": ("manager",),
    "view_runs": ("manager",),
}

PERMISSION_DENIED_HINTS: dict[str, str] = {
    "review_pickup": "Chỉ ban quản lý được duyệt yêu cầu thu gom vượt ngưỡng",
    "review_route": "Chỉ ban quản lý được duyệt tuyến do agent đề xuất",
    "verify_label": "Chỉ đội vệ sinh và ban quản lý được xác nhận nhãn",
    "view_original_media": "Chỉ ban quản lý được xem ảnh gốc, và mỗi lần xem đều được ghi log",
    "view_ops": "Trang vận hành dành cho ban quản lý",
    "view_eval": "Trang chất lượng AI dành cho ban quản lý",
    "view_runs": "Trang trace agent dành cho ban quản lý",
    "create_pickup": "Đội vệ sinh không tạo yêu cầu thay cư dân",
}


class AuthError(Exception):
    """Sai thông tin đăng nhập hoặc token không hợp lệ."""

    def __init__(self, message_vi: str, code: str = "AUTH-401") -> None:
        super().__init__(message_vi)
        self.message_vi = message_vi
        self.code = code


def create_token(user: User) -> str:
    """Sinh JWT cho một người dùng."""
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Giải mã JWT.

    Raises:
        AuthError: token hết hạn hoặc không hợp lệ.
    """
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Phiên đăng nhập đã hết hạn, đăng nhập lại giúp mình nhé.", code="AUTH-419") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError("Phiên đăng nhập không hợp lệ.", code="AUTH-401") from exc


def authenticate(session: Session, email: str, password: str) -> User:
    """Kiểm tra email + mật khẩu.

    Raises:
        AuthError: khi sai email hoặc sai mật khẩu. Thông báo giống nhau cho cả
            hai trường hợp để không lộ email nào có tồn tại.
    """
    user = session.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError("Email hoặc mật khẩu không đúng.", code="AUTH-401")
    return user


def can(user: User, permission: str) -> bool:
    """Vai trò của người dùng có quyền này không."""
    return user.role in PERMISSIONS.get(permission, ())


def permission_matrix(user: User) -> dict[str, dict[str, Any]]:
    """Toàn bộ ma trận quyền của người dùng hiện tại, để UI vẽ trạng thái mờ.

    Trả cả quyền không có kèm lý do — vì spec yêu cầu hiện mờ có tooltip chứ
    không ẩn hẳn.
    """
    return {
        name: {
            "allowed": user.role in roles,
            "reason": "" if user.role in roles else PERMISSION_DENIED_HINTS.get(name, "Vai trò của bạn không có quyền này"),
        }
        for name, roles in PERMISSIONS.items()
    }


def write_audit(
    session: Session,
    *,
    actor: User | None,
    action: str,
    entity: str,
    entity_id: str = "",
    detail: dict[str, Any] | None = None,
) -> None:
    """Ghi nhật ký kiểm toán cho hành động rủi ro hoặc chạm dữ liệu nhạy cảm."""
    session.add(
        AuditLog(
            actor_id=actor.id if actor else None,
            action=action,
            entity=entity,
            entity_id=entity_id,
            detail=detail or {},
        )
    )
    session.flush()
