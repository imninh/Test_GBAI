"""Hàng rào an toàn cho phần phân loại — phần mạnh nhất của đề, không được cắt.

Ba cơ chế, xếp theo thứ tự ưu tiên:

1. **Danh sách chặn cứng** — vật sắc nhọn y tế, bình gas, hoá chất. Gặp là
   chuyển người ngay, **bỏ qua confidence**, dù model có chắc tới đâu.
2. **Ngưỡng riêng theo nhóm** — nhóm nguy hại dùng ngưỡng cao hơn hẳn. Dưới
   ngưỡng thì từ chối trả lời dứt khoát, không trả lời nước đôi cho ra vẻ hữu ích.
3. **Cảnh báo an toàn là text cố định lấy từ danh mục trong CSDL**, không bao
   giờ để LLM tự sinh.

Mọi lần từ chối đều ghi ``refusal_reason`` chọn từ danh sách cố định bên dưới —
gõ tự do là mất dữ liệu cho vòng lặp cải tiến (PLO 7).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum

from src.config import get_settings
from src.db.models import WasteCategory


class RefusalReason(StrEnum):
    """Danh sách lý do từ chối cố định. Không thêm lý do tự do."""

    DUOI_NGUONG = "duoi_nguong"
    NGHI_NGUY_HAI = "nghi_nguy_hai"
    CHAN_CUNG = "chan_cung"
    ANH_TOI = "anh_toi"
    ANH_MO = "mo"
    VAT_BI_CHE = "vat_bi_che"
    NHIEU_VAT = "nhieu_vat"
    KHONG_NHAN_RA = "khong_nhan_ra"
    MODEL_LOI = "model_loi"


REFUSAL_LABELS_VI: dict[str, str] = {
    RefusalReason.DUOI_NGUONG: "Độ tin cậy dưới ngưỡng của nhóm rác này",
    RefusalReason.NGHI_NGUY_HAI: "Nghi là rác nguy hại — nhóm này cần độ chắc cao hơn",
    RefusalReason.CHAN_CUNG: "Món này cần quy trình xử lý riêng, luôn chuyển cho người",
    RefusalReason.ANH_TOI: "Ảnh hơi tối nên không đọc được nhãn",
    RefusalReason.ANH_MO: "Ảnh bị mờ",
    RefusalReason.VAT_BI_CHE: "Vật bị che một phần",
    RefusalReason.NHIEU_VAT: "Nhiều món chồng lên nhau",
    RefusalReason.KHONG_NHAN_RA: "Chưa nhận ra món này thuộc nhóm nào",
    RefusalReason.MODEL_LOI: "Hệ thống nhận diện đang gặp sự cố",
}

# Câu chữ hiện cho người dùng, lấy nguyên văn từ FRONTEND_SPEC mục 11.
REFUSAL_HEADLINE_VI = "Mình chưa đủ chắc để hướng dẫn món này"
REFUSAL_HAZARD_VI = (
    "Món này có thể là rác nguy hại. Hướng dẫn sai ở nhóm này gây nguy hiểm thật, "
    "nên mình không đoán bừa."
)
REFUSAL_HARD_BLOCK_VI = "Món này cần quy trình xử lý riêng. Mình chuyển cho ban quản lý ngay."


@dataclass(frozen=True)
class HardBlockRule:
    """Một luật chặn cứng: nhóm vật + từ khoá nhận biết + câu dặn cho người dùng."""

    code: str
    label_vi: str
    keywords: tuple[str, ...]
    instruction_vi: str


# Ba nhóm trong CLAUDE.md mục 5. Từ khoá viết KHÔNG DẤU vì đầu vào được chuẩn
# hoá bỏ dấu trước khi so — người dùng gõ "kim tiem" hay "kim tiêm" đều bắt được.
HARD_BLOCK_RULES: tuple[HardBlockRule, ...] = (
    HardBlockRule(
        code="vat_sac_nhon_y_te",
        label_vi="Vật sắc nhọn y tế",
        keywords=(
            "kim tiem",
            "ong tiem",
            "syringe",
            "dao mo",
            "luoi lam",
            "kim luon",
            "que thu duong huyet",
            "vat sac nhon y te",
            "rac y te",
            "bom tiem",
        ),
        instruction_vi=(
            "Không bỏ vào bất kỳ thùng rác nào và không chạm tay trần. "
            "Ban quản lý sẽ hướng dẫn quy trình thu gom riêng."
        ),
    ),
    HardBlockRule(
        code="binh_gas",
        label_vi="Bình gas / bình chịu áp",
        keywords=("binh gas", "binh ga", "gas mini", "binh chua khi", "binh oxy", "binh cuu hoa", "binh xit son"),
        instruction_vi=(
            "Không nén, không đốt, không vứt chung rác. Để nơi thoáng và báo ban quản lý "
            "để chuyển cho đơn vị có giấy phép."
        ),
    ),
    HardBlockRule(
        code="hoa_chat",
        label_vi="Hoá chất",
        keywords=(
            "hoa chat",
            "axit",
            "acid",
            "thuoc tru sau",
            "thuoc sau",
            "dung moi",
            "xang",
            "dau nhot",
            "thuoc diet con trung",
            "chat tay rua cong nghiep",
        ),
        instruction_vi=(
            "Giữ nguyên trong chai gốc, đậy kín nắp, không đổ xuống cống. "
            "Ban quản lý sẽ hướng dẫn điểm tiếp nhận."
        ),
    ),
)


def _normalize(text: str) -> str:
    """Bỏ dấu, hạ chữ thường, gom khoảng trắng — để so khớp từ khoá ổn định."""
    lowered = unicodedata.normalize("NFD", text.lower())
    stripped = "".join(c for c in lowered if unicodedata.category(c) != "Mn")
    stripped = stripped.replace("đ", "d")
    return re.sub(r"\s+", " ", stripped).strip()


def check_hard_block(*texts: str) -> HardBlockRule | None:
    """Tìm luật chặn cứng khớp với tên món / câu mô tả của người dùng.

    Chạy trên **cả câu hỏi gốc lẫn tên món model đoán ra**: người dùng gõ
    "kim tiêm" thì chặn ngay, mà model nhìn ảnh ra "ống tiêm" cũng chặn.
    """
    haystack = _normalize(" ".join(t for t in texts if t))
    if not haystack:
        return None
    for rule in HARD_BLOCK_RULES:
        for keyword in rule.keywords:
            if keyword in haystack:
                return rule
    return None


def min_confidence_for(category: WasteCategory | None) -> float:
    """Ngưỡng tin cậy tối thiểu của một nhóm rác.

    Nhóm chưa khai báo thì lấy mặc định; nhóm nguy hại không bao giờ được thấp
    hơn ``hazardous_min_confidence`` dù ai đó sửa nhầm trong màn quản trị.
    """
    settings = get_settings()
    if category is None:
        return settings.default_min_confidence
    threshold = category.min_confidence or settings.default_min_confidence
    if category.is_hazardous:
        return max(threshold, settings.hazardous_min_confidence)
    return threshold


def confidence_level(confidence: float, min_confidence: float) -> str:
    """Ba mức hiển thị theo FRONTEND_SPEC mục 2.4.

    Returns:
        ``"chac_chan"`` · ``"kha_chac"`` · ``"duoi_nguong"``
    """
    if confidence < min_confidence:
        return "duoi_nguong"
    if confidence >= min_confidence + 0.15:
        return "chac_chan"
    return "kha_chac"


CONFIDENCE_LABELS_VI: dict[str, str] = {
    "chac_chan": "Chắc chắn",
    "kha_chac": "Khá chắc — nên kiểm tra lại",
    "duoi_nguong": "Chưa đủ chắc",
}


def should_escalate_to_t2(
    confidence: float,
    min_confidence: float,
    suspect_hazardous: bool,
    quality_issue: str = "",
) -> str:
    """Có phải leo từ T1 lên T2 không, và vì lý do gì.

    Ba điều kiện, đúng theo CLAUDE.md mục 4: **confidence thấp · nhiều vật ·
    nghi rác nguy hại**. Hai điều kiện sau không phụ thuộc confidence — model
    hoàn toàn có thể rất tự tin mà vẫn đang nhìn một đống rác lẫn lộn.

    Returns:
        Chuỗi lý do bằng tiếng Việt, hoặc chuỗi rỗng nếu không cần leo tầng.
    """
    if suspect_hazardous:
        return "Nghi rác nguy hại — luôn kiểm tra bằng model mạnh hơn"
    if quality_issue == RefusalReason.NHIEU_VAT.value:
        return "Ảnh có nhiều món rác — kiểm lại bằng model mạnh hơn"
    if confidence < min_confidence:
        return f"Độ tin cậy {confidence:.2f} dưới ngưỡng {min_confidence:.2f} của nhóm"
    return ""


def nhieu_nhom_khac_nhau(items: list[dict]) -> bool:
    """Danh sách món rác model liệt kê có trải trên nhiều nhóm khác nhau không.

    Một nhãn duy nhất cho ảnh gồm chai nhựa + bình thuỷ tinh + chuột máy tính
    là **câu trả lời sai**, dù confidence có cao đến đâu: thuỷ tinh và rác
    điện tử đi đường khác nhựa. Gặp trường hợp này thì chuyển người, không đoán.
    """
    ma_nhom = {str(i.get("category_code", "")).strip() for i in items if i.get("category_code")}
    return len(ma_nhom) > 1


def safety_warning_for(category: WasteCategory | None) -> str:
    """Cảnh báo an toàn cố định của nhóm rác.

    Lấy nguyên văn từ CSDL. **Không bao giờ để LLM sinh phần này** — trên UI có
    dòng "Cảnh báo an toàn theo danh mục chuẩn — không do AI tự viết", và câu đó
    phải đúng.
    """
    if category is None or not category.is_hazardous:
        return ""
    return category.safety_warning or ""
