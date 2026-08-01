---
# DỰ ÁN GREENBIN AI – AGENT PHÂN LOẠI RÁC & ĐIỀU PHỐI THU GOM TÁI CHẾ

*(Giải pháp tối ưu cho App Cư dân & Ban Quản lý Khu đô thị VinHomes)*

---

## I. BỐI CẢNH & PHÂN TẦNG XỬ LÝ RÁC (PRODUCT STRATEGY)

### 1. Thực trạng & Bài toán tại Chung cư VinHomes

* **Phòng rác tầng nhỏ hẹp:** Tận dụng không gian cho diện tích ở nên phòng rác tầng chỉ chứa được 2–3 thùng rác tiêu chuẩn.
* **Túi rác sinh hoạt đóng kín:** 80% rác hàng ngày là rác bếp/rác ướt được đóng trong túi nilon kín/đục. Cư dân không bao giờ mở túi ra chụp ảnh và AI cũng không thể nhìn xuyên qua túi.
* **Vấn nạn Rác Cồng kềnh & Tái chế lớn:** Sofa, đệm cũ, thùng carton lớn, đồ điện tử... vứt bừa bãi tại phòng rác tầng hoặc lối thoát hiểm $\rightarrow$ **Vi phạm an toàn PCCC, làm quá tải nhân viên vệ sinh và gây mất mỹ quan.**
* **Thiếu động lực phân loại:** Cư dân tiện tay vứt chung tất cả rác vì không có lợi ích kinh tế hoặc sự tiện lợi đi kèm.

### 2. Chiến lược Phân tầng Xử lý Rác (Tiered Waste Strategy)

```
                          ┌─────────────────────────────────────────┐
                          │     RÁC PHÁT SINH TẠI CĂN HỘ           │
                          └────────────────────┬────────────────────┘
                                               │
                      ┌────────────────────────┴────────────────────────┐
                      ▼                                                 ▼
        [1. Rác Sinh Hoạt Hàng Ngày]                       [2. Rác Tái Chế & Cồng Kềnh]
      (Đ đồ ăn thừa, khăn giấy, rác ướt)                 (Chai nhựa, lon, carton, sofa, pin)
                      │                                                 │
                      ▼                                                 ▼
        [ BỎ QUA AI / KHÔNG BẮT CHỤP ]                       [ DÙNG VISION AI TẠI NGUỒN ]
          • Buộc kín túi nilon                             • Fast Scan tại bàn bếp (1s)
          • Thả thẳng vào "Rác còn lại"                    • Đặt lịch hẹn thu gom tận nơi
          • Không tích điểm                                • Tích điểm / Đổi voucher

```

---

## II. MA TRẬN PHÂN TÍCH STAKEHOLDERS & ĐỘNG LỰC (CARROT & STICK)

### 1. Ma trận Giá trị (Value Matrix)

| Stakeholder | Pain Point (Nỗi đau) | Giải pháp từ GreenBin AI | Incentive (Động lực) |
| --- | --- | --- | --- |
| **Cư dân** | • Đồ cồng kềnh nặng, khó bê vác.<br>

<br>• Rác nguy hại (pin, điện tử) không biết bỏ đâu.<br>

<br>• Không có thời gian phân loại cầu kỳ. | • AI hướng dẫn vị trí vứt đồ lạ.<br>

<br>• Đặt lịch có người lên tận nhà hỗ trợ bê đồ cồng kềnh.<br>

<br>• Quét ảnh 1s siêu nhanh. | • **Kinh tế:** Trừ điểm vào Phí gửi xe / Phí quản lý.<br>

<br>• **Tiện ích:** Ưu tiên đặt lịch Sân BBQ, Tennis, Bể bơi. |
| **Nhân viên Vệ sinh** | • Bị động, quá tải do đồ nặng vứt chui.<br>

<br>• Phải gom rác thủ công vất vả. | • Nhận lịch thu gom chủ động theo ca.<br>

<br>• Nhận đúng loại rác đã được phân loại/bóp dẹp sẵn. | • Giảm sức lao động nặng bộc phát.<br>

<br>• Tăng năng suất làm việc có quy trình. |
| **Ban Quản lý (BQL)** | • Bị phạt vi phạm PCCC.<br>

<br>• Không kiểm soát được lượng rác tái chế.<br>

<br>• Tốn chi phí vận chuyển quá định mức. | • Dashboard theo dõi lượng rác.<br>

<br>• Quy trình HITL kiểm soát duyệt lịch.<br>

<br>• Tự động cảnh báo vi phạm. | • Đạt chỉ số Xanh / ESG doanh nghiệp.<br>

<br>• Giảm chi phí vận hành & phạt hành chính. |

### 2. Cơ chế "Cây gậy & Củ cà rốt" (Carrot & Stick)

* **Củ cà rốt (Tạo Động lực Tích cực):**
* Tích lũy **"Điểm Xanh"** để trừ trực tiếp vào Phí quản lý tòa nhà hoặc Phí gửi xe VinFast/Ô tô hàng tháng.
* Đạt danh hiệu *Căn hộ Xanh (Rank Vàng/Kim Cương)* $\rightarrow$ Được ưu tiên quyền *Book trước Sân BBQ / Sân Tennis* vào cuối tuần trong App Vin Resident.


* **Cây gậy (Ràng buộc & Phản hồi):**
* Cấp tem/mã QR định danh căn hộ cho túi rác tái chế/đồ cồng kềnh.
* Nhân viên vệ sinh quét QR khi thu gom. Nếu vứt sai quy định (ví dụ: nhét rác ướt vào túi tái chế), hệ thống gửi cảnh báo đích danh tới App căn hộ và trừ điểm uy tín.



---

## III. KIẾN TRÚC KỸ THUẬT & TECH STACK TỐI ƯU

### 1. Sơ đồ Kiến trúc Tổng quan

```
[ User App / Next.js ] ──► [ Client Compression (<100KB) ]
                                    │
                                    ▼
                          [ API Gateway: FastAPI ]
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
              [ Auth/DB: Supabase ]   [ Agent: LangGraph ]
              (RLS, Storage, PG)               │
                                       ┌───────┴───────┐
                                       ▼               ▼
                                 [GPT-4o-mini]     [GPT-4o]
                                 (Fast Scan 1s)  (Bulky Waste)

```

### 2. Chi tiết Tech Stack

* **LLM Engine:**
* **GPT-4o-mini / Gemini 1.5 Flash:** Dùng cho tính năng *Quét Nhanh (Fast Scan)* tại bàn bếp. Tối ưu thời gian phản hồi $< 1.2$ giây.
* **GPT-4o:** Dùng cho bài toán *Rác cồng kềnh / Khối lượng lớn*, cần phân tích ngữ cảnh phức tạp và ước tính thể tích/khối lượng.


* **Orchestration (LangGraph):** Quản lý luồng xử lý đa bước (Stateful Workflow) và tích hợp cơ chế **HITL (Human-In-The-Loop)** để Lao công/BQL xác nhận lịch hẹn trước khi chốt đơn.
* **Backend:** **FastAPI** (Python) xử lý Async I/O, WebSocket và tương tác với AI Agents.
* **Database & Auth:** **Supabase (PostgreSQL)** quản lý Auth, Row Level Security (RLS) bảo mật ảnh cư dân, và Supabase Storage chứa dữ liệu ảnh.
* **Frontend & Mobile:** **Next.js** (Web Client / PWA) tối ưu cho cả Cư dân và Dashboard BQL.
* **Deployment:** API Backend & Agent deploy trên **Railway**; Frontend deploy trên **Vercel**.

### 3. Chiến lược Tối ưu Latency & Cost cho Vision AI (Fast Scan)

Toàn bộ quy trình Quét Nhanh được tối ưu kỹ thuật theo 3 bước:

1. **Client-side Image Resize:** App tự động nén ảnh xuống kích thước $512 \times 512$ px (JPEG quality 70%, dung lượng $< 100$ KB) trước khi gửi API.
2. **Structured JSON Output:** Prompt ép AI chỉ trả về một chuỗi JSON ngắn gọn:
```json
{
  "loai_rac": "TAI_CHE",
  "ten_vat_pham": "Chai nhựa PET",
  "huong_dan": "Súc sạch, bóp dẹp và cho vào Túi Treo Tái Chế",
  "diem_thuong": 5
}

```


3. **Semantic Caching:** Lưu kết quả các vật phẩm phổ biến vào Cache để tránh gọi lại LLM khi gặp cùng mẫu ảnh.

---

## IV. QUY TRÌNH LUỒNG CÔNG VIỆC CỐT LÕI (CORE WORKFLOWS)

### Luồng 1: Fast Scan (Quét Nhanh 1s tại Bàn Bếp)

1. Cư dân giơ camera quét chai lọ/vỏ hộp vừa dùng xong.
2. App nén ảnh $\rightarrow$ Gọi API `GPT-4o-mini`.
3. Màn hình hiển thị Pop-up kết quả ngay lập tức ($<1.2$s): Hướng dẫn vứt & Điểm thưởng dự kiến.
4. Cư dân bỏ vật phẩm vào **Túi Treo Tái Chế** tại nhà.

### Luồng 2: Đặt lịch Thu gom Rác Cồng Kềnh / Tái chế lớn (HITL Workflow)

1. Cư dân chụp ảnh góc rộng khu vực chứa đồ cồng kềnh (sofa, đệm, thùng carton lớn).
2. AI (`GPT-4o`) nhận diện danh sách vật phẩm, tự động phân loại và ước tính khối lượng.
3. App tự điền Form Đăng Ký $\rightarrow$ Cư dân chọn khung giờ hẹn (ví dụ: 14:00 - 15:00).
4. **HITL Node:** Request chuyển đến App Lao công/BQL ca trực đó để bấm "Xác nhận nhận Task".
5. Lịch hẹn được chốt $\rightarrow$ Thông báo gửi lại cho Cư dân.

### Luồng 3: Xác nhận & Tích điểm Tự động (Automated Reward Loop)

1. Đến giờ hẹn, Lao công lên tận phòng nhận đồ cồng kềnh / túi tái chế.
2. Lao công chụp 1 tấm ảnh xác nhận đã nhận hàng qua App.
3. Vision AI kiểm tra tính hợp lệ của ảnh xác nhận (xác minh đúng là đồ đã đăng ký).
4. Hệ thống tự động cộng **Điểm Xanh** vào tài khoản Cư dân và cập nhật dữ liệu báo cáo ESG cho BQL.

---

## V. LỘ TRÌNH TRIỂN KHAI SẢN PHẨM (PRODUCT ROADMAP)

### Giai đoạn 1: MVP Core (Tập trung Tính khả thi)

* [x] Dựng sơ đồ Cơ sở dữ liệu Supabase (Users, Waste_Requests, Point_Ledger).
* [x] Xây dựng FastAPI + LangGraph tích hợp `GPT-4o-mini` cho tính năng Fast Scan.
* [x] Triển khai giao diện Mobile Web trên Next.js: Camera Scan & Form đăng ký gom đồ cồng kềnh.
* [x] Tích hợp luồng HITL đơn giản cho Nhân viên vệ sinh duyệt lịch thu gom.

### Giai đoạn 2: Advanced & Production Scaling

* [ ] Tích hợp hệ thống Gamification: Bảng xếp hạng Căn hộ Xanh, Voucher đổi điểm.
* [ ] Tối ưu hóa tuyến đường gom rác (Smart Routing) gộp các Request cùng tầng/tòa nhà cho Lao công.
* [ ] Phát triển Dashboard Analytics cho BQL VinHomes (Đo lường sản lượng rác tái chế, biểu đồ chi phí vận hành).
* [ ] Đóng gói API để sẵn sàng tích hợp thẳng vào App **Vinhomes Resident**.

---
