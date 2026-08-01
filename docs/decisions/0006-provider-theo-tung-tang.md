# ADR-0006 — Mỗi tầng model một nhà cung cấp riêng

**Ngày:** 01/08/2026 · **Trạng thái:** đã chốt

## Bối cảnh

`VISION_PROVIDER` là **một lựa chọn duy nhất cho toàn hệ thống**: cả T1, T2 và
bước sinh hướng dẫn đều dùng chung một client. Nhóm có ba nguồn miễn phí
(Gemini · NVIDIA NIM · CLIP local) mà tại một thời điểm chỉ dùng được một.

Hậu quả đo được ngay trên bản deploy ngày 01/08:

- Free tier của `gemini-flash-latest` (hiện trỏ tới `gemini-3.6-flash`) chỉ
  **20 request/ngày**. Bước `advise` chạy sau **mọi** lần phân loại thành công
  → mỗi lần chụp ảnh tiêu **2 request** → **10 lần chụp là hết quota**.
- Sau đó cùng một câu hỏi trả về `tier=t1_mini` thay vì `t2_full`: **tầng T2
  chết**, sản phẩm chỉ còn chạy 2 trong 4 tầng, trong khi slide nói "định tuyến
  4 tầng".

Hạn mức của ba nguồn **khác kiểu nhau**: Gemini đếm số request và rất hẹp;
NVIDIA cấp ~1.000 credit và không tính token vào hạn mức; CLIP local thì $0
nhưng chỉ dám chốt ca dễ.

## Quyết định

Khai nhà cung cấp **theo từng tầng**, không phải theo hệ thống:

| Tầng | Nhà cung cấp | Vì sao |
|---|---|---|
| T0 cache pHash | — | không gọi API |
| T0.5 | CLIP local | $0 · ~650ms · lọc bớt ca dễ |
| **T1** | **NVIDIA** | ăn phần lớn lưu lượng → cần chỗ quota rộng nhất |
| **T2** | **Gemini flash** | chỉ chạy khi ca khó → chịu được quota hẹp |
| **advise / hỏi bằng chữ** | **Gemini flash-lite** | quota riêng, còn dư |

Cách khai: `VISION_PROVIDER` giữ vai trò mặc định chung; thêm
`VISION_PROVIDER_T1` / `_T2` / `_TEXT` để ghi đè cho riêng một tầng. Để trống cả
ba là quay về đúng hành vi cũ.

## Lý do

1. **Hết quota một nơi không còn làm đứng cả sản phẩm.** Mất Gemini thì T1 vẫn
   trả lời được và bước advise lui về hướng dẫn chuẩn lấy từ CSDL (vẫn có trích
   nguồn); mất NVIDIA thì T2 vẫn kiểm được ca khó.
2. **Đặt đúng nguồn vào đúng chỗ tiêu.** Tầng tiêu nhiều nhất đặt ở nguồn rộng
   nhất — đây là tối ưu chi phí thật, đo được, không phải khẩu hiệu.
3. **Ăn điểm PLO 1.** Định tuyến model **đa nhà cung cấp** là thứ rất ít nhóm
   làm; trang Vận hành hiện thẳng bảng tầng → nhà cung cấp → model → có key
   chưa, nên hội đồng nhìn thấy ba nguồn cùng chạy chứ không phải nghe kể.
4. **Không đổi kiến trúc định tuyến.** Điều kiện leo tầng vẫn là confidence ·
   nhiều vật · nghi nguy hại. Chỉ đổi chỗ *lấy client ở đâu*.

## Đánh đổi đã chấp nhận

- **Phải giữ nhiều API key cùng lúc.** Thiếu key của tầng nào thì **chỉ tầng đó
  dừng**; trang Vận hành báo rõ tầng nào thiếu thay vì một cờ `has_api_key`
  chung che mất.
- **Chất lượng T1 và T2 không cùng một họ model nữa.** So sánh accuracy giữa hai
  tầng giờ là so hai nhà cung cấp khác nhau — phải ghi rõ điều đó trong báo cáo
  eval, không được đọc như so hai kích cỡ của cùng một model.
- **NVIDIA chậm hơn và tốn token hơn** (đo được: 8,5s · 7.126 token vào, so với
  ~2s · 1.805 token của Gemini). Chấp nhận vì free tier NVIDIA tính theo số
  request, token không ăn vào hạn mức — và độ trễ T1 không nằm trên đường găng
  của người dùng như quota nằm.
- **Mỗi nhà cung cấp trả `usage` một khuôn khác nhau**, nên phần đo chi phí phải
  kiểm lại theo từng nguồn.

## Hệ quả

- `get_vision_client(tier)` **bắt buộc nhận tầng**; `resolve_model_for(tier)`
  lấy model mặc định theo provider của **chính tầng đó** — chỗ dễ sai nhất là
  lấy nhầm mặc định của provider chung.
- Điều kiện gọi T2 so **cặp (provider, model)** chứ không chỉ tên model: cùng
  tên model trên hai nhà cung cấp vẫn là hai đường độc lập, vẫn đáng gọi lại.
- `render.yaml` khai thêm `NVIDIA_API_KEY` và ba biến provider theo tầng.
- Test giữ hành vi này ở `tests/test_services/test_vision_routing.py` và phần
  "Trộn nhà cung cấp theo tầng" trong `tests/test_services/test_classifier.py` —
  gồm cả ca **T2 hết quota mà T1 vẫn trả lời được**, đúng tình huống đã gặp thật.
- **Vẫn còn việc rẻ hơn chưa làm:** cắt lệnh gọi `advise` khi không cần (nhóm
  rác thường gặp + confidence cao thì dùng `_template_advice` sẵn có) sẽ giảm
  ngay 50% lượng gọi API. ADR này không thay thế việc đó.
