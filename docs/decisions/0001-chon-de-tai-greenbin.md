# ADR-0001 — Chọn đề tài VHR-17 GreenBin AI

**Ngày:** 27/07/2026
**Trạng thái:** Đã chốt

## Bối cảnh

Đã cân nhắc 4 đề trong ngân hàng đề tài. Nút thắt lớn nhất khi chọn là **dữ liệu**: đề nào cũng cần một bộ dữ liệu có nhãn để eval, mà nhóm không có dữ liệu thật của doanh nghiệp.

| Đề | Vấn đề dữ liệu |
|---|---|
| BDSO2O-18 VoiceOfCustomer | Lấy được (Google Maps + YouTube API + mô phỏng), nhưng phải gán nhãn chủ đề tay cho ~250 câu tiếng Việt — tốn công và dễ bất đồng giữa người gán |
| BDSO2O-16 ResaleValuer | **Không có giá chốt thực** — mà đó chính là chỉ số eval cốt lõi mà đề yêu cầu. Chỉ đo được sai số so với giá rao |
| AIP-20 Prompt Optimization | Dữ liệu dễ nhất, nhưng chi phí API cao (vòng lặp N biến thể × M mẫu × K vòng) và demo khó hấp dẫn |
| **VHR-17 GreenBin** | Dataset ảnh rác công khai có sẵn (TrashNet, TACO, Kaggle) + tự chụp bổ sung |

## Quyết định

Chọn **VHR-17 GreenBin AI**.

## Lý do

1. **Gán nhãn ảnh nhanh hơn gán nhãn text nhiều lần.** Nhìn ảnh biết ngay loại rác; ~400 ảnh gán trong 1,5 giờ. Gán chủ đề + sentiment cho 250 câu tiếng Việt mất cả buổi và còn phải tranh luận về ranh giới nhãn.
2. **Ảnh tự chụp là dữ liệu sạch tuyệt đối về tuân thủ** — mình sở hữu, không license, không dữ liệu cá nhân người khác. Và dataset quốc tế không phản ánh rác Việt Nam, nên phần tự chụp có giá trị nghiên cứu thật.
3. **Demo trực quan nhất trong 4 đề.** Giơ điện thoại chụp, app trả lời ngay — ai cũng hiểu trong 3 giây. Failure case nhìn thấy bằng mắt, trình chiếu được lên slide.
4. **Câu chuyện an toàn AI cụ thể nhất (PLO 6):** ảnh cư dân chứa EXIF GPS/khuôn mặt/giấy tờ, cộng với rủi ro hướng dẫn sai về rác nguy hại. Cả hai đều là rủi ro thật, không phải rủi ro giả định.
5. **Model routing có lý do kinh tế thật (PLO 1):** vision đắt, text rẻ → định tuyến 3 tầng đo được bằng tiền.
6. **RAG tự nhiên (PLO 3):** "bỏ đâu, khi nào" cần tri thức quy định, không chỉ nhận diện.

## Đánh đổi chấp nhận

- **Phạm vi rộng** (vision + RAG + lịch + tuyến + gamification) → cắt kỷ luật theo P0/P1/P2, gamification xuống P2, tối ưu tuyến đầy đủ xuống P2.
- **Chi phí vision cao hơn text** → bù bằng cache pHash tầng 0 và `detail: "low"`; đo token thật trước khi chạy lô lớn.
- Ảnh nhiều vật trong một khung: P0 chỉ hỗ trợ chụp từng món, ghi rõ vào mục giới hạn hệ thống.

## Hệ quả

- Code riêng của đề VoC chuyển vào `attic/voc/`, giữ lại để tham khảo.
- `src/services/pii.py`, `security.py`, `dedup.py`, `db/session.py` dùng lại nguyên vẹn.
- `src/db/models.py` viết lại hoàn toàn cho GreenBin (14 bảng).
- `docs/FRONTEND_SPEC.md` (viết cho VoC) cần viết lại cho GreenBin.
