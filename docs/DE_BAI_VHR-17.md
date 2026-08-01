# Đề bài gốc VHR-17 và quy định chung — bản chép lại

> **Nguồn:** `C:\AI20K\Screenshot_Infor\Topic.png` (thẻ đề VHR-17) và
> `C:\AI20K\Screenshot_Infor\Yêu cầu và Nhóm Topic.png` (quy định chung + PLO).
> Chép lại thành text ngày **30/07/2026** để mọi session sau đọc trực tiếp, không phải OCR lại ảnh.
> **Đây là bản chép nguyên văn — không sửa, không diễn giải.** Phần diễn giải của nhóm nằm ở
> mục 4 và ở `docs/decisions/`.

---

## 1. Thẻ đề VHR-17 (nguyên văn)

| Cột | Nội dung |
|---|---|
| STT | 73 |
| Nhóm ngành | BĐS X – App Ứng dụng cư dân X |
| Mã đề | **VHR-17** |
| Tên đề | **GreenBin AI – Agent Phân loại Rác & Điều phối Thu gom Tái chế** |
| Số team tối đa | **2** |

### 📍 Thực trạng

> Chương trình phân loại rác tại nguồn ở Doanh nghiệp bất động sản X gặp khó vì cư dân không
> biết phân loại đúng, và việc đăng ký thu gom đồ cồng kềnh/tái chế còn thủ công.

### 🎯 Vấn đề

> Cần AI Agent hướng dẫn phân loại rác qua ảnh/mô tả, giải đáp bỏ đâu-khi nào, nhận đăng ký
> thu gom đồ cồng kềnh/tái chế và điều phối lịch tới đội vệ sinh.

### 🔒 Ràng buộc

> HITL cho đăng ký thu gom khối lượng lớn cần BQL/đội vệ sinh xác nhận; bảo mật thông tin &
> ảnh cư dân; chính xác trong phân loại (tránh hướng dẫn sai); tối ưu chi phí vision và lịch
> thu gom.

### Tech stack gợi ý của đề

- **LLM:** GPT-4o (vision đọc ảnh rác) + GPT-4o-mini
- **Agent:** LangGraph (`classify_waste → advise → schedule_pickup`)
- **DB:** PostgreSQL
- **Backend:** FastAPI
- **Frontend:** Next.js
- **Auth:** Supabase (Cư dân, Đội vệ sinh/BQL)
- **Deploy:** Railway + Vercel

### Yêu cầu chức năng

**Cơ bản:**
- App deploy, đăng nhập
- Agent phân loại rác qua ảnh/mô tả & hướng dẫn, nhận đăng ký thu gom, tạo lịch cho đội vệ sinh

**Nâng cao:**
- Agent tối ưu tuyến & gộp lịch thu gom, gamification tích điểm tái chế, HITL xác nhận thu gom
  lớn, dashboard tỉ lệ phân loại đúng & eval độ chính xác nhận diện rác

---

## 2. Quy định chung khi chọn và thực hiện đề (nguyên văn)

**1. Phạm vi và số lượng đề:** Mỗi đề tài được đăng ký tối đa 2 team. **Nội dung trong ngân
hàng là gợi ý để nhóm lựa chọn và tinh chỉnh theo tình hình thực tế khi khảo sát, trao đổi
trực tiếp với người dùng trong quá trình phát triển sản phẩm.** Trường hợp team muốn đề xuất
đề tài mới, cần được BTC duyệt và tạo ticket.

**2. Sản phẩm tối thiểu:** Web/app deploy online; có ít nhất 2 vai trò; thể hiện workflow
agentic có trạng thái và tool-use; có human-in-the-loop (HITL) cho hành động rủi ro; xử lý lỗi
và cảnh báo rõ giới hạn của hệ thống.

**3. Dữ liệu và an toàn:** Chỉ dùng dữ liệu công khai, mô phỏng hoặc đã ẩn danh. Không đưa dữ
liệu cá nhân/nhạy cảm thật vào hệ thống. Các quyết định điểm số, tuyển sinh, tuyển dụng, y tế,
tài chính, an ninh hoặc điều khiển thiết bị phải có người chịu trách nhiệm phê duyệt.

**4. Đánh giá sản phẩm:** Có kịch bản demo chính và tình huống lỗi; eval/benchmark cho phần AI;
phân tích failure case; theo dõi tối thiểu độ trễ, lỗi và chi phí; nêu rõ giới hạn, rủi ro và
hướng cải tiến.

**5. Hồ sơ bàn giao:** Mã nguồn, hướng dẫn cài đặt/vận hành, dữ liệu mẫu, tài khoản demo, kiến
trúc hệ thống, test/eval, nhật ký quyết định quan trọng và video/demo, và theo các yêu cầu khác
của BTC.

---

## 3. Năng lực thể hiện qua sản phẩm — 8 PLO (nguyên văn)

| PLO | Nội dung |
|---|---|
| 1 | **Kiến trúc AI Agent:** Chọn đúng design pattern, quản lý context, memory và model routing hợp lý. |
| 2 | **Hệ thống Multi-Agent:** Khi bài toán cần nhiều agent phối hợp, sản phẩm phải phân vai, điều phối, trace và debug được chuỗi xử lý. |
| 3 | **RAG chất lượng cao:** Khi cần truy xuất tri thức, phải vượt mức naive RAG, có đo lường và cải tiến chất lượng retrieval. |
| 4 | **Phân tích bài toán kinh doanh:** Xác định đúng vấn đề, có user stories/PRD và lập luận về giá trị hoặc ROI. |
| 5 | **Hạ tầng và vận hành:** Sản phẩm được deploy thật, có giám sát cơ bản về độ trễ, lỗi, chi phí và tích hợp hệ thống ngoài khi cần. |
| 6 | **An toàn và kiểm soát AI:** Có guardrails, HITL, phòng chống prompt injection/rò rỉ dữ liệu và lưu ý tuân thủ khi chạm dữ liệu nhạy cảm. |
| 7 | **Đánh giá và tối ưu:** Có eval pipeline/benchmark, tiêu chí đánh giá, kết quả đo và chuyển failure case thành hành động cải tiến. |
| 8 | **Vibe Coding và làm việc nhóm:** Dùng AI coding assistant có kiểm soát, phối hợp nhóm hiệu quả và trình bày sản phẩm thuyết phục. |

**Ba cấu phần cần cân bằng:** đúng bài toán và giá trị kinh doanh (CP1); hạ tầng/dữ liệu/vận
hành triển khai được (CP2); lõi ứng dụng AI vững (CP3).

---

## 4. Đối chiếu: nhóm đang làm khác đề bài ở đâu, và vì sao

Quy định chung mục 1 nói rõ nội dung đề là **gợi ý**, và nhóm **được kỳ vọng tinh chỉnh theo
khảo sát người dùng thực tế**. Bốn chỗ dưới đây là chỗ nhóm chủ động lệch, mỗi chỗ đều có ADR.

| Hạng mục | Đề bài gợi ý | Nhóm làm | Lý do |
|---|---|---|---|
| Người dùng trung tâm | Cư dân ("cư dân không biết phân loại đúng") | **Đội vệ sinh + BQL**; cư dân là vai phụ | [ADR-0002](decisions/0002-chuyen-trong-tam-sang-van-hanh.md) — phỏng vấn 28/07 |
| Phạm vi rác đi qua AI | Không nói | Chỉ tái chế + cồng kềnh + nguy hại; **rác ướt đóng túi kín nằm ngoài phạm vi** | [ADR-0003](decisions/0003-phan-tang-rac-va-trong-tam-doi-ve-sinh.md) |
| Auth | Supabase | **Tự làm** (PBKDF2, `src/services/security.py`) | Chỉ cần 3 tài khoản demo; thêm Supabase Auth là thêm một dependency ngoài mà không thêm điểm. **Chưa có ADR — cần ghi.** |
| DB | PostgreSQL | SQLite khi dev → PostgreSQL khi deploy | Không cần Docker lúc dev; viết qua SQLAlchemy nên đổi `DATABASE_URL` là xong |

**Giữ đúng đề bài, không lệch:** cả 4 ràng buộc gốc · LangGraph 3 node đúng tên
`classify_waste → advise → schedule_pickup` · FastAPI · Next.js · Railway + Vercel · GPT-4o /
GPT-4o-mini.

**Hai mục "Nâng cao" của đề mà nhóm cần đối chiếu lại:**
- *Gamification tích điểm tái chế* — nhóm đang xếp **P2**. Cần biết rõ: đây là hạng mục **nâng
  cao chính thức của đề**, không phải ý phụ. Nếu cắt thì phải cắt có lý do nói được, không phải
  cắt vì quên. Lý do hiện tại: điểm thưởng chỉ có nghĩa khi có hệ thống thu phí để trừ vào, mà
  nhóm không tích hợp được hệ thống đó.
- *Dashboard tỉ lệ phân loại đúng & eval độ chính xác* — nhóm đang làm ở trang Vận hành + trang
  Eval. **Đây là chỗ trùng khớp mạnh nhất giữa đề bài và kế hoạch, ưu tiên cao.**
