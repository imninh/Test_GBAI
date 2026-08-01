# GreenBin AI — Agent Phân loại Rác & Điều phối Thu gom Tái chế

Mã đề **VHR-17** · AI20K Build Phase Cohort 2

Lớp vận hành cho toà chung cư: AI Agent phân loại rác qua **ảnh hoặc mô tả bằng
chữ** → **tự sinh hành động trong hệ thống** (cảnh báo rác nguy hại, tạo yêu cầu
thu gom, gộp tuyến) → **người duyệt trước khi chốt**.

Người dùng chính là **ban quản lý và đội vệ sinh**, không phải cư dân
([ADR-0002](docs/decisions/0002-chuyen-trong-tam-sang-van-hanh.md)).

> README của template gốc giữ ở [README_boilerplate.md](README_boilerplate.md).

---

## Chạy thử

```bash
pip install -r requirements.txt
python scripts/seed.py --reset --demo
python -m uvicorn src.main:app --port 8000
```

```bash
npm --prefix frontend install
npm --prefix frontend run dev
```

Mở http://localhost:3000 · API docs ở http://localhost:8000/docs

Muốn chạy thêm **tầng T0.5 (model local CLIP)** thì cài riêng — `torch` nặng
1,19 GB nên không nằm trong `requirements.txt`:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements-local-model.txt
```

### Tài khoản demo

Màn đăng nhập có **3 nút vào thẳng**, không cần gõ gì.

| Vai trò | Email | Mật khẩu |
|---|---|---|
| Cư dân | `resident@demo.vn` | `demo1234` |
| Đội vệ sinh | `cleaner@demo.vn` | `demo1234` |
| Ban quản lý | `manager@demo.vn` | `demo1234` |

---

## Cài app

**Cư dân và đội vệ sinh dùng app trên điện thoại; ban quản lý dùng web trên máy
tính** — console của họ là bảng nhiều cột, thiết kế cho màn hình rộng. Đăng nhập
vai ban quản lý *trong app* sẽ hiện màn chỉ sang web thay vì nhồi console vào
màn 6 inch.

Trang hướng dẫn ngay trong sản phẩm: **`/tai-app`**.

| Máy | Cách cài | Ghi chú |
|---|---|---|
| Android | Tải `.apk` ở [Releases](../../releases/latest) | Bản **debug**, chưa ký để lên Google Play |
| Android (không muốn cài APK) | Mở web bằng Chrome → *Cài ứng dụng* | Cùng một giao diện |
| iPhone / iPad | Safari → Chia sẻ → *Thêm vào MH chính* | |
| Máy tính | Mở thẳng web | |

⚠️ **Không có bản cài cho iPhone.** Nhóm phát triển trên Windows nên không build
được IPA; iPhone đi đường PWA. Nói rõ ở đây và trên `/tai-app` thay vì hứa suông.

APK do GitHub Actions build: đẩy một tag `v*` là workflow
[`android.yml`](.github/workflows/android.yml) build rồi đính file vào Release
của tag đó.

```bash
git tag v0.1.0 && git push origin v0.1.0
```

Trước đó phải đặt hai biến trong *Settings → Secrets and variables → Actions →
Variables*: `NEXT_PUBLIC_API_URL` và `NEXT_PUBLIC_WEB_URL`. **URL bị nướng vào
lúc build**, nên thiếu là APK ra sẽ trỏ vào `localhost` và không chạy trên điện
thoại — workflow dừng sớm với câu lỗi rõ ràng nếu thiếu.

### Xem offline

Service worker (`frontend/public/sw.js`, viết tay ~120 dòng) cache vỏ ứng dụng
và **ba endpoint tra cứu công khai** (`/categories`, `/meta/enums`,
`/buildings/*/schedule`) theo kiểu stale-while-revalidate → **màn Lịch thu gom
xem được khi không có mạng**. Hầm để xe và khu thùng rác sóng rất yếu; đó là bối
cảnh sử dụng thật.

**Không bao giờ cache ảnh cư dân hay endpoint có token** — quyền riêng tư đứng
trước tiện lợi.

---

## Deploy

| Phần | Nơi | File cấu hình |
|---|---|---|
| Backend + PostgreSQL | Render | [`render.yaml`](render.yaml) |
| Frontend (web) | Vercel | thư mục gốc `frontend`, đặt `NEXT_PUBLIC_API_URL` |
| APK | GitHub Actions → Releases | [`android.yml`](.github/workflows/android.yml) |

Thứ tự bắt buộc: **backend trước**, vì URL của nó bị nướng vào lúc build cả web
lẫn APK. Có URL Render rồi mới build hai cái kia; sau khi có domain Vercel thì
quay lại cập nhật `CORS_ORIGINS` trên Render.

`CORS_ORIGINS` phải chứa cả `https://localhost` và `capacitor://localhost` —
đó là origin mà app Android đóng gói bằng Capacitor tự dùng. Thiếu là app cài về
gọi API bị chặn.

### Giới hạn của hạ tầng miễn phí

Ba điều dưới đây đã ghi thẳng lên **trang Vận hành của sản phẩm**, không giấu
trong báo cáo:

- **Máy chủ ngủ khi rảnh** → request đầu tiên chậm vài chục giây. *Trước lúc
  demo phải mở web một lần cho nó thức dậy.*
- **Đĩa là tạm thời** → ảnh cư dân đã tải lên mất khi service khởi động lại.
- **Không đủ RAM cho `torch`** → tầng T0.5 tắt trên bản deploy
  (`LOCAL_MODEL_ENABLED=false`), ảnh đi thẳng lên T1. Trang Vận hành hiện
  "Model local: đang tắt" nên số liệu vẫn trung thực.

Render tự nạp dữ liệu nền lúc khởi động (`SEED_ON_START=true`) vì ở đó không có
chỗ chạy tay `scripts/seed.py`. Gọi lại nhiều lần vô hại — dữ liệu nền cập nhật
bản ghi cũ, dữ liệu demo bị chặn nếu đã có.

---

## Cấu hình model

**Đổi nhà cung cấp model chỉ bằng sửa `.env`, không sửa code.**

```bash
cp .env.example .env
# VISION_PROVIDER=gemini | openai | openrouter | nvidia | local_only
# rồi điền key tương ứng
```

| Provider | Nhận ảnh? | Ghi chú |
|---|---|---|
| Gemini | ✅ | mặc định, free tier rộng |
| OpenAI | ✅ | `gpt-4o-mini` → `gpt-4o`, đúng kiến trúc gốc trong ADR |
| OpenRouter | ✅ | một key vào được nhiều model |
| NVIDIA NIM | ✅ | API tương thích OpenAI |
| DeepSeek | ❌ | **chỉ text** — không dùng được cho phân loại ảnh |

Tầng **T0.5 chạy local** bằng CLIP zero-shot (`openai/clip-vit-base-patch32`,
~350MB, tải một lần rồi chạy offline trên CPU). Chưa có API key thì phần chặn
cứng, thu gom, tuyến, vận hành **vẫn chạy đầy đủ**; chỉ luồng nhận diện ảnh cần key.

---

## Kiến trúc

```
Ảnh / mô tả bằng chữ
      ▼
TIỀN XỬ LÝ ẢNH  tước EXIF · làm mờ khuôn mặt · nén 512px · tính pHash
      ▼
classify_waste   T0 cache pHash ($0) → T0.5 CLIP local ($0) → T1 → T2
      ▼
   chặn cứng? / dưới ngưỡng nhóm?  ──►  TỪ CHỐI trả lời + chuyển người
      ▼ không
advise (RAG)  truy hồi quy định của ĐÚNG TOÀ ĐÓ → hướng dẫn có trích nguồn
      ▼
schedule_pickup  vượt ngưỡng → HITL ban quản lý → gộp tuyến → HITL đội trưởng
```

Chi tiết: [ARCHITECTURE.md](ARCHITECTURE.md) · [CLAUDE.md](CLAUDE.md) mục 4

### Ba điểm HITL

1. Yêu cầu thu gom vượt ngưỡng → ban quản lý duyệt. Ngưỡng so với **cận trên**
   của khoảng khối lượng, vì vision ước lượng kg từ ảnh sai là chuyện bình thường
   và sai số phải nghiêng về phía cần người duyệt.
2. Phân loại confidence thấp / nghi nguy hại → người xác nhận nhãn.
3. Tuyến do agent gộp → đội trưởng duyệt. **Agent không được tự đổi lịch làm
   việc của con người.**

### An toàn AI

- Nhóm nguy hại dùng **ngưỡng confidence cao hơn hẳn**; dưới ngưỡng thì từ chối
  trả lời dứt khoát và chuyển người, vẫn hiện phỏng đoán nhưng **không kèm
  hướng dẫn xử lý**.
- **Danh sách chặn cứng** (vật sắc nhọn y tế · bình gas · hoá chất) chặn **trước
  khi gọi model**, bỏ qua confidence.
- Cảnh báo an toàn là **text cố định lấy từ danh mục trong CSDL**, không do LLM
  sinh — UI ghi rõ điều đó.
- Ảnh: tước toàn bộ EXIF (gồm GPS), làm mờ khuôn mặt, nén 512px, có hạn lưu trữ.
  Màn "Ảnh của tôi được xử lý thế nào" cho cư dân xem hệ thống đã xoá những gì.
  Ảnh gốc chỉ ban quản lý mở được và **mỗi lần mở đều ghi audit log**.

---

## Kiểm thử

```bash
python -m pytest tests -q      # 76 test, không test nào gọi API thật
python -m ruff check src tests
```

Model được mock qua `FakeVisionClient` trong `tests/conftest.py` — chi phí test bằng 0.

---

## Cấu trúc

```
src/
  agents/       graph LangGraph: classify → advise → schedule
  api/          router, dependency, khuôn lỗi, serializer
  db/           models (21 bảng), session, dữ liệu nền
  services/     image · vision/ · classifier · safety · rag · pickup ·
                route_planner · metrics · auth · runs
frontend/       Next.js 15 + Tailwind v4 — 21 màn, 3 vai trò
  public/sw.js  service worker: vỏ ứng dụng + 3 endpoint tra cứu, xem offline
  android/      khung app Capacitor, GitHub Actions build APK từ đây
scripts/seed.py nạp dữ liệu nền và dữ liệu demo
scripts/build_assets.py  cắt ảnh linh vật, sinh bộ icon PWA
docs/           FRONTEND_SPEC (hợp đồng API) · decisions/ (ADR) · research/
original/       bản thiết kế giao diện gốc
```

---

## Dữ liệu

**Chỉ dùng dữ liệu công khai, mô phỏng hoặc đã ẩn danh.** Toàn bộ toà nhà, căn
hộ, cư dân trong hệ thống là nhân vật mô phỏng.

Bản ghi sinh bằng `--demo` gắn cờ `is_seed=True`, và UI **hiện nhãn "dữ liệu
demo mô phỏng"** ở mọi nơi chúng xuất hiện — số mô phỏng và số đo thật không
trộn vào nhau mà không nói gì.

⚠️ Các đoạn trích luật trong kho quy định là **diễn giải rút gọn**, có cờ
`needs_verification`. Phải mở văn bản gốc đối chiếu điều khoản và hiệu lực hiện
hành trước khi trích dẫn ra ngoài.

Nguồn dataset dự kiến cho eval: TrashNet · RealWaste · TACO · Roboflow Universe,
cộng bộ ảnh tự chụp tại Việt Nam. **Bộ tự chụp là bộ quan trọng nhất** — model
đạt 94% trên TrashNet chỉ còn 41% trên ảnh rác thật
([khảo sát](docs/research/sota-model-nhe-phan-loai-rac.md)).

---

## Giới hạn đã biết

Khối này hiển thị ngay trên trang Vận hành của sản phẩm, không giấu trong báo cáo:

- Nhận diện tốt nhất với **một món rác, chụp rõ, đủ sáng**.
- **Không nhìn xuyên được túi nilon đục** — rác đã đóng túi kín nằm ngoài phạm
  vi, có chủ đích ([ADR-0003](docs/decisions/0003-phan-tang-rac-va-trong-tam-doi-ve-sinh.md)).
- Không phân biệt được nhựa PET và HDPE khi nhãn bị mờ.
- **Không xác định được rác y tế lây nhiễm** — luôn chuyển người.
- Quy định khác nhau giữa các toà; hướng dẫn chỉ đúng với toà đang chọn.
- Khối lượng AI ước lượng sai số ±40% — đội vệ sinh cân lại tại chỗ.
- **Bản demo trên hạ tầng miễn phí lưu ảnh trên đĩa tạm** — ảnh đã tải lên mất
  khi máy chủ khởi động lại.
- **Tầng T0.5 tắt trên bản deploy** vì máy chủ miễn phí không đủ bộ nhớ cho
  `torch`; ảnh đi thẳng lên tầng T1.
