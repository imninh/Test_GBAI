"""Schema request/response của API.

Bám sát hợp đồng dữ liệu ở ``docs/FRONTEND_SPEC.md`` mục 7 — đó là bản cam kết
với frontend. Đổi tên trường hay đường dẫn thì **sửa cả hai nơi cùng lúc**.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field

# --- Auth -----------------------------------------------------------------


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=200)


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    unit: str = ""
    building: str = ""
    building_id: int | None = None
    green_points: int = 0


class LoginResponse(BaseModel):
    token: str
    user: UserOut
    permissions: dict[str, dict[str, Any]]


# --- Phân loại ------------------------------------------------------------


class ClassifyTextRequest(BaseModel):
    text_query: str = Field(min_length=1, max_length=500)
    building_id: int | None = None


class FeedbackRequest(BaseModel):
    is_correct: bool
    suggested_category_code: str = ""


class VerifyRequest(BaseModel):
    """Xác nhận nhãn cho ca nghi ngờ — HITL #2."""

    category_code: str = Field(min_length=1, max_length=40)
    reply_text: str = ""


# --- Thu gom --------------------------------------------------------------


class PickupItem(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category_code: str = ""
    qty: int = Field(default=1, ge=1, le=99)
    media_id: int | None = None
    est_weight_kg: float = Field(default=0.0, ge=0)


class CreatePickupRequest(BaseModel):
    items: list[PickupItem] = Field(min_length=1)
    est_weight_kg: float = Field(default=0.0, ge=0)
    weight_min_kg: float | None = None
    weight_max_kg: float | None = None
    preferred_date: date | None = None
    preferred_window: str = ""
    note: str = ""
    # Bắt buộc tick ở bước 3 của wizard (spec 4.7).
    confirmed_no_hazardous: bool = False


class ReviewPickupRequest(BaseModel):
    action: Literal["approve", "approve_with_changes", "reject"]
    reason: str = ""
    note: str = ""
    changes: dict[str, Any] | None = None


# --- Tuyến ----------------------------------------------------------------


class ProposeRouteRequest(BaseModel):
    service_date: date
    window: str = ""
    team_id: int | None = None
    capacity_kg: float | None = Field(default=None, gt=0)


class ReviewRouteRequest(BaseModel):
    action: Literal["approve", "approve_with_changes", "regenerate", "cancel"]
    stop_order: list[int] | None = None
    removed_stops: list[int] | None = None


class CompleteStopRequest(BaseModel):
    issue: str = ""
    issue_note: str = ""
    actual_weight_kg: float | None = Field(default=None, ge=0)


# --- Danh mục và kho quy định --------------------------------------------


class UpdateCategoryRequest(BaseModel):
    min_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    bin_color: str | None = None
    handling_note: str | None = None
    safety_warning: str | None = None


class RetrievalTestRequest(BaseModel):
    """Ô "Thử truy hồi" trong màn Kho quy định — công cụ debug RAG nhìn thấy được."""

    query: str = Field(min_length=1, max_length=300)
    building_id: int | None = None
    top_k: int = Field(default=5, ge=1, le=20)
