# FRONTEND SPEC — GreenBin AI (VHR-17)

> **Cách dùng file này:** dán trực tiếp cho công cụ thiết kế (Claude design / v0 / Figma AI).
> File tự chứa đủ bối cảnh — không cần đọc thêm tài liệu nào khác.
> Cách chia nhỏ để dán từng phần: xem **mục 12** ở cuối.
>
> Phiên bản: 1.0 · Cập nhật: 28/07/2026 · Thay cho spec cũ của đề VoiceOfCustomer (đã chuyển vào `attic/voc/FRONTEND_SPEC_voc.md`).

---

## 0. TÓM TẮT SẢN PHẨM

**Tên:** GreenBin AI — Agent Phân loại Rác & Điều phối Thu gom Tái chế
**Ngành:** Bất động sản — app ứng dụng cho cư dân chung cư.

**Vấn đề:** Doanh nghiệp BĐS phải triển khai phân loại rác tại nguồn theo Luật Bảo vệ môi trường 2020, nhưng cư dân không biết phân loại đúng (hộp sữa giấy tráng nhôm bỏ đâu? ly trà sữa có màng nhựa? pin cũ?). Việc đăng ký thu gom đồ cồng kềnh và rác tái chế khối lượng lớn vẫn làm thủ công qua điện thoại, đội vệ sinh chạy nhiều chuyến lẻ tốn chi phí.

**Giải pháp:** Một AI Agent để cư dân **chụp ảnh hoặc gõ mô tả** món rác → nhận hướng dẫn "bỏ vào thùng nào, để ở đâu, thu gom lúc mấy giờ" **có trích dẫn quy định** → nếu là đồ cồng kềnh thì đặt lịch thu gom ngay trong app → agent **gộp các yêu cầu cùng toà cùng khung giờ thành một tuyến** → **BQL/đội trưởng duyệt** rồi mới chốt lịch.

**Ba nguyên tắc thiết kế xuyên suốt — quan trọng hơn mọi chi tiết khác:**

1. **Không chắc thì phải nói là không chắc, và phải chuyển cho người.**
   Đây là sản phẩm có thể gây hại thật: hướng dẫn sai về pin lithium, bóng đèn huỳnh quang, thuốc hết hạn, hoá chất là nguy hiểm. Giao diện **không bao giờ được trả lời nước đôi cho ra vẻ hữu ích**. Dưới ngưỡng tin cậy → hiện màn "Mình chưa chắc" một cách dứt khoát và tự tin, không phải như một lỗi hệ thống.

2. **Mọi lời khuyên đều phải chỉ ra được nguồn.**
   Mỗi hướng dẫn kèm chip nguồn bấm được: *Nội quy toà S1 · mục 4.2* hoặc *Nghị định 45/2022/NĐ-CP · Điều 26*. Khối UI nào đưa kết luận mà không có đường dẫn về văn bản gốc là khối thiết kế sai.

3. **AI đề xuất, người chốt.**
   Ba việc AI **không được tự làm**: duyệt yêu cầu thu gom vượt ngưỡng, xác nhận nhãn cho ca nghi ngờ, và **thay đổi lịch làm việc của đội vệ sinh**. Cả ba đều ở trạng thái *chờ duyệt* cho tới khi có người bấm, và trạng thái đó hiển thị rõ ở mọi nơi nó xuất hiện.

---

## 1. NGƯỜI DÙNG VÀ VAI TRÒ

Hệ thống có **3 vai trò** (chương trình yêu cầu tối thiểu 2 — ta làm 3 vì luồng thu gom cần cả người thực thi lẫn người duyệt).

### Vai trò A — Cư dân (`resident`) — **thiết bị chính: điện thoại**
- **Ai:** người đang đứng cạnh thùng rác, tay cầm túi rác, muốn biết bỏ vào đâu trong 10 giây.
- **Việc chính:** chụp ảnh/gõ mô tả để hỏi · đọc hướng dẫn · xem lịch thu gom của toà mình · đăng ký thu gom đồ cồng kềnh · theo dõi yêu cầu của mình · xem "ảnh của tôi đã được xử lý thế nào".
- **Không được:** duyệt bất cứ thứ gì, xem ảnh của cư dân khác, xem trang vận hành/chi phí.

### Vai trò B — Đội vệ sinh (`cleaner`) — **thiết bị chính: điện thoại / tablet, dùng ngoài trời**
- **Ai:** nhân viên đi thu gom, cầm điện thoại một tay, đeo găng, nắng chói.
- **Việc chính:** xem tuyến hôm nay theo thứ tự điểm dừng · đánh dấu đã thu · báo phát sinh (không có người, khối lượng khác dự kiến) · xác nhận nhãn cho ca phân loại nghi ngờ.
- **Yêu cầu riêng về giao diện:** nút to tối thiểu 48×48px, chữ tối thiểu 16px, tương phản cao, **dùng được bằng một ngón cái**, và **hoạt động khi mạng chập chờn** (xem mục 2.5).

### Vai trò C — Ban quản lý (`manager`) — **thiết bị chính: máy tính**
- **Ai:** BQL toà nhà / đội trưởng vệ sinh, ngồi bàn, cần nhìn tổng thể và ra quyết định.
- **Việc chính:** duyệt 3 loại hàng đợi HITL · quản lý danh mục rác và kho quy định · xem vận hành (độ trễ, lỗi, chi phí) · xem chất lượng AI và các ca phân loại sai · xem trace agent.
- **Được thêm:** mở **ảnh gốc chưa xử lý** (có ghi audit log).

### Ma trận quyền — phải thể hiện được trên UI

| Chức năng | resident | cleaner | manager |
|---|:---:|:---:|:---:|
| Hỏi phân loại (ảnh / chữ) | ✅ | ✅ | ✅ |
| Xem lịch thu gom của toà | ✅ | ✅ | ✅ |
| Đăng ký thu gom đồ cồng kềnh | ✅ | ❌ | ✅ (thay cư dân) |
| Xem yêu cầu của chính mình | ✅ | — | — |
| Xem toàn bộ yêu cầu của toà | ❌ | ✅ (tuyến của mình) | ✅ |
| **Duyệt yêu cầu thu gom vượt ngưỡng** | ❌ | 👁 chỉ đọc | ✅ |
| **Xác nhận nhãn ca nghi ngờ** | ❌ | ✅ | ✅ |
| **Duyệt tuyến gộp** | ❌ | ❌ | ✅ |
| Đánh dấu đã thu tại điểm dừng | ❌ | ✅ | ✅ |
| Sửa danh mục rác / kho quy định | ❌ | ❌ | ✅ |
| Xem ảnh gốc chưa xử lý | ❌ | ❌ | ✅ (ghi log) |
| Trang Vận hành (độ trễ/lỗi/chi phí) | ❌ | ❌ | ✅ |
| Trang Chất lượng AI / Eval | ❌ | ❌ | ✅ |
| Agent Run / Trace | ❌ | ❌ | ✅ |

**Yêu cầu UI:** chức năng không có quyền thì **hiện mờ kèm tooltip giải thích lý do**, không ẩn hoàn toàn — để người chấm thấy được ranh giới phân quyền là có chủ đích.

### Tài khoản demo (phải có nút bấm-1-phát trên màn đăng nhập)

| Nút | Tài khoản | Nhân vật |
|---|---|---|
| `Vào với vai trò Cư dân` | `resident@demo.vn` / `demo1234` | Nguyễn Thị Lan — căn S1-1203, toà Sunrise S1 |
| `Vào với vai trò Đội vệ sinh` | `cleaner@demo.vn` / `demo1234` | Lê Văn Hùng — tổ vệ sinh ca sáng |
| `Vào với vai trò Ban quản lý` | `manager@demo.vn` / `demo1234` | Trần Minh Đức — BQL Sunrise Residence |

---

## 2. HỆ THỐNG THIẾT KẾ

### 2.1 Hai "bộ mặt" của sản phẩm — quyết định thiết kế quan trọng nhất

Đây **không phải một dashboard dùng chung**. Hai bối cảnh sử dụng khác nhau hoàn toàn:

| | **App Cư dân + Đội vệ sinh** | **Console Ban quản lý** |
|---|---|---|
| Thiết bị chính | Điện thoại 375–430px | Desktop 1440px |
| Bối cảnh | đứng cạnh thùng rác, một tay, vội | ngồi bàn, hai màn hình, có thời gian |
| Mật độ thông tin | thấp — mỗi màn một việc | cao — bảng, biểu đồ, hàng đợi |
| Cảm giác | thân thiện, sạch, xanh, dứt khoát | nghiêm túc, dày, đọc nhanh |
| Điều hướng | tab bar dưới, 4 mục | sidebar trái, có nhóm |
| Tham chiếu tinh thần | Grab / MoMo / Google Lens | Linear · Vercel dashboard |

**Cả hai vẫn dùng chung một bảng màu, một bộ chữ, một bộ icon** — phải nhìn ra là cùng một sản phẩm.

### 2.2 Bắt buộc kỹ thuật

- **Ngôn ngữ giao diện: tiếng Việt toàn bộ**, có dấu đầy đủ, tránh viết tắt lạ. Không trộn tiếng Anh trong nội dung người dùng đọc (trừ tên model ở trang kỹ thuật).
- **Dark mode + light mode**, toggle được, nhớ lựa chọn. Đội vệ sinh dùng ngoài nắng → light mode phải có tương phản cao thật sự.
- **Responsive:** app cư dân thiết kế mobile-first 375px rồi mở rộng; console BQL desktop 1440 là chính, tablet 768 phải dùng được.
- **Accessibility:** tương phản tối thiểu AA. **Mọi thông tin truyền bằng màu phải có thêm icon hoặc chữ** — điều này đặc biệt quan trọng ở đây vì màu thùng rác chính là thông tin (người mù màu vẫn phải phân biệt được thùng xanh lá và thùng cam).
- Bảng/biểu đồ rộng cuộn ngang **trong khung riêng**, không để cả trang cuộn ngang.
- Ảnh cư dân **không bao giờ đặt ở URL công khai đoán được** — mọi ảnh phải qua endpoint có kiểm tra quyền.

### 2.3 Bảng màu ngữ nghĩa

**Nhóm rác** — màu này là thông tin nghiệp vụ, **UI phải đọc `bin_color` từ API chứ không hardcode**, vì mỗi toà có thể quy định khác nhau. Bảng dưới là giá trị mặc định để thiết kế:

| Nhóm | Mã | Màu | Icon gợi ý |
|---|---|---|---|
| Tái chế (giấy, nhựa, kim loại, thuỷ tinh) | `recyclable` | xanh dương | ♻️ mũi tên vòng |
| Rác thực phẩm / hữu cơ | `organic` | xanh lá | 🍃 lá |
| Rác sinh hoạt khác | `other` | xám | 🗑 thùng |
| **Rác nguy hại** | `hazardous` | **đỏ cam** | ⚠️ tam giác cảnh báo |
| Đồ cồng kềnh | `bulky` | tím | 📦 kiện hàng |

**Nhóm nguy hại phải nhìn khác hẳn về mặt thị giác** — không chỉ đổi màu chip mà đổi cả nền khối, viền và icon. Người dùng lướt nhanh phải khựng lại.

**Trạng thái yêu cầu thu gom:** `pending` vàng hổ phách · `approved` xanh lá · `rejected` xám · `scheduled` xanh dương · `done` xanh lá đậm · `cancelled` xám gạch ngang.
**Trạng thái tuyến:** `proposed` vàng (AI đề xuất) · `approved` xanh lá · `in_progress` xanh dương nhấp nháy nhẹ · `done` xám.
**Cảnh báo:** `critical` đỏ · `warning` cam · `info` xanh dương.

### 2.4 Quy ước hiển thị độ tin cậy — dùng ở MỌI nơi có kết quả AI

Ngưỡng **không cố định** — mỗi nhóm rác có `min_confidence` riêng lấy từ API, nhóm nguy hại cao hơn hẳn. UI hiển thị theo bảng:

| Điều kiện | Hiển thị | Hành vi |
|---|---|---|
| `confidence >= min_confidence + 0.15` | chip xanh `Chắc chắn` | trả lời bình thường |
| `min_confidence <= confidence < +0.15` | chip vàng `Khá chắc — nên kiểm tra lại` | trả lời + gợi ý xem quy định gốc |
| `confidence < min_confidence` | **không hiện kết quả** | → màn "Mình chưa chắc" (4.4) |
| Ảnh có nhiều vật | chip `Thấy nhiều món` | tách từng món, hỏi lại người dùng chọn |
| Trong danh sách chặn cứng | **bỏ qua confidence** | luôn chuyển người, luôn hiện cảnh báo an toàn |

**Chip tầng model** (`tier`) — hiện ở màn kết quả dạng nhỏ, xám nhạt, và hiện đầy đủ ở console BQL:

| `tier` | Nhãn hiển thị cho cư dân | Nhãn ở console |
|---|---|---|
| `t0_cache` | `Đã biết câu trả lời` ⚡ | `T0 · cache pHash · $0` |
| `t1_mini` | *(không hiện gì)* | `T1 · gpt-4o-mini` |
| `t2_full` | `Đã kiểm tra kỹ` 🔍 | `T2 · gpt-4o · escalate: <lý do>` |

Đây là chi tiết nhỏ nhưng ăn điểm: cư dân thấy được hệ thống "kiểm tra kỹ hơn" khi cần, người chấm thấy được định tuyến 3 tầng có thật.

### 2.5 Xử lý mạng kém — bắt buộc, không phải tuỳ chọn

Hầm để xe và khu vực thùng rác chung cư **sóng rất yếu**. Đây là bối cảnh sử dụng thật của sản phẩm, nên phải thiết kế cho nó:

- Ảnh nén **phía client** trước khi gửi (512px) — hiện dòng `Đang nén ảnh… 2,1 MB → 180 KB`.
- Upload có **thanh tiến trình và nút Huỷ**, không phải spinner vô định.
- Mất mạng giữa chừng → thẻ `Chưa gửi được — đã lưu vào máy` + nút `Thử lại`, không mất ảnh.
- Màn tra cứu lịch thu gom của toà **xem được offline** (dữ liệu tĩnh, cache lại).
- Đội vệ sinh: đánh dấu "đã thu" khi offline → xếp hàng đồng bộ, hiện huy hiệu `3 thao tác chờ đồng bộ`.

---

## 3. KHUNG LAYOUT

### 3.1 App Cư dân (mobile)

```
┌─────────────────────────────┐
│ GreenBin      S1-1203  🌙 👤│  ← header mảnh
├─────────────────────────────┤
│                             │
│        VÙNG NỘI DUNG        │
│                             │
│                             │
│         ┌─────────┐         │
│         │   📷    │         │  ← nút chụp nổi, to, luôn thấy
│         └─────────┘         │
├─────────────────────────────┤
│  Hỏi   Lịch   Yêu cầu   Tôi │  ← tab bar 4 mục
└─────────────────────────────┘
```

- **Nút chụp là trung tâm tuyệt đối của app.** Mở app ra là thấy ngay, không cần bấm gì trước.
- Tab `Yêu cầu` có badge số yêu cầu đang chờ duyệt.
- Header hiện **mã căn hộ** — vì mọi hướng dẫn đều phụ thuộc toà nhà, người dùng cần thấy mình đang xem quy định của toà nào.

### 3.2 App Đội vệ sinh (mobile/tablet)

Cùng khung với app cư dân nhưng tab bar khác: `Tuyến hôm nay · Xác nhận nhãn · Lịch sử · Tôi`.
Thêm dải trạng thái đồng bộ dính dưới header khi có thao tác chờ.

### 3.3 Console Ban quản lý (desktop)

```
┌──────────────────────────────────────────────────────────────────┐
│ [GreenBin]  Toà: [Sunrise S1 ▾]  Kỳ: [T7/2026 ▾]                 │
│                              [🔔 3]  [🌙]  [Trần Minh Đức ▾ BQL] │
├────────────────┬─────────────────────────────────────────────────┤
│ Tổng quan      │                                                  │
│ ──────────────│                                                  │
│ CẦN DUYỆT      │                                                  │
│  Thu gom    ④ │                                                  │
│  Nhãn nghi ngờ⑦│              VÙNG NỘI DUNG                       │
│  Tuyến      ② │                                                  │
│ ──────────────│                                                  │
│ Phân loại      │                                                  │
│ Thu gom & tuyến│                                                  │
│ ──────────────│                                                  │
│ Agent run      │                                                  │
│ Vận hành       │                                                  │
│ Chất lượng AI  │                                                  │
│ Danh mục & QĐ  │                                                  │
└────────────────┴─────────────────────────────────────────────────┘
```

- **Nhóm "CẦN DUYỆT" đặt trên cùng, có badge số** — đây là công việc hàng ngày của BQL và là nơi thể hiện HITL.
- Bộ lọc **Toà + Kỳ nằm trên topbar, áp dụng toàn cục**: mọi màn đều đổi theo. Người dùng luôn tư duy theo "toà nào, tháng nào".

---

## 4. ĐẶC TẢ TỪNG MÀN HÌNH

Ưu tiên: **P0 = bắt buộc cho demo** · P1 = nên có · P2 = làm nếu còn thời gian.

---

### 4.1 Đăng nhập — `P0` — chung

Màn tối giản, logo + tên + một câu mô tả: *"Chụp ảnh — biết ngay bỏ vào thùng nào."*

- Form email / mật khẩu.
- **Khối "Tài khoản demo":** 3 nút lớn theo mục 1, mỗi nút có 1 dòng mô tả quyền của vai trò đó. Bấm là vào thẳng.
- Ghi chú nhỏ dưới cùng, **bắt buộc có**:
  > *"Hệ thống demo dùng dữ liệu mô phỏng và dữ liệu công khai. Ảnh tải lên được tự động xoá thông tin vị trí và làm mờ khuôn mặt trước khi xử lý."*

---

### 4.2 Hỏi phân loại — `P0` — **MÀN CHÍNH CỦA CƯ DÂN**

Màn mặc định sau khi cư dân đăng nhập. Mục tiêu: **từ lúc mở app tới lúc có câu trả lời ≤ 10 giây.**

**Trạng thái nghỉ (mặc định):**
- Nút chụp cực to ở giữa dưới: `📷 Chụp món rác`
- Nút phụ: `🖼 Chọn ảnh có sẵn` · `✍️ Mô tả bằng chữ`
- Ô gợi ý nhanh (chip bấm được): `Hộp sữa giấy` · `Ly trà sữa` · `Pin cũ` · `Hộp xốp` · `Túi nilon` — bấm là hỏi luôn bằng chữ, không cần chụp. **Quan trọng khi demo**: không phải lúc nào cũng có sẵn rác để chụp.
- Dưới cùng: `3 câu hỏi gần đây` dạng danh sách rút gọn.

**Khi mô tả bằng chữ:** ô nhập 1 dòng + gợi ý *"VD: hộp sữa giấy có lớp bạc bên trong"*. Chấp nhận câu tiếng Việt tự nhiên.

**Trạng thái đang xử lý — phải cho thấy agent đang làm gì, không chỉ spinner:**
```
◉ Đang nén ảnh…                    ✓ 2,1 MB → 180 KB
◉ Xoá thông tin vị trí…            ✓
◉ Làm mờ khuôn mặt…                ✓ đã mờ 1 khuôn mặt
◉ Nhận diện món rác…               ⟳
○ Tra quy định của toà S1…
```
Từng dòng tích xanh dần. Đây là **màn ăn điểm về minh bạch AI** — nó cho người xem thấy quyền riêng tư được xử lý *trước khi* ảnh rời máy, không phải lời hứa suông. Trung bình 3–6 giây, đủ để đọc.

Có nút `Huỷ` suốt quá trình.

---

### 4.3 Kết quả phân loại — `P0` — cư dân

Bố cục dọc, đọc từ trên xuống, phần quan trọng nhất ở trên.

**① Khối đáp án (chiếm ~40% màn hình đầu tiên)**
```
┌─────────────────────────────────────┐
│  ♻️   TÁI CHẾ — THÙNG XANH DƯƠNG    │  ← nền màu nhóm, chữ to
│                                     │
│  Hộp sữa giấy tráng nhôm            │  ← tên món
│  [Chắc chắn 0,91]  [Đã kiểm tra kỹ] │  ← chip tin cậy + chip tầng
└─────────────────────────────────────┘
```

**② Việc cần làm trước khi bỏ** — danh sách 2–4 gạch đầu dòng ngắn, có icon:
`• Đổ hết sữa thừa` · `• Bóp dẹp hộp` · `• Không cần tách lớp bạc`
Đây là phần `handling_note` — viết như người thật nói, không như văn bản pháp quy.

**③ Bỏ ở đâu, thu gom lúc nào** — khối riêng, gắn với toà nhà cụ thể:
```
📍 Phòng rác tầng 3, toà S1 — thùng xanh dương thứ 2
🕕 Thu gom: Thứ 3, 5, 7 lúc 18:00–20:00
   Lần thu gần nhất: hôm nay 18:00 (còn 4 giờ)
```
"Còn 4 giờ" là chi tiết nhỏ nhưng làm sản phẩm sống hẳn lên.

**④ Nguồn** — 1–3 chip bấm được: `Nội quy toà S1 · mục 4.2` `Nghị định 45/2022/NĐ-CP · Điều 26`. Bấm → bottom sheet hiện **nguyên văn đoạn trích**, có nút mở toàn văn bản.
*(Kỹ thuật: đây là `advice_sources` — id các chunk RAG đã trích dẫn.)*

**⑤ Hành động tiếp** — 3 nút:
`👍 Hữu ích` / `👎 Sai rồi` (mở dialog chọn nhãn đúng — dữ liệu này chảy vào tập cải tiến và vào hàng đợi xác nhận của BQL) · `📦 Món này cồng kềnh, đặt lịch thu gom →`

**⑥ Riêng nhóm NGUY HẠI — khác hoàn toàn về mặt thị giác:**
```
┌═════════════════════════════════════┐
║ ⚠️  RÁC NGUY HẠI — KHÔNG BỎ CHUNG   ║  ← viền đôi, nền cam nhạt
║                                     ║
║ Pin lithium (pin sạc dự phòng)      ║
║                                     ║
║ ❗ KHÔNG bỏ vào thùng rác thường,   ║
║    KHÔNG vứt chung rác thực phẩm,   ║
║    KHÔNG làm thủng hay đốt.         ║
║                                     ║
║ ✓ Mang tới điểm thu pin tầng hầm B1 ║
║   hoặc đăng ký để đội vệ sinh nhận  ║
└═════════════════════════════════════┘
```
**Quy tắc kỹ thuật bắt buộc:** phần cảnh báo an toàn (`safety_warning`) là **text cố định lấy từ database**, không phải do LLM sinh. Trên UI hiện dòng nhỏ: `Cảnh báo an toàn theo danh mục chuẩn — không do AI tự viết.` Đây là câu mà người chấm sẽ để ý.

**⑦ Khi ảnh có nhiều món:** hiện lưới các món đã nhận diện, mỗi món một thẻ nhỏ với nhóm rác riêng + nút `Đây không phải rác của tôi` để loại bớt. Không gộp thành một câu trả lời chung.

---

### 4.4 "Mình chưa chắc" — `P0` — **MÀN QUAN TRỌNG NHẤT VỀ AN TOÀN**

Hiện khi `confidence < min_confidence`, ảnh mờ/thiếu sáng, hoặc món nằm trong danh sách chặn cứng (vật sắc nhọn y tế, bình gas, hoá chất).

**Đây không phải màn lỗi. Thiết kế nó như một hành vi tự tin, không phải một sự cố.** Tông màu trung tính-xanh dương, không đỏ, không có icon buồn.

```
🤔  Mình chưa đủ chắc để hướng dẫn món này

Ảnh hơi tối nên mình không đọc được nhãn.
Đoán gần nhất: có thể là chai hoá chất tẩy rửa —
nhưng nhóm này nếu hướng dẫn sai thì nguy hiểm,
nên mình không đoán bừa.

[ 📷 Chụp lại rõ hơn ]
[ 💬 Hỏi ban quản lý  ]   ← gửi vào hàng đợi HITL
[ 📖 Xem danh mục rác nguy hại ]
```

- **Vẫn hiện phỏng đoán gần nhất**, nhưng dán nhãn rõ là phỏng đoán và **không kèm hướng dẫn xử lý**.
- Có gợi ý cụ thể vì sao chưa chắc: `ảnh tối` / `vật bị che` / `nhiều món chồng lên nhau` / `nhóm nguy hại cần độ chắc cao hơn`.
- Bấm `Hỏi ban quản lý` → tạo mục trong hàng đợi 4.11, cư dân nhận thông báo khi có người trả lời. Hiện dòng `Thường được trả lời trong vòng 2 giờ làm việc.`
- Ghi `refused=True` + `refusal_reason` — con số này lên trang Chất lượng AI.

**Ghi chú cho người thiết kế:** hầu hết các nhóm khác sẽ không có màn này. Nó là bằng chứng mạnh nhất cho tiêu chí an toàn AI của đề. Đầu tư cho nó bằng với màn kết quả thành công.

---

### 4.5 Quyền riêng tư — "Ảnh của tôi đã được xử lý thế nào" — `P0` — cư dân

Mở từ màn kết quả (link nhỏ `Ảnh của bạn được xử lý thế nào?`) hoặc từ tab `Tôi`.

**Khối so sánh 2 ảnh cạnh nhau**, có thanh trượt kéo qua lại giữa `Ảnh gốc (chỉ có trên máy bạn)` và `Ảnh đã gửi cho AI`:
- Trên ảnh đã gửi: khoanh vùng khuôn mặt đã làm mờ.
- Bên dưới, bảng đối chiếu:

| Thông tin | Ảnh gốc | Đã gửi đi |
|---|---|---|
| Toạ độ GPS | 10.7769, 106.7009 | ❌ đã xoá |
| Thời gian chụp | 28/07/2026 14:22 | ❌ đã xoá |
| Model điện thoại | iPhone 13 | ❌ đã xoá |
| Khuôn mặt | 1 khuôn mặt | ✅ đã làm mờ |
| Kích thước | 3024×4032 (2,1 MB) | 512×683 (180 KB) |

- Dòng cuối: `Ảnh này sẽ tự động xoá sau 30 ngày` + nút `Xoá ngay`.
- Nút `Tải bản đã xử lý về máy`.

**Vì sao màn này đáng làm:** ảnh chụp thùng rác vô tình chứa số căn hộ, hoá đơn có tên và địa chỉ, nhãn thuốc, biển số xe — và mọi ảnh điện thoại đều mang EXIF với GPS chính xác tới mét. Màn này biến một việc backend vô hình thành bằng chứng tuân thủ nhìn thấy được.

---

### 4.6 Lịch thu gom của toà — `P1` — cư dân + đội vệ sinh

Tab `Lịch`. **Phải xem được offline.**

- Lịch tuần dạng lưới: hàng = nhóm rác, cột = thứ trong tuần, ô có màu nhóm + khung giờ.
- Khối `Sắp tới` nổi trên cùng: `Rác tái chế — hôm nay 18:00 (còn 4 giờ)`.
- Danh sách điểm tập kết trong toà, có thể xem theo tầng.
- Nút `Nhắc tôi trước 1 giờ` (P2 — chỉ cần UI, không cần push thật).

---

### 4.7 Đăng ký thu gom đồ cồng kềnh — `P0` — cư dân

Wizard 3 bước, mỗi bước một màn, có thanh tiến trình trên cùng.

**Bước 1 — Món cần thu gom**
- Danh sách món, mỗi món: ảnh (chụp/chọn) · tên · nhóm rác (AI tự điền, sửa được) · số lượng · ước lượng khối lượng.
- **AI hỗ trợ điền:** chụp ảnh → tự điền tên + nhóm + gợi ý khối lượng, kèm chip `AI ước lượng — kiểm tra lại giúp mình`. Người dùng luôn sửa được.
- Nút `+ Thêm món`.
- Tổng khối lượng ước tính hiện realtime ở dưới.

**Bước 2 — Thời gian**
- Chọn ngày (lịch, chặn ngày không có ca thu gom).
- Chọn khung giờ: các thẻ khung giờ, **thẻ nào đã có chuyến của toà thì đánh dấu**:
  `Thứ 5, 08:00–10:00  🚛 Đã có chuyến của toà S1 — chọn khung này giúp tiết kiệm 1 chuyến xe`
  Đây là chỗ **giá trị kinh doanh của agent hiện ra trước mắt người dùng**, đừng bỏ.
- Ghi chú thêm (text tự do).

**Bước 3 — Xác nhận**
- Tóm tắt toàn bộ.
- **Nếu vượt ngưỡng → hiện rõ ngay tại đây, trước khi bấm gửi:**
  > ⏳ Yêu cầu này có tổng khối lượng **48 kg**, vượt ngưỡng tự động (30 kg), nên cần **ban quản lý duyệt** trước khi lên lịch. Bạn sẽ nhận thông báo trong vòng 1 ngày làm việc.

  Nói ngưỡng bằng con số cụ thể. Người dùng phải hiểu vì sao mình phải chờ.
- Checkbox: *"Tôi xác nhận các món trên không chứa rác nguy hại (pin, hoá chất, bóng đèn, thuốc)."* — bắt buộc tick. Nếu ở bước 1 AI đã nhận diện có món nguy hại → khoá checkbox và chuyển sang luồng riêng.
- Nút `Gửi yêu cầu`.

**Sau khi gửi:** màn xác nhận có mã yêu cầu `#PR-2026-0147`, trạng thái hiện tại, và các bước tiếp theo dạng timeline.

---

### 4.8 Yêu cầu của tôi — `P0` — cư dân

Danh sách các yêu cầu, mỗi thẻ: mã · các món (thu gọn) · khối lượng · ngày mong muốn · **badge trạng thái** · thời điểm cập nhật cuối.

**Chi tiết một yêu cầu — timeline dọc, đây là nơi HITL hiện ra với người dùng cuối:**
```
✅ 28/07 14:20  Đã gửi yêu cầu
✅ 28/07 14:20  Hệ thống kiểm tra — vượt ngưỡng 30 kg, cần duyệt
✅ 28/07 16:45  Ban quản lý đã duyệt — Trần Minh Đức
✅ 28/07 16:50  Đã xếp vào chuyến sáng thứ 5 cùng 3 hộ khác
⏳ 30/07 08:00  Dự kiến thu gom
```
- Nếu bị từ chối: hiện **lý do cụ thể** (từ danh sách cố định) + gợi ý hành động (`Chia nhỏ thành 2 đợt` / `Đổi sang khung giờ khác`) + nút `Tạo lại yêu cầu`.
- Nếu đã xếp tuyến: hiện `Đi cùng chuyến với 3 hộ khác trong toà — giảm 2 chuyến xe`. Cho cư dân thấy mình đang góp phần vào việc tốt.
- Nút `Huỷ yêu cầu` (chỉ khi chưa `scheduled`).

---

### 4.9 Tuyến hôm nay — `P0` — đội vệ sinh

Màn mặc định của đội vệ sinh. Thiết kế cho **một tay, đeo găng, ngoài nắng**.

**Đầu màn:** `Chuyến sáng · Thứ 5, 30/07 · 08:00–10:00` · `5 điểm dừng · 142 kg · ~4,2 km` · thanh tiến trình `2/5 đã thu`.

**Danh sách điểm dừng theo thứ tự**, mỗi thẻ cao ~120px:
```
┌───────────────────────────────────┐
│ ② Toà S1 — căn 1203        38 kg  │
│    Nguyễn Thị Lan · 0901•••456    │
│    📦 1 tủ gỗ, 2 thùng carton      │
│    ┌─────────────┐ ┌────────────┐ │
│    │ ✓ ĐÃ THU    │ │ ⚠ Báo lỗi  │ │  ← nút cao 48px
│    └─────────────┘ └────────────┘ │
└───────────────────────────────────┘
```
- **Số điện thoại che một phần**, bấm mới hiện đầy đủ + gọi (hành động này ghi audit log).
- `Báo lỗi` mở bảng chọn nhanh: `Không có người` · `Khối lượng khác dự kiến` · `Có rác nguy hại lẫn vào` · `Không tiếp cận được` · `Khác`. Chọn `Có rác nguy hại` → cảnh báo an toàn hiện lên ngay và tạo cảnh báo cho BQL.
- Nút `📍 Mở bản đồ` cho toàn tuyến (P2 — có thể chỉ là ảnh tĩnh khi demo).
- Khi xong hết: màn tổng kết chuyến `5/5 điểm · 142 kg · 2 giờ 10 phút`.

---

### 4.10 Duyệt yêu cầu thu gom — `P0` — BQL — **HITL #1**

Bố cục 2 cột: trái hàng đợi, phải chi tiết. Đây là màn BQL dùng hàng ngày.

**Cột trái — hàng đợi:** lọc theo trạng thái (`chờ duyệt / đã duyệt / đã từ chối / tất cả`), sắp xếp theo thời gian hoặc khối lượng. Mỗi thẻ: mã · toà + căn · khối lượng · ngày mong muốn · thời gian chờ (`đã chờ 3 giờ` — chuyển cam sau 24 giờ).

**Cột phải — chi tiết:**

**① Đầu khối:** badge `CHỜ DUYỆT` · mã · cư dân + căn hộ · thời điểm gửi.

**② Vì sao yêu cầu này cần duyệt** — khối nền xám, nói rõ luật đã kích hoạt:
```
Khối lượng ước tính:  48 kg   (ngưỡng tự động: 30 kg)  ⚠ vượt
Số món:               5       (ngưỡng: 3)              ⚠ vượt
Có món nghi nguy hại: Không
```
**Bắt buộc hiển thị ngưỡng.** Một hàng đợi duyệt mà không nói vì sao mục này rơi vào đây là hàng đợi vô nghĩa.

**③ Danh sách món** — lưới ảnh + tên + nhóm rác + khối lượng. Ảnh bấm được để phóng to. Mỗi món có chip nhóm; món nào AI phân loại với độ tin cậy thấp thì đánh dấu.

**④ Bối cảnh ra quyết định** — dữ liệu do SQL tính, không phải LLM:
```
Cư dân này: 4 yêu cầu trước, 4 lần đúng hẹn, 0 lần huỷ
Toà S1 tuần này: 12 yêu cầu, tổng 310 kg
Ngày mong muốn (30/07): đã có 1 chuyến, còn trống ~85 kg
```

**⑤ Đề xuất của agent** — khối viền nét đứt, nhãn `AI đề xuất`:
> Gộp vào chuyến sáng thứ 5 (08:00–10:00) cùng 3 yêu cầu khác của toà S1.
> Ước tính: tiết kiệm 1 chuyến xe, ~6 km.

**Thanh hành động (dính dưới):**

| Nút | Hành vi |
|---|---|
| ✅ **Duyệt** | → `approved`, đưa vào nhóm chờ xếp tuyến. Toast + **nút Hoàn tác trong 10 giây**. |
| 📝 **Duyệt kèm điều chỉnh** | sửa ngày/khung giờ/khối lượng rồi duyệt, ghi chú gửi cho cư dân. |
| ❌ **Từ chối** | **bắt buộc chọn lý do** từ danh sách cố định: `Vượt năng lực xử lý trong ngày` · `Có rác nguy hại cần quy trình riêng` · `Thông tin không đủ` · `Trùng với yêu cầu đã có` · `Sai địa chỉ/căn hộ` · `Khác (ghi rõ)`. |

**Vì sao lý do từ chối phải chọn từ danh sách:** nó chảy ngược vào tập cải tiến và lên biểu đồ ở trang Chất lượng AI (PLO 7). Cho gõ tự do là mất dữ liệu.

**Điều hướng bàn phím:** `J`/`K` chuyển mục · `A` duyệt · `R` từ chối · `?` hiện bảng phím tắt. Chi tiết nhỏ, gây ấn tượng mạnh khi demo.

---

### 4.11 Xác nhận nhãn nghi ngờ — `P0` — BQL + đội vệ sinh — **HITL #2**

Hàng đợi các lần phân loại mà hệ thống **đã từ chối trả lời** hoặc cư dân bấm `👎 Sai rồi`.

**Bố cục:** lưới thẻ hoặc danh sách 2 cột.

Mỗi mục hiện:
- Ảnh đã xử lý (nút `Xem ảnh gốc` — chỉ BQL, có dialog xác nhận và ghi log).
- Câu hỏi của cư dân nếu là dạng chữ.
- `AI đoán: chai hoá chất tẩy rửa · 0,52` — kèm chip `Dưới ngưỡng 0,80 của nhóm nguy hại`.
- Lý do từ chối: `ảnh tối` / `nghi nguy hại` / `nhiều vật`.
- **Hành động:** chọn nhãn đúng từ danh mục (ô tìm kiếm + danh sách nhóm) → `Xác nhận và trả lời cư dân`. Có ô soạn câu trả lời, **điền sẵn `handling_note` chuẩn của nhóm được chọn** để người duyệt chỉ cần sửa nhẹ.
- Nút phụ: `Không xác định được — yêu cầu chụp lại`.

**Khối "Ca khó" ghim trên cùng** — các cặp nhãn hay bị nhầm, lấy từ eval:
`Hộp sữa giấy tráng nhôm ↔ Giấy` · `Ly nhựa có màng ↔ Nhựa tái chế` · `Khay cơm dính dầu ↔ Rác thực phẩm`
Người duyệt biết trước chỗ dễ sai thì duyệt chính xác hơn.

Mỗi lần xác nhận ghi vào `human_label_id` + `verified_by` — đây là nguồn dữ liệu cho eval và vòng lặp cải tiến.

---

### 4.12 Duyệt tuyến gộp — `P0` — BQL — **HITL #3, MÀN ĂN ĐIỂM CAO NHẤT**

Đây là màn thể hiện đủ một lúc: agent có tool-use và trạng thái · HITL cho hành động rủi ro · giá trị kinh doanh đo được. **Nếu buộc phải cắt bớt màn, giữ màn này bằng mọi giá.**

**Nguyên tắc:** agent **không được tự đổi lịch làm việc của con người**. Tuyến do agent gộp luôn ở trạng thái `proposed` cho tới khi đội trưởng bấm duyệt.

**Bố cục 3 phần:**

**① Đầu màn — tuyến được đề xuất**
```
┌──────────────────────────────────────────────────────────┐
│ [AI ĐỀ XUẤT — CHỜ DUYỆT]   Chuyến sáng · Thứ 5, 30/07    │
│ 5 điểm dừng · 142 kg · ~4,2 km · ước tính 2 giờ          │
│ Đội: Tổ vệ sinh ca sáng (Lê Văn Hùng)                    │
└──────────────────────────────────────────────────────────┘
```

**② Thân màn — hai cột**

*Cột trái: danh sách điểm dừng, kéo thả đổi thứ tự được.* Mỗi điểm: số thứ tự · toà + căn · khối lượng · các món · nút `✕ Bỏ khỏi tuyến`. Kéo thả xong hiện `Đã đổi thứ tự — quãng đường ước tính 4,2 → 4,6 km` ngay lập tức.

*Cột phải: khối "Vì sao gộp thế này" — nhãn `AI giải thích`:*
```
Tiêu chí gộp:
• Cùng toà S1 và S2 (cách nhau 300 m)
• Cùng khung giờ mong muốn 08:00–10:00
• Tổng 142 kg — trong tải trọng 200 kg của xe
• 2 yêu cầu ngày 30/07 của toà S3 KHÔNG gộp
  vì lệch khung giờ (14:00–16:00) → xếp chuyến chiều

So với đi lẻ từng yêu cầu:
  5 chuyến → 1 chuyến
  ~18 km  → ~4,2 km   (giảm 77%)
```
**Khối này quan trọng bằng chính cái tuyến.** Người duyệt phải hiểu logic mới dám duyệt, và người chấm thấy được agent có suy luận chứ không phải gom bừa.

Kèm sơ đồ tuyến đơn giản (các điểm nối bằng đường, đánh số) — không cần bản đồ thật, hình minh hoạ là đủ.

**③ Thanh hành động**

| Nút | Hành vi |
|---|---|
| ✅ **Duyệt tuyến** | → `approved`, đẩy sang app đội vệ sinh, thông báo cho từng cư dân. |
| ✏️ **Sửa rồi duyệt** | sau khi kéo thả/bỏ điểm — **hiện diff giữa bản AI đề xuất và bản đã sửa** trước khi chốt. Phần diff này rất đáng giá khi demo. |
| 🔄 **Đề xuất lại** | chạy lại agent với ràng buộc mới (đổi ngày, đổi đội, giới hạn tải trọng). |
| ❌ **Huỷ tuyến** | các yêu cầu quay về nhóm chờ xếp tuyến. |

**Sau khi duyệt:** toast + dòng `Đã thông báo cho 5 cư dân và tổ vệ sinh ca sáng.`

---

### 4.13 Tổng quan BQL — `P0`

Màn mặc định của BQL. Trả lời trong 10 giây: *"Hôm nay có gì cần tôi xử lý?"*

**Khối 1 — Dải cảnh báo (chỉ hiện khi có):**
`🔴 Đội vệ sinh báo có rác nguy hại lẫn trong yêu cầu #PR-0147 tại S1-1203` + nút `Xem` / `Đã xử lý`.

**Khối 2 — 4 thẻ KPI, mỗi thẻ bấm được:**

| Thẻ | Nội dung | Phụ chú |
|---|---|---|
| Cần duyệt | `13` | `4 thu gom · 7 nhãn · 2 tuyến` + nút `Duyệt ngay →` |
| Lượt phân loại tuần này | `1.284` | `+18% so với tuần trước` + sparkline |
| Độ chính xác (có người xác nhận) | `91,4%` | `trên 213 ca đã xác nhận` |
| **Rác nguy hại bị bỏ sót** | `0` | `mục tiêu 0 — trên 213 ca` |

Thẻ thứ 4 là **chỉ số an toàn cốt lõi của đề**. Nó phải nằm ở tổng quan, không giấu trong trang eval. Nếu > 0 thì cả thẻ chuyển đỏ.

**Khối 3 — Phân bố nhóm rác trong tuần:** thanh ngang xếp chồng theo nhóm, kèm % và xu hướng.

**Khối 4 — Hiệu quả điều phối:** `12 yêu cầu → 4 chuyến · giảm 8 chuyến xe · ~46 km tiết kiệm trong tuần`. Đây là câu chuyện kinh doanh, để nó ở nơi dễ thấy.

**Khối 5 — Hoạt động gần đây:** dòng thời gian rút gọn các sự kiện (duyệt, từ chối, tuyến chốt, cảnh báo).

**Trạng thái rỗng:** minh hoạ nhẹ + `Chưa có yêu cầu nào cần duyệt hôm nay 🎉`.

---

### 4.14 Lịch sử phân loại — `P1` — BQL

Bảng dữ liệu dày, tối ưu cho tra cứu và tìm ca sai.

**Thanh lọc (dính trên):** tìm kiếm · toà · nhóm rác · tầng model (`T0/T1/T2`) · khoảng tin cậy (thanh trượt) · `chỉ hiện ca bị từ chối` · `chỉ hiện ca có người xác nhận` · `chỉ hiện ca AI sai` · khoảng thời gian.

**Cột bảng:**

| Cột | Nội dung |
|---|---|
| Thời gian | `28/07 14:22` |
| Ảnh | thumbnail nhỏ (ảnh đã xử lý) |
| Đầu vào | ảnh / chữ (hiện câu hỏi rút gọn) |
| AI đoán | chip nhóm + độ tin cậy |
| Nhãn người xác nhận | chip nhóm, rỗng nếu chưa xác nhận |
| Kết quả | ✅ đúng / ❌ sai / ⏸ từ chối / — chưa xác nhận |
| Tầng | `T0` / `T1` / `T2` |
| Độ trễ | `1.240 ms` |
| Chi phí | `$0,0021` |

**Hàng mở rộng được:** ảnh lớn (có nút xem ảnh gốc — ghi log), toàn văn hướng dẫn đã trả, các nguồn đã trích dẫn, `prompt_version`, `model`, lý do escalate lên T2 nếu có, link `Agent run #...`.

**Trạng thái:** loading = skeleton rows · rỗng sau lọc = "Không có kết quả khớp bộ lọc" + nút xoá lọc · lỗi = thông báo + nút thử lại.

---

### 4.15 Agent Run / Trace — `P1` — BQL

Màn chứng minh "workflow agentic có trạng thái, tool-use, trace và debug được" — yêu cầu tối thiểu của chương trình, đừng bỏ.

**Danh sách các lần chạy:** `ID · thời điểm · loại (classify / schedule / batch_eval) · trigger · số mục · trạng thái · thời gian · chi phí`.

**Chi tiết một lần chạy — timeline dọc các node:**
```
● preprocess_image   ✅  EXIF sạch, 1 mặt đã mờ    340 ms   $0
│                        2,1 MB → 180 KB
● cache_lookup       ⚡  trượt cache (pHash)        12 ms   $0
│
● classify_waste     ✅  T1 gpt-4o-mini            1.180 ms  $0,0018
│                        conf 0,62 < ngưỡng 0,80 nhóm nguy hại
│                        ⚠ escalate → T2
● classify_waste_t2  ✅  T2 gpt-4o                 2.240 ms  $0,0121
│                        conf 0,91 → chấp nhận
● safety_check       ✅  không thuộc danh sách chặn   8 ms   $0
│
● advise (RAG)       ✅  truy hồi 5 chunk, dùng 2   410 ms  $0,0004
│                        lọc theo building_id = S1
● schedule_pickup    ⏭  bỏ qua (không phải đồ cồng kềnh)
```

Bấm vào node → panel phải hiện: state vào, state ra, prompt đã dùng (rút gọn + nút xem đầy đủ), tokens in/out/image, số lần thử lại, lỗi nếu có.

Kèm **sơ đồ graph LangGraph** (node + cạnh), đường đã đi tô đậm, nhánh không đi để mờ. Node đang chạy nhấp nháy nhẹ khi chạy live.

**Bắt buộc thấy được trên màn này:** điều kiện escalate T1→T2, và **cache hit tiết kiệm bao nhiêu**. Đó là hai thứ chứng minh kiến trúc 3 tầng có thật.

---

### 4.16 Vận hành & Chi phí — `P0` — BQL

Chương trình yêu cầu theo dõi tối thiểu **độ trễ, lỗi, chi phí**. Ba khối tương ứng.

**Khối Chi phí**
- Thẻ lớn: `Chi phí tháng này: $3,42` · `4.180 lượt phân loại` · `$0,82 / 1.000 lượt`
- Biểu đồ cột theo ngày, chia màu theo tầng (T0 / T1 / T2).
- **Bảng so sánh 3 tầng — đây tự nó là một slide demo:**

| Tầng | Tỉ lệ lượt | Độ chính xác | Chi phí/ảnh | Độ trễ p95 |
|---|---|---|---|---|
| T0 — cache pHash | 22% | 100%* | $0 | 15 ms |
| T1 — gpt-4o-mini | 63% | 88,2% | $0,0018 | 1,4 s |
| T2 — gpt-4o | 15% | 96,7% | $0,0121 | 2,8 s |

  *\*bằng độ chính xác của lần phân loại gốc đã cache.*
- **Thẻ so sánh nổi bật:** `Định tuyến 3 tầng: $3,42` vs `Nếu dùng gpt-4o cho mọi ảnh: $50,58` → **`Tiết kiệm 93%`**
- Thanh ngân sách: `$3,42 / $25,00` + cảnh báo khi vượt 80%.
- Tỉ lệ cache hit và tỉ lệ escalate lên T2, kèm xu hướng.

**Khối Độ trễ**
- p50 / p95 mỗi node, dạng bar ngang.
- Độ trễ theo thời gian, đánh dấu các spike.
- **Thời gian từ lúc chụp tới lúc có câu trả lời** (p50/p95) — chỉ số người dùng thật sự cảm nhận, quan trọng hơn độ trễ từng node.

**Khối Lỗi & Giới hạn**
- Tỉ lệ lỗi theo node · 10 lỗi gần nhất (thời điểm, node, loại, số lần thử lại).
- Số lần chạm rate limit.
- **Khối "Giới hạn đã biết của hệ thống"** — text cứng, luôn hiển thị:
  > • Nhận diện tốt nhất với **một món rác, chụp rõ, đủ sáng**. Ảnh nhiều món chồng lên nhau có độ chính xác thấp hơn đáng kể.
  > • Không phân biệt được **nhựa PET và nhựa HDPE** khi nhãn bị mờ hoặc mất.
  > • **Không xác định được rác y tế lây nhiễm** — luôn chuyển người, không tự trả lời.
  > • Quy định phân loại **khác nhau giữa các toà**; hướng dẫn chỉ đúng với toà đang chọn.
  > • Khối lượng do AI ước lượng có sai số lớn (±40%) — chỉ dùng để gợi ý, đội vệ sinh cân lại tại chỗ.
  > • Dữ liệu demo là dữ liệu mô phỏng và ảnh tự chụp, **không phải dữ liệu cư dân thật**.

Khối cuối này đáp thẳng yêu cầu "nêu rõ giới hạn, rủi ro" — và rất ít nhóm nghĩ tới việc đưa nó lên UI thay vì giấu trong báo cáo.

---

### 4.17 Chất lượng AI / Eval — `P1` — BQL

- **Thẻ chỉ số an toàn đặt to nhất, trên cùng:**
  ```
  ┌────────────────────────────────────────┐
  │  RÁC NGUY HẠI BỊ PHÂN LOẠI THÀNH       │
  │  RÁC THƯỜNG                            │
  │              0 / 68                    │
  │           mục tiêu: 0                  │
  └────────────────────────────────────────┘
  ```
- Bảng metrics: `accuracy` · `macro-F1` · `recall nhóm nguy hại` · `precision@5 của retrieval`, kèm cỡ tập test và ngày chạy.
- **Tách riêng hai bộ dữ liệu** — bảng 2 cột `Dataset công khai (TrashNet/TACO)` vs `Ảnh tự chụp tại VN`. Chênh lệch giữa hai cột là một phát hiện đáng nói, thiết kế cho nó chỗ đứng riêng.
- **Ma trận nhầm lẫn** — heatmap, bấm ô để xem các ảnh bị nhầm ở cặp đó.
- **Thư viện failure case** — lưới ảnh: ảnh · nhãn đúng · AI đoán · độ tin cậy · phân loại nguyên nhân (`ảnh tối` / `nhiều vật` / `vật bị che` / `chất liệu hỗn hợp` / `góc chụp lạ`) · trạng thái đã xử lý.
  Đây là **lợi thế demo lớn nhất của đề này**: trình chiếu được ảnh thật bị nhận sai. Thiết kế lưới này cho đẹp, nó sẽ lên slide.
- **Bảng so sánh phiên bản prompt:** `v1 / v2 / v3` × `macro-F1 · recall nguy hại · chi phí/ảnh · độ trễ p95`.
- Biểu đồ tỉ lệ từ chối trả lời theo thời gian — quá cao thì phiền người dùng, quá thấp thì rủi ro. Vẽ cả hai ngưỡng.

---

### 4.18 Danh mục rác & Kho quy định — `P2` — BQL

Hai tab.

**Tab "Danh mục rác":** bảng các nhóm — `mã · tên · nhóm cha · nguy hại? · ngưỡng tin cậy · màu thùng · hướng dẫn xử lý · cảnh báo an toàn`.
Sửa được. Khi sửa `min_confidence` của nhóm nguy hại → hiện cảnh báo: `Hạ ngưỡng làm tăng rủi ro hướng dẫn sai cho nhóm nguy hại. Bạn chắc chứ?`

**Tab "Kho quy định":** danh sách tài liệu — `tiêu đề · loại (luật / nội quy toà / lịch thu gom / danh mục nguy hại) · toà áp dụng · ngày hiệu lực · số đoạn đã cắt`.
Upload tài liệu mới → hiện preview các đoạn đã cắt. Có ô `Thử truy hồi` để gõ câu hỏi và xem hệ thống lấy ra đoạn nào — công cụ debug RAG nhìn thấy được.

---

## 5. THƯ VIỆN COMPONENT

| Component | Mô tả | Dùng ở |
|---|---|---|
| `WasteCategoryBadge` | icon + tên nhóm + màu thùng, 5 nhóm; biến thể `hazardous` khác hẳn | khắp nơi |
| `ConfidenceChip` | 3 mức theo mục 2.4, tooltip giải thích ngưỡng của nhóm | kết quả, bảng, hàng đợi |
| `TierChip` | T0/T1/T2, hai biến thể (cư dân / kỹ thuật) | kết quả, bảng, ops |
| `SourceChip` | chip nguồn quy định, bấm mở nguyên văn đoạn trích | kết quả, hướng dẫn |
| `SafetyWarningBlock` | khối cảnh báo nguy hại viền đôi + nhãn "không do AI sinh" | kết quả, xác nhận nhãn |
| `RefusalCard` | màn/khối "Mình chưa chắc" + lý do + 3 lối ra | 4.4 |
| `PrivacyDiff` | so sánh ảnh gốc / ảnh đã xử lý + bảng metadata đã xoá | 4.5 |
| `ProcessingSteps` | danh sách bước xử lý tích dần | 4.2 |
| `RequestStatusBadge` | 6 trạng thái yêu cầu thu gom | khắp nơi |
| `RequestTimeline` | timeline trạng thái yêu cầu, có mốc HITL | 4.8, 4.10 |
| `ThresholdExplainer` | khối "vì sao mục này cần duyệt" + con số ngưỡng | 4.10, 4.7 bước 3 |
| `RouteStopCard` | thẻ điểm dừng, nút to cho đội vệ sinh | 4.9, 4.12 |
| `AgentReasoningBlock` | khối viền nét đứt nhãn "AI đề xuất / AI giải thích" | 4.10, 4.12 |
| `NodeTimelineItem` | 1 dòng trace: icon, tên node, số liệu, thời gian, chi phí | 4.15 |
| `CostMeter` | thanh ngân sách + ngưỡng cảnh báo | 4.16 |
| `SafetyMetricCard` | thẻ chỉ số an toàn cỡ lớn, 0 = xanh, >0 = đỏ | 4.13, 4.17 |
| `FailureCaseCard` | ảnh + nhãn đúng + nhãn AI + nguyên nhân | 4.17 |
| `LimitationNote` | khối giới hạn hệ thống, nền vàng nhạt | 4.16, kết quả |
| `EmptyState` | icon + giải thích + hành động gợi ý | mọi bảng |
| `ErrorState` | câu tiếng Việt dễ hiểu + nút thử lại + mã lỗi ngắn | mọi màn |
| `OfflineBanner` | dải trạng thái mạng + số thao tác chờ đồng bộ | app mobile |

---

## 6. BỐN TRẠNG THÁI BẮT BUỘC CHO MỌI MÀN

Thiết kế thiếu bốn trạng thái này là thiết kế chưa xong.

1. **Loading** — skeleton đúng hình dạng nội dung thật. Không spinner giữa màn. Riêng màn phân loại dùng `ProcessingSteps` (4.2) vì thời gian chờ dài và có nội dung đáng khoe.
2. **Rỗng** — phân biệt *chưa có dữ liệu bao giờ* (kèm hướng dẫn bắt đầu) và *không có kết quả sau khi lọc* (kèm nút xoá lọc).
3. **Lỗi** — tiếng Việt dễ hiểu, không hiện stack trace, có nút thử lại và mã lỗi ngắn để đối chiếu log. Ví dụ: `Không kết nối được tới máy chủ. Ảnh của bạn vẫn được lưu trên máy. [Thử lại]  (mã: NET-503)`
4. **Suy giảm một phần** — pipeline chạy xong nhưng một node lỗi. Vẫn hiện phần làm được, kèm băng cảnh báo:
   `Đã nhận diện được món rác nhưng chưa tra được quy định của toà S1. Hướng dẫn dưới đây là hướng dẫn chung, có thể khác quy định riêng của toà bạn.`

Trạng thái số 4 hiếm nhóm nào làm, và nó chính là "xử lý lỗi và cảnh báo giới hạn hệ thống" mà chương trình yêu cầu.

---

## 7. HỢP ĐỒNG DỮ LIỆU (API)

Khớp với schema ở `src/db/models.py`. Frontend cứ code theo hợp đồng này, backend sẽ khớp vào.

```
POST /api/v1/auth/login                    → {token, user:{id, full_name, role, unit, building}}

# Phân loại
POST /api/v1/classify                      body: multipart(image) hoặc {text_query}, building_id
                                           → {classification_id, media_id, category:{code,name,bin_color,
                                              is_hazardous,handling_note,safety_warning},
                                              confidence, min_confidence, tier, model,
                                              refused, refusal_reason, items[]?,
                                              advice, advice_sources[{doc_title,section,quote,doc_id}],
                                              latency_ms, cost_usd, run_id}
GET  /api/v1/classifications?filters&page  → {items[], total, page_size}
GET  /api/v1/classifications/{id}          → {…đầy đủ + prompt_version, escalation_reason}
POST /api/v1/classifications/{id}/feedback body: {is_correct, suggested_category_code?}
POST /api/v1/classifications/{id}/verify   body: {category_code, reply_text}   (cleaner|manager)

# Ảnh & quyền riêng tư
GET  /api/v1/media/{id}                    → ảnh đã xử lý (kiểm tra quyền)
GET  /api/v1/media/{id}/privacy            → {exif_stripped, removed_fields[], faces_blurred,
                                              original_size, processed_size, expires_at}
GET  /api/v1/media/{id}/original           → ảnh gốc (manager, ghi audit log)
DELETE /api/v1/media/{id}                  → xoá ngay theo yêu cầu cư dân

# Danh mục & kho quy định
GET  /api/v1/categories                    → [{code,name,parent_code,is_hazardous,min_confidence,
                                               bin_color,handling_note,safety_warning}]
GET  /api/v1/buildings/{id}/schedule       → [{category_code, weekdays[], window, location}]
GET  /api/v1/knowledge?building_id&type    → [{id,title,doc_type,effective_date,chunk_count}]
GET  /api/v1/knowledge/chunks/{id}         → {content, section, doc:{title,source}}

# Thu gom
POST /api/v1/pickups                       body: {items[{name,category_code,qty,media_id}],
                                                  est_weight_kg, preferred_date, preferred_window, note}
                                           → {id, status, requires_hitl, threshold_hit[]}
GET  /api/v1/pickups?status&building&page  → {items[], total}
GET  /api/v1/pickups/{id}                  → {…, timeline[], resident_history, capacity_context,
                                              agent_suggestion}
POST /api/v1/pickups/{id}/review           body: {action: approve|approve_with_changes|reject,
                                                  reason?, note?, changes?}
DELETE /api/v1/pickups/{id}                → huỷ (cư dân, chỉ khi chưa scheduled)

# Tuyến
POST /api/v1/routes/propose                body: {service_date, window, constraints?} → {route}
GET  /api/v1/routes?date&status            → [{id,service_date,window,status,total_weight_kg,
                                                est_distance_km,stop_count,team}]
GET  /api/v1/routes/{id}                   → {…, stops[{seq,request_id,unit,weight,items,done_at}],
                                              reasoning{criteria[], excluded[], baseline_km, saved_km}}
POST /api/v1/routes/{id}/review            body: {action: approve|approve_with_changes|regenerate|cancel,
                                                  stop_order?[], removed_stops?[]}
POST /api/v1/routes/{id}/stops/{sid}/done  body: {issue?: string}   (cleaner)

# Vận hành / eval / trace
GET  /api/v1/runs                          → [{id,kind,trigger,status,items_processed,
                                                duration_ms,total_cost_usd,started_at}]
GET  /api/v1/runs/{id}                     → {nodes[{node,status,duration_ms,tokens_in,tokens_out,
                                                image_tokens,cost_usd,cache_hits,llm_calls,
                                                retries,error_type,meta}]}
GET  /api/v1/ops/metrics?from&to           → {cost{total,by_tier[],by_day[],baseline_full_model},
                                              latency{p50,p95,by_node[],end_to_end},
                                              errors{rate,by_node[],recent[]},
                                              budget{used,limit}, cache_hit_rate, escalation_rate}
GET  /api/v1/eval/summary                  → {accuracy, macro_f1, hazard_recall, hazard_missed_count,
                                              test_size, by_dataset{public,own}, confusion_matrix,
                                              retrieval_precision_at_5, versions[], failures[]}
GET  /api/v1/alerts                        → [{id,severity,title,building,triggered_at,threshold,ack}]
```

**Khuôn lỗi thống nhất:** `{error: {code, message_vi, detail?}}` — frontend hiện `message_vi` cho người dùng và `code` ở góc để đối chiếu log.

---

## 8. KỊCH BẢN DEMO — UI PHẢI ĐI TRỌN 7 BƯỚC

Video demo ≤5 phút. Thiết kế phải hỗ trợ đúng mạch này, không thiếu màn nào.

1. **Cư dân** mở app → chụp **hộp sữa giấy tráng nhôm** → thấy các bước xử lý quyền riêng tư tích dần → kết quả `Tái chế · thùng xanh dương · 0,91` kèm nguồn `Nội quy toà S1 mục 4.2` → mở màn quyền riêng tư, thấy GPS đã bị xoá và 1 khuôn mặt đã làm mờ.
2. **Cư dân** chụp tiếp **cục pin lithium** → khối cảnh báo nguy hại đỏ cam, chữ to, `Cảnh báo an toàn theo danh mục chuẩn — không do AI tự viết`.
3. **Cư dân** chụp **chai hoá chất, ảnh tối** → hệ thống **từ chối trả lời**: `Mình chưa đủ chắc` → bấm `Hỏi ban quản lý`. *(Đây là khoảnh khắc mạnh nhất của bài demo — đừng để nó trôi nhanh.)*
4. **Cư dân** đăng ký thu gom **48 kg đồ cồng kềnh** → màn xác nhận nói rõ *vượt ngưỡng 30 kg, cần BQL duyệt*.
5. Đổi sang **Ban quản lý** → hàng đợi `4 thu gom · 7 nhãn · 2 tuyến` → duyệt yêu cầu 48 kg (thấy rõ ngưỡng đã kích hoạt) → xử lý ca chai hoá chất ở bước 3, chọn nhãn đúng và trả lời cư dân.
6. **Ban quản lý** mở **Duyệt tuyến** → agent đề xuất gộp 5 yêu cầu thành 1 chuyến, giải thích tiêu chí gộp và `5 chuyến → 1 chuyến, giảm 77% quãng đường` → kéo bỏ 1 điểm → xem diff → duyệt.
7. **Ban quản lý** mở **Vận hành**: `$3,42 vs $50,58 nếu dùng model lớn toàn bộ — tiết kiệm 93%`, bảng so sánh 3 tầng, và đọc khối **Giới hạn đã biết**. Ghé **Chất lượng AI** xem thẻ `Rác nguy hại bị bỏ sót: 0/68` và lưới failure case.

**Kịch bản lỗi (chương trình yêu cầu demo cả tình huống lỗi) — chọn 1 trong 2:**
- Mất mạng giữa lúc upload → `Chưa gửi được — đã lưu vào máy` → bật lại mạng → `Thử lại` thành công, không mất ảnh.
- Node `advise` lỗi → vẫn hiện nhóm rác nhận diện được kèm băng cảnh báo suy giảm một phần (mục 6 trạng thái 4).

Bảy bước này chạm đủ: 3 vai trò · workflow agentic có trạng thái và tool-use · **cả 3 điểm HITL** · quyền riêng tư ảnh · từ chối trả lời an toàn · định tuyến 3 tầng · theo dõi độ trễ/lỗi/chi phí · eval và failure case · nêu rõ giới hạn.

---

## 9. ĐỐI CHIẾU VỚI TIÊU CHÍ CHẤM

| Yêu cầu chương trình | Màn hình chứng minh |
|---|---|
| Web deploy online, ≥2 vai trò | 4.1 + ma trận quyền mục 1 (3 vai trò) |
| Workflow agentic có trạng thái, tool-use, trace được | 4.15 Agent Run |
| HITL cho hành động rủi ro | 4.10 + 4.11 + 4.12 (ba điểm HITL) |
| Xử lý lỗi, cảnh báo giới hạn hệ thống | mục 6 (4 trạng thái) + 4.16 khối Giới hạn + 2.5 mạng kém |
| Dữ liệu công khai/mô phỏng/ẩn danh | 4.5 Quyền riêng tư + ghi chú ở 4.1 |
| Theo dõi độ trễ, lỗi, chi phí | 4.16 Vận hành |
| Eval/benchmark, phân tích failure case | 4.17 Chất lượng AI |
| PLO 1 — kiến trúc agent, model routing | 2.4 TierChip + 4.15 escalate + 4.16 bảng 3 tầng |
| PLO 2 — multi-agent, trace được | 4.15 |
| PLO 3 — RAG vượt naive, có đo lường | 4.3 khối nguồn + 4.18 thử truy hồi + 4.17 precision@5 |
| PLO 4 — giá trị kinh doanh | 4.13 khối hiệu quả điều phối + 4.12 giảm 77% quãng đường |
| PLO 5 — hạ tầng, giám sát | 4.16 |
| PLO 6 — guardrails, HITL, chống rò rỉ dữ liệu | 4.4 từ chối trả lời + 4.5 quyền riêng tư + 4.3 cảnh báo cố định |
| PLO 7 — eval pipeline, failure → cải tiến | 4.17 + lý do từ chối cố định ở 4.10 + `👎 Sai rồi` ở 4.3 |
| **Ràng buộc gốc của đề** | |
| HITL cho thu gom khối lượng lớn | 4.10 |
| Bảo mật thông tin và ảnh cư dân | 4.5 + che SĐT ở 4.9 + audit log khi xem ảnh gốc |
| Chính xác trong phân loại | 4.4 + ngưỡng riêng nhóm nguy hại + 4.17 |
| Tối ưu chi phí vận chuyển và lịch thu | 4.12 + 4.7 bước 2 (gợi ý khung giờ đã có chuyến) |

---

## 10. THỨ TỰ LÀM (khi chỉ có một người)

**Đợt 1 — đủ để demo (làm trước):**
4.1 Đăng nhập · 4.2 Hỏi phân loại · 4.3 Kết quả · **4.4 Mình chưa chắc** · 4.7 Đăng ký thu gom · 4.10 Duyệt yêu cầu · **4.12 Duyệt tuyến** · 4.13 Tổng quan BQL · 4.16 Vận hành

**Đợt 2:** 4.5 Quyền riêng tư · 4.8 Yêu cầu của tôi · 4.9 Tuyến hôm nay · 4.11 Xác nhận nhãn · 4.17 Chất lượng AI

**Đợt 3:** 4.6 Lịch thu gom · 4.14 Lịch sử phân loại · 4.15 Agent Run · 4.18 Danh mục & Kho quy định

**Nếu buộc phải cắt:** giữ bằng mọi giá **4.4 (Mình chưa chắc)** và **4.12 (Duyệt tuyến)**. Một cái là toàn bộ câu chuyện an toàn AI, cái kia là toàn bộ câu chuyện HITL + giá trị kinh doanh. Mất một trong hai là mất mảng điểm lớn nhất của đề.

---

## 11. MICRO-COPY TIẾNG VIỆT — DÙNG NGUYÊN VĂN

Giọng văn: **thân thiện nhưng dứt khoát, xưng "mình", không dùng "chúng tôi" cứng nhắc, không đùa cợt ở chỗ liên quan an toàn.**

| Tình huống | Câu chữ |
|---|---|
| Đang xử lý | `Đang xem giúp bạn…` |
| Xoá EXIF | `Đã xoá thông tin vị trí khỏi ảnh` |
| Làm mờ mặt | `Đã làm mờ 1 khuôn mặt trong ảnh` |
| Kết quả chắc chắn | `Bỏ vào thùng xanh dương — rác tái chế` |
| Kết quả khá chắc | `Nhiều khả năng là rác tái chế. Bạn xem quy định của toà để chắc hơn nhé.` |
| Từ chối trả lời | `Mình chưa đủ chắc để hướng dẫn món này` |
| Từ chối, nhóm nguy hại | `Món này có thể là rác nguy hại. Hướng dẫn sai ở nhóm này gây nguy hiểm thật, nên mình không đoán bừa.` |
| Chặn cứng | `Món này cần quy trình xử lý riêng. Mình chuyển cho ban quản lý ngay.` |
| Vượt ngưỡng thu gom | `Yêu cầu này vượt ngưỡng tự động (30 kg) nên cần ban quản lý duyệt.` |
| Gộp tuyến thành công | `Yêu cầu của bạn đi cùng chuyến với 3 hộ khác — giảm 2 chuyến xe.` |
| Mất mạng | `Chưa gửi được — ảnh đã lưu vào máy bạn. Thử lại khi có mạng nhé.` |
| Suy giảm một phần | `Mình nhận ra món rác nhưng chưa tra được quy định riêng của toà S1. Hướng dẫn dưới đây là hướng dẫn chung.` |
| Rỗng, chưa có gì | `Chưa có yêu cầu nào. Chụp món rác đầu tiên để bắt đầu nhé.` |
| Nhãn cảnh báo cố định | `Cảnh báo an toàn theo danh mục chuẩn — không do AI tự viết.` |
| Nhãn AI ước lượng | `AI ước lượng — bạn kiểm tra lại giúp mình` |
| Nhãn AI đề xuất | `AI đề xuất — cần người duyệt trước khi áp dụng` |

---

## 12. CÁCH DÙNG FILE NÀY VỚI CÔNG CỤ DESIGN

File dài, đừng dán một lần. Chia làm 4 lượt, mỗi lượt **luôn kèm mục 0, 1, 2** làm nền:

| Lượt | Dán các mục | Yêu cầu công cụ tạo |
|---|---|---|
| 1 | 0 · 1 · 2 · 3.1 · 4.1 · 4.2 · 4.3 · 4.4 · 11 | App cư dân — luồng chụp → kết quả → từ chối |
| 2 | 0 · 1 · 2 · 3.1 · 4.5 · 4.6 · 4.7 · 4.8 · 11 | App cư dân — quyền riêng tư + đăng ký thu gom |
| 3 | 0 · 1 · 2 · 3.3 · 4.10 · 4.11 · 4.12 · 4.13 | Console BQL — ba hàng đợi HITL + tổng quan |
| 4 | 0 · 1 · 2 · 3.3 · 4.15 · 4.16 · 4.17 · 5 · 6 | Console BQL — trace, vận hành, eval + component |

Câu mở đầu gợi ý cho mỗi lượt:

> Thiết kế giao diện cho sản phẩm dưới đây bằng **Next.js + Tailwind + shadcn/ui**, toàn bộ chữ **tiếng Việt**, có **dark/light mode**, đủ **4 trạng thái loading/rỗng/lỗi/suy giảm một phần** cho mọi màn. Dùng **dữ liệu mẫu tiếng Việt sát thực tế chung cư Việt Nam** (tên toà, mã căn hộ, tên người, loại rác), không dùng lorem ipsum. Bám sát đặc tả, đừng tự thêm màn hình ngoài danh sách.

**Khi mang code về repo:** đặt ở thư mục `frontend/` riêng, gọi API theo mục 7, và giữ nguyên các nhãn minh bạch (`không do AI tự viết`, `AI đề xuất — cần người duyệt`) — đó là những chỗ ăn điểm, đừng để bị lược mất trong lúc dọn code.
