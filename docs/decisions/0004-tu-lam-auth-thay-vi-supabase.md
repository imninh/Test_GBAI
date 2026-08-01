# ADR-0004 — Tự làm xác thực thay vì dùng Supabase

**Ngày:** 01/08/2026 · **Trạng thái:** đã chốt

## Bối cảnh

Thẻ đề VHR-17 gợi ý dùng Supabase cho phần tài khoản và xác thực. Nhóm đã đi
lệch khỏi gợi ý đó từ lúc dựng schema (bảng `users` tự quản lý, băm mật khẩu
bằng PBKDF2 trong `src/services/security.py`) nhưng chưa ghi ADR — mục 4 của
`docs/DE_BAI_VHR-17.md` đã nêu đây là một trong bốn chỗ lệch chưa có lý do
chính thức.

## Quyết định

Tự làm xác thực: PBKDF2-HMAC-SHA256 cho mật khẩu, JWT ký bằng `JWT_SECRET` cho
phiên, ma trận quyền khai báo trong `src/services/auth.py`.

## Lý do

1. **Hệ thống chỉ có ba vai trò cố định và tài khoản demo.** Không có đăng ký
   tự do, không có SSO, không có quên mật khẩu. Toàn bộ nhu cầu danh tính gói
   trong một bảng và một hàm kiểm quyền.
2. **Phần đắt giá của đề nằm ở AI, không ở quản lý danh tính.** Thời gian bỏ ra
   để tích hợp Supabase không đổi được điểm ở bất kỳ tiêu chí nào trong năm cột.
3. **Thêm một dịch vụ ngoài là thêm một điểm hỏng khi demo.** Buổi demo có thể
   diễn ra ở nơi mạng kém; hệ thống chạy được với SQLite và không phụ thuộc
   dịch vụ đám mây nào là một lợi thế thật.
4. **Ma trận quyền cần hiển thị được lên UI.** Spec yêu cầu chức năng không có
   quyền thì *hiện mờ kèm tooltip giải thích*, không ẩn hẳn. Tự làm auth thì
   `GET /auth/me` trả thẳng ma trận quyền kèm lý do bị cấm cho từng mục —
   với Supabase phải tự dựng thêm một lớp nữa để có đúng dữ liệu đó.

## Đánh đổi đã chấp nhận

- Không có refresh token, không thu hồi được token trước hạn. Chấp nhận được
  với hệ thống demo dùng dữ liệu mô phỏng; token hết hạn sau 12 giờ.
- PBKDF2 200.000 vòng chậm hơn bcrypt/argon2 về mặt hiện đại nhưng nằm trong
  thư viện chuẩn, không thêm phụ thuộc. Nếu có người dùng thật thì đổi sang
  argon2 — đây là một hàm, không phải một kiến trúc.
- `JWT_SECRET` mặc định trong `.env.example` là chuỗi placeholder. **Phải đổi
  trước khi deploy** — đã ghi rõ trong file.

## Hệ quả

- `src/services/auth.py` là nơi duy nhất khai báo quyền; `src/api/deps.py`
  cung cấp `require("<quyền>")` cho mọi router.
- Mọi hành động rủi ro (duyệt thu gom, chốt tuyến, xem ảnh gốc, sửa danh mục)
  đều ghi `AuditLog` qua `write_audit`.
- Bảng quyền ở `docs/FRONTEND_SPEC.md` mục 1 và `PERMISSIONS` trong code là hai
  bản của cùng một thứ — **sửa một bên thì sửa cả hai**.
