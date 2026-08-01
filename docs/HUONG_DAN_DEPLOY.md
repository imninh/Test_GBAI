# Hướng dẫn deploy GreenBin AI

> Làm **đúng thứ tự dưới đây**. Lý do: `NEXT_PUBLIC_API_URL` bị **nướng vào lúc
> build** cả bản web lẫn file APK. Build trước khi có URL backend thì ra một bản
> trỏ vào `localhost` — mở lên là màn trắng, và phải build lại từ đầu.

Tổng thời gian: khoảng **60–90 phút** cho lần đầu. Ba tài khoản cần tạo, đều
miễn phí và không cần thẻ: **GitHub · Render · Vercel**.

```
GitHub  ──►  Render (backend + PostgreSQL)  ──►  Vercel (web)  ──►  APK
   1              2  ← có URL API ở đây          3                  4
```

---

## Bước 0 — Chuẩn bị (5 phút)

Cần có sẵn:

- [ ] Tài khoản GitHub
- [ ] **API key vision.** Không có thì mọi thứ vẫn deploy được, chỉ luồng nhận
      diện ảnh dừng ở màn "không đủ chắc chắn". Lấy Gemini ở
      [aistudio.google.com](https://aistudio.google.com/apikey) hoặc NVIDIA ở
      [build.nvidia.com](https://build.nvidia.com) — xem mục "Chọn model" cuối file.

Repo đã `git init` và tạo sẵn commit đầu. Kiểm nhanh:

```bash
git log --oneline -1
```

---

## Bước 1 — Đưa mã lên GitHub (10 phút)

Tạo repo **rỗng** trên github.com (đừng tick "Add README" — repo này đã có sẵn).
Đặt **Private** cũng được; Render và Vercel vẫn đọc được sau khi bạn cấp quyền.

```bash
git remote add origin https://github.com/<tên-bạn>/<tên-repo>.git
git branch -M main
git push -u origin main
```

Ngay sau khi push xong, bật AI logging (deliverable #4):

```bash
powershell -ExecutionPolicy Bypass -File scripts/setup_hooks.ps1
```

Nhớ thay `AI_LOG_API_KEY` trong `.env` bằng key riêng từ link mời của ban tổ
chức — giá trị trong `.env.example` chỉ là chỗ giữ chỗ.

> ⚠️ Kiểm trước khi push: `git ls-files | grep -E "^\.env$"` phải **không ra gì**.
> File `.env` chứa API key và không bao giờ được commit.

---

## Bước 2 — Backend lên Render (20 phút)

1. Đăng ký [render.com](https://render.com) bằng chính tài khoản GitHub.
2. Vào thẳng **<https://dashboard.render.com/blueprints>** → **New Blueprint Instance**
   → chọn repo vừa push.

   > ⚠️ **Không dùng nút "New service"** ở cuối danh sách service trong một
   > project — menu đó chỉ tạo từng service lẻ (Static Site, Web Service,
   > Postgres…) và **không có mục Blueprint**. Blueprint nằm ở nút **"New"**
   > toàn cục phía trên, hoặc đi thẳng bằng đường dẫn ở trên cho nhanh.
3. Render đọc [`render.yaml`](../render.yaml) và tự dựng **hai** thứ: một web
   service (`greenbin-api`) và một PostgreSQL (`greenbin-db`), tự nối
   `DATABASE_URL` giữa chúng. Không phải cấu hình tay.
4. Render sẽ hỏi ba biến để trống có chủ đích:

   | Biến | Điền gì |
   |---|---|
   | `GEMINI_API_KEY` | key Gemini — lo tầng T2 và bước sinh hướng dẫn |
   | `NVIDIA_API_KEY` | key NVIDIA NIM — lo tầng T1, tầng ăn phần lớn lưu lượng |
   | `CLIP_ASSETS_URL` | link tải bộ model T0.5 (xem mục bên dưới). **Để trống cũng chạy** — chỉ là tầng T0.5 tự tắt |
   | `CORS_ORIGINS` | **tạm** điền `https://localhost,capacitor://localhost`. Bước 3 sẽ quay lại sửa |

   > Thiếu key của tầng nào thì **chỉ tầng đó dừng**, các tầng còn lại vẫn chạy.
   > Trang Vận hành có bảng chỉ rõ tầng nào đang thiếu key.

5. Bấm Apply rồi chờ. Lần build đầu mất **5–10 phút** (dựng Docker image).

**Kiểm:** mở `https://<tên-service>.onrender.com/health`, phải ra:

```json
{"status":"ok","env":"production"}
```

**Ghi lại URL này.** Ba bước sau đều cần nó.

<details>
<summary>Máy chủ tự nạp dữ liệu nền — không phải chạy seed tay</summary>

`render.yaml` đặt `SEED_ON_START=true`, nên lúc khởi động máy chủ tự tạo bảng và
nạp 9 nhóm rác, 3 toà, 8 tài khoản demo, lịch thu gom, 5 tài liệu quy định.
Gọi lại nhiều lần vô hại: nhóm dữ liệu nền cập nhật bản ghi cũ, còn dữ liệu demo
bị chặn nếu đã có. Đăng nhập bằng `manager@demo.vn` / `demo1234` để kiểm.
</details>

---

## Bước 3 — Web lên Vercel (15 phút)

1. Đăng ký [vercel.com](https://vercel.com) bằng tài khoản GitHub.
2. **Add New → Project** → chọn repo.
3. **Root Directory: `frontend`** ← quan trọng, không đặt là gãy build.
4. Thêm Environment Variables:

   | Tên | Giá trị |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | URL Render ở bước 2, **không có dấu `/` cuối** |
   | `NEXT_PUBLIC_WEB_URL` | domain Vercel (điền sau lần deploy đầu, rồi deploy lại) |
   | `NEXT_PUBLIC_GITHUB_REPO` | `<tên-bạn>/<tên-repo>` — để trang `/tai-app` trỏ đúng chỗ tải APK |

5. Deploy. Ghi lại domain, dạng `https://<tên>.vercel.app`.

### Quay lại Render mở CORS — **bỏ bước này là app không gọi được API**

Vào Render → service `greenbin-api` → Environment → sửa `CORS_ORIGINS` thành:

```
https://<tên>.vercel.app,https://localhost,capacitor://localhost
```

Hai giá trị `localhost` phía sau là origin mà **app Android đóng gói bằng
Capacitor** tự dùng khi phục vụ giao diện từ trong máy. Thiếu chúng thì web chạy
bình thường nhưng **app cài về gọi API bị chặn** — lỗi rất khó đoán vì trình
duyệt chạy tốt.

Render tự khởi động lại sau khi lưu.

**Kiểm:** mở domain Vercel, đăng nhập cả 3 vai trò bằng ba nút vào thẳng ở màn
đăng nhập.

---

## Bước 4 — File APK (15 phút, chờ CI)

1. Trên GitHub: **Settings → Secrets and variables → Actions → Variables** →
   New repository variable:

   | Tên | Giá trị |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | URL Render |
   | `NEXT_PUBLIC_WEB_URL` | domain Vercel |

   Đây là **Variables**, không phải Secrets — chúng nằm trong bundle công khai
   nên giấu cũng vô nghĩa.

2. Đẩy một tag:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. Xem tiến trình ở tab **Actions**. Khoảng 5–8 phút. Xong thì file
   `GreenBinAI-v0.1.0.apk` nằm trong **Releases**.

Nếu quên đặt hai biến trên, workflow **dừng sớm** với câu lỗi rõ ràng thay vì
build ra một file APK hỏng.

**Kiểm:** tải APK về máy Android, cài, mở, đăng nhập, chụp thử một tấm.

---

## Bước 5 — Kiểm chứng cuối (10 phút)

- [ ] `https://<render>/health` ra `{"status":"ok","env":"production"}`
- [ ] Vào web Vercel, đăng nhập cả **3 vai trò**
- [ ] Chạy lại mạch demo: gõ "kim tiêm" ở màn Hỏi → phải **chặn cứng, chuyển người**
- [ ] Vai ban quản lý: duyệt một tuyến gộp → thông báo về phía cư dân
- [ ] **Kiểm offline:** DevTools → Network → Offline → tải lại. Màn **Lịch thu gom
      vẫn xem được**; các màn khác hiện `ErrorState` mã `NET-503`
- [ ] Trên điện thoại Android: mở web bằng Chrome → menu → **Cài ứng dụng**
- [ ] Cài file APK, chụp thử một tấm bằng camera thật
- [ ] Đăng nhập vai **ban quản lý trong app** → phải hiện màn chỉ sang web,
      không phải console bị bóp vào màn 6 inch

---

## Ba giới hạn của hạ tầng miễn phí — nói trước khi bị hỏi

Cả ba đã hiện sẵn trên **trang Vận hành của sản phẩm**, không giấu trong báo cáo:

| Giới hạn | Hệ quả thực tế |
|---|---|
| Máy chủ **ngủ khi rảnh** | Request đầu tiên chậm 30–60 giây. **Trước lúc demo phải mở web một lần cho nó thức dậy** |
| Đĩa là **tạm thời** | Ảnh cư dân đã tải lên **mất khi service khởi động lại** |
| Không đủ RAM cho `torch` | Tầng T0.5 tắt (`LOCAL_MODEL_ENABLED=false`), ảnh đi thẳng lên T1. Trang Vận hành hiện "Model local: đang tắt" nên số liệu vẫn trung thực |

---

## Chọn model vision

Đổi nhà cung cấp **chỉ bằng sửa biến môi trường trên Render**, không sửa code:

```
VISION_PROVIDER=gemini      # hoặc nvidia | openai | openrouter
GEMINI_API_KEY=...
```

### Mỗi tầng một nhà cung cấp

`VISION_PROVIDER` là mặc định chung. Khai thêm ba biến dưới đây để **trộn nhà
cung cấp theo tầng** — để trống thì tầng đó dùng mặc định chung:

```
VISION_PROVIDER_T1=nvidia     # tầng ăn phần lớn lưu lượng → nơi có quota rộng
VISION_PROVIDER_T2=gemini     # chỉ chạy khi ca khó → chịu được quota hẹp
VISION_PROVIDER_TEXT=gemini   # sinh hướng dẫn + hỏi bằng chữ
```

Vì sao cần: free tier của `gemini-flash-latest` chỉ **20 request/ngày** (đo
01/08/2026), mà mỗi lần chụp ảnh tiêu 2 request → **10 lần chụp là hết**. Để cả
hệ thống trên một nhà cung cấp thì cạn quota là sản phẩm đứng; trải ra ba nguồn
thì mất một nguồn chỉ mất một tầng.

Cả hai key phải có mặt cùng lúc: `GEMINI_API_KEY` **và** `NVIDIA_API_KEY`.
Kiểm bằng `GET /api/v1/ops/metrics` → khối `provider.tiers` liệt kê từng tầng
kèm cờ `has_api_key`; trang Vận hành hiện đúng bảng đó.

---

## Bật tầng T0.5 trên bản deploy

Máy chủ gói free chỉ có **512 MB RAM** nên không cõng nổi CLIP bản đầy đủ. Bản
đã nén (chỉ nửa ảnh, int8) thì vừa: đo được **185 MB RAM · 56 ms/ảnh**. Xem
[ADR-0007](decisions/0007-tang-t05-chay-onnx-int8.md).

Ba bước, làm một lần:

1. **Sinh bộ file** trên máy có torch (hoặc Google Colab bản miễn phí):

   ```bash
   pip install -r requirements-local-model.txt
   python scripts/export_clip_onnx.py --anh data/media/<một-ảnh>.jpg
   ```

   Ra hai file trong `assets/clip/`: `clip_vision_int8.onnx` (~89 MB) và
   `clip_text_embeddings.json`. Script in ra mức lệch so với bản gốc — **đọc
   con số đó**, nếu nó báo hai bản chọn khác nhóm thì đừng dùng.

2. **Nén rồi đính vào GitHub Release** (không commit vào repo — 89 MB sẽ nằm
   trong lịch sử git vĩnh viễn):

   ```bash
   tar -czf clip-assets.tar.gz -C assets/clip clip_vision_int8.onnx clip_text_embeddings.json
   ```

   Tải file này lên phần Releases của repo.

3. **Dán link vào `CLIP_ASSETS_URL`** trên Render rồi redeploy.

   Nhận cả hai dạng link:
   - link **file**: `…/releases/download/<tag>/clip-assets.tar.gz` — chuẩn nhất;
   - link **trang** Release: `…/releases/tag/<tag>` — máy chủ tự tra ra file
     `.tar.gz` đính kèm. Nút copy của GitHub cho ra dạng này nên rất dễ dán nhầm.

   Máy chủ tự tải về lúc khởi động — đĩa gói free là đĩa tạm nên nó tải lại sau
   mỗi lần restart, chạy ở luồng nền nên không chặn request nào.

**Kiểm:** trang Vận hành, dòng T0.5 phải hiện *"bản nén int8, chạy tại chỗ"*.

⚠️ Đổi câu mô tả `clip_prompts` trong danh mục rác thì **phải chạy lại bước 1**.
Không chạy lại thì tầng T0.5 tự tắt kèm cảnh báo trong log — cố ý làm vậy để nó
không chấm bằng bộ câu cũ trong im lặng.

| Provider | Free tier | Nhận ảnh | Ghi chú |
|---|---|---|---|
| **Gemini** | rộng, không cần thẻ | ✅ | Mặc định. Bám khuôn JSON chắc nhất |
| **NVIDIA NIM** | ~1.000 credit, không cần thẻ | ✅ | Phải chọn **model vision-language**, không phải model "object detection" — xem dưới |
| OpenRouter | tuỳ model | ✅ | Một key vào được nhiều model |
| DeepSeek | — | ❌ | **Chỉ text**, không dùng được cho T1/T2 |

### Trên NVIDIA phải lấy đúng nhóm model

Nhóm **Object Detection** trên build.nvidia.com **không dùng được cho đề này** —
toàn bộ là model bóc bố cục tài liệu (phát hiện bảng, biểu đồ, tiêu đề trong văn
bản), và chúng chỉ cho tải về tự host chứ không có endpoint miễn phí.

Cái cần lấy là **vision-language model**: nó nhận ảnh và trả về **văn bản JSON**
có `category_code`, `confidence`, `reason` — đúng khuôn mà `classify_waste` cần
để chảy tiếp vào ngưỡng an toàn và luồng từ chối trả lời.

Tên model điền vào `.env` (để trống thì tự lấy mặc định của provider):

```
VISION_MODEL_T1=meta/llama-3.2-11b-vision-instruct
VISION_MODEL_T2=meta/llama-3.2-90b-vision-instruct
```

Đáng thử thêm nếu hai cái trên yếu: `nvidia/llama-3.1-nemotron-nano-vl-8b-v1`,
`meta/llama-4-scout-17b-16e-instruct`, `nvidia/nemotron-nano-12b-v2-vl`.

> **Lỗi có thể gặp:** code gửi kèm `response_format: {"type":"json_object"}`; một
> số model trên NIM không nhận tham số này và trả về **400**. Câu lỗi sẽ là
> *"Model trả về lỗi 400. Kiểm tra tên model và API key trong .env."* Sửa 3 dòng
> trong `src/services/vision/openai_compat.py` là xong.

---

## Gặp sự cố

| Triệu chứng | Nguyên nhân thường gặp |
|---|---|
| Web chạy nhưng mọi lệnh gọi API lỗi | `CORS_ORIGINS` trên Render chưa có domain Vercel |
| App cài về gọi API bị chặn, web thì không | Thiếu `https://localhost` và `capacitor://localhost` trong `CORS_ORIGINS` |
| APK mở ra màn trắng | Build lúc chưa đặt `NEXT_PUBLIC_API_URL` → đang trỏ `localhost` |
| Backend chết ngay khi khởi động | DSN PostgreSQL kiểu `postgres://`. Code đã tự chuẩn hoá — nếu vẫn lỗi thì xem log Render |
| Request đầu tiên rất chậm rồi sau đó nhanh | Máy chủ miễn phí vừa ngủ dậy. Bình thường |
| Đổi biến môi trường mà web không đổi theo | Biến `NEXT_PUBLIC_*` nướng vào lúc build — phải **deploy lại** Vercel, không chỉ lưu biến |
