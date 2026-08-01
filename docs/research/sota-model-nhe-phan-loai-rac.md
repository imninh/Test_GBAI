# SOTA — Model nhẹ cho phân loại rác (lightweight / quantization / edge)

**Ngày:** 29/07/2026 · **Người làm:** Thế Ninh ·
**Trạng thái:** báo cáo khảo sát — **chưa phải quyết định kỹ thuật**

---

## 1. Vì sao khảo sát này liên quan tới GreenBin

Kiến trúc hiện tại gọi API vision (gpt-4o-mini → gpt-4o), không chạy model local. Khảo sát này không nhằm thay thế kiến trúc đó, mà nhằm trả lời một câu hỏi hẹp:

> **Có nên chèn thêm một tầng "model nhẹ tự train, chạy local, $0/ảnh" vào giữa cache pHash và gpt-4o-mini không?**

Gọi là **tầng T0.5**. Nếu có, định tuyến thành 4 tầng:

| Tầng | Xử lý | Chi phí/ảnh |
|---|---|---|
| T0 — cache pHash | ảnh trùng/gần trùng | $0 |
| **T0.5 — CNN nhẹ tự train** | **ảnh dễ, vật đơn lẻ, nền sạch** | **$0** |
| T1 — gpt-4o-mini vision | T0.5 confidence thấp | thấp |
| T2 — gpt-4o vision | nhiều vật · nghi rác nguy hại | cao |

Lợi ích nếu làm, gắn với cột chấm:

| Lợi ích | Cột điểm / PLO |
|---|---|
| Nhóm thật sự **train một model** (ML + DL), không chỉ gọi API | System Design · PLO 1 |
| Bảng so sánh 4 tầng: accuracy × cost/ảnh × p95 latency | Eval · PLO 7 |
| Demo không phụ thuộc mạng và API | DevOps · giảm rủi ro ngày demo |
| Cắt phần lớn lượt gọi API → giữ trong ngân sách $25/tháng | Ràng buộc gốc #4 |

---

## 2. Model ứng viên — số liệu đã công bố

Bảng dưới lấy từ nghiên cứu 2026 so sánh nhóm model nhẹ trên TrashNet, huấn luyện 100 epoch, teacher là MobileNetV4 ([Frontiers in AI, 2026](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1804734/full)):

| Model | Top-1 TrashNet | Kích thước (INT8) |
|---|---|---|
| MobileNetV4 (teacher) | 97,09% | ~3,60 MB |
| **LCNet-0.5** | **94,18%** | **0,58 MB** |
| EfficientNet-Lite0 | 93,99% | 3,22 MB |
| MobileNetV3-Small-0.5 | 87,73% | 0,55 MB |

Latency đo trên Raspberry Pi 3B+: LCNet-0.5 khoảng **1,0 giây/ảnh** cho toàn luồng camera → hiển thị. Trên laptop/server thường sẽ nhanh hơn nhiều bậc.

Một khảo sát khác chạy 6 kiến trúc trên Raspberry Pi 4B với các mức lượng tử hoá FP32/FP16/DRQ/INT8 ([Research Square](https://www.researchsquare.com/article/rs-9732262/v1)) rút ra hai kết luận đáng nhớ:
- **FP16 gần như không mất accuracy; INT8 nhanh hơn nhưng mức mất accuracy thay đổi tuỳ kiến trúc.**
- Kiến trúc càng nhẹ càng **chịu được lượng tử hoá mạnh** tốt hơn.

Kết quả tham chiếu khác trên TrashNet với transfer learning thông thường: EfficientNet-B0 92,6% · MobileNetV2 91,3% · ResNet-18 89,7% ([arXiv 2510.21833](https://arxiv.org/pdf/2510.21833)).

Pruning kết hợp INT8 giảm được **77%** kích thước MobileNet ([Springer, 2025](https://link.springer.com/article/10.1007/s11235-025-01363-2)).

---

## 3. Phát hiện quan trọng nhất — và nó quyết định cả kế hoạch dữ liệu

**Model đạt 94,18% trên TrashNet chỉ còn 41,04% khi đem sang RealWaste (ảnh rác thật tại bãi rác).** Fine-tune trên RealWaste kéo lên 79,67%, nhưng khi đó accuracy trên TrashNet tụt xuống 65,08%.

Nguyên nhân: TrashNet chụp từng món rác **sạch, đơn lẻ, trên nền bìa trắng**. Rác thật thì bẩn, chồng lấn, ánh sáng kém, bị che khuất.

**Ba hệ quả cho nhóm:**

1. **Mọi con số accuracy công bố trên TrashNet đều không dùng được để hứa hẹn.** Nếu slide ghi "94%" mà không nói rõ đo trên bộ nào thì đó là số sai.
2. **Bộ 300–500 ảnh tự chụp ở mục 6 `CLAUDE.md` không phải việc phụ — nó là bộ dữ liệu quan trọng nhất.** Chỉ nó mới đo được sản phẩm có chạy thật không.
3. **Chênh lệch accuracy giữa bộ công khai và bộ tự chụp là phát hiện đắt giá nhất trong report.** Đừng giấu, in to lên slide. Rất ít đội có được một phát hiện định lượng như vậy.

Dataset nên tải thêm: **RealWaste** (4.752 ảnh, 524×524, 9 lớp, chụp tại bãi rác Whyte's Gully — [UCI](https://archive.ics.uci.edu/dataset/908/realwaste)). Nó lấp đúng khoảng trống mà TrashNet để lại.

---

## 4. Đường tắt: baseline không cần train

Nếu muốn có số so sánh trong 1 buổi thay vì vài ngày: chạy **CLIP / SigLIP zero-shot** làm mốc. Không train, không gán nhãn, chỉ mô tả lớp bằng câu chữ.

Cảnh báo: zero-shot trên lĩnh vực chuyên biệt thường **dưới ~50% accuracy** ([Fraunhofer](https://publica.fraunhofer.de/bitstreams/935df0b0-8ea7-4f8c-b528-4f34703db334/download)), nên đừng kỳ vọng nó thay được T0.5. Giá trị của nó là **làm mốc dưới** trong bảng so sánh — có mốc dưới thì con số của model tự train mới có nghĩa.

Ngược lại, hướng dùng vision-language model kèm prompt engineering cho phân loại rác đã có nghiên cứu nghiêm túc ([ScienceDirect, 2025](https://www.sciencedirect.com/science/article/pii/S0956053X25003502)) — tức là hướng gọi API hiện tại của nhóm không hề "kém sang" so với train model, chỉ khác đánh đổi.

---

## 5. Khuyến nghị

**Nên làm, nhưng là P1 — sau khi luồng T1 + eval đã chạy được đầu-cuối.**

Lý do xếp P1: giá trị lớn nhất của T0.5 là **bảng so sánh**, mà muốn có bảng so sánh thì phải có sẵn pipeline eval và tầng T1 để làm mốc. Train model trước khi có eval là làm ngược.

Nếu làm, đề xuất cấu hình:

- **Kiến trúc:** `EfficientNet-Lite0` hoặc `MobileNetV3-Small`. Bỏ LCNet dù nó đứng đầu bảng — hệ sinh thái mỏng, ít ví dụ, không đáng rủi ro trong thời gian này. Chênh lệch accuracy không đáng kể.
- **Huấn luyện:** transfer learning, freeze backbone rồi mở dần. Colab free T4 là đủ, khoảng 30–60 phút/lần chạy.
- **Dữ liệu:** TrashNet + RealWaste + bộ tự chụp. **Bộ tự chụp phải nằm cả trong tập train lẫn tập test giữ riêng** — không được chỉ train trên dữ liệu quốc tế.
- **Lượng tử hoá:** làm FP16 trước (gần như miễn phí về accuracy). INT8 chỉ làm nếu cần và phải đo lại accuracy sau khi lượng tử.
- **Triển khai:** xuất ONNX, chạy bằng ONNX Runtime **trên backend** — không chạy trong trình duyệt. Backend đã có sẵn, thêm một tầng ở đó là rẻ nhất.
- **Ngưỡng chuyển tầng:** T0.5 chỉ được tự quyết khi confidence trên ngưỡng **và** không thuộc nhóm nguy hại. Nhóm nguy hại **luôn** đẩy lên T2, bất kể T0.5 nói gì — đây là ràng buộc an toàn ở mục 5 `CLAUDE.md`, không được nới.

**Không nên làm:** chạy model trong trình duyệt · phần cứng edge thật (Raspberry Pi, Jetson) · knowledge distillation · neural architecture search. Đều ngoài phạm vi chấm điểm và tốn thời gian không tương xứng.

---

## 6. Chốt lại cho nhóm

1. Câu hỏi "sao không train model thay vì đi validate bộ tài liệu?" (chat 28/07 dòng 60) — hai việc khác nhau. Model học **nhận diện vật thể**. Kho tri thức RAG trả lời **"toà này thu rác cồng kềnh thứ mấy"** và **"quy định nào áp dụng"**. Loại tri thức thứ hai thay đổi theo từng toà và theo thời gian, không thể nhét vào trọng số model.
2. Con số duy nhất nhóm được phép đưa lên slide là con số **tự đo trên tập test giữ riêng của mình**. Mọi số trong báo cáo này là số của người khác, dùng để chọn hướng đi, không dùng để hứa.
3. Việc cần quyết: **có đưa T0.5 vào backlog P1 không**, và **ai làm**. Nếu thời gian còn lại dưới 2 tuần thì bỏ, giữ nguyên 3 tầng.

---

## Nguồn

- [Compact waste image classification with multi-student CNNs and edge-oriented model selection — Frontiers in AI, 2026](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1804734/full)
- [Hardware-Aware CNN Deployment for Waste Classification: Quantization–Architecture Trade-offs on Edge Device — Research Square](https://www.researchsquare.com/article/rs-9732262/v1)
- [Towards Accurate and Efficient Waste Image Classification — arXiv 2510.21833](https://arxiv.org/pdf/2510.21833)
- [TinyML model compression: pruning and quantization — Telecommunication Systems, 2025](https://link.springer.com/article/10.1007/s11235-025-01363-2)
- [RealWaste — UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/908/realwaste)
- [RealWaste: A Novel Real-Life Data Set for Landfill Waste Classification — MDPI Information 14(12)](https://www.mdpi.com/2078-2489/14/12/633)
- [Enhancing waste recognition with vision-language models — ScienceDirect, 2025](https://www.sciencedirect.com/science/article/pii/S0956053X25003502)
- [A Comparative Evaluation of Vision Language Models — Fraunhofer](https://publica.fraunhofer.de/bitstreams/935df0b0-8ea7-4f8c-b528-4f34703db334/download)
- [WasteNet: Waste Classification at the Edge for Smart Bins — arXiv 2006.05873](https://arxiv.org/pdf/2006.05873)
- [waste-datasets-review — danh mục dataset rác](https://github.com/AgaMiko/waste-datasets-review)
