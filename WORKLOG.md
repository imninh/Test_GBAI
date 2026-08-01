# Worklog — Team [Tên Team] · GreenBin AI (VHR-17)

> Ghi lại tất cả công việc đã làm theo ngày. Ai làm gì, kết quả gì.
> Đây là deliverable #9 — đừng bỏ ngày, viết bù cả tuần là nhìn ra ngay.

---

## 2026-07-27

| Member | Task | Status | Output | Time |
|--------|------|--------|--------|------|
| [Tên] | Rà 4 đề tài, so sánh dữ liệu / demo / giá trị KD / độ phủ PLO | ✅ Done | `docs/decisions/0001-chon-de-tai-greenbin.md` | — |
| [Tên] | **Chốt đề VHR-17 GreenBin AI** | ✅ Done | ADR-0001 | — |
| [Tên] | Thiết kế schema DB (14 bảng) | ✅ Done | `src/db/models.py` — smoke test tạo bảng OK | — |
| [Tên] | Lớp kết nối DB | ✅ Done | `src/db/session.py` | — |
| [Tên] | Ẩn danh PII trong text | ✅ Done | `src/services/pii.py` — test tay: SĐT/email/tên bị che, `contains_pii()` trả rỗng | — |
| [Tên] | Gộp trùng + ước lượng token | ✅ Done | `src/services/dedup.py` | — |
| [Tên] | Băm mật khẩu PBKDF2 | ✅ Done | `src/services/security.py` | — |
| [Tên] | Cấu hình 2 tầng model + ngân sách | ✅ Done | `src/config.py` | — |
| [Tên] | Bối cảnh dự án nạp tự động cho session sau | ✅ Done | `CLAUDE.md` | — |
| [Tên] | `git init`, `.env`, `setup_hooks.ps1` | ❌ Blocked | chưa làm — AI logging (deliverable #4) chưa chạy | — |
| [Tên] | Viết lại `docs/FRONTEND_SPEC.md` cho GreenBin | 🔄 WIP | spec hiện tại đang là của đề VoC cũ | — |

**Tổng kết ngày:** Chốt được đề tài và dựng xong phần nền dùng chung (DB, PII, bảo mật, cấu hình). Chưa chạm vision/RAG/API. Việc tiếp theo xem mục 11 của `CLAUDE.md`.

---

## 2026-07-28

| Member | Task | Status | Output | Time |
|--------|------|--------|--------|------|
| [Tên] | Viết lại đặc tả frontend cho GreenBin (thay bản của đề VoC cũ) | ✅ Done | `docs/FRONTEND_SPEC.md` v1.0 — 18 màn, 3 vai trò, 3 điểm HITL, hợp đồng API, kịch bản demo 7 bước | — |
| [Tên] | Lưu spec frontend cũ của đề VoC vào attic | ✅ Done | `attic/voc/FRONTEND_SPEC_voc.md` | — |
| [Tên] | Mang spec sang công cụ design, dựng giao diện | 🔄 WIP | chia 4 lượt dán theo mục 12 của spec | — |
| [Tên] | `git init`, `.env`, `setup_hooks.ps1` | ❌ Blocked | vẫn chưa làm — AI logging (deliverable #4) chưa chạy | — |

**Tổng kết ngày:** Chốt xong đặc tả giao diện. Hợp đồng API ở mục 7 của spec là ràng buộc cho backend về sau. Bước kế: dựng giao diện bằng công cụ design, song song với các việc backend ở mục 11 của `CLAUDE.md`.

---

## 2026-07-29

| Member | Task | Status | Output | Time |
|--------|------|--------|--------|------|
| Quân | Phỏng vấn 2 cư dân chung cư — phát hiện cư dân đã outsource việc phân loại cho lao công | ✅ Done | ghi nhận trong ADR-0002, mục Bối cảnh | — |
| Nghĩa | Đặt lại hướng: pain point nằm ở lao công / BQL / công ty xử lý rác | ✅ Done | ADR-0002 | — |
| Ninh | **ADR-0002 — chuyển trọng tâm sản phẩm từ cư dân sang vận hành** | ✅ Done | `docs/decisions/0002-chuyen-trong-tam-sang-van-hanh.md` | — |
| Ninh | Khảo sát SOTA model nhẹ / quantization / edge (Nghĩa giao) | ✅ Done | `docs/research/sota-model-nhe-phan-loai-rac.md` — khuyến nghị T0.5 để P1 | — |
| Ninh | Cập nhật `CLAUDE.md` theo ADR-0002 + thêm cảnh báo khoảng cách miền TrashNet↔RealWaste | ✅ Done | `CLAUDE.md` mục 1, 3, 6, 10, 11 | — |
| — | Phỏng vấn lao công + BQL để xác nhận pain point phía vận hành | ⬜ Chưa làm | chỗ yếu nhất của ADR-0002 | — |
| — | `git init`, `.env`, `setup_hooks.ps1` | ❌ Blocked | **treo sang ngày thứ 3** — AI logging (deliverable #4) vẫn chưa chạy | — |

**Tổng kết ngày:** Phỏng vấn cư dân cho kết quả ngược giả định ban đầu, nhóm chốt chuyển người dùng chính sang BQL + đội vệ sinh — giữ nguyên đề tài, kiến trúc và spec giao diện, chỉ đổi trọng tâm và câu chuyện. Phát hiện kỹ thuật quan trọng: model đạt 94% trên TrashNet chỉ còn 41% trên ảnh rác thật, nên bộ ảnh tự chụp là bộ dữ liệu quan trọng nhất chứ không phải bộ bổ sung. Loại dứt điểm hướng phần cứng/IoT/robot.

---

## 2026-07-30

| Member | Task | Status | Output | Time |
|--------|------|--------|--------|------|
| Ninh | Brainstorm thêm insight với Gemini về bối cảnh chung cư VinHomes | ✅ Done | `docs/Gemini_GBAI.md` — tài liệu brainstorm, không phải kế hoạch | — |
| Ninh | Rà soát tài liệu brainstorm: rút 3 insight có giá trị, bác phần lấy cư dân làm trung tâm | ✅ Done | ADR-0003 | — |
| Ninh | Chép đề bài gốc + quy định chung + 8 PLO từ ảnh thành text | ✅ Done | `docs/DE_BAI_VHR-17.md` — kèm mục 4 đối chiếu 4 chỗ nhóm lệch khỏi thẻ đề | — |
| Ninh | **ADR-0003 — phân tầng rác, giới hạn phạm vi vision, đội vệ sinh là người thao tác trung tâm** | ✅ Done | `docs/decisions/0003-phan-tang-rac-va-trong-tam-doi-ve-sinh.md` | — |
| Ninh | Cập nhật `CLAUDE.md` theo ADR-0003 (mục 1, 3, 10, 11) | ✅ Done | `CLAUDE.md` — thêm phạm vi luồng A/B, cảnh báo về tài liệu brainstorm, việc 16–22 | — |
| — | Đi chụp ảnh phòng rác tầng để kiểm ràng buộc "2–3 thùng" | ⬜ Chưa làm | 10 phút, ảnh thật dùng được cho slide | — |
| — | Phỏng vấn lao công + BQL để xác nhận pain point phía vận hành | ⬜ Chưa làm | vẫn là chỗ yếu nhất của ADR-0002 và ADR-0003 | — |
| — | `git init`, `.env`, `setup_hooks.ps1` | ❌ Blocked | **treo sang ngày thứ 4** — AI logging (deliverable #4) vẫn chưa chạy | — |

**Tổng kết ngày:** Phát hiện ràng buộc vật lý làm rõ phạm vi sản phẩm: vision không nhìn xuyên túi
nilon đục, nên phần lớn khối lượng rác hàng ngày **không đi qua AI, và đó là quyết định đúng** —
phần rác đi qua AI (tái chế, cồng kềnh, nguy hại) đúng là phần sinh tiền, sinh rủi ro pháp lý và
sinh rủi ro sức khoẻ. Ràng buộc này củng cố ADR-0002 chứ không phủ nhận: điểm chụp phải dịch về
phòng rác tầng do lao công thao tác, vì đó là nơi rác được mở túi. Hai trong ba ràng buộc chính
của ADR-0003 chưa được kiểm — cả hai kiểm được rẻ và nhanh, phải làm trước khi lên pitch deck.
Việc `git init` vẫn treo, sang ngày thứ 4.

---

## 2026-08-01

| Member | Task | Status | Output | Time |
|--------|------|--------|--------|------|
| Ninh | Cấu hình đa nhà cung cấp model — đổi provider chỉ bằng sửa `.env` | ✅ Done | `src/config.py`, `src/services/vision/` (Gemini · OpenAI-compatible · CLIP local) | — |
| Ninh | Tiền xử lý ảnh: tước EXIF, làm mờ mặt, nén 512px, pHash | ✅ Done | `src/services/image.py` + 6 test, có test khẳng định EXIF đã sạch | — |
| Ninh | Định tuyến 4 tầng T0 cache → T0.5 CLIP → T1 → T2 | ✅ Done | `src/services/classifier.py` — escalate cả khi **nghi nguy hại**, không chỉ khi confidence thấp | — |
| Ninh | Hàng rào an toàn: danh sách chặn cứng, ngưỡng riêng nhóm nguy hại, luồng từ chối trả lời | ✅ Done | `src/services/safety.py` — cảnh báo an toàn lấy từ CSDL, không do LLM sinh | — |
| Ninh | RAG hybrid BM25 + embedding, lọc theo toà trước khi xếp hạng | ✅ Done | `src/services/rag.py` — chạy được cả khi chưa có API key | — |
| Ninh | Thu gom + gộp tuyến + 3 điểm HITL | ✅ Done | `src/services/pickup.py`, `route_planner.py` — ngưỡng so với **cận trên** khoảng khối lượng (ADR-0003) | — |
| Ninh | Graph LangGraph thật `classify → advise → schedule` + ghi trace từng node | ✅ Done | `src/agents/`, `src/services/runs.py` | — |
| Ninh | API đầy đủ theo hợp đồng mục 7 + auth JWT phân quyền 3 vai trò | ✅ Done | `src/api/` — 44 route, khuôn lỗi `{error:{code,message_vi}}` | — |
| Ninh | Seed dữ liệu nền + dữ liệu demo gắn cờ `is_seed` | ✅ Done | `scripts/seed.py --reset --demo` — 9 nhóm rác, 3 toà, 8 tài khoản, 140 lượt phân loại mô phỏng | — |
| Ninh | Port toàn bộ bản thiết kế sang Next.js 15 + Tailwind v4 | ✅ Done | `frontend/` — 21 màn, 3 vai trò, build sạch | — |
| Ninh | **ADR-0004 — tự làm auth thay vì Supabase** | ✅ Done | `docs/decisions/0004-tu-lam-auth-thay-vi-supabase.md` | — |
| Ninh | Chạy thử đầu-cuối trên trình duyệt thật | ✅ Done | Đăng nhập 3 vai trò · chặn cứng "kim tiêm" → chuyển người · duyệt tuyến gộp 4 điểm → thông báo 4 cư dân | — |
| — | Lấy API key vision (Gemini / OpenRouter / NVIDIA) và chạy đo token thật trên 50 ảnh | ⬜ Chưa làm | **việc chặn duy nhất** để luồng chụp ảnh chạy hết | — |
| — | Phỏng vấn lao công + BQL | ⬜ Chưa làm | vẫn là chỗ yếu nhất của ADR-0002 và ADR-0003 | — |
| — | `git init`, `.env`, `setup_hooks.ps1` | ❌ Blocked | **treo sang ngày thứ 5** — AI logging (deliverable #4) vẫn chưa chạy | — |

**Tổng kết ngày:** Dựng xong sản phẩm chạy thật đầu-cuối: backend FastAPI 44
route, agent LangGraph có trace, frontend Next.js 21 màn theo đúng bản thiết
kế, 76 test pass. Ba điểm HITL đều thao tác được trên giao diện thật với dữ
liệu thật. Quyết định kỹ thuật đáng chú ý nhất trong ngày: **tách lớp nhà cung
cấp model** — DeepSeek không nhận ảnh nên không dùng được cho T1/T2, và nhóm
chưa có key OpenAI, nên hệ thống được viết để đổi provider chỉ bằng sửa một
dòng `.env`; câu chuyện định tuyến nhiều tầng trong ADR giữ nguyên. Phần chưa
chạy được là luồng chụp ảnh thật vì chưa có API key vision — mọi thứ khác
(chặn cứng, từ chối trả lời, thu gom, tuyến, vận hành) đều chạy không cần key.

---

## 2026-08-01 — buổi 2: app cài được + sẵn sàng deploy

Thực hiện `docs/PLAN_APP_DEPLOY.md` theo thứ tự đã chốt **A → C → B → D → E → F**.

| Member | Task | Status | Output | Time |
|--------|------|--------|--------|------|
| Ninh | **A** — Linh vật thật thay SVG vẽ tạm | ✅ Done | 3 tư thế × 3 bề rộng WebP (2,3 MB → 22–80 KB) + bộ icon PWA. `Mascot` nhận prop `tuThe`, giữ SVG làm ảnh dự phòng | — |
| Ninh | Sửa `build_assets.py`: ảnh gốc có lớp alpha mờ phủ kín khung nên bbox không cắt được gì | ✅ Done | Cắt theo ngưỡng alpha > 24 và xoá hẳn lớp mờ — trước đó linh vật lọt thỏm trong icon | — |
| Ninh | **C** — Backend sẵn sàng Render | ✅ Done | `render.yaml`, tách `torch` sang `requirements-local-model.txt`, bật `psycopg2`, `SEED_ON_START`, `Dockerfile` nghe `$PORT` | — |
| Ninh | Chặn dữ liệu demo bị nhân đôi mỗi lần Render khởi động lại | ✅ Done | `bootstrap()` + `da_co_du_lieu_demo()` trong `scripts/seed.py` — kiểm chứng chạy `--demo` hai lần không sinh thêm bản ghi | — |
| Ninh | Chuẩn hoá `postgres://` → `postgresql://` + `pool_pre_ping` | ✅ Done | `src/db/session.py` — Render phát DSN kiểu cũ, SQLAlchemy 2 không nhận | — |
| Ninh | **B** — PWA: manifest, service worker viết tay, nút cài, trang `/tai-app` | ✅ Done | Cache vỏ ứng dụng + 3 endpoint tra cứu công khai theo stale-while-revalidate | — |
| Ninh | **D** — Capacitor → khung APK | ✅ Done | `output: "export"` chạy sạch, `frontend/android/`, `platform.ts` gói camera, ban quản lý vào app native thì được chỉ sang web | — |
| Ninh | **E** — `git init` + CI kiểm frontend + workflow build APK theo tag | ✅ Done | `.github/workflows/android.yml`, job `frontend` trong `ci.yml` (typecheck + build) | — |
| Ninh | **F** — Kiểm chứng thật trên trình duyệt | ✅ Done | 76 test pass · ruff sạch · `tsc` sạch · export tĩnh sạch · **tắt máy chủ tĩnh rồi tải lại: app vẫn chạy đủ từ cache**, lịch thu gom nằm trong cache với dữ liệu thật | — |
| Ninh | **ADR-0005 — PWA + Capacitor thay vì viết lại native** | ✅ Done | `docs/decisions/0005-pwa-va-capacitor-thay-vi-viet-lai-native.md` | — |
| — | Tạo repo GitHub + push, nối Render và Vercel | ⬜ Chưa làm | cần tài khoản của chủ dự án | — |
| — | `scripts/setup_hooks.ps1` → AI logging (deliverable #4) | ⬜ Chưa làm | làm ngay sau khi push — `git init` đã xong nên hết vướng | — |
| — | Cắm điện thoại Android thử APK do CI build | ⬜ Chưa làm | phải có người cầm máy thật | — |
| — | Lấy API key vision | ❌ Blocked | **vẫn là việc chặn duy nhất** của luồng chụp ảnh | — |

**Tổng kết ngày:** Sản phẩm đã có hình dạng cài được: cùng một bản build phục vụ
cả web, PWA và APK. Kiểm chứng đáng giá nhất là phần offline — tắt hẳn máy chủ
tĩnh rồi tải lại trang, app vẫn dựng đủ và lịch thu gom vẫn nằm trong cache với
dữ liệu thật, tức là yêu cầu ở `FRONTEND_SPEC.md` mục 2.5 đã thành thật chứ
không còn là lời hứa. Hai chỗ đáng ghi lại vì suýt sai: **ảnh linh vật gốc có
một lớp alpha rất mờ phủ gần kín khung**, khiến cách cắt theo bounding box cho
ra icon với con vật lọt thỏm ở giữa; và **nhóm hàm seed dữ liệu demo vốn không
idempotent**, mà Render thì gọi seed mỗi lần khởi động — không chặn thì sau vài
lần restart trang Vận hành sẽ đầy bản ghi trùng. Cả hai chỉ lộ ra khi chạy thật
và nhìn kết quả, không lộ ra khi đọc code.

---

## [YYYY-MM-DD]

| Member | Task | Status | Output | Time |
|--------|------|--------|--------|------|
| [Tên] | [mô tả task] | ✅ Done | [link/kết quả] | 2h |
| [Tên] | [mô tả task] | 🔄 WIP | [mô tả tiến độ] | 1.5h |
| [Tên] | [mô tả task] | ❌ Blocked | [lý do block] | - |

**Tổng kết ngày:** [1-2 câu về tiến độ chung]

---

## [YYYY-MM-DD]

| Member | Task | Status | Output | Time |
|--------|------|--------|--------|------|
| | | | | |

**Tổng kết ngày:**

---

<!-- Format: copy block trên cho mỗi ngày làm việc -->
