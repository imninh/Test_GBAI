"""Dữ liệu nền của hệ thống, khai báo một chỗ để test và script seed dùng chung.

**Quy định dữ liệu của chương trình:** chỉ dùng dữ liệu công khai, mô phỏng hoặc
đã ẩn danh. Toàn bộ toà nhà, căn hộ, cư dân dưới đây là **nhân vật mô phỏng** —
không có dữ liệu cá nhân thật nào trong hệ thống.

⚠️ **Về phần trích dẫn pháp luật:** các đoạn thuộc `doc_type="law"` là **diễn
giải rút gọn**, có gắn cờ ``needs_verification`` trong ``meta``. Trước khi đưa
lên pitch deck hoặc lên UI như trích dẫn nguyên văn, phải mở văn bản gốc tại
nguồn đã ghi và đối chiếu điều khoản lẫn hiệu lực hiện hành.
"""

from __future__ import annotations

from typing import Any

# --- Danh mục rác --------------------------------------------------------
# ``clip_prompts``: các câu mô tả tiếng Anh cho CLIP zero-shot ở tầng T0.5,
# phân cách bằng dấu "|". Viết tiếng Anh vì CLIP được huấn luyện trên tiếng Anh.

WASTE_CATEGORIES: list[dict[str, Any]] = [
    {
        "code": "recyclable",
        "name": "Rác tái chế",
        "parent_code": "",
        "is_hazardous": False,
        "min_confidence": 0.60,
        "bin_color": "#3a8fea",
        "icon": "♻️",
        "sort_order": 10,
        "handling_note": "Đổ hết phần thừa bên trong · Để ráo · Bóp dẹp cho gọn thùng",
        "safety_warning": "",
        "clip_prompts": "a photo of a recyclable item|a photo of clean packaging waste",
    },
    {
        "code": "recyclable_paper",
        "name": "Giấy, bìa carton",
        "parent_code": "recyclable",
        "is_hazardous": False,
        "min_confidence": 0.60,
        "bin_color": "#3a8fea",
        "icon": "📄",
        "sort_order": 11,
        "handling_note": "Gỡ băng dính và ghim · Xếp phẳng · Giấy dính dầu mỡ thì bỏ sang rác khác",
        "safety_warning": "",
        "clip_prompts": (
            "a photo of cardboard boxes|a photo of waste paper|a photo of a paper carton|"
            "a photo of a milk carton"
        ),
    },
    {
        "code": "recyclable_plastic",
        "name": "Nhựa tái chế",
        "parent_code": "recyclable",
        "is_hazardous": False,
        "min_confidence": 0.60,
        "bin_color": "#3a8fea",
        "icon": "🥤",
        "sort_order": 12,
        "handling_note": "Đổ hết nước · Tráng qua nếu dính đường sữa · Bóp dẹp · Giữ lại nắp",
        "safety_warning": "",
        "clip_prompts": (
            "a photo of a plastic bottle|a photo of a plastic cup|a photo of plastic packaging|"
            "a photo of a plastic container"
        ),
    },
    {
        "code": "recyclable_metal",
        "name": "Kim loại",
        "parent_code": "recyclable",
        "is_hazardous": False,
        "min_confidence": 0.60,
        "bin_color": "#3a8fea",
        "icon": "🥫",
        "sort_order": 13,
        "handling_note": "Đổ sạch phần thừa · Cẩn thận mép hộp sắc · Bóp dẹp lon nếu được",
        "safety_warning": "",
        "clip_prompts": "a photo of an aluminium can|a photo of a metal tin can|a photo of scrap metal",
    },
    {
        "code": "recyclable_glass",
        "name": "Thuỷ tinh",
        "parent_code": "recyclable",
        "is_hazardous": False,
        "min_confidence": 0.65,
        "bin_color": "#3a8fea",
        "icon": "🍾",
        "sort_order": 14,
        "handling_note": "Để nguyên chai lọ, không đập vỡ · Bọc riêng nếu đã vỡ · Không lẫn gương và bóng đèn",
        "safety_warning": "",
        "clip_prompts": "a photo of a glass bottle|a photo of a glass jar|a photo of glass containers",
    },
    {
        "code": "organic",
        "name": "Rác thực phẩm",
        "parent_code": "",
        "is_hazardous": False,
        "min_confidence": 0.60,
        "bin_color": "#2fae66",
        "icon": "🍃",
        "sort_order": 20,
        "handling_note": "Để ráo nước · Buộc kín túi · Bỏ đúng khung giờ thu gom để tránh mùi",
        "safety_warning": "",
        "clip_prompts": (
            "a photo of food waste|a photo of vegetable scraps|a photo of leftover food|"
            "a photo of fruit peels"
        ),
    },
    {
        "code": "other",
        "name": "Rác sinh hoạt khác",
        "parent_code": "",
        "is_hazardous": False,
        "min_confidence": 0.55,
        "bin_color": "#8a938a",
        "icon": "🗑",
        "sort_order": 30,
        "handling_note": "Buộc kín túi · Không lẫn pin, bóng đèn, thuốc vào nhóm này",
        "safety_warning": "",
        "clip_prompts": (
            "a photo of general household waste|a photo of a dirty foam food box|"
            "a photo of used tissues|a photo of a plastic bag of trash"
        ),
    },
    {
        "code": "hazardous",
        "name": "Rác nguy hại",
        "parent_code": "",
        "is_hazardous": True,
        # Ngưỡng cao hơn hẳn: sai ở nhóm này gây hại thật (CLAUDE.md mục 5).
        "min_confidence": 0.80,
        "bin_color": "#e8622a",
        "icon": "⚠️",
        "sort_order": 40,
        "handling_note": "Để riêng, không bỏ chung bất kỳ thùng nào · Mang tới điểm thu gom chuyên dụng",
        # Text cố định — KHÔNG BAO GIỜ để LLM sinh phần này.
        "safety_warning": (
            "KHÔNG bỏ vào thùng rác thường, KHÔNG vứt chung rác thực phẩm, "
            "KHÔNG làm thủng, không nén và không đốt. "
            "Mang tới điểm thu gom rác nguy hại của toà hoặc đăng ký để đội vệ sinh tới nhận."
        ),
        "clip_prompts": (
            "a photo of used batteries|a photo of a fluorescent light bulb|a photo of expired medicine|"
            "a photo of a chemical bottle|a photo of a spray can|a photo of an electronic device to discard"
        ),
    },
    {
        "code": "bulky",
        "name": "Đồ cồng kềnh",
        "parent_code": "",
        "is_hazardous": False,
        "min_confidence": 0.55,
        "bin_color": "#8b5cf6",
        "icon": "📦",
        "sort_order": 50,
        "handling_note": "Không để ở hành lang hay lối thoát hiểm · Đăng ký lịch thu gom trong app",
        "safety_warning": "",
        "clip_prompts": (
            "a photo of an old wooden cabinet|a photo of a discarded mattress|a photo of broken furniture|"
            "a photo of a large cardboard box pile|a photo of an old sofa"
        ),
    },
]


# --- Toà nhà và căn hộ ---------------------------------------------------

BUILDINGS: list[dict[str, Any]] = [
    {"code": "S1", "name": "Sunrise Residence — Toà S1", "address": "Khu đô thị mô phỏng, TP.HCM", "lat": 10.7769, "lng": 106.7009},
    {"code": "S2", "name": "Sunrise Residence — Toà S2", "address": "Khu đô thị mô phỏng, TP.HCM", "lat": 10.7782, "lng": 106.7021},
    {"code": "S3", "name": "Sunrise Residence — Toà S3", "address": "Khu đô thị mô phỏng, TP.HCM", "lat": 10.7801, "lng": 106.7044},
]

UNITS: list[dict[str, str]] = [
    {"building_code": "S1", "code": "S1-1203"},
    {"building_code": "S1", "code": "S1-0805"},
    {"building_code": "S1", "code": "S1-1508"},
    {"building_code": "S1", "code": "S1-0302"},
    {"building_code": "S2", "code": "S2-0501"},
    {"building_code": "S2", "code": "S2-1102"},
    {"building_code": "S3", "code": "S3-0710"},
]


# --- Tài khoản demo ------------------------------------------------------
# Ba nút "vào thẳng" trên màn đăng nhập, đúng bảng ở FRONTEND_SPEC mục 1.

DEMO_PASSWORD = "demo1234"

USERS: list[dict[str, Any]] = [
    {
        "email": "resident@demo.vn",
        "full_name": "Nguyễn Thị Lan",
        "role": "resident",
        "unit_code": "S1-1203",
        "green_points": 120,
    },
    {
        "email": "cleaner@demo.vn",
        "full_name": "Lê Văn Hùng",
        "role": "cleaner",
        "unit_code": "",
        "green_points": 0,
    },
    {
        "email": "manager@demo.vn",
        "full_name": "Trần Minh Đức",
        "role": "manager",
        "unit_code": "",
        "green_points": 0,
    },
    # Cư dân phụ — để tuyến gộp có nhiều điểm dừng thật, không phải bịa số.
    {"email": "resident2@demo.vn", "full_name": "Phạm Quốc Anh", "role": "resident", "unit_code": "S1-0805", "green_points": 60},
    {"email": "resident3@demo.vn", "full_name": "Đỗ Thu Hà", "role": "resident", "unit_code": "S1-1508", "green_points": 45},
    {"email": "resident4@demo.vn", "full_name": "Vũ Minh Khôi", "role": "resident", "unit_code": "S2-0501", "green_points": 30},
    {"email": "resident5@demo.vn", "full_name": "Ngô Bảo Trâm", "role": "resident", "unit_code": "S2-1102", "green_points": 15},
    {"email": "resident6@demo.vn", "full_name": "Lý Gia Huy", "role": "resident", "unit_code": "S3-0710", "green_points": 10},
]


# --- Lịch thu gom --------------------------------------------------------
# weekdays: 0 = Thứ 2 … 6 = Chủ nhật.

COLLECTION_SCHEDULES: list[dict[str, Any]] = [
    {"building_code": "S1", "category_code": "recyclable", "weekdays": [1, 3, 5], "window": "18:00-20:00", "location": "Phòng rác tầng — thùng xanh dương thứ 2"},
    {"building_code": "S1", "category_code": "organic", "weekdays": [0, 1, 2, 3, 4, 5, 6], "window": "06:00-08:00", "location": "Phòng rác tầng — thùng xanh lá"},
    {"building_code": "S1", "category_code": "other", "weekdays": [0, 2, 4], "window": "18:00-20:00", "location": "Phòng rác tầng — thùng xám"},
    {"building_code": "S1", "category_code": "hazardous", "weekdays": [5], "window": "09:00-11:00", "location": "Điểm thu rác nguy hại — tầng hầm B1"},
    {"building_code": "S1", "category_code": "bulky", "weekdays": [3], "window": "08:00-10:00", "location": "Khu tập kết sân sau, cần đăng ký trước"},
    {"building_code": "S2", "category_code": "recyclable", "weekdays": [1, 4], "window": "17:00-19:00", "location": "Phòng rác tầng — thùng xanh dương"},
    {"building_code": "S2", "category_code": "organic", "weekdays": [0, 1, 2, 3, 4, 5, 6], "window": "06:00-08:00", "location": "Phòng rác tầng — thùng xanh lá"},
    {"building_code": "S2", "category_code": "hazardous", "weekdays": [5], "window": "09:00-11:00", "location": "Điểm thu rác nguy hại — tầng hầm B1"},
    {"building_code": "S2", "category_code": "bulky", "weekdays": [3], "window": "08:00-10:00", "location": "Khu tập kết sân sau, cần đăng ký trước"},
    {"building_code": "S3", "category_code": "recyclable", "weekdays": [2, 5], "window": "17:00-19:00", "location": "Phòng rác tầng — thùng xanh dương"},
    {"building_code": "S3", "category_code": "bulky", "weekdays": [3], "window": "14:00-16:00", "location": "Khu tập kết sân sau, cần đăng ký trước"},
]


# --- Kho tri thức (RAG) --------------------------------------------------

KNOWLEDGE_DOCS: list[dict[str, Any]] = [
    {
        "title": "Nội quy phân loại rác — Toà Sunrise S1",
        "building_code": "S1",
        "doc_type": "building_rule",
        "source": "Nội quy toà nhà (tài liệu mô phỏng cho demo)",
        "effective_date": "2026-01-01",
        "chunks": [
            {
                "section": "Mục 4.1 — Nguyên tắc chung",
                "content": (
                    "Cư dân toà S1 phân loại rác tại nguồn thành bốn nhóm: rác tái chế, rác thực phẩm, "
                    "rác sinh hoạt khác và rác nguy hại. Đồ cồng kềnh không bỏ tại phòng rác tầng mà "
                    "phải đăng ký lịch thu gom riêng."
                ),
            },
            {
                "section": "Mục 4.2 — Rác tái chế",
                "content": (
                    "Rác tái chế gồm giấy, bìa carton, nhựa, kim loại và thuỷ tinh, bỏ vào thùng xanh dương "
                    "đặt tại phòng rác mỗi tầng. Vỏ hộp sữa giấy tráng nhôm được tính là rác tái chế và "
                    "KHÔNG cần tách lớp bạc; chỉ cần đổ hết phần sữa thừa và bóp dẹp hộp. "
                    "Thu gom vào thứ Ba, thứ Năm và thứ Bảy, khung 18:00–20:00."
                ),
            },
            {
                "section": "Mục 4.3 — Rác thực phẩm",
                "content": (
                    "Rác thực phẩm để ráo nước, buộc kín túi, bỏ vào thùng xanh lá. Thu gom tất cả các ngày "
                    "trong tuần, khung 06:00–08:00. Không bỏ vỏ sò, xương lớn và dầu mỡ lỏng vào nhóm này."
                ),
            },
            {
                "section": "Mục 4.4 — Rác nguy hại",
                "content": (
                    "Pin, ắc quy, bóng đèn huỳnh quang, thuốc hết hạn, hoá chất tẩy rửa mạnh và thiết bị "
                    "điện tử hỏng thuộc nhóm rác nguy hại. Cư dân mang tới điểm thu gom tại tầng hầm B1, "
                    "hoặc đăng ký để đội vệ sinh tới nhận. Tuyệt đối không bỏ chung với rác sinh hoạt."
                ),
            },
            {
                "section": "Mục 4.5 — Đồ cồng kềnh",
                "content": (
                    "Đồ cồng kềnh gồm tủ, giường, đệm, ghế sofa, thùng carton số lượng lớn. Cư dân đăng ký "
                    "trước ít nhất một ngày. Yêu cầu có tổng khối lượng ước tính vượt 30 kg hoặc trên 3 món "
                    "cần ban quản lý duyệt trước khi xếp lịch. Không để đồ tại hành lang hoặc lối thoát hiểm."
                ),
            },
        ],
    },
    {
        "title": "Nội quy phân loại rác — Toà Sunrise S2",
        "building_code": "S2",
        "doc_type": "building_rule",
        "source": "Nội quy toà nhà (tài liệu mô phỏng cho demo)",
        "effective_date": "2026-01-01",
        "chunks": [
            {
                "section": "Mục 3.1 — Nhóm rác và thùng chứa",
                "content": (
                    "Toà S2 dùng chung bảng màu thùng với toà S1. Khác biệt: rác tái chế của S2 thu gom "
                    "vào thứ Ba và thứ Sáu, khung 17:00–19:00, sớm hơn S1 một tiếng."
                ),
            },
            {
                "section": "Mục 3.2 — Điểm tập kết",
                "content": (
                    "Phòng rác tầng của S2 chỉ đặt được hai thùng, nên thùng kim loại và thuỷ tinh gộp chung "
                    "với thùng nhựa. Đội vệ sinh tách lại tại khu tập kết sân sau."
                ),
            },
        ],
    },
    {
        "title": "Danh mục rác nguy hại và cách xử lý",
        "building_code": "",
        "doc_type": "hazard",
        "source": "Danh mục nội bộ, biên soạn theo hướng dẫn phân loại rác tại nguồn",
        "effective_date": "2026-01-01",
        "chunks": [
            {
                "section": "Pin và ắc quy",
                "content": (
                    "Pin tiểu, pin cúc áo, pin sạc dự phòng và ắc quy chứa kim loại nặng. Không làm thủng, "
                    "không nén, không đốt. Pin phồng hoặc rò rỉ phải để riêng trong hộp kín và báo ban quản lý ngay."
                ),
            },
            {
                "section": "Bóng đèn huỳnh quang",
                "content": (
                    "Bóng đèn huỳnh quang chứa thuỷ ngân. Giữ nguyên bóng, bọc giấy báo, không đập vỡ. "
                    "Nếu đã vỡ thì mở cửa thông gió, không dùng máy hút bụi để dọn."
                ),
            },
            {
                "section": "Thuốc hết hạn",
                "content": (
                    "Thuốc hết hạn không đổ xuống bồn cầu và không bỏ chung rác sinh hoạt. Giữ nguyên vỉ, "
                    "mang tới điểm thu gom của toà hoặc nhà thuốc có nhận lại."
                ),
            },
            {
                "section": "Vật sắc nhọn y tế",
                "content": (
                    "Kim tiêm, bơm tiêm, que thử đường huyết và dao mổ thuộc nhóm rác y tế lây nhiễm. "
                    "Hệ thống KHÔNG tự hướng dẫn nhóm này trong mọi trường hợp, luôn chuyển cho ban quản lý "
                    "để xử lý theo quy trình riêng."
                ),
            },
        ],
    },
    {
        "title": "Luật Bảo vệ môi trường 2020 — phân loại chất thải rắn sinh hoạt tại nguồn",
        "building_code": "",
        "doc_type": "law",
        "source": "Luật Bảo vệ môi trường số 72/2020/QH14",
        "effective_date": "2022-01-01",
        "chunks": [
            {
                "section": "Diễn giải — nghĩa vụ phân loại tại nguồn",
                "content": (
                    "Luật Bảo vệ môi trường 2020 đặt ra nghĩa vụ phân loại chất thải rắn sinh hoạt tại nguồn "
                    "đối với hộ gia đình và cá nhân, và giao trách nhiệm tổ chức thực hiện cho đơn vị quản lý "
                    "khu chung cư. Đây là nền pháp lý cho việc toà nhà triển khai phân loại rác."
                ),
                "needs_verification": True,
            }
        ],
    },
    {
        "title": "Nghị định 45/2022/NĐ-CP — xử phạt vi phạm hành chính trong lĩnh vực bảo vệ môi trường",
        "building_code": "",
        "doc_type": "law",
        "source": "Nghị định 45/2022/NĐ-CP",
        "effective_date": "2022-08-25",
        "chunks": [
            {
                "section": "Diễn giải — chế tài với hành vi không phân loại",
                "content": (
                    "Nghị định 45/2022/NĐ-CP quy định chế tài xử phạt hành chính đối với hành vi không phân loại "
                    "chất thải rắn sinh hoạt theo quy định. Mức phạt cụ thể và điều khoản áp dụng phải tra tại "
                    "văn bản gốc trước khi trích dẫn ra ngoài."
                ),
                "needs_verification": True,
            }
        ],
    },
]


# --- Giới hạn đã biết của hệ thống ---------------------------------------
# Text cứng, luôn hiển thị trên trang Vận hành và trên màn kết quả (spec 4.16).
# Đây là phần đáp thẳng yêu cầu "nêu rõ giới hạn, rủi ro" của chương trình.

KNOWN_LIMITATIONS: list[str] = [
    "Nhận diện tốt nhất với một món rác, chụp rõ, đủ sáng. Ảnh nhiều món chồng lên nhau có độ chính xác thấp hơn đáng kể.",
    "Không nhìn xuyên được túi nilon đục — rác đã đóng túi kín nằm ngoài phạm vi xử lý của hệ thống, có chủ đích.",
    "Không phân biệt được nhựa PET và nhựa HDPE khi nhãn bị mờ hoặc mất.",
    "Không xác định được rác y tế lây nhiễm — luôn chuyển người, không tự trả lời.",
    "Quy định phân loại khác nhau giữa các toà; hướng dẫn chỉ đúng với toà đang chọn.",
    "Khối lượng do AI ước lượng có sai số lớn (±40%) — chỉ dùng để gợi ý, đội vệ sinh cân lại tại chỗ.",
    "Dữ liệu demo là dữ liệu mô phỏng và ảnh tự chụp, không phải dữ liệu cư dân thật.",
    "Bản demo trên hạ tầng miễn phí lưu ảnh trên đĩa tạm — ảnh đã tải lên sẽ mất khi máy chủ khởi động lại.",
    "Tầng T0.5 (model local CLIP) tắt trên bản deploy vì máy chủ miễn phí không đủ bộ nhớ; ảnh đi thẳng lên tầng T1.",
]

# Lý do từ chối yêu cầu thu gom — danh sách cố định, không cho gõ tự do, để dữ
# liệu chảy ngược vào trang Chất lượng AI (PLO 7).
PICKUP_REJECT_REASONS: list[dict[str, str]] = [
    {"code": "vuot_nang_luc", "label_vi": "Vượt năng lực xử lý trong ngày"},
    {"code": "co_rac_nguy_hai", "label_vi": "Có rác nguy hại cần quy trình riêng"},
    {"code": "thieu_thong_tin", "label_vi": "Thông tin không đủ"},
    {"code": "trung_yeu_cau", "label_vi": "Trùng với yêu cầu đã có"},
    {"code": "sai_dia_chi", "label_vi": "Sai địa chỉ hoặc căn hộ"},
    {"code": "khac", "label_vi": "Khác (ghi rõ)"},
]

# Các cặp nhãn hay bị nhầm, ghim trên đầu hàng đợi xác nhận nhãn (spec 4.11).
HARD_CASES: list[dict[str, str]] = [
    {"pair": "Hộp sữa giấy tráng nhôm ↔ Giấy", "note": "Lớp tráng nhôm làm model nghiêng về nhóm kim loại"},
    {"pair": "Ly nhựa có màng ↔ Nhựa tái chế", "note": "Màng dán miệng ly thường bị bỏ qua khi chụp từ trên xuống"},
    {"pair": "Khay cơm dính dầu ↔ Rác thực phẩm", "note": "Khay bẩn không còn tái chế được nhưng nhìn vẫn giống nhựa sạch"},
]
