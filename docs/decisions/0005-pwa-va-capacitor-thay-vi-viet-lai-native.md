# ADR-0005 — PWA + Capacitor thay vì viết lại app native

**Ngày:** 01/08/2026 · **Trạng thái:** đã chốt

## Bối cảnh

Yêu cầu tối thiểu của chương trình là **"web/app deploy online"**. Sản phẩm đến
cuối Slice 1 vẫn là web app chạy `localhost`: chưa ai cài về máy được, chưa ai
ngoài máy phát triển mở được.

Đội vệ sinh là người thao tác trung tâm (ADR-0003) và họ làm việc **tại phòng
rác tầng, một tay, đeo găng, sóng yếu**. Một cái link mở bằng trình duyệt không
phải hình dạng đúng cho bối cảnh đó. Nhưng nhóm đã có 21 màn Next.js chạy được,
và chỉ còn vài ngày.

## Quyết định

Không viết lại native. Dùng **cùng một bản build** cho cả ba đường phân phối:

1. `output: "export"` của Next → thư mục tĩnh `out/`;
2. **PWA** (manifest + service worker viết tay) → cài từ web, xem lịch offline;
3. **Capacitor** bọc `out/` thành **APK Android**, build bằng GitHub Actions.

Backend lên **Render**, frontend lên **Vercel**.

## Lý do

1. **Dùng lại 100% code đã có.** `frontend/src` không có server action, route
   handler hay `next/image` nào, nên `output: "export"` chạy sạch ngay từ lần
   đầu — đã kiểm chứng trước khi quyết. Viết lại native là ném đi 21 màn.
2. **Chỉ có một thứ thật sự cần API của hệ điều hành: camera.** Gói gọn trong
   một file `src/lib/platform.ts` với hai hàm; mọi màn hình khác không biết mình
   đang chạy ở đâu.
3. **Offline là nhu cầu thật, không phải điểm cộng trang trí.** Hầm để xe và khu
   thùng rác sóng rất yếu. Service worker cho phép xem lịch thu gom khi mất mạng
   — đúng thứ `FRONTEND_SPEC.md` mục 2.5 đã yêu cầu mà chưa làm.
4. **Máy phát triển không cần Android SDK.** `npx cap add android` chỉ chép
   khung dự án; GitHub Actions build APK. Việc này còn kéo theo một cột điểm
   khác: CI/CD là chỗ **0/12 đội Cohort 1 bỏ trống**.

## Đánh đổi đã chấp nhận

- **Không có bản cài cho iPhone.** Không build được IPA trên Windows. iPhone đi
  đường "Thêm vào màn hình chính" của Safari. Ghi rõ trong README và trên trang
  `/tai-app` — không hứa suông.
- **APK là bản debug, chưa ký.** Cài thẳng được, không phải giữ keystore trong
  secret của repo. Muốn lên Google Play mới cần bản ký release; nằm trong
  backlog, không làm bây giờ.
- **URL bị nướng vào lúc build.** Đổi địa chỉ backend là phải build lại cả web
  lẫn APK. Đổi lại: không có bước cấu hình lúc chạy nào có thể sai.
- **Hạ tầng miễn phí có ba giới hạn thật** — máy chủ ngủ khi rảnh, đĩa tạm thời
  làm mất ảnh đã tải lên, không đủ RAM cho `torch` nên tầng T0.5 tắt. Cả ba
  **hiện thẳng trên trang Vận hành của sản phẩm**, không giấu trong báo cáo.

## Hệ quả

- Thứ tự deploy bị ràng buộc: **backend trước**, rồi mới build web và APK.
- `CORS_ORIGINS` phải chứa `https://localhost` và `capacitor://localhost` —
  origin mà app Capacitor tự dùng. Thiếu là app cài về gọi API bị chặn.
- `torch` + `transformers` tách sang `requirements-local-model.txt`; bản deploy
  chạy `LOCAL_MODEL_ENABLED=false`.
- Ban quản lý đăng nhập **trong app** thì thấy màn chỉ sang web, không phải
  console bị bóp vào màn 6 inch — giữ đúng "hai bộ mặt của sản phẩm"
  (`FRONTEND_SPEC.md` mục 2.1).
- Service worker **không bao giờ cache ảnh cư dân hay endpoint có token**. Chỉ
  ba endpoint tra cứu công khai được cache. Quyền riêng tư đứng trước tiện lợi.
