# ADR-0007 — Tầng T0.5 chạy bản CLIP nén int8 thay vì torch

**Ngày:** 02/08/2026 · **Trạng thái:** đã chốt

## Bối cảnh

Tầng T0.5 (CLIP zero-shot) chạy tốt ở máy dev nhưng **tắt trên bản deploy**, nên
sản phẩm thật chỉ chạy 3 trong 4 tầng — trong khi slide nói "định tuyến 4 tầng".

Chẩn đoán cũ ghi trong `requirements-local-model.txt` là *"torch chiếm 1,19 GB,
gói free không đủ dung lượng lẫn RAM"*. Chỗ này lẫn giữa **dung lượng đĩa của
gói cài** và **RAM lúc chạy**. Đo lại cho đúng:

| | RAM |
|---|---|
| Máy chủ Render gói free | **512 MB** tổng |
| CLIP ViT-B/32 đầy đủ, fp32 (151M tham số) | ~605 MB |
| Riêng nửa ảnh, fp32 (88M tham số) | ~350 MB |

Nên bản đầy đủ là không có cửa, kể cả trả tiền gói Starter (cũng 512 MB).

Nhưng CLIP có **hai nửa tách rời**: nửa ảnh và nửa chữ. Phân loại zero-shot chỉ
là so dãy số của ảnh với dãy số của từng câu mô tả. Mà các câu mô tả
(`clip_prompts` trong danh mục rác) **cố định**, trong khi code cũ mã hoá lại cả
35 câu **mỗi lần có ảnh mới** — đúng thứ `rag.embed_chunks()` đã tránh được từ
đầu ở phía kho quy định.

## Quyết định

Tách tầng T0.5 thành **hai đường chạy**, chọn bằng `CLIP_RUNTIME`:

- **`onnx`** — chỉ nửa ảnh, xuất sang ONNX và nén int8; dãy số của 35 câu mô tả
  tính sẵn một lần và cất kèm. Không cần `torch`. Đây là đường của bản deploy.
- **`torch`** — bản đầy đủ như cũ, giữ lại ở máy dev làm **mốc đối chiếu** cho
  phần eval.
- **`auto`** (mặc định) — có bộ ONNX thì dùng, không thì lui về torch.

Sinh bộ ONNX bằng `scripts/export_clip_onnx.py`, chạy **một lần** trên máy có
torch hoặc trên Google Colab bản miễn phí. Hai file kết quả đính vào GitHub
Release; máy chủ tải về qua `CLIP_ASSETS_URL` (đĩa gói free là đĩa tạm nên nó tự
tải lại sau mỗi lần khởi động lại).

## Số đo — tất cả đo trên máy dev, không ước tính

| | torch (bản đầy đủ) | ONNX int8 |
|---|---|---|
| Dung lượng | 1,19 GB gói + ~605 MB trọng số | **88,7 MB** |
| RAM tiến trình (đo bằng `psutil`) | không đo được dưới 512 MB | **185 MB** |
| Độ trễ mỗi ảnh | 458 ms | **56 ms** (114 ms tính cả giải mã ảnh) |
| Độ tương đồng cosine với bản gốc | 1,0 (là chính nó) | **0,970 / 0,980** |

Bản ONNX **fp32** cũng đã đo: cosine đúng 1,0000 nhưng **446 MB RAM** — quá sát
trần 512 MB khi còn phải cõng FastAPI và SQLAlchemy, nên loại.

Đã thử ba cách nén khác để kéo cosine lên, **không cách nào ăn thua**:
`per_channel` 0,9636 · `reduce_range` 0,9407 · loại trừ các phép nhân trong
attention 0,9699. Bản fp16 (176 MB) thì `onnxruntime` từ chối nạp vì xung đột
kiểu ở node `Conv` và `Cast` — bỏ, không đáng đào thêm khi int8 đã vừa thoải mái.

Con số cosine 1,0000 của bản fp32 còn xác nhận thêm một điều quan trọng: **phần
tiền xử lý ảnh tự viết bằng PIL + numpy khớp đúng `CLIPImageProcessor`**, sai
lệch của bản int8 hoàn toàn đến từ bước nén chứ không phải từ chỗ khác.

## Đánh đổi đã chấp nhận

- **Điểm số lệch đi thật.** Trên ảnh thử, cùng một ảnh: bản gốc 0,3072 → bản
  int8 0,4466. **Nhóm chọn ra vẫn giống nhau**, nhưng thang điểm đã khác.
  ⚠️ **`CLIP_ACCEPT_CONFIDENCE=0.82` bắt buộc phải chuẩn lại**, không được bê
  nguyên sang. Việc đó chỉ làm đàng hoàng được sau khi có bộ 100 ảnh tự chụp.
- **Một ảnh không đủ kết luận.** Hai con số cosine ở trên đo trên đúng hai ảnh
  có trong repo. Phải chạy lại trên bộ ảnh thật rồi mới được đưa số nào lên slide.
- **Thêm một bước phát hành.** Đổi `clip_prompts` trong danh mục rác thì phải
  chạy lại script xuất. Chốt chặn: file kèm theo lưu **mã băm của bộ câu mô tả**;
  lệch là tầng T0.5 tự tắt kèm cảnh báo trong log, thay vì chấm bằng bộ câu cũ
  trong im lặng. `tests/test_services/test_local_clip.py` giữ hợp đồng này ở CI.
- **File 89 MB không commit vào repo** (nằm trong lịch sử git vĩnh viễn), nên
  phải qua GitHub Release — thêm một chỗ có thể quên cập nhật.

## Hệ quả

- Bản deploy lên **4/4 tầng**. `render.yaml` đổi `LOCAL_MODEL_ENABLED=true`,
  thêm `CLIP_RUNTIME=onnx` và `CLIP_ASSETS_URL`.
- `onnxruntime` + `numpy` chuyển vào `requirements.txt`; `torch` ở lại
  `requirements-local-model.txt` và giờ chỉ còn cần cho máy dev + bước xuất.
- Trang Vận hành hiện rõ T0.5 đang chạy **bản nén** hay **bản đầy đủ** — hai bản
  cho điểm số khác nhau nên nhìn nhầm là đọc sai số liệu.
- Tầng T0.5 nhanh hơn **8 lần** ở máy dev (458 ms → 56 ms), phần lớn nhờ bỏ
  được 35 lượt mã hoá chữ mỗi ảnh. Đây là món lợi ngoài dự tính.
- **Hàng rào an toàn không đổi:** T0.5 vẫn không bao giờ được chốt nhãn nhóm
  nguy hại, và dưới ngưỡng thì đẩy lên T1. Nên sai lệch do nén **không mở rộng
  vùng rủi ro** — nó chỉ làm tầng này nhận hoặc nhường sai số ca, tức là chuyện
  chi phí, không phải chuyện an toàn.
