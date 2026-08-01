# Kế hoạch: biến GreenBin AI thành app cài được + deploy online

> **Trạng thái: ĐÃ THỰC HIỆN XONG PHẦN CODE** — 01/08/2026 buổi 2.
> Quyết định được ghi lại ở
> [ADR-0005](decisions/0005-pwa-va-capacitor-thay-vi-viet-lai-native.md);
> nhật ký ở `WORKLOG.md` mục *2026-08-01 — buổi 2*.
>
> Giai đoạn A→F đã làm hết. **Còn lại là việc cần tài khoản của chủ dự án**
> (mục "Việc chủ dự án phải tự làm" ở cuối file) — xem `CLAUDE.md` mục 11 việc 0
> để biết thứ tự bắt buộc.
>
> Hai chỗ lệch so với kế hoạch, đều là do chạy thật mới lộ ra:
> - **Giai đoạn A:** ảnh gốc có một lớp alpha rất mờ phủ gần kín khung, nên cắt
>   theo bounding box không cắt được gì. Phải cắt theo **ngưỡng alpha** và xoá
>   hẳn lớp mờ đó.
> - **Giai đoạn C:** kế hoạch nói "các hàm seed vốn đã idempotent" — đúng với
>   nhóm dữ liệu nền, **sai với nhóm dữ liệu demo** (chúng sinh bản ghi mới mỗi
>   lần gọi). Đã thêm chốt chặn `da_co_du_lieu_demo`, không thì mỗi lần Render
>   khởi động lại là nhân đôi dữ liệu trang Vận hành.

## Bối cảnh

Sản phẩm hiện là **web app chạy localhost**: `frontend/` (Next.js, 21 màn) gọi
`http://localhost:8000`. Chưa ai cài về máy được, chưa ai ngoài máy này mở được,
mà yêu cầu tối thiểu của chương trình là **"web/app deploy online"**.

Ba việc, theo đúng lựa chọn đã chốt:

1. **PWA** — mở link là cài được lên màn hình chính, chạy toàn màn hình, xem lịch
   thu gom offline (`FRONTEND_SPEC.md` mục 2.5 đã yêu cầu offline mà chưa làm).
2. **File APK tải về cài thật trên Android**, bọc bằng Capacitor để **dùng lại
   100% code đã có**, build bằng GitHub Actions nên máy không phải cài Android SDK.
3. **Backend deploy lên Render** — không có bước này thì app cài về vẫn trỏ vào
   `localhost` và không chạy.

Kèm theo: thay linh vật SVG vẽ tạm bằng **3 file PNG thật** ở `assets/`
(`GBAI_Hello`, `GBAI_KínhLup`, `GBAI_Mascot` — 1536×1024, nền trong suốt thật,
đã kiểm kênh alpha).

Phân vai: **cư dân + đội vệ sinh cài app**, **ban quản lý dùng web trên máy tính**
— đúng "hai bộ mặt của sản phẩm" ở `FRONTEND_SPEC.md` mục 2.1.

---

## Ràng buộc kỹ thuật đã kiểm, quyết định thiết kế theo đó

| Phát hiện | Hệ quả |
|---|---|
| `torch` đã cài chiếm **1,19 GB**, `transformers` 90 MB | **Tách khỏi `requirements.txt`.** Image deploy chỉ cài phần lõi; gói miễn phí không đủ RAM lẫn dung lượng cho torch. Bản deploy chạy `LOCAL_MODEL_ENABLED=false`, tầng T0.5 chỉ chạy khi dev trên máy |
| `frontend/src` 19 file, **không có** server action / route handler / `next/image` | `output: "export"` chạy sạch → thư mục `out/` tĩnh → Capacitor bọc được, Vercel phục vụ được, cùng một bản build |
| `NEXT_PUBLIC_API_URL` được nướng vào lúc build | URL Render phải có **trước** khi build APK và build Vercel |
| Capacitor Android phục vụ web từ origin `https://localhost` | Phải thêm origin đó vào `CORS_ORIGINS`, không thì app cài về gọi API bị chặn |
| Đĩa của gói miễn phí Render là tạm thời | **Ảnh cư dân upload sẽ mất khi service khởi động lại.** Ghi thẳng vào khối "Giới hạn đã biết" trên UI thay vì giấu |
| Repo **chưa `git init`** | Điều kiện tiên quyết của GitHub Actions. Làm ở đầu Giai đoạn E, tiện chạy `scripts/setup_hooks.ps1` để AI logging (deliverable #4) bắt đầu chạy |
| Không build được IPA trên Windows | iPhone dùng đường PWA. Nói rõ trong README, không hứa suông |

---

## Giai đoạn A — Linh vật thật thay SVG vẽ tạm

**Đã có:** `scripts/build_assets.py` — cắt theo bounding box của kênh alpha, xuất
WebP 3 bề rộng (240/360/512) vào `frontend/public/mascot/`, sinh bộ icon PWA
(192/512 + bản maskable có lề an toàn + apple-touch + favicon) vào
`frontend/public/icons/`. **Chưa chạy.**

**Còn phải làm:**
- Chạy `python scripts/build_assets.py`, kiểm dung lượng file ra (kỳ vọng mỗi
  ảnh vài chục KB thay vì 2,3 MB).
- Sửa `frontend/src/components/resident/onboarding.tsx` (hàm `Mascot`) và
  `ask.tsx`: thay SVG bằng `<img>` có `width`/`height` cố định để không giật
  layout. **Giữ lại hàm SVG** làm ảnh dự phòng khi file lỗi.
- Ba tư thế map vào ba màn: `GBAI_Mascot` → onboarding · `GBAI_Hello` → màn Hỏi ·
  `GBAI_KínhLup` → màn đang xử lý (đúng ý "đang soi" của bản thiết kế gốc).

## Giai đoạn B — PWA

**Thêm:** `frontend/public/manifest.webmanifest`, `frontend/public/sw.js`,
`frontend/src/components/pwa/register-sw.tsx`, `frontend/src/app/tai-app/page.tsx`.
**Sửa:** `frontend/src/app/layout.tsx`.

- Manifest: tên "GreenBin AI", `display: standalone`, `theme_color #2fae66`,
  `background_color #f4f1ea`, bộ icon ở Giai đoạn A, `lang: vi`.
- Service worker **viết tay ~70 dòng**, không thêm phụ thuộc (`next-pwa` chưa
  theo kịp App Router, không đáng rước rủi ro):
  - app shell: cache-first cho tài nguyên tĩnh của `out/`;
  - **stale-while-revalidate** cho `GET /categories`, `GET /buildings/*/schedule`,
    `GET /meta/enums` → **màn Lịch thu gom xem được offline**, đúng spec 2.5;
  - mọi thứ khác network-only. **Không bao giờ cache ảnh cư dân hay endpoint có
    token** — quyền riêng tư đứng trước tiện lợi.
- Nút "Cài app" bắt sự kiện `beforeinstallprompt`, hiện ở màn Tôi và ở `/tai-app`.
- Trang `/tai-app`: hướng dẫn 3 đường cài (Android tải APK · iPhone thêm vào màn
  hình chính · máy tính mở web), kèm nút tải APK trỏ tới GitHub Releases mới nhất.

## Giai đoạn C — Backend sẵn sàng deploy Render

**Sửa:** `requirements.txt`, `Dockerfile`, `src/config.py`, `src/main.py`,
`scripts/seed.py`, `src/db/seed_data.py` (khối `KNOWN_LIMITATIONS`).
**Thêm:** `requirements-local-model.txt`, `render.yaml`.

- Tách `torch` + `transformers` sang `requirements-local-model.txt`; README ghi rõ
  dev muốn chạy tầng T0.5 thì cài thêm file đó. Bật lại `psycopg2-binary`.
- `config.py`: thêm `seed_on_start: bool = False`; `cors_origins` mặc định thêm
  `https://localhost` và `capacitor://localhost` (origin của app cài về).
- `scripts/seed.py`: rút phần thân thành hàm `bootstrap(session, demo: bool)` để
  gọi được từ code — các hàm seed **vốn đã idempotent** (kiểm tra tồn tại trước
  khi thêm), nên gọi lại nhiều lần vô hại.
- `src/main.py` lifespan: nếu `SEED_ON_START=true` thì `init_db()` rồi
  `bootstrap()` — Render khởi động lần đầu là có sẵn danh mục, toà, tài khoản demo.
- `render.yaml`: web service chạy từ `Dockerfile` sẵn có + PostgreSQL, khai báo env
  (`DATABASE_URL`, `VISION_PROVIDER`, `GEMINI_API_KEY`, `JWT_SECRET`,
  `LOCAL_MODEL_ENABLED=false`, `SEED_ON_START=true`, `CORS_ORIGINS`).
- Thêm vào `KNOWN_LIMITATIONS` một dòng: *"Bản demo trên hạ tầng miễn phí lưu ảnh
  trên đĩa tạm — ảnh đã tải lên sẽ mất khi máy chủ khởi động lại."* Khối này đã
  hiển thị sẵn trên trang Vận hành nên không phải sửa UI.

## Giai đoạn D — Capacitor → APK

**Thêm:** `frontend/capacitor.config.ts`, `frontend/android/` (commit vào repo),
`frontend/src/lib/platform.ts`.
**Sửa:** `frontend/next.config.ts`, `frontend/src/components/resident/ask.tsx`,
`frontend/src/app/page.tsx`.

- Cài `@capacitor/core`, `@capacitor/cli`, `@capacitor/android`, `@capacitor/camera`,
  `@capacitor/splash-screen`.
- `next.config.ts`: `output: "export"`, `images: { unoptimized: true }`.
- `capacitor.config.ts`: `appId: "vn.greenbin.app"`, `appName: "GreenBin AI"`,
  `webDir: "out"`.
- `npx cap add android` chạy **được trên máy không có Android SDK** (nó chỉ chép
  khung dự án); commit `frontend/android/`, thêm thư mục build của nó vào
  `.gitignore`. Chỉnh `AndroidManifest.xml`: quyền `CAMERA` + `INTERNET`.
- `platform.ts` — một hàm `chupAnh(): Promise<File>`:
  - chạy trong app native → `@capacitor/camera` (mở camera thật, đúng quyền);
  - chạy trên web → giữ nguyên `<input type="file" capture>` hiện có.

  `ask.tsx` gọi hàm này thay vì thao tác trực tiếp với `<input>`.
- `page.tsx`: đăng nhập vai **manager** trong app native → hiện màn "Console ban
  quản lý thiết kế cho máy tính, mở `<link web>` giúp mình nhé" kèm nút đăng xuất.
  Trên web thì vẫn vào console như hiện tại.

## Giai đoạn E — Git, CI, phát hành

**Thêm:** `.github/workflows/android.yml`. **Sửa:** `.github/workflows/ci.yml`.

- `git init` → commit đầu → tạo repo GitHub → push. Ngay sau đó chạy
  `scripts/setup_hooks.ps1` để AI logging bắt đầu ghi (deliverable #4).
- `ci.yml`: thêm job `frontend` chạy `npm ci`, `tsc --noEmit`, `next build` —
  hiện CI mới kiểm phần Python.
- `android.yml`: kích hoạt khi đẩy tag `v*` → JDK 17 + Android SDK (action có
  sẵn) → `npm ci` → `next build` (với `NEXT_PUBLIC_API_URL` từ secret) →
  `cap sync android` → `gradlew assembleDebug` → đính `app-debug.apk` vào
  GitHub Release của tag đó.
  Dùng **APK debug**: cài được ngay, không cần giữ keystore trong secret. Muốn lên
  Google Play mới cần bản ký release — ghi vào backlog, không làm bây giờ.
- Vercel: nối repo, thư mục gốc `frontend`, đặt `NEXT_PUBLIC_API_URL` = URL Render.
- Cập nhật `CORS_ORIGINS` trên Render bằng domain Vercel thật sau khi có.

## Giai đoạn F — Kiểm chứng và tài liệu

- `python -m pytest tests -q` (76 test hiện có phải còn xanh sau khi tách
  requirements và sửa lifespan).
- `npx tsc --noEmit` + `npx next build` — xác nhận export tĩnh ra `out/` sạch.
- Mở web đã deploy bằng trình duyệt: đăng nhập cả 3 vai trò, chạy lại đúng mạch
  đã kiểm ngày 01/08 (chặn cứng "kim tiêm" → duyệt tuyến gộp), lần này qua **URL
  thật** chứ không phải localhost.
- Kiểm offline: bật chế độ ngoại tuyến trong trình duyệt → màn Lịch thu gom phải
  vẫn xem được, các màn khác hiện `ErrorState` có mã `NET-503` (đã có sẵn).
- Tải APK từ Release về, cài lên điện thoại Android, thử chụp một tấm.
  *Việc này phải có người cầm máy thật.*
- Cập nhật `README.md` (mục "Cài app" + 3 đường cài), `CLAUDE.md` mục 10–11,
  `WORKLOG.md`, và **ADR-0005: chọn PWA + Capacitor thay vì viết lại native**.

---

## Thứ tự thực hiện

**A → C → B → D → E → F.**

Giai đoạn C đứng trước B và D vì **URL Render phải có trước** khi build PWA và APK
(URL bị nướng vào lúc build). A làm trước vì icon của Giai đoạn B lấy từ đó.

## Việc chủ dự án phải tự làm

1. Tạo tài khoản Render + Vercel, bấm nối repo GitHub.
2. Tạo repo trên GitHub (session sau sẽ chuẩn bị sẵn commit và lệnh push).
3. Điền `GEMINI_API_KEY` vào biến môi trường trên Render — **vẫn là việc chặn
   luồng chụp ảnh**, không có nó thì app cài về vẫn không nhận diện được rác.
4. Cắm điện thoại Android thử file APK sau khi CI build xong.

## Rủi ro đã lường trước

- **Máy chủ miễn phí ngủ khi rảnh** → request đầu tiên chậm. Trước lúc demo phải
  mở web một lần cho nó thức dậy. Ghi vào README.
- **Ảnh upload mất khi restart** — đã nêu ở Giai đoạn C, ghi thẳng lên UI.
- **Tầng T0.5 không chạy trên bản deploy** (thiếu RAM cho torch). Trang Vận hành
  đã có sẵn dòng "Model local: đang tắt" nên số liệu vẫn trung thực.
- **CI build APK lần đầu hay hỏng vặt** (phiên bản JDK, Gradle). Quá 2 lần chạy
  vẫn đỏ thì lui về build tay trên máy.
