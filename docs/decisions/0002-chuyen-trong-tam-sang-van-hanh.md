# ADR-0002 — Chuyển trọng tâm sản phẩm từ cư dân sang vận hành

**Ngày:** 29/07/2026
**Trạng thái:** Đã chốt
**Thay thế:** không — bổ sung cho [ADR-0001](0001-chon-de-tai-greenbin.md), đề tài VHR-17 giữ nguyên

## Bối cảnh

Tối 28/07 nhóm phỏng vấn **2 cư dân chung cư** (phân khúc có dịch vụ vệ sinh trọn gói) và thu được ba phát hiện đi ngược giả định ban đầu:

1. **Cư dân không tự phân loại rác — và cũng không thấy đó là vấn đề của mình.** Toà nhà đã bố trí nhân viên phân loại lại toàn bộ rác sau khi thu.
2. **Việc thu gom đồ cồng kềnh không gây khó chịu cho cư dân.** Mỗi tầng có phòng rác riêng, có thang máy chở rác riêng, đội vệ sinh thu khoảng 22h, rác không tồn quá một ngày.
3. **Pin và rác nguy hại bị vứt chung vào túi rác sinh hoạt**, không có chế tài, và người phân loại tự lọc ra bằng tay.

Người được phỏng vấn nói thẳng: một sản phẩm **chỉ cung cấp thông tin** thì họ không có lý do dùng, vì "hiện đang có người phân loại rồi".

Nhận xét độc lập từ lab coach trùng khớp: nếu sản phẩm dừng ở phân loại ảnh thì không tạo ra giá trị.

## Vấn đề cần quyết

Giả định ban đầu — *"cư dân muốn phân loại đúng nhưng không biết cách"* — không đứng vững ở phân khúc đã khảo sát. Vậy giữ đề tài hay đổi?

## Quyết định

**Giữ nguyên đề VHR-17 và toàn bộ kiến trúc. Chuyển người dùng chính từ cư dân sang vận hành:**

| | Trước | Sau |
|---|---|---|
| Người dùng chính | Cư dân | **BQL toà nhà** (người chịu rủi ro pháp lý và chi phí) |
| Người thao tác chính | Cư dân | **Đội vệ sinh** (người đang thực sự phân loại) |
| Cư dân | Người dùng duy nhất | Vai trò phụ, chạm nhẹ, **không nằm trên đường găng** |
| Giá trị cốt lõi | Trả lời "bỏ đâu" | **Kích hoạt hành động trong hệ thống** |

Nguyên tắc mới, áp cho mọi tính năng về sau:

> **Mỗi kết quả AI phải sinh ra một hành động hoặc một bản ghi trong hệ thống, không được dừng ở một màn hình trả lời.**

Ví dụ: nhận diện pin lithium → tạo cảnh báo cho đội vệ sinh tầng đó **và** ghi vào sổ theo dõi rác nguy hại của toà. Phòng rác đầy → tạo yêu cầu thu gom → gộp tuyến → đội trưởng duyệt. Cuối tháng → tự sinh báo cáo tuân thủ.

## Lý do

1. **Bản thân đề bài đã nghiêng về vận hành.** 3 trong 4 ràng buộc gốc của VHR-17 nói về vận hành, không về cư dân: HITL do BQL/đội vệ sinh duyệt · chính xác trong phân loại · tối ưu chi phí vận chuyển và lịch thu gom. Nhóm đã đọc đề thành "app cư dân" nên mới bí. Đây là **chỉnh trọng tâm bên trong đề, không phải đổi đề.**

2. **Không phát sinh việc mới.** `docs/FRONTEND_SPEC.md` v1.0 (28/07) đã đặc tả sẵn 3 vai trò và 18 màn, trong đó phần vận hành đã là phần lớn nhất:

   | Phát hiện từ phỏng vấn | Đã có sẵn ở |
   |---|---|
   | Lao công mới là người phân loại | Vai trò B — Đội vệ sinh (mục 1) |
   | Phải hỗ trợ bằng hành động | 4.7 · 4.10 · **4.12 Duyệt tuyến gộp** |
   | Pin vứt chung, không ai phạt | 4.4 "Mình chưa chắc" + luồng nguy hại |
   | BQL chịu áp lực tuân thủ | Vai trò C · 4.13 Tổng quan · 4.16 Vận hành & Chi phí |

   Thay đổi nằm ở **cách kể câu chuyện và thứ tự ưu tiên**, không ở phạm vi code.

3. **Người trả tiền và người có pain point trùng nhau.** Cư dân không mất gì khi phân loại sai. BQL thì có nghĩa vụ phân loại tại nguồn theo Luật Bảo vệ môi trường 2020 và chịu chế tài theo Nghị định 45/2022/NĐ-CP, đồng thời trả chi phí xử lý và chi phí nhân công phân loại. Đội vệ sinh chịu rủi ro sức khoẻ khi bới rác nguy hại bằng tay.

4. **Sản phẩm không được chết vì cư dân không hợp tác.** Người được phỏng vấn cho biết nhiều cư dân lớn tuổi không dùng nổi ứng dụng thông thường. Nếu hệ thống phụ thuộc vào việc cư dân chịu cài app và chịu chụp ảnh thì nó sẽ không chạy. Sau quyết định này, hệ thống vẫn vận hành đầy đủ ngay cả khi **không có cư dân nào dùng**.

## Hệ quả

**Thay đổi ngay:**
- Đoạn mô tả sản phẩm ở mục 0 của `FRONTEND_SPEC.md` và mục 1 của `CLAUDE.md` viết lại theo góc vận hành.
- Luồng cư dân bỏ bắt buộc đăng nhập: vào bằng QR dán tại phòng rác, chụp là ra kết quả.
- Thêm màn **Báo cáo tuân thủ theo tháng** cho BQL vào backlog (P1) — đây là hiện thân rõ nhất của nguyên tắc "AI phải sinh ra bản ghi".

**Không thay đổi:** kiến trúc 3 tầng model · 3 điểm HITL · toàn bộ phần an toàn AI · kế hoạch dữ liệu · kế hoạch eval · tech stack.

## Đánh đổi chấp nhận

- **Bằng chứng mỏng: n = 2, cùng một phân khúc.** Cả hai người đều ở chung cư có dịch vụ trọn gói. Kết luận đúng phải phát biểu là *"ở phân khúc có dịch vụ vệ sinh trọn gói, cư dân không có động lực thay đổi hành vi"* — một phát hiện về phân khúc, không phải về đề tài. Chung cư cũ và nhà tập thể có thể ngược lại. **Cần phỏng vấn thêm ít nhất 1 lao công và 1 người thuộc BQL** để xác nhận phía vận hành; cho tới lúc đó, phần pain point của lao công vẫn là giả định.
- Vai trò cư dân nhẹ đi làm giảm sức hút cảm xúc khi demo. Bù lại bằng cách mở đầu demo từ góc BQL và số tiền tiết kiệm được.

## Đã cân nhắc và loại

- **Đổi sang đề khác.** Loại — phát hiện này không phủ nhận đề, và đổi đề vào ngày thứ 3 sẽ vứt bỏ toàn bộ phần nền đã dựng.
- **Làm thiết bị IoT / robot phân loại** (ý nảy ra trong lúc brainstorm). Loại — chương trình yêu cầu web/app deploy online và chấm trên 5 cột phần mềm; phần cứng không có cột điểm nào nhưng sẽ nuốt toàn bộ thời gian còn lại.
- **Thêm trợ lý giọng nói cho cư dân lớn tuổi.** Loại khỏi P0 — cách xử lý đúng cho vấn đề "cư dân không dùng được app" là bỏ cư dân ra khỏi đường găng, không phải thêm một kênh tương tác nữa.
