# FRONTEND SPEC — VoiceOfCustomer AI Agent (BDSO2O-18)

> Tài liệu này viết để **dán trực tiếp cho công cụ thiết kế** (Claude design / v0 / Figma AI).
> Nó mô tả đầy đủ: bối cảnh, vai trò, từng màn hình, trạng thái, component, và dữ liệu.
> Không cần đọc thêm tài liệu nào khác.

---

## 0. TÓM TẮT SẢN PHẨM

**Tên:** VoiceOfCustomer AI Agent
**Ngành:** Bất động sản — doanh nghiệp kinh doanh O2O, nhiều dự án căn hộ.

**Vấn đề:** Phản hồi khách hàng nằm rải rác ở 4 nguồn — khảo sát sau bàn giao, ghi chú của sale trong CRM, comment mạng xã hội, transcript cuộc gọi CSKH. Ban kinh doanh không có bức tranh tổng hợp về việc khách khen/chê gì ở từng dự án, và luôn phát hiện vấn đề quá muộn.

**Giải pháp:** Một AI Agent gom phản hồi đa nguồn → ẩn danh dữ liệu cá nhân → phân loại chủ đề + chấm cảm xúc → gom cụm phát hiện chủ đề mới → tổng hợp thành *insight* kèm bằng chứng và đề xuất hành động → **quản lý duyệt trước khi insight được công bố**.

**Nguyên tắc thiết kế xuyên suốt — nhớ kỹ 3 điều này:**

1. **Không có con số nào đứng một mình.** Mọi phát biểu của AI đều đi kèm cỡ mẫu (`n=47/312`), độ tin cậy, và nút xem bằng chứng gốc. Nếu một khối UI hiển thị kết luận mà không có đường dẫn tới dữ liệu thô, khối đó thiết kế sai.
2. **Sự không chắc chắn phải nhìn thấy được.** Mẫu nhỏ, độ tin cậy thấp, dữ liệu ngoài phạm vi — đều có cảnh báo trực quan, không giấu.
3. **AI đề xuất, người quyết định.** Mọi thứ AI sinh ra đều ở trạng thái *chờ duyệt* cho tới khi có người bấm duyệt. Trạng thái này phải hiển thị rõ ở mọi nơi.

---

## 1. NGƯỜI DÙNG VÀ VAI TRÒ

Hệ thống có **2 vai trò bắt buộc** (yêu cầu của chương trình):

### Vai trò A — Nhân viên CSKH / Sale (`staff`)
- **Ai:** người tiếp xúc trực tiếp khách hàng, hàng ngày nạp phản hồi vào hệ thống.
- **Việc chính:** upload file phản hồi, nhập phản hồi lẻ, tra cứu phản hồi, xem insight **đã được duyệt**.
- **Không được:** duyệt insight, xem dữ liệu cá nhân gốc, xem trang vận hành/chi phí.

### Vai trò B — Quản lý kinh doanh (`manager`)
- **Ai:** trưởng phòng kinh doanh / marketing, người ra quyết định hành động.
- **Việc chính:** duyệt hoặc từ chối insight và đề xuất hành động, theo dõi xu hướng, nhận cảnh báo sớm, xem chi phí và độ tin cậy hệ thống.
- **Được thêm:** mở dữ liệu gốc chưa ẩn danh (có ghi log), xem trang Ops, xem trace của agent.

### Ma trận quyền — thể hiện trực tiếp trên UI

| Chức năng | staff | manager |
|---|:---:|:---:|
| Upload / nhập phản hồi | ✅ | ✅ |
| Xem danh sách phản hồi (đã ẩn danh) | ✅ | ✅ |
| Xem bản gốc chưa ẩn danh | ❌ | ✅ (có log) |
| Xem insight đã duyệt | ✅ | ✅ |
| Xem hàng đợi insight chờ duyệt | 👁 chỉ đọc | ✅ |
| Duyệt / sửa / từ chối insight | ❌ | ✅ |
| Chạy pipeline phân tích | ❌ | ✅ |
| Trang Ops (độ trễ, lỗi, chi phí) | ❌ | ✅ |
| Trang Eval / chất lượng AI | ❌ | ✅ |

**Yêu cầu UI:** chức năng không có quyền thì **hiện mờ kèm tooltip giải thích**, không ẩn hoàn toàn — để người demo thấy được ranh giới phân quyền.

**Tài khoản demo** (phải có sẵn trên màn đăng nhập, bấm 1 nút là vào):
- `staff@demo.vn` / `demo1234` — Nguyễn Thị Lan, CSKH
- `manager@demo.vn` / `demo1234` — Trần Văn Minh, Trưởng phòng KD

---

## 2. HỆ THỐNG THIẾT KẾ

### 2.1 Tông và cảm giác
Công cụ nội bộ cho doanh nghiệp BĐS — **nghiêm túc, mật độ thông tin cao, dễ đọc nhanh**. Không màu mè, không gradient trang trí, không illustration vui nhộn. Tham chiếu tinh thần: Linear, Vercel dashboard, Notion — sạch, chữ rõ, khoảng trắng có kỷ luật.

### 2.2 Bắt buộc kỹ thuật
- **Dark mode + light mode**, chuyển bằng toggle, nhớ lựa chọn (đây là tiêu chí chấm điểm riêng).
- **Responsive**: desktop 1440 là chính; tablet 768 phải dùng được; mobile 375 ít nhất đọc được insight và duyệt được.
- **Ngôn ngữ giao diện: tiếng Việt** toàn bộ. Chữ có dấu, tránh viết tắt lạ.
- Bảng và biểu đồ rộng phải cuộn ngang trong khung riêng, **không để cả trang cuộn ngang**.
- Accessibility: tương phản tối thiểu AA, mọi thông tin truyền bằng màu phải có thêm icon hoặc chữ (người mù màu phải phân biệt được tích cực/tiêu cực).

### 2.3 Bảng màu ngữ nghĩa
Sentiment dùng thang **-2 đến +2**:

| Giá trị | Nhãn | Màu | Icon |
|---|---|---|---|
| +2 | Rất tích cực | xanh lá đậm | ▲▲ |
| +1 | Tích cực | xanh lá nhạt | ▲ |
| 0 | Trung tính | xám | ● |
| -1 | Tiêu cực | cam | ▼ |
| -2 | Rất tiêu cực | đỏ | ▼▼ |

Trạng thái insight: `pending` = vàng/hổ phách, `approved` = xanh lá, `rejected` = xám, `edited` = xanh dương.
Cảnh báo: `critical` = đỏ, `warning` = cam, `info` = xanh dương.

### 2.4 Quy ước hiển thị độ tin cậy (dùng ở mọi nơi)

| Điều kiện | Hiển thị | Ý nghĩa |
|---|---|---|
| `confidence >= 0.8` | chip xanh "Tin cậy cao" | dùng được để ra quyết định |
| `0.6 <= confidence < 0.8` | chip vàng "Tin cậy trung bình" | nên đọc thêm bằng chứng |
| `confidence < 0.6` | chip đỏ "Tin cậy thấp — cần người xem" | không tự động hiển thị cho staff |
| `n < 10` | banner "⚠ Mẫu nhỏ (n=7) — chưa đủ để kết luận" | luôn hiện, không cho ẩn |
| `share < 3%` của tổng | ghi chú "chiếm 2% tổng phản hồi" | tránh thổi phồng vấn đề nhỏ |

---

## 3. KHUNG LAYOUT CHUNG

```
┌────────────────────────────────────────────────────────────────┐
│ [Logo VoC]   Dự án: [Sunrise Riverside ▾]  Kỳ: [T4–T6/2026 ▾] │  ← Topbar
│                          [🔔 3]  [🌙]  [Trần Văn Minh ▾ Quản lý]│
├──────────┬─────────────────────────────────────────────────────┤
│ Tổng quan│                                                      │
│ Phản hồi │                                                      │
│ Chủ đề   │              VÙNG NỘI DUNG                           │
│ ─────────│                                                      │
│ Duyệt ⑤ │                                                      │
│ ─────────│                                                      │
│ Agent run│                                                      │
│ Vận hành │                                                      │
│ Chất lượng│                                                     │
└──────────┴─────────────────────────────────────────────────────┘
```

- **Sidebar trái** thu gọn được. Mục "Duyệt" có badge số insight đang chờ. Nhóm dưới (Agent run / Vận hành / Chất lượng) **chỉ hiện với manager**.
- **Bộ lọc Dự án + Kỳ nằm trên topbar và áp dụng toàn cục** — đổi ở đây thì mọi màn đều đổi theo. Đây là quyết định quan trọng: người dùng luôn tư duy theo "dự án nào, tháng nào".
- Chuông thông báo mở panel cảnh báo (mục 4.7).

---

## 4. ĐẶC TẢ TỪNG MÀN HÌNH

Ưu tiên: **P0 = bắt buộc cho demo**, P1 = nên có, P2 = làm nếu còn thời gian.

---

### 4.1 Đăng nhập — `P0`

Màn tối giản, giữa trang. Logo + tên sản phẩm + một câu mô tả.

- Form email/mật khẩu.
- **Khối "Tài khoản demo"**: 2 nút lớn `Đăng nhập với vai trò Nhân viên CSKH` và `Đăng nhập với vai trò Quản lý`, mỗi nút có mô tả 1 dòng về quyền của vai trò đó. Bấm là vào thẳng.
- Ghi chú nhỏ dưới cùng: *"Hệ thống demo sử dụng dữ liệu mô phỏng và dữ liệu công khai đã ẩn danh. Không chứa thông tin cá nhân thật của khách hàng."* — câu này bắt buộc, thể hiện tuân thủ quy định dữ liệu.

---

### 4.2 Tổng quan — `P0` — cả 2 vai trò

Màn mặc định sau đăng nhập. Trả lời trong 10 giây: *"Sức khoẻ cảm xúc khách hàng đang thế nào, có gì cần xử lý gấp không?"*

**Khối 1 — Dải cảnh báo (trên cùng, chỉ hiện khi có)**
Băng đỏ/cam full-width: `🔴 Cảnh báo: Sunrise B — điểm cảm xúc giảm 0,31 trong 14 ngày, chủ yếu do "Tiến độ & bàn giao" (47 phản hồi tiêu cực).` Kèm nút `Xem chi tiết` và `Bỏ qua` (bỏ qua phải hỏi lý do).

**Khối 2 — 4 thẻ KPI**
| Thẻ | Nội dung | Phụ chú |
|---|---|---|
| Tổng phản hồi | `3.847` | `+412 so với kỳ trước` + sparkline |
| Điểm cảm xúc | `0,42 / 2,0` | mũi tên xu hướng + delta |
| Chủ đề nổi cộm | `Tiến độ & bàn giao` | `chiếm 23% phản hồi tiêu cực` |
| Insight chờ duyệt | `5` | nút `Duyệt ngay →` |

Mỗi thẻ KPI đều **bấm được**, dẫn tới màn chi tiết tương ứng.

**Khối 3 — Biểu đồ xu hướng cảm xúc theo thời gian**
Đường theo tuần/tháng, có thể chồng nhiều dự án để so sánh. Trục Y = điểm cảm xúc trung bình. **Có đánh dấu sự kiện** trên trục X (chấm tròn kèm tooltip: "12/5 — bắt đầu bàn giao lô C"). Chọn một khoảng thời gian trên biểu đồ sẽ lọc toàn bộ trang.

**Khối 4 — Phân bố chủ đề**
Biểu đồ thanh ngang, mỗi thanh là một chủ đề, **chia đoạn theo màu sentiment** (stacked). Sắp xếp theo số lượng giảm dần. Bấm vào thanh → mở màn Chủ đề.

**Khối 5 — Insight mới nhất đã duyệt**
3 thẻ insight rút gọn (tiêu đề + n + độ tin cậy + huy hiệu "Đã duyệt bởi Trần Văn Minh"). Staff chỉ nhìn thấy khối này ở dạng đã duyệt.

**Trạng thái rỗng:** khi chưa có dữ liệu → minh hoạ nhẹ + nút `Nạp phản hồi đầu tiên` + link tải file CSV mẫu.

---

### 4.3 Khám phá phản hồi — `P0` — cả 2 vai trò

Đây là màn của nhân viên CSKH. Bảng dữ liệu dày, tối ưu cho lọc và tra cứu.

**Thanh lọc (dính trên cùng):** ô tìm kiếm toàn văn · nguồn (khảo sát / CRM / mạng xã hội / cuộc gọi) · chủ đề (đa chọn) · sentiment (đa chọn) · khoảng thời gian · độ tin cậy · trạng thái xử lý.
Bộ lọc đang bật hiện thành các chip có nút ✕, kèm nút `Xoá tất cả`.

**Bảng — các cột:**

| Cột | Nội dung |
|---|---|
| Ngày | `12/05/2026` |
| Nguồn | icon + tên nguồn |
| Nội dung | text **đã ẩn danh**, cắt 2 dòng, hover xem đầy đủ |
| Chủ đề | các chip, tối đa 2 chip + `+2` |
| Cảm xúc | badge màu + icon, **theo từng chủ đề** khi mở rộng |
| Tin cậy | chip theo mục 2.4 |
| Dự án | tên dự án |

**Hàng mở rộng được** (bấm mũi tên): hiện toàn văn, danh sách `(chủ đề → cảm xúc)` đầy đủ, thời điểm phân tích, model đã dùng, `prompt_version`, và nút `Báo nhãn sai` (mở dialog chọn nhãn đúng — dữ liệu này chảy vào golden set).

**Hiển thị dữ liệu ẩn danh:** placeholder `[TÊN_1]`, `[SĐT_1]` hiển thị dưới dạng chip nhỏ màu xám nhạt, không phải text thường — để người xem biết ngay chỗ đó đã bị che.

**Nút "Xem bản gốc"** — chỉ manager. Bấm → dialog xác nhận: *"Bạn sắp xem dữ liệu cá nhân chưa ẩn danh. Hành động này được ghi vào nhật ký kiểm toán."* → hiện bản gốc + dòng `Đã ghi log lúc 14:32 bởi Trần Văn Minh`.

**Trạng thái:** loading = skeleton rows · rỗng sau lọc = "Không có phản hồi nào khớp bộ lọc" + nút xoá lọc · lỗi tải = thông báo + nút thử lại.

---

### 4.4 Chủ đề & Cụm — `P1` — cả 2 vai trò

Hai tab.

**Tab "Chủ đề cố định"** — bảng theo taxonomy 8 nhóm:
`Chủ đề · Số phản hồi · % tổng · Cảm xúc TB · Thay đổi so kỳ trước · Xu hướng (sparkline)`.
Mở rộng hàng → các chủ đề con (VD "Giá & tài chính" → giá bán, chiết khấu, lãi suất vay, phí quản lý).
Ô nào giảm mạnh thì tô nền đỏ nhạt.

**Tab "Cụm phát hiện tự động"** — các thẻ cụm do AI gom bằng embedding:
- Nhãn cụm do AI đặt (VD *"Tiếng ồn thi công lô C ảnh hưởng cư dân lô A"*)
- Kích thước cụm, cảm xúc trung bình
- Huy hiệu `MỚI` nếu cụm chưa từng xuất hiện kỳ trước
- 3 câu phản hồi tiêu biểu
- Nếu >60% thành viên cụm rơi vào nhãn "Khác" → hiện đề xuất: `AI đề xuất bổ sung chủ đề mới vào danh mục` + nút `Gửi quản lý duyệt` (**đây cũng là một luồng HITL**)

Kèm một sơ đồ phân tán 2D (scatter) các cụm — không bắt buộc chính xác, mục đích minh hoạ trực quan.

---

### 4.5 Duyệt Insight (HITL) — `P0` — **MÀN QUAN TRỌNG NHẤT**

Đây là màn ăn điểm cao nhất. Bố cục 2 cột: trái là hàng đợi, phải là chi tiết.

```
┌─────────────────┬──────────────────────────────────────────┐
│ HÀNG ĐỢI (5)    │  CHI TIẾT INSIGHT                        │
│ ┌─────────────┐ │  ┌────────────────────────────────────┐  │
│ │ ● Insight 1 │ │  │ [CHỜ DUYỆT] [Tin cậy cao 0,84]     │  │
│ │   n=47 0,84 │ │  │ Khách hàng Sunrise B phản ứng      │  │
│ ├─────────────┤ │  │ mạnh về chậm bàn giao lô C         │  │
│ │   Insight 2 │ │  └────────────────────────────────────┘  │
│ │   n=12 0,61 │ │  📊 Cơ sở dữ liệu                        │
│ ├─────────────┤ │  🔍 Bằng chứng (8 phản hồi)              │
│ │   Insight 3 │ │  🎯 Đề xuất hành động (3)                │
│ └─────────────┘ │  ⚙️ Nguồn gốc & minh bạch                │
│                 │  [Duyệt] [Sửa & duyệt] [Từ chối] [Thêm DL]│
└─────────────────┴──────────────────────────────────────────┘
```

**Cột trái — hàng đợi:** lọc theo trạng thái (`chờ duyệt / đã duyệt / đã từ chối / tất cả`), sắp xếp theo mức độ nghiêm trọng hoặc thời gian. Mỗi thẻ: chấm màu mức độ, tiêu đề rút gọn, `n`, độ tin cậy, dự án, thời gian tạo.

**Cột phải — chi tiết, 5 khối theo thứ tự:**

**① Tiêu đề & phân loại**
Badge trạng thái · chip độ tin cậy · chip mức độ nghiêm trọng · tiêu đề insight · dự án + kỳ.

**② Cơ sở dữ liệu** (khối nền xám nhạt, số liệu do SQL tính — không phải LLM sinh)
```
Số phản hồi liên quan:  47 / 312  (15,1%)
Cảm xúc trung bình:     -1,4  (kỳ trước: -0,3)
Chủ đề:                 Tiến độ & bàn giao › Chậm bàn giao
Khoảng thời gian:       28/04/2026 – 26/05/2026
Nguồn:                  Khảo sát 61%, CSKH 27%, Mạng XH 12%
```
Nếu `n < 10` → banner cảnh báo mẫu nhỏ ngay tại đây.

**③ Nội dung insight**
Đoạn văn AI viết. **Mọi con số trong đoạn văn được gạch chân nét đứt**, hover hiện tooltip cho biết con số đó tính từ đâu.

**④ Bằng chứng — không được lược bỏ khối này**
Danh sách 8 phản hồi gốc (đã ẩn danh) dạng thẻ trích dẫn: nội dung, nguồn, ngày, sentiment. Có nút `Xem tất cả 47 phản hồi →` (mở màn Khám phá phản hồi với bộ lọc tương ứng đã áp sẵn).
Mỗi thẻ bằng chứng có nút nhỏ 👎 `Không liên quan` — phản hồi này dùng để đo chất lượng retrieval.

**⑤ Đề xuất hành động**
Mỗi đề xuất là một thẻ: nội dung · mức ưu tiên (Cao/TB/Thấp) · công sức ước tính · bộ phận chịu trách nhiệm · **checkbox chọn/bỏ chọn từng đề xuất** (quản lý có thể duyệt insight nhưng chỉ chấp nhận 2/3 hành động).

**⑥ Nguồn gốc & minh bạch** (khối gập lại, mặc định đóng)
`Model: gpt-4o-mini (phân loại) + gpt-4o (tổng hợp)` · `prompt_version: v3` · `Thời gian xử lý: 4,2 giây` · `Chi phí: $0,018` · `Agent run: #a3f9 →` (link sang màn Trace) · `Tạo lúc: 26/05/2026 09:14`.

**Thanh hành động (dính dưới cùng) — 4 nút:**

| Nút | Hành vi |
|---|---|
| ✅ **Duyệt** | insight chuyển `approved`, hiện trên dashboard staff. Toast xác nhận + nút Hoàn tác trong 10 giây. |
| ✏️ **Sửa & duyệt** | mở editor sửa tiêu đề/nội dung/hành động. **Hiện diff giữa bản AI và bản đã sửa** — phần này rất đáng giá khi demo. |
| ❌ **Từ chối** | **bắt buộc chọn lý do** từ danh sách: `Sai chủ đề` · `Sai cảm xúc` · `Mẫu quá nhỏ` · `Vấn đề đã biết` · `Đề xuất không khả thi` · `Bằng chứng không thuyết phục` · `Khác (ghi rõ)`. |
| 🔄 **Cần thêm dữ liệu** | đưa về hàng đợi, đánh dấu chờ đủ mẫu. |

**Điều hướng bàn phím:** `J`/`K` chuyển insight, `A` duyệt, `R` từ chối, `E` sửa. Có bảng phím tắt bấm `?`. Chi tiết nhỏ nhưng gây ấn tượng mạnh khi demo.

**Sau khi duyệt xong hàng đợi:** màn chúc mừng + thống kê phiên làm việc (`Bạn đã duyệt 4, từ chối 1. Tỷ lệ duyệt của bạn: 78%`).

---

### 4.6 Agent Run / Trace — `P1` — chỉ manager

Màn này chứng minh "workflow agentic có trạng thái và tool-use, trace và debug được". Đừng bỏ qua — nó là yêu cầu tối thiểu của chương trình.

**Danh sách các lần chạy:** `ID · thời điểm · trigger (thủ công/tự động) · số phản hồi xử lý · trạng thái · thời gian · chi phí`.

**Chi tiết một lần chạy — timeline dọc các node:**
```
● ingest          ✅  1.240 phản hồi   0,8s    $0
│
● redact_pii      ✅  che 891 thực thể 1,2s    $0
│                     ⚠ 3 mục nghi ngờ còn sót → xem
● classify        ✅  1.240 mục        42,1s   $0,124
│                     cache hit 38% · 12 lần thử lại
● cluster         ✅  17 cụm, 4 mới    8,3s    $0,004
│
● detect_anomaly  ⚠️  2 cảnh báo       0,4s    $0
│
● synthesize      ✅  5 insight        12,7s   $0,089
│
● guardrail_check ✅  chặn 2 mục đáng ngờ 0,3s $0
```
Bấm vào node → panel bên phải hiện: input state, output state, prompt đã dùng (rút gọn, có nút xem đầy đủ), số token, lỗi nếu có.

Kèm **sơ đồ graph** của LangGraph (node + cạnh), node đang chạy nhấp nháy khi chạy live.

**Node `guardrail_check` phải có** — phản hồi khách hàng là dữ liệu không tin cậy đi thẳng vào prompt, nên hệ thống cần phát hiện prompt injection. UI hiển thị các mục bị chặn: `2 phản hồi chứa nội dung nghi ngờ chèn lệnh — đã cách ly, không đưa vào phân tích` + nút xem nội dung bị chặn.

---

### 4.7 Cảnh báo sớm — `P1` — panel + trang

Mở từ chuông trên topbar.

Mỗi cảnh báo: mức độ (đỏ/cam/xanh) · tiêu đề · dự án · thời điểm phát hiện · lý do kích hoạt (`điểm cảm xúc giảm 0,31 > ngưỡng 0,25 trong 14 ngày`) · nút `Xem insight liên quan` · nút `Xác nhận đã đọc`.

**Bắt buộc hiển thị ngưỡng kích hoạt** — cảnh báo không nói vì sao mình kêu là cảnh báo vô dụng.

Có trang cài đặt ngưỡng đơn giản: ngưỡng giảm sentiment, số phản hồi tối thiểu, cửa sổ thời gian.

---

### 4.8 Vận hành & Chi phí — `P0` — chỉ manager

Chương trình yêu cầu theo dõi tối thiểu **độ trễ, lỗi và chi phí**. Ba khối tương ứng:

**Khối Chi phí**
- Thẻ lớn: `Tổng chi phí kỳ này: $2,14` · `Đã xử lý: 3.847 phản hồi` · `$0,56 / 1.000 phản hồi`
- Biểu đồ cột chi phí theo ngày, chia màu theo node (classify / synthesize / embedding)
- **Thẻ so sánh:** `Kiến trúc phân tầng: $2,14` vs `Nếu gọi model lớn cho mọi phản hồi: $14,60` → `Tiết kiệm 85%`. Đây là một slide demo tự nó.
- Tỷ lệ cache hit, tỷ lệ escalation lên model lớn
- Thanh ngân sách: `$2,14 / $25,00` + cảnh báo khi vượt 80%

**Khối Độ trễ**
- p50 / p95 thời gian xử lý mỗi node, dạng bar ngang
- Thời gian phản hồi API theo endpoint
- Biểu đồ độ trễ theo thời gian, có đánh dấu các spike

**Khối Lỗi & Giới hạn**
- Tỷ lệ lỗi theo node, danh sách 10 lỗi gần nhất (thời điểm, node, loại lỗi, số lần thử lại)
- Số lần chạm rate limit của API
- **Khối "Giới hạn đã biết của hệ thống"** — viết cứng, luôn hiển thị:
  > • Chỉ phân tích tiếng Việt; phản hồi tiếng Anh có độ chính xác thấp hơn ~15%
  > • Câu mỉa mai/châm biếm vẫn bị nhận nhầm trong ~18% trường hợp
  > • Chủ đề không có trong danh mục sẽ rơi vào nhóm "Khác" (hiện chiếm 7%)
  > • Insight cần tối thiểu 10 phản hồi cùng chủ đề mới được sinh
  > • Dữ liệu demo là dữ liệu mô phỏng, không phải khách hàng thật

Khối cuối cùng này trực tiếp đáp ứng yêu cầu "nêu rõ giới hạn, rủi ro" — và rất ít nhóm nghĩ tới việc đưa nó lên UI.

---

### 4.9 Chất lượng AI / Eval — `P2` — chỉ manager

- Bảng metrics: `macro-F1 phân loại chủ đề`, `F1 sentiment`, `độ chính xác retrieval bằng chứng`, kèm cỡ golden set và ngày cập nhật.
- **Ma trận nhầm lẫn** (confusion matrix) cho sentiment — heatmap, bấm ô xem các case bị sai.
- **Bảng so sánh phiên bản:** `baseline từ khoá` vs `prompt v1` vs `v2` vs `v3`, các cột F1 + chi phí + độ trễ.
- **Danh sách failure case:** nội dung, nhãn đúng, nhãn AI đoán, phân loại nguyên nhân (mỉa mai / đa chủ đề / teencode / thiếu ngữ cảnh), và trạng thái đã xử lý hay chưa.
- Biểu đồ `tỷ lệ insight được duyệt` theo từng phiên bản prompt — chứng minh vòng lặp cải tiến có hiệu quả.

---

### 4.10 Nạp dữ liệu — `P1` — cả 2 vai trò

Wizard 3 bước.

**Bước 1 — Chọn nguồn:** 4 thẻ (Khảo sát CSV · CRM · Mạng xã hội · Transcript cuộc gọi) + tuỳ chọn `Nhập một phản hồi lẻ`. Có nút tải file mẫu cho từng loại.

**Bước 2 — Ánh xạ cột:** hiện preview 5 dòng đầu, cho map cột file → trường hệ thống (nội dung, ngày, dự án, nguồn). Cảnh báo nếu thiếu cột bắt buộc.

**Bước 3 — Xem trước khi ẩn danh:** bảng 2 cột **Gốc | Sau khi ẩn danh**, tô nổi phần bị che.
Tóm tắt: `Phát hiện 47 số điện thoại, 12 email, 89 tên riêng — tất cả đã được thay thế trước khi gửi tới mô hình AI.`
Checkbox xác nhận: *"Tôi xác nhận dữ liệu này là dữ liệu công khai, mô phỏng, hoặc đã được phép sử dụng."* — bắt buộc tick mới cho phép nạp.

**Trong lúc chạy:** thanh tiến trình theo node + số phản hồi đã xử lý + chi phí đang phát sinh theo thời gian thực. Có nút `Huỷ`.

**Xử lý lỗi phải thấy được:** nếu 23/1240 dòng lỗi → hiện bảng dòng lỗi kèm lý do, nút tải file lỗi về, và **vẫn cho nạp 1217 dòng thành công** (không đánh sập cả lô).

---

## 5. THƯ VIỆN COMPONENT CẦN THIẾT KẾ

| Component | Mô tả | Dùng ở |
|---|---|---|
| `SentimentBadge` | badge màu + icon + số, 5 mức | khắp nơi |
| `ConfidenceChip` | 3 mức theo mục 2.4, có tooltip giải thích | khắp nơi |
| `SampleSizeNote` | `n=47/312 (15,1%)` + cảnh báo khi n nhỏ | insight, chủ đề |
| `EvidenceCard` | thẻ trích dẫn phản hồi + nguồn + ngày + nút 👎 | màn Duyệt |
| `RedactedText` | text có chip placeholder cho phần bị che | bảng phản hồi |
| `TopicChip` | chip chủ đề, có màu riêng theo nhóm | khắp nơi |
| `StatusBadge` | pending / approved / rejected / edited | insight |
| `TrendDelta` | mũi tên + số thay đổi + màu | KPI, bảng chủ đề |
| `NodeTimelineItem` | 1 dòng trong trace: icon, tên, số liệu, thời gian, chi phí | Agent run |
| `AlertBanner` | 3 mức, có nút hành động và bỏ qua | tổng quan |
| `CostMeter` | thanh ngân sách + cảnh báo ngưỡng | Ops |
| `EmptyState` | icon + câu giải thích + hành động gợi ý | mọi bảng |
| `ErrorState` | thông báo lỗi thân thiện + nút thử lại + mã lỗi để báo cáo | mọi màn |
| `LimitationNote` | khối ghi chú giới hạn hệ thống, nền vàng nhạt | Ops, insight |

---

## 6. TRẠNG THÁI BẮT BUỘC CHO MỌI MÀN

Thiết kế thiếu 4 trạng thái này là thiết kế chưa xong:

1. **Loading** — skeleton đúng hình dạng nội dung thật, không dùng spinner giữa màn.
2. **Rỗng** — phân biệt *chưa có dữ liệu bao giờ* (kèm hướng dẫn bắt đầu) và *không có kết quả sau khi lọc* (kèm nút xoá lọc).
3. **Lỗi** — câu tiếng Việt dễ hiểu, không hiện stack trace, có nút thử lại và mã lỗi ngắn để đối chiếu log.
4. **Suy giảm một phần** — pipeline chạy xong nhưng một node lỗi: vẫn hiện dữ liệu có được kèm băng cảnh báo `Một phần dữ liệu chưa được phân tích do lỗi ở bước gom cụm. Kết quả hiển thị dựa trên 1.217/1.240 phản hồi.`

Trạng thái số 4 hiếm ai làm, và nó chính là "xử lý lỗi và cảnh báo giới hạn của hệ thống" mà chương trình yêu cầu.

---

## 7. HỢP ĐỒNG DỮ LIỆU (API)

```
POST /api/v1/auth/login                  → {token, user:{id,name,role}}
GET  /api/v1/projects                    → [{id,name,feedback_count,sentiment_score,trend}]
GET  /api/v1/overview?project&from&to    → {kpis, timeline[], by_topic[], alerts[], recent_insights[]}
GET  /api/v1/feedback?filters&page       → {items[], total, page_size}
GET  /api/v1/feedback/{id}/original      → {raw_text}   (manager, ghi audit log)
GET  /api/v1/topics?project&period       → [{topic,subtopics[],count,share,avg_sentiment,delta}]
GET  /api/v1/clusters?project            → [{id,label,size,avg_sentiment,is_new,samples[]}]
GET  /api/v1/insights?status             → [{id,title,body,n,total,confidence,severity,
                                             evidence_ids[],proposed_actions[],status,provenance}]
GET  /api/v1/insights/{id}/evidence      → [{id,redacted_text,source,date,sentiment,topics[]}]
POST /api/v1/insights/{id}/review        → {action, reason?, note?, edited_body?, accepted_actions[]}
GET  /api/v1/runs                        → [{id,started_at,trigger,items,status,duration_ms,cost_usd}]
GET  /api/v1/runs/{id}                   → {nodes[{name,status,metrics,duration_ms,cost_usd,error}]}
GET  /api/v1/ops/metrics                 → {cost{...}, latency{p50,p95,by_node}, errors{...}, budget{...}}
GET  /api/v1/eval/summary                → {macro_f1, sentiment_f1, confusion_matrix, versions[], failures[]}
POST /api/v1/ingest                      → {job_id}
GET  /api/v1/jobs/{id}                   → {status, progress, current_node, errors[]}
GET  /api/v1/alerts                      → [{id,severity,title,project,threshold,triggered_at,ack}]
```

Mọi phản hồi lỗi theo một khuôn: `{error: {code, message_vi, detail?}}`.

---

## 8. KỊCH BẢN DEMO — UI PHẢI ĐI TRỌN 6 BƯỚC NÀY

1. Đăng nhập vai trò **Nhân viên CSKH** → nạp file 300 phản hồi mới của Sunrise B → xem bước ẩn danh che 47 số điện thoại → chạy.
2. Đổi sang vai trò **Quản lý** → Tổng quan hiện **cảnh báo đỏ**: cảm xúc Sunrise B giảm 0,31.
3. Bấm cảnh báo → drill-down thấy chủ đề "Tiến độ & bàn giao" tăng vọt, và một **cụm mới** AI tự phát hiện: *"tiếng ồn thi công lô C"*.
4. Vào màn **Duyệt** → đọc insight `n=47/312, tin cậy 0,84` → mở 8 bằng chứng gốc → sửa 1 câu → duyệt. Từ chối insight thứ 2 với lý do "mẫu quá nhỏ".
5. Mở **Agent run** → xem timeline 7 node, thấy `guardrail_check` đã chặn 2 phản hồi chứa nội dung chèn lệnh.
6. Mở **Vận hành** → `3.847 phản hồi, $2,14, tiết kiệm 85% so với gọi model lớn toàn bộ` + đọc khối giới hạn hệ thống.

Sáu bước này chạm đủ: 2 vai trò, workflow agentic có tool-use, HITL, ẩn danh dữ liệu, guardrail, theo dõi độ trễ/lỗi/chi phí, và nêu rõ giới hạn.

---

## 9. ĐỐI CHIẾU VỚI TIÊU CHÍ CHẤM

| Yêu cầu chương trình | Màn hình chứng minh |
|---|---|
| Web deploy online, ít nhất 2 vai trò | 4.1 Đăng nhập + ma trận quyền mục 1 |
| Workflow agentic có trạng thái, tool-use, trace được | 4.6 Agent Run |
| HITL cho hành động rủi ro | 4.5 Duyệt Insight |
| Xử lý lỗi, cảnh báo giới hạn hệ thống | mục 6 (4 trạng thái) + 4.8 khối Giới hạn |
| Dữ liệu ẩn danh, không dữ liệu cá nhân thật | 4.10 bước 3 + 4.3 RedactedText |
| Theo dõi độ trễ, lỗi, chi phí | 4.8 Vận hành |
| Eval/benchmark, phân tích failure case | 4.9 Chất lượng AI |
| PLO 1 — kiến trúc, model routing | 4.6 (thấy rõ model nào chạy node nào) + 4.8 (so sánh chi phí) |
| PLO 2 — multi-agent, trace được | 4.6 |
| PLO 3 — retrieval vượt naive RAG, có đo lường | 4.5 khối bằng chứng + nút 👎 + 4.9 metric retrieval |
| PLO 4 — giá trị kinh doanh | 4.2 KPI + 4.5 đề xuất hành động có ưu tiên |
| PLO 5 — giám sát độ trễ/lỗi/chi phí | 4.8 |
| PLO 6 — guardrail, chống prompt injection, ẩn danh | 4.6 node guardrail + 4.10 bước 3 |
| PLO 7 — eval pipeline, failure → cải tiến | 4.9 |

---

## 10. THỨ TỰ LÀM (khi chỉ có một người)

**Đợt 1 — đủ để demo:** 4.1 Đăng nhập · 4.2 Tổng quan · 4.3 Khám phá phản hồi · 4.5 Duyệt Insight · 4.8 Vận hành.
**Đợt 2:** 4.6 Agent Run · 4.10 Nạp dữ liệu · 4.7 Cảnh báo.
**Đợt 3:** 4.4 Chủ đề & Cụm · 4.9 Chất lượng AI.

Nếu buộc phải cắt, **giữ bằng mọi giá màn 4.5 (Duyệt Insight)** — nó là nơi thể hiện HITL, bằng chứng, độ tin cậy và giá trị kinh doanh cùng một lúc.
