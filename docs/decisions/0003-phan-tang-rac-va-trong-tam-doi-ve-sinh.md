# ADR-0003 — Phân tầng rác, giới hạn phạm vi vision, và đội vệ sinh là người thao tác trung tâm

**Ngày:** 30/07/2026
**Trạng thái:** Đã chốt
**Quan hệ:** làm rõ và thu hẹp [ADR-0002](0002-chuyen-trong-tam-sang-van-hanh.md); không thay thế. Đề tài VHR-17 giữ nguyên.

## Bối cảnh

ADR-0002 (29/07) chuyển trọng tâm từ cư dân sang "vận hành", nhưng để lại hai câu hỏi chưa trả lời:

1. **"Vận hành" là ai cụ thể?** ADR-0002 gộp BQL và đội vệ sinh làm một, và mô tả đội vệ sinh là
   "người thao tác" mà không nói họ thao tác ở đâu, lúc nào, trên loại rác nào.
2. **Bao nhiêu phần rác thực sự đi qua AI?** Cả ADR-0001 và ADR-0002 đều mặc định là "rác" nói
   chung, chưa ai hỏi câu này.

Ngày 29–30/07, chủ dự án brainstorm thêm với Gemini (`docs/Gemini_GBAI.md` — **tài liệu brainstorm,
không phải kế hoạch**) và thu được hai ràng buộc vật lý chưa từng nằm trong tài liệu nhóm:

- **Túi rác sinh hoạt được đóng kín bằng túi nilon đục.** Cư dân không mở túi ra để chụp, và
  vision không nhìn xuyên qua túi. Phần lớn khối lượng rác hàng ngày thuộc loại này.
- **Phòng rác mỗi tầng chật, chỉ chứa được khoảng 2–3 thùng tiêu chuẩn.** Không có chỗ cho mô hình
  "4 thùng phân loại mỗi tầng".

Đọc lại thẻ đề (`docs/DE_BAI_VHR-17.md`) xác nhận thêm: quy định chung mục 1 ghi rõ nội dung đề là
**gợi ý**, và nhóm **được kỳ vọng tinh chỉnh theo khảo sát người dùng thực tế**. Việc lệch khỏi
câu "cư dân không biết phân loại đúng" trong thẻ đề là hành vi được chương trình khuyến khích, miễn
là có bằng chứng và ghi lại — đúng cái ADR-0002 đang làm.

## Vấn đề cần quyết

Nếu vision không thể phân loại phần lớn khối lượng rác hàng ngày, thì lời hứa "AI phân loại rác tại
nguồn" có còn đứng được không, và phải phát biểu lại thế nào cho trung thực?

## Quyết định

### 1. Phân tầng rác — chốt phạm vi áp dụng của vision

Rác trong toà nhà chia làm hai luồng, và **chỉ luồng B đi qua AI**:

| | **Luồng A — Rác sinh hoạt hàng ngày** | **Luồng B — Tái chế, cồng kềnh, nguy hại** |
|---|---|---|
| Gồm | Đồ ăn thừa, khăn giấy, rác ướt, đóng túi kín | Chai nhựa, lon, carton, sofa, đệm, pin, bóng đèn, điện tử |
| Qua AI? | **Không.** Nằm ngoài phạm vi, có chủ đích | **Có.** Toàn bộ luồng AI phục vụ nhóm này |
| Xử lý | Vào "rác còn lại", không bắt chụp ảnh, không ghi nhận | Phân loại → hướng dẫn có nguồn → tạo yêu cầu → gộp tuyến → người duyệt |
| Vì sao | Không ai tranh chấp nhãn của nó; vision không nhìn xuyên túi đục | Có giá trị kinh tế (bán được), có rủi ro pháp lý và rủi ro sức khoẻ |

**Cách phát biểu chuẩn, dùng thống nhất ở slide, README và demo:**

> GreenBin không phân loại toàn bộ rác của toà nhà, và không cố làm việc đó. Rác ướt đóng túi kín
> không cần AI — nó luôn đi vào "rác còn lại" và không ai tranh chấp nhãn của nó. Phần rác còn lại
> mới là phần **có giá trị kinh tế, có rủi ro pháp lý và có rủi ro sức khoẻ** — và đó chính là phần
> mà hôm nay đội vệ sinh đang phải **bới bằng tay để tìm**. GreenBin nhắm đúng phần đó.

### 2. Đội vệ sinh là người thao tác trung tâm, không phải cư dân

Điểm chụp ảnh chính của hệ thống là **phòng rác tầng và khu tập kết**, do đội vệ sinh thao tác trong
ca làm việc — không phải bàn bếp căn hộ.

Hệ quả trên sản phẩm:
- Nghiệp vụ chính của luồng phân loại là **"lao công gặp một món rác không rõ nhãn hoặc nghi nguy
  hại trong lúc làm việc"**, không phải "cư dân tò mò hỏi bỏ đâu".
- Mỗi lần lao công chụp phải sinh ra **một bản ghi hoặc một hành động** (cảnh báo nguy hại tới
  đúng tầng đúng ca · thêm vào yêu cầu thu gom · ghi sổ tuân thủ), đúng nguyên tắc ADR-0002.
- Giao diện lao công thiết kế cho **điện thoại một tay, dùng ngoài trời, tay bẩn, mạng yếu**: nút
  to, ít chữ, chụp là xong, chịu được offline.

### 3. Giữ luồng cư dân, nhưng không ai được phụ thuộc vào nó

Luồng cư dân **không bị cắt** — thẻ đề ghi nó ở mục "Cơ bản" (`agent phân loại rác qua ảnh/mô tả &
hướng dẫn`), và nó vẫn là bước mở đầu đẹp nhất của video demo. Nhưng:
- Vào bằng **QR dán tại phòng rác**, không bắt đăng nhập (đã chốt ở ADR-0002).
- **Hệ thống phải chạy đủ và demo được trọn vẹn ngay cả khi không có cư dân nào dùng.**

### 4. Ước lượng khối lượng: trả về khoảng, ngưỡng HITL tính theo cận trên

Vision ước lượng khối lượng từ ảnh rất không đáng tin (sai vài lần là bình thường), nhưng ngưỡng
HITL 30kg lại phụ thuộc đúng con số đó. Vì vậy:
- Model trả về **khoảng kèm căn cứ**: `"sofa 2 chỗ · ~40–60kg"`, không trả một con số đơn.
- Người nhập lại hoặc chỉnh được, và lần chỉnh đó được ghi lại.
- **Ngưỡng HITL so với cận trên của khoảng** → sai số luôn nghiêng về phía "cần người duyệt".

### 5. Tem QR định danh nguồn phát sinh — P1, mục đích là bản ghi truy vết

Cấp mã QR định danh căn hộ/tầng cho túi tái chế và đồ cồng kềnh; lao công quét khi thu. Mục đích là
**sinh bản ghi "món này từ đâu, ai thu, lúc nào"** — nền cho báo cáo tuân thủ theo tháng.

**Không dùng để trừ điểm uy tín hay phạt cư dân.** Xếp **P1**, làm sau khi luồng P0 đã chạy.

## Lý do

1. **Trung thực về giới hạn là điểm cộng, không phải điểm trừ.** Quy định chung mục 4 yêu cầu "nêu
   rõ giới hạn, rủi ro và hướng cải tiến". Một nhóm nói được "80% rác không đi qua AI của tôi, và
   đây là lý do đó là quyết định đúng" thì thuyết phục hơn nhiều một nhóm ngầm hứa phân loại tất cả
   rồi bị hỏi vỡ trong Q&A. Câu hỏi *"thế túi rác đóng kín thì AI làm gì?"* gần như chắc chắn sẽ
   được hỏi — tốt nhất là nhóm tự nêu trước.

2. **Ràng buộc túi kín củng cố ADR-0002 chứ không phủ nhận.** Nếu vision không phân loại được rác
   cư dân đã đóng túi, thì càng không thể xây sản phẩm dựa trên hành vi chụp ảnh của cư dân. Điểm
   chụp bắt buộc phải dịch về nơi rác đã được mở ra và đang được phân loại bằng tay — tức phòng rác
   và khu tập kết, do lao công thao tác. Hai ADR chỉ về cùng một hướng.

3. **Phạm vi hẹp lại nhưng giá trị không giảm.** Phần rác đi qua AI đúng là phần sinh ra tiền (tái
   chế bán được), sinh ra rủi ro pháp lý (nguy hại phải có sổ theo dõi) và sinh ra chi phí vận
   chuyển (cồng kềnh phải điều xe). Ba trục giá trị ở mục 3.1 báo cáo mentor **không mất trục nào**.

4. **Ràng buộc phòng rác chật loại bỏ một hướng thiết kế sai.** Không thể giải bài toán này bằng
   cách thêm thùng phân loại mỗi tầng. Phải giải bằng lớp thông tin và lớp điều phối — đúng cái
   nhóm đang làm, và cũng là lý do thêm để không đi hướng phần cứng.

## Mức độ bằng chứng — đọc kỹ trước khi đưa lên slide

ADR này dựa trên **brainstorm với LLM, không phải phỏng vấn**. Phân loại rõ để không nói quá:

| Phát biểu | Mức độ | Cách xác nhận |
|---|---|---|
| Vision không nhìn xuyên túi nilon đục | **Hiển nhiên đúng** — không cần bằng chứng | — |
| Mỗi tầng có phòng rác riêng, đội vệ sinh thu ~22h | **Đã xác nhận** — phỏng vấn cư dân 28/07 | ADR-0002 |
| Đội vệ sinh phân loại lại rác bằng tay, kể cả pin | **Đã xác nhận qua cư dân**, chưa xác nhận qua chính lao công | Phỏng vấn lao công |
| *"~80% khối lượng rác là rác ướt đóng túi"* | ⚠️ **Chưa kiểm — con số từ LLM** | Xin số liệu khối lượng rác theo loại từ BQL, hoặc đếm tay 1 tầng 1 ngày |
| *"Phòng rác tầng chỉ chứa 2–3 thùng"* | ⚠️ **Chưa kiểm** | **Dễ nhất: đi xuống phòng rác chụp ảnh.** Làm được trong 10 phút |
| Pain point cụ thể của lao công (rủi ro sức khoẻ, quá tải) | ⚠️ **Vẫn là giả định** | Phỏng vấn 1 lao công + 1 BQL — vẫn là việc nghiên cứu ưu tiên số 1 |

**Quy tắc áp dụng:** trên slide và trong báo cáo, dùng **"phần lớn"** thay cho con số 80% cho tới
khi có số đo. Ảnh chụp phòng rác thật thì đưa được vào slide ngay và mạnh hơn mọi con số dẫn lại.

## Hệ quả

**Thay đổi ngay:**
- `CLAUDE.md`: thêm mục "Giới hạn đã biết" ghi rõ phạm vi luồng A / luồng B.
- Trang Vận hành và slide: khối **"Giới hạn đã biết"** phải có dòng về túi rác đóng kín.
- `FRONTEND_SPEC.md`: luồng phân loại viết lại lấy **lao công tại phòng rác** làm nghiệp vụ chính,
  cư dân là cửa vào thứ hai. Ảnh hưởng mục 0 (đang chờ viết lại) và các màn thuộc vai trò B.
- Schema yêu cầu thu gom: khối lượng lưu thành **khoảng** (`weight_min`, `weight_max`) chứ không
  phải một số; so ngưỡng HITL với `weight_max`.
- Prompt phân loại: bắt model trả khoảng khối lượng kèm căn cứ, không trả một con số.
- **Không sinh trường `diem_thuong` từ LLM** — điểm do hệ thống tính từ `waste_categories`. Để model
  tự sinh điểm là một bề mặt prompt injection (PLO 6).

**Không thay đổi:** định tuyến 3 tầng model · 3 điểm HITL · toàn bộ phần an toàn AI và quyền riêng
tư · kế hoạch dữ liệu · kế hoạch eval · tech stack · kịch bản demo 7 bước.

**Việc mới sinh ra:** đi chụp ảnh phòng rác tầng (10 phút, làm được ngay) · xin số liệu khối lượng
rác theo loại từ BQL (gộp vào buổi phỏng vấn BQL).

## Đánh đổi chấp nhận

- **Phạm vi hẹp lại có thể bị đọc thành "làm ít".** Cách xử lý: không trình bày đây là phần bị cắt,
  mà là **phần được chọn**, kèm lý do kinh tế và lý do an toàn. Cùng một sự thật, hai cách kể, và
  cách kể đúng là cách có lập luận.
- **Lao công trung tâm làm demo kém cảm xúc hơn cư dân chụp ảnh.** Đã chấp nhận từ ADR-0002. Bù
  bằng bước 1 của kịch bản demo (cư dân) và bằng con số tiền tiết kiệm ở bước 7.
- **ADR này dựa trên brainstorm LLM, chưa phải phỏng vấn.** Hai trong ba ràng buộc chính chưa được
  kiểm. Rủi ro thấp vì cả hai đều kiểm được rẻ và nhanh, nhưng phải kiểm trước khi lên pitch deck.

## Đã cân nhắc và loại

- **Bắt cư dân phân loại rác ướt bằng cách mở túi ra chụp.** Loại — không ai làm việc đó, và ép sẽ
  làm sản phẩm chết ngay ở bước đầu.
- **Xây bàn/khay soi rác tại khu tập kết để chụp rác đã mở túi.** Loại — là phần cứng, đã loại ở
  ADR-0002 vì không có cột điểm nào.
- **Quay lại lấy cư dân làm trung tâm với cơ chế điểm thưởng trừ vào phí quản lý/phí gửi xe**
  (đề xuất trong `docs/Gemini_GBAI.md`). Loại khỏi P0 — hai cư dân đã phỏng vấn thuộc phân khúc
  dịch vụ trọn gói, mức tiền này gần như vô hiệu; và cơ chế trừ phí đòi tích hợp hệ thống thu phí
  của chủ đầu tư, thứ nhóm không có. Giữ ở P2 như thẻ đề xếp nó (mục "Nâng cao").
- **Để AI tự xác minh ảnh lao công chụp lúc thu gom rồi tự cộng điểm** (Luồng 3 trong tài liệu
  brainstorm). Loại ở dạng tự động. Ảnh bằng chứng thì **giữ** — nó là bản ghi tốt — nhưng việc
  đối chiếu "đúng món đã đăng ký hay không" là ca vision khó, sai là mất tiền của người thật.
  Người chốt, AI chỉ gợi ý.
