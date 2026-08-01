# BÁO CÁO DỰ ÁN — GreenBin AI

**Mã đề:** VHR-17 · **Nhóm ngành:** Bất động sản X — App ứng dụng cư dân
**Chương trình:** AI20K Build Phase — Cohort 2 (VinUni)
**Nhóm:** [tên nhóm] — Ninh, Quân, Nghĩa, [thành viên 4]
**Ngày báo cáo:** 29/07/2026 · **Giai đoạn:** Slice 0 — dựng nền, chưa chạm vision

---

## 1. Tổng quan

### 1.1. Bối cảnh

Luật Bảo vệ môi trường 2020 yêu cầu phân loại rác tại nguồn, Nghị định 45/2022/NĐ-CP quy định chế tài. Chủ thể chịu nghĩa vụ và chịu phạt tại chung cư là **Ban quản lý toà nhà**, không phải cư dân.

Trên thực tế tại các toà nhà có dịch vụ trọn gói, nghĩa vụ này đang được thực hiện bằng cách **đội vệ sinh phân loại lại toàn bộ rác bằng tay sau khi thu**, bao gồm cả pin và rác nguy hại mà cư dân vứt lẫn vào. Việc đăng ký và điều phối thu gom đồ cồng kềnh vẫn làm thủ công qua điện thoại, xe chạy nhiều chuyến lẻ.

> *Cần tra cứu lại điều khoản và hiệu lực hiện hành trước khi trích dẫn chính thức trong pitch deck.*

### 1.2. Vấn đề

| Chủ thể | Vấn đề đang chịu |
|---|---|
| Ban quản lý | Chịu nghĩa vụ pháp lý và chế tài, trả chi phí xử lý rác và chi phí nhân công phân loại, không có bằng chứng tuân thủ có hệ thống |
| Đội vệ sinh | Phân loại lại toàn bộ rác bằng tay; rủi ro sức khoẻ khi tiếp xúc pin, bóng đèn, hoá chất lẫn trong rác sinh hoạt |
| Vận hành thu gom | Điều phối thủ công, nhiều chuyến lẻ cùng toà cùng khung giờ, chi phí vận chuyển cao |

### 1.3. Sản phẩm

**GreenBin AI — Agent Phân loại Rác & Điều phối Thu gom Tái chế.**

Một **lớp vận hành cho toà nhà**: AI Agent phân loại rác qua **ảnh hoặc mô tả bằng chữ** → **tự sinh hành động trong hệ thống** (cảnh báo rác nguy hại, tạo yêu cầu thu gom, gộp tuyến, ghi sổ tuân thủ) → **người duyệt trước khi chốt**.

---

## 2. Nghiên cứu người dùng và quyết định đổi trọng tâm

### 2.1. Việc đã làm

Tối 28/07, nhóm phỏng vấn **2 cư dân chung cư** thuộc phân khúc có dịch vụ vệ sinh trọn gói.

### 2.2. Ba phát hiện đi ngược giả định ban đầu

1. **Cư dân không tự phân loại rác — và không coi đó là vấn đề của mình.** Toà nhà đã bố trí nhân viên phân loại lại toàn bộ rác sau khi thu.
2. **Thu gom đồ cồng kềnh không gây khó chịu cho cư dân.** Mỗi tầng có phòng rác riêng, có thang máy chở rác riêng, đội vệ sinh thu khoảng 22h, rác không tồn quá một ngày.
3. **Pin và rác nguy hại bị vứt chung vào túi rác sinh hoạt**, không có chế tài, người phân loại tự lọc ra bằng tay.

Người được phỏng vấn nói thẳng: một sản phẩm **chỉ cung cấp thông tin** thì họ không có lý do dùng, vì "hiện đang có người phân loại rồi". Nhận xét độc lập của lab coach trùng khớp: nếu sản phẩm dừng ở phân loại ảnh thì không tạo ra giá trị.

### 2.3. Quyết định — ADR-0002 (29/07)

**Giữ nguyên đề VHR-17 và toàn bộ kiến trúc. Chuyển người dùng chính từ cư dân sang vận hành.**

| | Trước | Sau |
|---|---|---|
| Người dùng chính | Cư dân | **BQL toà nhà** — người chịu rủi ro pháp lý và chi phí |
| Người thao tác chính | Cư dân | **Đội vệ sinh** — người đang thực sự phân loại |
| Cư dân | Người dùng duy nhất | Vai trò phụ, chạm nhẹ, **không nằm trên đường găng** |
| Giá trị cốt lõi | Trả lời "bỏ đâu" | **Kích hoạt hành động trong hệ thống** |

**Nguyên tắc mới, áp cho mọi tính năng về sau:**

> Mỗi kết quả AI phải sinh ra **một hành động hoặc một bản ghi** trong hệ thống, không được dừng ở một màn hình trả lời.

**Ba lý do:**

1. **Đề bài vốn đã nghiêng về vận hành.** 3 trong 4 ràng buộc gốc của VHR-17 nói về vận hành: HITL do BQL/đội vệ sinh duyệt · chính xác trong phân loại · tối ưu chi phí vận chuyển và lịch thu gom. Nhóm đã đọc đề thành "app cư dân" nên mới bí. Đây là **chỉnh trọng tâm bên trong đề, không phải đổi đề**.
2. **Không phát sinh phạm vi code mới.** Đặc tả giao diện v1.0 (28/07) đã có sẵn 3 vai trò và 18 màn, trong đó phần vận hành vốn đã là phần lớn nhất. Thay đổi nằm ở **cách kể câu chuyện và thứ tự ưu tiên**.
3. **Sản phẩm không được chết vì cư dân không hợp tác.** Sau quyết định này, hệ thống vẫn vận hành đầy đủ ngay cả khi **không có cư dân nào dùng**.

### 2.4. Giới hạn của bằng chứng — điểm yếu nhất hiện nay

- **n = 2, cùng một phân khúc.** Kết luận đúng phải phát biểu là *"ở phân khúc có dịch vụ vệ sinh trọn gói, cư dân không có động lực thay đổi hành vi"* — một phát hiện về **phân khúc**, không phải về đề tài. Chung cư cũ và nhà tập thể có thể ngược lại.
- **Chưa phỏng vấn phía vận hành.** Pain point của lao công và BQL hiện **vẫn là giả định**. Cần tối thiểu **1 lao công + 1 người thuộc BQL** để xác nhận. Đây là việc ưu tiên cao nhất về mặt nghiên cứu.

---

## 3. Giá trị và nguyên tắc thiết kế

### 3.1. Giá trị kinh doanh

| Trục giá trị | Cơ chế |
|---|---|
| Giảm chi phí nhân công phân loại | Phân loại tại điểm phát sinh thay vì phân loại lại toàn bộ ở cuối luồng |
| Giảm chi phí vận chuyển | Gộp yêu cầu cùng toà, cùng khung giờ thành một tuyến |
| Giảm rủi ro pháp lý | Sổ theo dõi rác nguy hại và báo cáo tuân thủ theo tháng sinh tự động |
| Giảm rủi ro sức khoẻ đội vệ sinh | Cảnh báo rác nguy hại tới đúng tầng, đúng ca trước khi người chạm vào |

### 3.2. Ba nguyên tắc xuyên suốt

1. **Không chắc thì phải nói là không chắc, và phải chuyển cho người.** Đây là sản phẩm có thể gây hại thật — hướng dẫn sai về pin lithium, bóng đèn huỳnh quang, thuốc hết hạn, hoá chất là nguy hiểm. Hệ thống không bao giờ trả lời nước đôi cho ra vẻ hữu ích.
2. **Mọi lời khuyên đều phải chỉ ra được nguồn.** Mỗi hướng dẫn kèm trích dẫn bấm được về văn bản gốc: *Nội quy toà S1 · mục 4.2* hoặc *Nghị định 45/2022/NĐ-CP · Điều 26*.
3. **AI đề xuất, người chốt.** Ba việc AI không được tự làm: duyệt yêu cầu thu gom vượt ngưỡng, xác nhận nhãn cho ca nghi ngờ, thay đổi lịch làm việc của đội vệ sinh.

---

## 4. MVP — Minimum Viable Product

### 4.1. Mục tiêu MVP

Xây dựng **lớp vận hành phân loại rác và điều phối thu gom cho một toà chung cư**, từ lúc rác phát sinh tại phòng rác đến lúc Ban quản lý duyệt xong tuyến thu gom và có bản ghi tuân thủ, với mức hỗ trợ tự động của AI được giới hạn bằng ba điểm dừng bắt buộc để người xác nhận.

MVP tập trung vào **bốn chức năng cốt lõi**:

1. Phân loại rác qua ảnh hoặc mô tả bằng chữ, có độ tin cậy và có trích dẫn nguồn quy định.
2. Từ chối trả lời và chuyển cho người khi độ tin cậy dưới ngưỡng hoặc nghi ngờ rác nguy hại.
3. Tạo yêu cầu thu gom và gộp các yêu cầu cùng toà, cùng khung giờ thành một tuyến đề xuất.
4. Ba hàng đợi duyệt cho Ban quản lý và đội vệ sinh, kèm trang vận hành theo dõi độ trễ, lỗi, chi phí.

Agent chỉ phân loại, đề xuất và tổng hợp bằng chứng. **Agent không tự duyệt yêu cầu, không tự xác nhận nhãn, không tự đổi lịch làm việc của người.**

### 4.2. Người dùng MVP

Hệ thống có **3 vai trò** (chương trình yêu cầu tối thiểu 2 — làm 3 vì luồng thu gom cần cả người thực thi lẫn người duyệt).

| Vai trò | Chức năng chính |
|---|---|
| **Ban quản lý** (`manager`) — máy tính | Duyệt 3 hàng đợi HITL; quản lý danh mục rác và kho quy định; xem vận hành (độ trễ, lỗi, chi phí); xem chất lượng AI và các ca phân loại sai; xem trace agent; mở ảnh gốc chưa xử lý (có ghi audit log) |
| **Đội vệ sinh** (`cleaner`) — điện thoại/tablet, dùng ngoài trời | Xem tuyến hôm nay theo thứ tự điểm dừng; đánh dấu đã thu; báo phát sinh; xác nhận nhãn cho ca phân loại nghi ngờ; nhận cảnh báo rác nguy hại |
| **Cư dân** (`resident`) — điện thoại | Chụp ảnh hoặc gõ mô tả để hỏi; đọc hướng dẫn có nguồn; đăng ký thu gom đồ cồng kềnh; theo dõi yêu cầu của mình; xem "ảnh của tôi đã được xử lý thế nào" |

**Ma trận quyền (rút gọn)**

| Chức năng | resident | cleaner | manager |
|---|:---:|:---:|:---:|
| Hỏi phân loại (ảnh / chữ) | ✅ | ✅ | ✅ |
| Đăng ký thu gom đồ cồng kềnh | ✅ | ❌ | ✅ (thay cư dân) |
| **Duyệt yêu cầu thu gom vượt ngưỡng** | ❌ | 👁 chỉ đọc | ✅ |
| **Xác nhận nhãn ca nghi ngờ** | ❌ | ✅ | ✅ |
| **Duyệt tuyến gộp** | ❌ | ❌ | ✅ |
| Xem ảnh gốc chưa xử lý | ❌ | ❌ | ✅ (ghi log) |
| Trang Vận hành / Eval / Trace | ❌ | ❌ | ✅ |

Chức năng không có quyền thì **hiện mờ kèm tooltip giải thích lý do**, không ẩn hoàn toàn — để ranh giới phân quyền là thứ nhìn thấy được, có chủ đích.

### 4.3. Phạm vi MVP

**Có trong MVP (P0)**

| Nhóm | Nội dung |
|---|---|
| Phân loại | Tiền xử lý ảnh (tước EXIF, làm mờ mặt, nén 512px, pHash) · phân loại T0/T1/T2 · output có cấu trúc |
| An toàn | Ngưỡng riêng cho nhóm nguy hại · luồng từ chối trả lời · cảnh báo an toàn dạng text cố định · danh sách chặn cứng |
| RAG | Kho quy định + nội quy toà + lịch thu gom, truy hồi có lọc theo toà, trả lời kèm trích dẫn |
| Thu gom | Tạo yêu cầu · gợi ý khung giờ · gộp tuyến theo toà + khung giờ |
| HITL | 3 hàng đợi duyệt, lý do từ chối chọn từ danh sách cố định |
| Vận hành | Trang theo dõi độ trễ, lỗi, chi phí; khối "Giới hạn đã biết" |
| Eval | Accuracy, macro-F1, confusion matrix, recall nhóm nguy hại, precision@5, bảng so sánh 3 tầng |

**Không làm trong MVP**

| Hạng mục | Lý do loại |
|---|---|
| Phần cứng / IoT / robot phân loại | Chương trình chấm trên 5 cột phần mềm; phần cứng không có cột điểm nhưng nuốt hết thời gian còn lại (ADR-0002) |
| Model nhẹ tự train (tầng T0.5) | P1 — chỉ có giá trị khi đã có eval và T1 làm mốc so sánh |
| VRP đầy đủ bằng OR-Tools | Bẫy nuốt thời gian; gộp theo toà + khung giờ đã đủ chứng minh giá trị |
| Gamification | P2 — vui nhưng không chứng minh năng lực AI |
| Trợ lý giọng nói cho cư dân lớn tuổi | Cách xử lý đúng cho "cư dân không dùng được app" là bỏ cư dân khỏi đường găng, không phải thêm một kênh nữa |

### 4.4. Kịch bản demo MVP (video ≤ 5 phút, 7 bước)

1. **Cư dân** chụp **hộp sữa giấy tráng nhôm** → thấy các bước xử lý quyền riêng tư tích dần → kết quả `Tái chế · thùng xanh dương · 0,91` kèm nguồn `Nội quy toà S1 mục 4.2` → mở màn quyền riêng tư, thấy GPS đã bị xoá và khuôn mặt đã làm mờ.
2. **Cư dân** chụp **pin lithium** → khối cảnh báo nguy hại, kèm dòng `Cảnh báo an toàn theo danh mục chuẩn — không do AI tự viết`.
3. **Cư dân** chụp **chai hoá chất, ảnh tối** → hệ thống **từ chối trả lời**: `Mình chưa đủ chắc` → bấm `Hỏi ban quản lý`. *(Khoảnh khắc mạnh nhất của bài demo.)*
4. **Cư dân** đăng ký thu gom **48 kg đồ cồng kềnh** → màn xác nhận nói rõ *vượt ngưỡng 30 kg, cần BQL duyệt*.
5. **Ban quản lý** mở hàng đợi → duyệt yêu cầu 48 kg → xử lý ca chai hoá chất ở bước 3, chọn nhãn đúng và trả lời cư dân.
6. **Ban quản lý** mở **Duyệt tuyến** → agent đề xuất gộp 5 yêu cầu thành 1 chuyến, giải thích tiêu chí gộp → kéo bỏ 1 điểm → xem diff → duyệt.
7. **Ban quản lý** mở **Vận hành**: bảng so sánh chi phí 3 tầng, thẻ chỉ số an toàn, lưới failure case, khối **Giới hạn đã biết**.

**Kịch bản lỗi (bắt buộc có):** mất mạng giữa lúc upload → `Chưa gửi được — đã lưu vào máy` → bật mạng → `Thử lại` thành công, không mất ảnh. Hoặc: node `advise` lỗi → vẫn hiện nhóm rác nhận diện được kèm băng cảnh báo suy giảm một phần.

Bảy bước này chạm đủ: 3 vai trò · workflow agentic có trạng thái và tool-use · cả 3 điểm HITL · quyền riêng tư ảnh · từ chối trả lời an toàn · định tuyến 3 tầng · giám sát độ trễ/lỗi/chi phí · eval và failure case · nêu rõ giới hạn.

### 4.5. Định nghĩa hoàn thành của MVP

- Chạy trọn 7 bước demo trên bản deploy online, không cần thao tác tay ngoài kịch bản.
- Cả 3 điểm HITL thực sự chặn được hành động, không phải chỉ là màn hình trang trí.
- Có số **đo được** (không phải ước lượng) cho: chi phí/ảnh từng tầng, độ trễ p95, tỉ lệ rác nguy hại bị phân loại thành rác thường.
- 10 deliverable của chương trình đủ mặt.

---

## 5. Kiến trúc hệ thống

### 5.1. Luồng agentic

```
Ảnh / mô tả bằng chữ
        ▼
TIỀN XỬ LÝ ẢNH: tước EXIF/GPS · làm mờ khuôn mặt · nén 512px · tính pHash
        ▼
classify_waste  →  T0 cache pHash ($0) → T1 gpt-4o-mini → T2 gpt-4o
        ▼
   confidence < ngưỡng của nhóm?  ──yes──►  TỪ CHỐI trả lời + chuyển BQL
        ▼ no
advise (RAG): truy hồi quy định + lịch thu gom CỦA TOÀ ĐÓ → hướng dẫn có trích nguồn
        ▼
   đồ cồng kềnh / khối lượng lớn?
        ▼ yes
schedule_pickup: tạo yêu cầu → gợi ý khung giờ → gộp tuyến
        ▼
   vượt ngưỡng?  ──yes──►  HITL: BQL / đội trưởng xác nhận
        ▼
   Chốt lịch, thông báo hai phía, ghi sổ tuân thủ
```

Graph LangGraph: `classify_waste → advise → schedule_pickup`, có trạng thái, có tool-use, trace được trên LangSmith và hiển thị lại ở màn Agent Run.

### 5.2. Định tuyến model 3 tầng

| Tầng | Dùng khi | Chi phí |
|---|---|---|
| **T0** — cache pHash | Ảnh trùng hoặc gần trùng đã phân loại trước đó | $0 |
| **T1** — gpt-4o-mini vision | Ảnh rõ, vật đơn lẻ (~75–85% lượng) | Thấp |
| **T2** — gpt-4o vision | Confidence thấp, nhiều vật, **hoặc nghi rác nguy hại** | Cao |

Điều kiện escalate lên T2 **phải bao gồm cả "nghi ngờ rác nguy hại"**, không chỉ confidence thấp — đây là điểm khác biệt giữa tối ưu chi phí và tối ưu chi phí một cách an toàn.

Cache pHash có lý do thực tế: trong chung cư, cùng một loại vỏ hộp được chụp lại rất nhiều lần.

> **Chi phí vision sẽ được ĐO, không đoán.** Việc đầu tiên khi chạm phần vision: chạy 50 ảnh, đọc `usage` trả về từ API, ghi token thật/ảnh cho cả `detail: "low"` và `"high"`, rồi mới nhân lên. Con số đo được đó mới đưa vào báo cáo.

### 5.3. Tech stack

| Layer | Lựa chọn |
|---|---|
| Agent | LangGraph |
| LLM | `gpt-4o-mini` (T1) · `gpt-4o` (T2 vision) |
| Backend | FastAPI + SQLAlchemy 2.x |
| Database | SQLite khi dev → PostgreSQL khi deploy |
| Vector | JSON list trong SQLite → pgvector khi lên Postgres |
| Xử lý ảnh | Pillow (EXIF, nén) + OpenCV (làm mờ mặt) + imagehash (pHash) |
| Frontend | Next.js — thiết kế riêng bằng công cụ design rồi mang code về |
| Tracing | LangSmith |
| Deploy | Railway (backend) + Vercel (frontend) |
| Test | pytest + pytest-asyncio, mock LLM — test không gọi API thật |

---

## 6. An toàn AI, quyền riêng tư và HITL

Đây là phần mạnh nhất của đề, không cắt trong bất kỳ tình huống nào.

### 6.1. Rủi ro 1 — Ảnh cư dân nhạy cảm hơn tưởng

Ảnh thùng rác có thể chứa khuôn mặt, biển số xe, số căn hộ, **hoá đơn/giấy tờ có tên và địa chỉ**, nhãn thuốc. Mọi ảnh chụp bằng điện thoại đều mang **EXIF chứa toạ độ GPS chính xác tới mét**.

Bắt buộc ở bước tiền xử lý: tước toàn bộ EXIF · làm mờ khuôn mặt · nén 512px · đặt hạn lưu trữ và tự xoá · không đặt đường dẫn ảnh vào URL công khai đoán được. Có màn hình cho người dùng xem **"hệ thống đã xoá gì khỏi ảnh của tôi"** — ảnh gốc và ảnh đã xử lý đặt cạnh nhau.

### 6.2. Rủi ro 2 — Hướng dẫn sai về rác nguy hại là nguy hiểm thật

| Biện pháp | Chi tiết |
|---|---|
| Ngưỡng riêng | Nhóm nguy hại dùng ngưỡng confidence cao hơn nhóm thường |
| Từ chối trả lời | Dưới ngưỡng → từ chối dứt khoát, chuyển người, ghi `refused=True` |
| Cảnh báo cố định | Cảnh báo an toàn cho nhóm nguy hại là **text cố định**, không để LLM tự sinh |
| Chặn cứng | Vật sắc nhọn y tế, bình gas, hoá chất → luôn chuyển người, không phân loại tự động |

### 6.3. Ba điểm HITL

| # | Điểm dừng | Người duyệt |
|---|---|---|
| 1 | Yêu cầu thu gom vượt ngưỡng khối lượng | BQL / đội vệ sinh |
| 2 | Phân loại confidence thấp hoặc nghi nguy hại | Nhân viên xác nhận nhãn |
| 3 | **Lịch thu gom do agent gộp tuyến** | Đội trưởng duyệt trước khi chốt |

Điểm 3 là ranh giới quan trọng nhất: **agent không được tự thay đổi lịch làm việc của người.**

Lý do từ chối phải chọn từ **danh sách cố định** → dữ liệu này chảy ngược vào tập cải tiến, biến mỗi lần người sửa AI thành một mẫu huấn luyện có cấu trúc.

---

## 7. Dữ liệu

| Tầng | Nguồn | Quy mô |
|---|---|---|
| 1 | TrashNet, **RealWaste**, TACO, Garbage Classification (Kaggle), Roboflow Universe | 2.000–5.000 ảnh |
| 2 | **Tự chụp** rác sinh hoạt Việt Nam: hộp xốp, ly trà sữa có màng, túi nilon đen, hộp sữa tráng nhôm, khay cơm dính dầu | 300–500 ảnh |
| 3 | Kho tri thức RAG: quy định pháp luật + nội quy toà + lịch thu gom + danh mục nguy hại | 20–40 trang |

Chỉ dùng dữ liệu **công khai, mô phỏng hoặc đã ẩn danh**. Kiểm tra license từng dataset và ghi nguồn vào README.

### Khoảng cách miền — phát hiện kỹ thuật quan trọng nhất tới nay

TrashNet chụp từng món rác **sạch, đơn lẻ, trên nền bìa trắng**. Nghiên cứu 2026 cho thấy model đạt **94,18% trên TrashNet chỉ còn 41,04% trên RealWaste** (ảnh rác thật tại bãi rác).

Hệ quả cho nhóm:
1. **Không bao giờ** đưa accuracy của dataset công khai lên slide như thể đó là năng lực sản phẩm.
2. Bộ ảnh tự chụp ở tầng 2 là **bộ dữ liệu quan trọng nhất**, không phải bộ bổ sung.
3. Chênh lệch accuracy giữa hai bộ tự nó là một phát hiện đáng đưa vào báo cáo cuối.

---

## 8. Kế hoạch đánh giá (Eval)

- **Tập test 300–400 ảnh giữ riêng tuyệt đối**, không dùng để chỉnh prompt dù chỉ một lần.
- Báo cáo **tách riêng** nhóm dataset công khai và nhóm ảnh tự chụp.
- Chỉ số: accuracy · **macro-F1** · confusion matrix · **recall riêng cho nhóm nguy hại**.
- **Chỉ số an toàn quan trọng nhất: tỉ lệ rác nguy hại bị phân loại thành rác thường — mục tiêu 0%.** In to trên slide.
- Bảng so sánh 3 tầng: accuracy × chi phí/ảnh × độ trễ p95.
- Retrieval: precision@5 trên ~60 câu hỏi "bỏ đâu, khi nào".
- Failure case: **trình chiếu được ảnh thật bị nhận sai** — lợi thế demo lớn nhất của đề này.

**Ca khó bắt buộc có trong tập test:** hộp sữa giấy tráng nhôm ↔ giấy · ly nhựa có màng ↔ nhựa tái chế · khay cơm dính dầu ↔ rác thực phẩm.

*Hiện chưa có số đo nào. Toàn bộ mục này là kế hoạch.*

---

## 9. Vận hành và kiểm soát chi phí

| Hạng mục | Cam kết |
|---|---|
| Giám sát | Trang Vận hành theo dõi độ trễ, tỉ lệ lỗi, chi phí theo tầng model |
| Tracing | LangSmith + AI logging hooks (deliverable #4) |
| Ngân sách | ~1,5 triệu VND cho cả dự án · hard limit **$25/tháng** trên OpenAI platform · email cảnh báo ở 80% |
| Kiểm soát chạy hàng loạt | Mọi script batch có `--limit` mặc định nhỏ (50–200) và in dự toán chi phí trước khi chạy |
| Cache | Cache mọi lệnh gọi LLM theo hash đầu vào |
| Code style | ruff (line-length 120, target py311), type hints ở mọi hàm public, **không bare `except`**, tách file khi vượt ~300 dòng |

**Bài học từ Cohort 1:** DevOps và Code Quality là hai cột điểm thấp nhất; 0/12 đội có CI/CD dù template cho sẵn; chỉ 2/12 đội có eval evidence. Nhóm coi CI/CD và eval là hạng mục bắt buộc, không phải phần thưởng thêm.

---

## 10. Trạng thái hiện tại

### 10.1. Đã có

| Thành phần | Nội dung | Trạng thái |
|---|---|---|
| `src/db/models.py` | 14 bảng cho GreenBin | ✅ chạy được, đã smoke test |
| `src/db/session.py` | engine, `session_scope`, `init_db` | ✅ |
| `src/services/pii.py` | Ẩn danh PII trong text (SĐT, email, CCCD, tên) | ✅ đã test tay |
| `src/services/dedup.py` | Chuẩn hoá text, hash gộp trùng, ước lượng token | ✅ |
| `src/services/security.py` | Băm mật khẩu PBKDF2 | ✅ |
| `src/config.py` | Cấu hình 2 tầng model, prompt version, ngân sách | ✅ |
| `docs/FRONTEND_SPEC.md` | 18 màn, 3 vai trò, hợp đồng API, kịch bản demo | ✅ v1.0 (28/07) |
| `docs/decisions/0001, 0002` | ADR chọn đề tài · ADR chuyển trọng tâm | ✅ |
| `docs/research/sota-model-nhe-phan-loai-rac.md` | Khảo sát model nhẹ / quantization / edge + khoảng cách miền | ✅ 29/07 |

### 10.2. Chưa có — nói thẳng

- **Chưa `git init`** — repo chưa được khởi tạo git, kéo theo **AI logging hooks (deliverable #4) chưa chạy**. Việc này đã treo sang **ngày thứ 3**, là món nợ kỹ thuật cần trả ngay trong hôm nay.
- Chưa có `.env`, chưa cài venv riêng cho dự án.
- Chưa seed `waste_categories`, chưa có tài khoản demo.
- **Chưa có bất kỳ phần vision, RAG hay API nào.**
- Chưa phỏng vấn phía vận hành — pain point của lao công và BQL vẫn là giả định.
- Mục 0 của `FRONTEND_SPEC.md` vẫn viết theo góc cư dân, cần viết lại theo ADR-0002.

### 10.3. Kế hoạch việc tiếp theo

| # | Việc | Vì sao ưu tiên vậy |
|---|---|---|
| 1 | `git init` + commit đầu · venv · `.env` · chạy `setup_hooks.ps1` | Chặn deliverable #4, đã treo 3 ngày |
| 2 | Phỏng vấn 1 lao công + 1 người BQL | Chỗ yếu nhất của ADR-0002 |
| 3 | Seed dữ liệu nền: `waste_categories` (kèm `is_hazardous`, `min_confidence`, `safety_warning`), 2 toà, 3 tài khoản demo | Mọi thứ phía sau đều cần |
| 4 | `src/services/image.py`: tước EXIF, làm mờ mặt, nén, pHash + test khẳng định EXIF đã sạch | Cửa vào của toàn bộ luồng, và là phần quyền riêng tư |
| 5 | Thu thập dữ liệu: 1 dataset công khai + 100 ảnh tự chụp đầu tiên | Có cái để chạy |
| 6 | Phân loại T1 + **đo token thật trên 50 ảnh trước** | Không đoán chi phí |
| 7 | Ngưỡng an toàn + luồng từ chối trả lời | Câu chuyện an toàn AI |
| 8 | `eval/run_eval.py` | Cột điểm mà Cohort 1 gần như bỏ trống |
| 9 | RAG + `advise` | |
| 10 | `schedule_pickup` + HITL | |

Song song: mang `FRONTEND_SPEC.md` sang công cụ design, code frontend đặt ở `frontend/`.

---

## 11. Rủi ro và giới hạn đã biết

| Rủi ro | Mức độ | Cách xử lý |
|---|---|---|
| Pain point phía vận hành vẫn là giả định (n=2, sai đối tượng) | **Cao** | Phỏng vấn 1 lao công + 1 BQL trong tuần này; nếu sai, điều chỉnh sớm còn kịp |
| Accuracy trên ảnh rác thật thấp hơn nhiều so với dataset công khai | **Cao** | Ưu tiên ảnh tự chụp; báo cáo tách riêng hai bộ; không dùng số dataset công khai để quảng cáo |
| Chi phí vision vượt ngân sách | Trung bình | Cache pHash, hard limit $25/tháng, đo token thật trước khi chạy hàng loạt |
| Deliverable #4 (AI logging) treo do chưa `git init` | Trung bình | Xử lý ngay hôm nay |
| Ôm quá nhiều tính năng, không kịp deploy | Trung bình | Danh sách cắt đã định sẵn: nếu buộc phải cắt, **giữ bằng mọi giá** màn "Mình chưa chắc" và màn "Duyệt tuyến" |
| Nhóm 4 người nhưng phần lớn code đang do 1 người làm | Trung bình | Chia việc theo ranh giới module sau khi có seed data và spec API ổn định |

**Giới hạn của sản phẩm sẽ nói rõ trong demo:** hoạt động trên tập danh mục rác đã định nghĩa, chưa xử lý ảnh nhiều vật chồng lấp, kho quy định giới hạn ở 2 toà mẫu, và mọi kết quả AI đều là đề xuất chờ người duyệt ở các điểm rủi ro.

---

## 12. Câu hỏi cho mentor

1. Việc chuyển trọng tâm từ cư dân sang vận hành (ADR-0002) dựa trên n=2 phỏng vấn cư dân, chưa có phỏng vấn phía vận hành. Nên tiếp tục code theo hướng mới ngay, hay dừng lại lấy thêm bằng chứng trước?
2. Với khoảng cách miền TrashNet ↔ ảnh thật (94% → 41%), nên đầu tư bao nhiêu thời gian cho việc tự chụp dữ liệu so với việc hoàn thiện luồng agentic?
3. Ba điểm HITL có bị coi là quá nhiều ma sát cho một sản phẩm vận hành thực tế không, hay đúng mức với mức rủi ro?
4. Trong phần điều phối tuyến, mức "gộp theo toà + khung giờ" có đủ để thể hiện giá trị kinh doanh, hay cần tới bài toán VRP thật?
5. Với thời gian còn lại, nên ưu tiên chiều sâu của eval hay chiều rộng của tính năng?

---

*Nguồn tham chiếu trong repo: `CLAUDE.md` · `WORKLOG.md` · `docs/decisions/0001`, `0002` · `docs/FRONTEND_SPEC.md` · `docs/research/sota-model-nhe-phan-loai-rac.md`*
