# Báo cáo tổng quan — GreenBin AI (VHR-17)

**Ngày:** 01/08/2026 · **Gửi:** nhóm 4 người · **Người viết:** Ninh

---

## 0. Đọc nhanh trong 60 giây

- **Sản phẩm đã chạy đầu-cuối.** Backend 44 route, agent LangGraph có trace, frontend 21 màn, 76 test pass. Đăng nhập được 3 vai trò, thao tác được cả 3 điểm HITL với dữ liệu thật.
- **Đã đóng gói xong thành app cài được** (PWA + APK Android qua Capacitor) và **mã đã sẵn sàng deploy**. Còn lại là bước tạo tài khoản Render/Vercel — không phải việc code.
- **Việc chặn duy nhất còn lại: chưa có API key vision.** Mọi phần khác chạy không cần key; riêng luồng nhận diện ảnh thì dừng ở màn "không đủ chắc chắn".
- **Mới có bằng chứng thực trạng từ ngoài đời** (mục 2). Nó **xác nhận** phạm vi ta đã chọn, nhưng **đụng vào một giả định** ta chốt ở ADR-0002 — cần cả nhóm đọc mục 3.
- **Chưa phỏng vấn lao công và ban quản lý.** Đây vẫn là chỗ yếu nhất của cả dự án, và bằng chứng mới **không** lấp được chỗ đó.

---

## 1. Sản phẩm đang ở đâu

### Đã xong

| Phần | Trạng thái |
|---|---|
| Phân loại 4 tầng T0 → T0.5 → T1 → T2 | Xong, escalate cả khi **nghi nguy hại** chứ không chỉ khi confidence thấp |
| An toàn AI: chặn cứng, ngưỡng riêng nhóm nguy hại, từ chối trả lời | Xong, cảnh báo an toàn lấy từ CSDL chứ không do LLM sinh |
| Tiền xử lý ảnh: tước EXIF, làm mờ mặt, nén 512px, pHash | Xong, có test khẳng định EXIF đã sạch |
| RAG hybrid BM25 + embedding, lọc theo toà | Xong, chạy được cả khi chưa có API key |
| Thu gom, gộp tuyến, 3 điểm HITL | Xong |
| Giao diện 21 màn, 3 vai trò | Xong |
| **App cài được: PWA + APK Android** | **Mới xong 01/08** |
| **CI/CD: kiểm cả Python lẫn frontend, build APK theo tag** | **Mới xong 01/08** |
| **Cấu hình deploy Render + Vercel** | **Mới xong 01/08**, chưa bấm deploy |

### Chưa xong

1. **API key vision** — chặn luồng nhận diện ảnh. Việc số một.
2. **Deploy thật** — mã sẵn sàng, cần tài khoản. Xem `docs/HUONG_DAN_DEPLOY.md`.
3. **Bộ ảnh tự chụp + chạy eval** — số liệu trang Chất lượng AI hiện là **dữ liệu mô phỏng**, có gắn nhãn rõ trên giao diện. Phải thay bằng số đo thật trước khi lên slide.
4. **Phỏng vấn 1 lao công + 1 người ban quản lý.**
5. **AI logging (deliverable #4)** — chạy được ngay sau khi có repo GitHub.

---

## 2. Bằng chứng thực trạng mới

Bốn bài đăng công khai trong nhóm cư dân của một khu chung cư, thu thập từ 27/05 đến 25/07/2026. Tổng tương tác: **khoảng 116 lượt thích và 89 bình luận**.

> **Về quyền riêng tư:** bốn ảnh gốc chứa **tên thật và số căn hộ của người đăng**. Theo quy định dữ liệu của chương trình (chỉ dùng dữ liệu công khai, mô phỏng hoặc **đã ẩn danh**), phần dưới đây **chỉ chép lại nội dung đã ẩn danh**, và **ảnh gốc không được đưa vào repo**. Ảnh giữ ngoài repo tại `C:\AI20K\Thực trạng\`. Muốn đưa lên slide thì phải che tên, ảnh đại diện và mã căn hộ trước.

### Bài A — 22/06 · 27 thích · 41 bình luận

> "Mọi người cho mình hỏi, có cái giường cũ và tủ cũ muốn vứt đi thì vứt ở đâu nhỉ, không thấy bãi rác nào gần đây."

**Vấn đề:** không biết đồ cồng kềnh vứt ở đâu. 41 bình luận cho một câu hỏi tưởng như đơn giản — nghĩa là **không có câu trả lời chính thức nào dễ tìm**.

### Bài B — 25/07 · 37 thích · 38 bình luận

> "Em có cái kệ gỗ qua dọn nhà tháo ra để ở phòng rác mà lễ tân bảo phải mang đi chỗ khác vứt. Mà nhà em đang ở quê không lên vứt được. Không biết có ai nhận đi vứt giúp em được không ạ?"

**Vấn đề:** cư dân làm sai quy trình → **bị từ chối tại chỗ** → không có kênh chính thức nào để xử lý tiếp, phải đi hỏi hàng xóm. Đây là bài giá trị nhất trong bốn bài: nó cho thấy **quy định nội bộ có tồn tại, nhưng cư dân chỉ biết tới nó sau khi đã làm sai**.

### Bài C — 27/05 · kèm ảnh

> "Tầng 18 – [căn hộ] nhà ai thiếu ý thức thì ra dọn hộ. Vứt 2 cái thùng xốp to đùng lại còn thối um, chặn ngay cửa phòng rác không để ai vứt rác vào được."

Ảnh cho thấy hai thùng xốp lớn chặn kín cửa phòng rác tầng.

**Vấn đề:** hệ quả trực tiếp của bài A và B. Không có kênh xử lý đồ cồng kềnh → người ta bỏ đại ở phòng rác tầng → **chặn lối, bốc mùi, và biến thành xung đột giữa cư dân với nhau**. Giọng bài quy về "thiếu ý thức", nhưng bài A và B cho thấy phần lớn là **thiếu thông tin và thiếu kênh**, không phải thiếu ý thức.

### Bài D — 06/07 · 16 thích · 10 bình luận

> "Trường hợp như thế này xử lý thế nào các bác nhỉ? Nhà em từ tối qua đến giờ vẫn chưa đi đổ rác được."

Ảnh cho thấy phòng rác tầng đầy tràn, túi rác chất kín lối vào.

**Vấn đề:** phòng rác quá tải, cư dân **không đổ được rác thường**. Đây là bài toán tần suất và điều phối thu gom.

### Bốn bài này nói chung điều gì

| Nhận xét | Số bài |
|---|---|
| Thuộc **luồng B** (cồng kềnh, tái chế, quá tải) | **4/4** |
| Là **rác ướt đóng túi bị phân loại sai** | **0/4** |
| Gốc rễ là **không biết vứt ở đâu / không có kênh đăng ký** | 3/4 (A, B, C) |
| Là bài toán **tần suất và điều phối thu gom** | 1/4 (D) |

---

## 3. Bằng chứng này đụng vào quyết định nào của nhóm

### Xác nhận ADR-0003 — phạm vi chỉ làm luồng B là đúng

**4/4 bài đều là đồ cồng kềnh hoặc quá tải phòng rác. Không có bài nào về rác ướt phân loại sai.** Quyết định để rác ướt đóng túi kín ra ngoài phạm vi không những không mất gì, mà còn đúng chỗ đau: **không ai lên mạng hỏi "túi rác này bỏ thùng nào", nhưng rất nhiều người hỏi "cái giường cũ này vứt đâu"**.

### Đụng vào ADR-0002 — cần cả nhóm đọc kỹ

ADR-0002 chốt rằng người dùng chính là ban quản lý và đội vệ sinh, còn **cư dân là vai phụ, chạm nhẹ, không nằm trên đường găng**, dựa trên một cuộc phỏng vấn ngày 28/07 kết luận *"cư dân ở phân khúc có dịch vụ trọn gói không có pain point"*.

**Bốn bài này cho thấy kết luận đó quá rộng.** Cư dân **có** một pain point rất rõ, và nó nằm gọn trong đúng một lát: **đồ cồng kềnh — không biết vứt ở đâu, không biết đăng ký với ai, làm sai thì bị từ chối tại chỗ.**

Đề xuất xử lý — **không lật ADR-0002**, vì lập luận cốt lõi của nó vẫn đúng: phần sinh tiền, sinh rủi ro pháp lý và rủi ro sức khoẻ vẫn nằm ở vận hành, và 3/4 ràng buộc gốc của đề vẫn nói về vận hành. Nhưng cần chỉnh một câu:

> Luồng cư dân **đăng ký thu gom đồ cồng kềnh** không còn là "chạm nhẹ". Nó là **đầu vào chính** của bài toán điều phối — không có yêu cầu từ cư dân thì không có gì để gộp tuyến.

Việc cần làm: **ghi ADR-0006** đính chính phạm vi câu "cư dân không có pain point" thành "cư dân không có pain point ở rác sinh hoạt hằng ngày, **nhưng có pain point rõ rệt ở đồ cồng kềnh**", kèm bốn bài này làm dẫn chứng.

### Củng cố phần RAG

Bài B là ca dùng RAG sạch nhất mà nhóm có: *"toà này nhận đồ cồng kềnh ở đâu, giờ nào, có phải đăng ký trước không"* — câu hỏi mà lễ tân trả lời được nhưng cư dân không tra được ở đâu. Đây là câu nên có trong bộ ~60 câu hỏi đo `precision@5`.

---

## 4. Giới hạn của bằng chứng này — đọc trước khi đưa lên slide

Phải nói thẳng những điều sau, nếu không sẽ bị hỏi ngay:

1. **Bốn bài là mẫu chọn thủ công, không phải mẫu ngẫu nhiên.** Bài gây bức xúc thì dễ được nhớ và lưu lại hơn. Không suy ra được tỉ lệ nào từ đây.
2. **Không biết mẫu số.** Không biết trong cùng kỳ nhóm cư dân đó có bao nhiêu bài, nên **không được nói "X% vấn đề rác là đồ cồng kềnh"**.
3. **Không xác minh được bốn bài cùng một khu.**
4. **Đây là tiếng nói cư dân, không phải người vận hành.** Nó **không** thay thế được việc phỏng vấn lao công và ban quản lý — chỗ yếu nhất của ADR-0002 và ADR-0003 vẫn còn nguyên.

**Cách vá rẻ nhất:** lấy toàn bộ bài trong nhóm cư dân đó trong 3 tháng, gán nhãn theo loại vấn đề (cồng kềnh / quá tải / phân loại / khác). Có mẫu số là có tỉ lệ, và tỉ lệ đó đưa lên slide được. Ước tính 2–3 giờ cho một người.

---

## 5. Việc còn lại và đề xuất chia cho nhóm

| # | Việc | Vì sao đáng làm | Ước tính |
|---|---|---|---|
| 1 | **Lấy API key vision** (Gemini và/hoặc NVIDIA), chạy thử luồng ảnh, **đo token thật trên 50 ảnh** | Chặn mọi thứ phía sau. Con số đo được đưa thẳng vào báo cáo (PLO 1) | 1–2 giờ |
| 2 | **Deploy Render + Vercel** theo `docs/HUONG_DAN_DEPLOY.md` | Yêu cầu tối thiểu của chương trình | 1–2 giờ |
| 3 | **Chụp 100 ảnh rác thật** tại phòng rác tầng | Bộ quan trọng nhất, không phải bộ bổ sung. Model đạt 94% trên TrashNet chỉ còn 41% trên ảnh rác thật | 2–3 giờ |
| 4 | **Phỏng vấn 1 lao công + 1 người ban quản lý** | Chỗ yếu nhất của cả dự án | 2 giờ |
| 5 | **Đếm có hệ thống bài đăng nhóm cư dân** (mục 4) | Biến 4 giai thoại thành một con số dùng được | 2–3 giờ |
| 6 | **Chạy `eval/run_eval.py`**, thay số mô phỏng bằng số đo thật | 2/12 đội Cohort 1 có eval evidence — đây là chỗ dễ vượt lên | 2 giờ |
| 7 | **ADR-0006** đính chính phạm vi ADR-0002 (mục 3) | Ghi lúc quyết định, không viết bù sau | 20 phút |

Việc 1 và 2 chặn phần còn lại — nên làm trước. Việc 3, 4, 5 độc lập nhau, ba người chạy song song được.

---

## 6. Rủi ro đang theo dõi

| Rủi ro | Mức | Đang xử lý thế nào |
|---|---|---|
| Không kịp có số eval thật, phải demo bằng dữ liệu mô phỏng | **Cao** | Dữ liệu mô phỏng đều gắn cờ `is_seed` và **hiện nhãn rõ trên giao diện**. Không trộn số mô phỏng với số đo thật — đây là ranh giới không được vượt |
| Hết quota API giữa buổi demo | Trung bình | Lớp provider tách rời: đổi Gemini ↔ NVIDIA ↔ OpenRouter chỉ bằng sửa `.env`. Cache pHash tầng T0 giảm số lần gọi thật |
| Máy chủ miễn phí ngủ, request đầu chậm | Trung bình | Đã ghi lên trang Vận hành. **Trước demo phải mở web một lần cho nó thức dậy** |
| Ảnh cư dân mất khi máy chủ khởi động lại | Thấp | Đã ghi thẳng lên giao diện thay vì giấu |
| Chưa ai cầm máy Android thử APK | Trung bình | Cần một người có máy Android nhận việc này |

---

## 7. Phụ lục — cách kiểm chứng lại các con số trong báo cáo

```bash
python -m pytest tests -q        # 76 test
python -m ruff check src tests   # sạch
npx --prefix frontend tsc --noEmit
npx --prefix frontend next build # xuất tĩnh ra frontend/out/
```

Tài liệu liên quan: [`CLAUDE.md`](../CLAUDE.md) (bối cảnh và trạng thái) · [`docs/decisions/`](decisions/) (ADR-0001 → 0005) · [`WORKLOG.md`](../WORKLOG.md) (nhật ký ngày) · [`docs/HUONG_DAN_DEPLOY.md`](HUONG_DAN_DEPLOY.md).
