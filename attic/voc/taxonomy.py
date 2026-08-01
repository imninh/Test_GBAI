"""Danh mục chủ đề (taxonomy) cho phản hồi khách hàng ngành bất động sản.

Taxonomy được cố định để số liệu so sánh được giữa các kỳ. Chủ đề mới do
clustering phát hiện KHÔNG được tự động thêm vào đây — phải qua HITL duyệt.

Mọi thay đổi taxonomy đều phải tăng ``TAXONOMY_VERSION`` và ghi ADR trong
``docs/decisions/``, vì nó làm số liệu các kỳ cũ không còn so sánh được.
"""

from __future__ import annotations

TAXONOMY_VERSION = "v1"

OTHER_TOPIC = "Khác"

TAXONOMY: dict[str, list[str]] = {
    "Giá & tài chính": [
        "Giá bán",
        "Chính sách chiết khấu",
        "Hỗ trợ vay & lãi suất",
        "Phí quản lý",
        "Tiến độ thanh toán",
    ],
    "Sản phẩm & chất lượng": [
        "Thiết kế căn hộ",
        "Vật liệu hoàn thiện",
        "Diện tích thực tế",
        "View & hướng",
    ],
    "Tiện ích": [
        "Hồ bơi & gym",
        "Khu vui chơi trẻ em",
        "Chỗ đậu xe",
        "An ninh",
        "Mảng xanh",
    ],
    "Tiến độ & bàn giao": [
        "Chậm tiến độ",
        "Chất lượng bàn giao",
        "Sửa lỗi sau bàn giao",
    ],
    "Đội ngũ bán hàng": [
        "Thái độ sale",
        "Thông tin sai lệch",
        "Tần suất làm phiền",
        "Tốc độ phản hồi",
    ],
    "Pháp lý & thủ tục": [
        "Sổ hồng",
        "Hợp đồng mua bán",
        "Thủ tục vay",
    ],
    "Vị trí & hạ tầng": [
        "Kết nối giao thông",
        "Tiện ích xung quanh",
        "Ngập nước & kẹt xe",
    ],
    "Dịch vụ hậu mãi": [
        "Chăm sóc khách hàng",
        "Ban quản lý toà nhà",
        "Xử lý khiếu nại",
    ],
    OTHER_TOPIC: [],
}

# Thang cảm xúc -2..+2. Dùng số nguyên để tính trung bình và so sánh giữa kỳ.
SENTIMENT_LABELS: dict[int, str] = {
    -2: "Rất tiêu cực",
    -1: "Tiêu cực",
    0: "Trung tính",
    1: "Tích cực",
    2: "Rất tích cực",
}

SENTIMENT_MIN = -2
SENTIMENT_MAX = 2

# Nguồn dữ liệu được hỗ trợ. Khớp với 4 nguồn nêu trong đề bài.
SOURCES: dict[str, str] = {
    "survey": "Khảo sát",
    "crm_note": "Ghi chú sale (CRM)",
    "social": "Mạng xã hội",
    "call_transcript": "Cuộc gọi CSKH",
}


def all_topics() -> list[str]:
    """Trả về danh sách chủ đề cấp 1."""
    return list(TAXONOMY.keys())


def subtopics(topic: str) -> list[str]:
    """Trả về danh sách chủ đề con của một chủ đề cấp 1."""
    return TAXONOMY.get(topic, [])


def is_valid_topic(topic: str, subtopic: str | None = None) -> bool:
    """Kiểm tra cặp (chủ đề, chủ đề con) có nằm trong taxonomy không.

    Dùng để validate output của LLM — LLM hay bịa ra chủ đề không tồn tại.
    """
    if topic not in TAXONOMY:
        return False
    if subtopic is None:
        return True
    return subtopic in TAXONOMY[topic]


def star_to_sentiment(stars: int) -> int:
    """Quy đổi số sao 1-5 (Google Maps) sang thang cảm xúc -2..+2.

    Đây là nguồn nhãn yếu (weak label) miễn phí: cho phép đo chất lượng
    sentiment trên hàng nghìn mẫu mà không phải gán tay.
    """
    mapping = {1: -2, 2: -1, 3: 0, 4: 1, 5: 2}
    if stars not in mapping:
        raise ValueError(f"Số sao không hợp lệ: {stars} (phải từ 1 đến 5)")
    return mapping[stars]


def as_prompt_block() -> str:
    """Render taxonomy thành khối text để chèn vào prompt.

    Khối này dài và lặp lại ở mọi request phân loại — luôn đặt ở ĐẦU prompt
    để tận dụng prompt caching, phần text thay đổi (phản hồi khách) đặt ở cuối.
    """
    lines: list[str] = []
    for topic, subs in TAXONOMY.items():
        if subs:
            lines.append(f"- {topic}: {', '.join(subs)}")
        else:
            lines.append(f"- {topic}: (dùng khi không khớp chủ đề nào ở trên)")
    return "\n".join(lines)
