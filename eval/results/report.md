# Báo cáo đánh giá — GreenBin AI (VHR-17)

> Deliverable #10. **Chỉ ghi số đã đo được.** Mục nào chưa đo thì để ⏳ kèm lý do
> và điều kiện để đo — không điền số ước lượng, không chép số của dataset công
> khai vào đây như thể đó là năng lực sản phẩm (`CLAUDE.md` mục 6).

**Cập nhật:** 02/08/2026

---

## 1. Truy hồi RAG — đã đo

Chạy: `python eval/run_retrieval_eval.py` · bộ câu hỏi: `eval/retrieval_questions.py`
(18 câu, mỗi câu có 1–2 đoạn quy định được tính là đúng) · kho: 13 đoạn, 13/13
đã có vector.

| Chỉ số | Thuần BM25 | **Hybrid BM25 + embedding** |
|---|---|---|
| hit@1 | 0,667 | **0,722** |
| hit@3 | 0,889 | **0,944** |
| hit@5 | 0,944 | **1,000** |
| MRR | 0,792 | **0,838** |

**Con số quan trọng nhất là hit@5 = 1,000.** Node `advise` đưa 5 đoạn đầu vào
prompt, nên nghĩa là **model luôn nhận được đoạn quy định đúng** — nó không thể
trả lời sai vì thiếu tài liệu, chỉ có thể sai vì đọc sai.

Không dùng `precision@5`: mỗi câu chỉ có 1–2 đoạn đúng nên chỉ số đó trần cứng ở
0,2–0,4, đọc lên gây hiểu nhầm.

### Quét trọng số vector

`python eval/run_retrieval_eval.py --quet-trong-so`

| Trọng số vector | hit@1 | hit@3 | MRR |
|---|---|---|---|
| 0,00 (thuần BM25) | 0,667 | 0,889 | 0,792 |
| **0,35 (đang dùng)** | 0,722 | 0,944 | 0,838 |
| 0,80 | 0,833 | 1,000 | 0,917 |
| 1,00 (thuần vector) | 0,889 | 1,000 | 0,935 |

⚠️ **Chưa đổi trọng số dù bảng gợi ý nên tăng.** Bộ 18 câu này cố ý viết theo
lối nói cư dân, không chép chữ trong văn bản quy định — tức thiên vị embedding và
bất lợi cho BM25. Chốt theo bảng này là overfit vào 18 câu do chính nhóm viết.
Chờ đủ ~60 câu, có cả câu gõ đúng thuật ngữ, rồi quét lại.

### 5 câu chưa đưa đoạn đúng lên hạng 1

| Câu hỏi | Đoạn hybrid trả về | Đoạn đúng |
|---|---|---|
| "đồ đạc to quá thì làm sao" | Pin và ắc quy | Mục 4.5 — Đồ cồng kềnh |
| "bỏ tủ quần áo cũ" | Pin và ắc quy | Mục 4.5 — Đồ cồng kềnh |
| "vỏ lon bia để đâu" | Mục 4.3 — Rác thực phẩm | Mục 4.2 — Rác tái chế |
| "cơm thừa canh cặn đổ đâu" | Mục 4.2 — Rác tái chế | Mục 4.3 — Rác thực phẩm |
| "nhà mình phải chia rác ra mấy loại" | Bóng đèn huỳnh quang | Mục 4.1 — Nguyên tắc chung |

Đoạn đúng của cả 5 câu **đều có trong kho** — đây là lỗi xếp hạng, không phải
thiếu nội dung. Đầu vào cho vòng cải tiến sau (PLO 7).

---

## 2. Chi phí và độ trễ theo tầng — đã đo

Đo trực tiếp, không ước lượng.

| Tầng | Model | Độ trễ | Token vào | Chi phí |
|---|---|---|---|---|
| T0 cache pHash | — | ~24 ms | 0 | $0 |
| T0.5 CLIP ONNX int8 | `clip-vit-base-patch32` | **56 ms** | 0 | **$0** |
| T1 | `llama-3.2-11b-vision-instruct` (NVIDIA) | 8,5 s | 2.358 (ảnh 512px) | free tier |
| T2 | `gemini-flash-latest` | ~2 s | 1.805 (ảnh 512px) | free tier |
| advise | `llama-3.1-8b-instruct` (NVIDIA) | 1,5–2,2 s | ~300 | free tier |

Ảnh chiếm ~60% token đầu vào của Gemini (1.080/1.805). Hỏi bằng chữ rẻ hơn 2,5 lần.

### T0.5: bản nén so với bản đầy đủ

| | torch fp32 | ONNX int8 |
|---|---|---|
| Trọng số | ~605 MB | **88,7 MB** |
| RAM tiến trình | không lọt máy chủ 512 MB | **185 MB** |
| Độ trễ/ảnh | 458 ms | **56 ms** |
| Cosine với bản gốc | 1,0 | 0,970 / 0,980 |

⚠️ Bản nén **đổi thang điểm** (cùng một ảnh: 0,3072 → 0,4466). Ngưỡng
`CLIP_ACCEPT_CONFIDENCE = 0,82` **chưa được chuẩn lại** — chưa dùng số accuracy
nào của T0.5 cho báo cáo.

---

## 3. Chất lượng phân loại — ⏳ chưa đo

| Chỉ số | Mục tiêu | Kết quả | Điều kiện để đo |
|---|---|---|---|
| Accuracy (ảnh tự chụp) | — | ⏳ | cần **100 ảnh tự chụp** |
| Macro-F1 | — | ⏳ | như trên |
| **Rác nguy hại bị phân loại thành rác thường** | **0%** | ⏳ | như trên |
| Confusion matrix | — | ⏳ | như trên |

Số hiện trên trang Chất lượng AI của bản deploy là **dữ liệu demo mô phỏng**, có
gắn cờ `is_seed` trong CSDL và dán nhãn rõ trên giao diện. Không được trích số
đó vào báo cáo.

---

## 4. Test tự động

```
pytest -q      → 116 passed
ruff check     → All checks passed
tsc --noEmit   → sạch
```

CI GitHub Actions chạy cả ba, xanh từ lần đầu.

---

## 5. Việc còn lại, theo thứ tự

- [ ] Chụp **100 ảnh rác thật** tại phòng rác tầng — chặn mục 3 và việc chuẩn ngưỡng T0.5
- [ ] Viết tiếp bộ câu hỏi truy hồi từ 18 lên ~60 câu, gồm cả câu gõ đúng thuật ngữ
- [ ] Chuẩn lại `CLIP_ACCEPT_CONFIDENCE` cho bản ONNX int8
- [ ] Quét lại `RAG_VECTOR_WEIGHT` trên bộ 60 câu rồi mới chốt
- [ ] Sửa 5 ca xếp hạng sai ở mục 1
- [ ] `eval/run_eval.py` cho phần phân loại ảnh (chưa viết, chờ có ảnh)
