"""Tầng T0.5 — CLIP zero-shot chạy tại chỗ, không gọi API.

Vì sao zero-shot mà không fine-tune: nhóm chưa có bộ ảnh tự chụp đủ lớn, mà
``docs/research/sota-model-nhe-phan-loai-rac.md`` đã chỉ ra model fine-tune trên
dataset công khai rớt từ 94% xuống 41% trên ảnh rác thật. Zero-shot không hứa
hẹn gì về accuracy, nên nó được dùng đúng vai trò của mình: **một cổng chặn rẻ
đứng trước API trả phí**, chỉ chốt khi rất chắc.

Hai ràng buộc an toàn cứng:

* dưới ``clip_accept_confidence`` thì không kết luận, đẩy lên T1;
* **không bao giờ được chốt nhãn cho nhóm nguy hại** — dù điểm số cao tới đâu.
  Sai ở nhóm đó gây hại thật, và một model 350MB không có khả năng đọc nhãn
  chai hoá chất (CLAUDE.md mục 5).

**Hai đường chạy, tự chọn (ADR-0007):**

``onnx``
    Chỉ nửa ảnh của CLIP, đã nén int8 (~85 MB), cộng dãy số của các câu mô tả
    tính sẵn từ trước. Không cần ``torch``. Vừa gói máy chủ 512 MB, và nhanh
    hơn vì bỏ được ~20 lượt mã hoá chữ mỗi ảnh. Sinh ra bằng
    ``scripts/export_clip_onnx.py``.

``torch``
    Bản đầy đủ như cũ. Cần ``torch`` (1,19 GB) nên chỉ chạy được ở máy dev.
    Giữ lại làm mốc đối chiếu cho phần eval — bản nén phải so được với nó.

Không có đường nào dùng được thì tầng T0.5 tự tắt và ảnh đi thẳng lên T1: mất
một tầng tiết kiệm chi phí, không ai bị chặn.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import threading
from pathlib import Path
from typing import Any

from PIL import Image

from src.config import get_settings
from src.services.vision.base import CategoryOption, Usage, VisionResult

logger = logging.getLogger(__name__)

# Tên hai file do `scripts/export_clip_onnx.py` sinh ra. Script import từ đây để
# hai bên không bao giờ lệch tên nhau.
ONNX_MODEL_FILE = "clip_vision_int8.onnx"
TEXT_EMBEDDING_FILE = "clip_text_embeddings.json"

_torch_model: Any = None
_torch_processor: Any = None
_torch_failed = False

_onnx_session: Any = None
_onnx_meta: dict[str, Any] | None = None
_onnx_failed = False

# Tải file model chỉ được chạy một lần dù nhiều luồng cùng gọi.
_tai_lock = threading.Lock()


# --- Tiền xử lý ảnh --------------------------------------------------------


def tien_xu_ly_anh(image: Image.Image, size: int, mean: list[float], std: list[float]):
    """Đưa ảnh về đúng khuôn CLIP nhận, **không dùng torch/transformers**.

    Lặp lại đúng các bước của ``CLIPImageProcessor``: co cạnh ngắn về ``size``
    (nội suy bicubic) → cắt giữa → chia 255 → chuẩn hoá theo mean/std.

    Script xuất model có phần đối chiếu đường này với ``CLIPProcessor`` gốc trên
    ảnh thật — lệch ở đây không ném lỗi, chỉ âm thầm làm sai mọi điểm số, nên
    phải đo chứ không tin.
    """
    import numpy as np

    rong, cao = image.size
    ti_le = size / min(rong, cao)
    image = image.resize((round(rong * ti_le), round(cao * ti_le)), Image.BICUBIC)

    rong, cao = image.size
    trai = (rong - size) // 2
    tren = (cao - size) // 2
    image = image.crop((trai, tren, trai + size, tren + size))

    arr = np.asarray(image, dtype=np.float32) / 255.0
    arr = (arr - np.asarray(mean, dtype=np.float32)) / np.asarray(std, dtype=np.float32)
    return arr.transpose(2, 0, 1)[None].astype(np.float32)


# --- Đường ONNX ------------------------------------------------------------


def _tai_asset_neu_thieu(thu_muc: Path) -> None:
    """Tải hai file model từ ``CLIP_ASSETS_URL`` nếu máy chưa có.

    Máy chủ miễn phí dùng đĩa tạm nên file mất sau mỗi lần khởi động lại — tải
    lại mỗi lần bật là chấp nhận được vì việc này chạy ở luồng nền, không chặn
    request nào.
    """
    url = get_settings().clip_assets_url
    if not url or (thu_muc / ONNX_MODEL_FILE).exists():
        return

    import tarfile
    import tempfile

    import httpx

    thu_muc.mkdir(parents=True, exist_ok=True)
    logger.info("Tải bộ model T0.5 từ %s …", url)
    try:
        with httpx.Client(timeout=300.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
        with tempfile.TemporaryDirectory() as tam:
            goi = Path(tam) / "clip_assets.tar.gz"
            goi.write_bytes(response.content)
            with tarfile.open(goi) as tf:
                # Chỉ giải nén đúng hai file mình cần, không tin danh sách trong
                # gói nén — tên kiểu `../..` là đường thoát ra ngoài thư mục.
                for ten in (ONNX_MODEL_FILE, TEXT_EMBEDDING_FILE):
                    thanh_vien = next((m for m in tf.getmembers() if Path(m.name).name == ten), None)
                    if thanh_vien is None or not thanh_vien.isfile():
                        continue
                    nguon = tf.extractfile(thanh_vien)
                    if nguon is not None:
                        (thu_muc / ten).write_bytes(nguon.read())
    except (httpx.HTTPError, OSError, tarfile.TarError) as exc:
        logger.warning("Không tải được bộ model T0.5: %s. Bỏ qua tầng này.", exc)


def _load_onnx() -> tuple[Any, dict[str, Any]] | None:
    """Nạp phiên ONNX + dãy số câu mô tả tính sẵn. ``None`` nếu không dùng được."""
    global _onnx_session, _onnx_meta, _onnx_failed
    if _onnx_failed:
        return None
    if _onnx_session is not None and _onnx_meta is not None:
        return _onnx_session, _onnx_meta

    with _tai_lock:
        if _onnx_session is not None and _onnx_meta is not None:
            return _onnx_session, _onnx_meta

        thu_muc = Path(get_settings().clip_onnx_dir)
        _tai_asset_neu_thieu(thu_muc)

        model_path = thu_muc / ONNX_MODEL_FILE
        meta_path = thu_muc / TEXT_EMBEDDING_FILE
        if not model_path.exists() or not meta_path.exists():
            logger.info("Chưa có bộ model T0.5 dạng ONNX ở %s — thử đường torch.", thu_muc)
            _onnx_failed = True
            return None

        try:
            import numpy as np
            import onnxruntime as ort
        except ImportError:
            logger.warning("Chưa cài onnxruntime — bỏ qua đường ONNX của tầng T0.5.")
            _onnx_failed = True
            return None

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["text_embeddings"] = np.asarray(meta["text_embeddings"], dtype=np.float32)
            session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        except (OSError, ValueError, KeyError) as exc:
            logger.warning("Bộ model T0.5 dạng ONNX hỏng: %s. Bỏ qua.", exc)
            _onnx_failed = True
            return None

        _onnx_session, _onnx_meta = session, meta
        logger.info("Đã nạp T0.5 dạng ONNX int8: %s", model_path)
        return session, meta


def _diem_onnx(image: Image.Image, prompts: list[str]) -> dict[str, float] | None:
    """Điểm cao nhất của từng nhóm rác. ``None`` nếu đường ONNX không dùng được."""
    loaded = _load_onnx()
    if loaded is None:
        return None
    session, meta = loaded

    # Câu mô tả trong CSDL đã đổi so với lúc xuất model → dãy số tính sẵn không
    # còn đúng. Thà tắt tầng còn hơn chấm bằng bộ câu cũ mà không ai biết.
    if _bam_prompt(prompts) != meta.get("prompt_hash"):
        logger.warning(
            "Câu mô tả CLIP trong CSDL khác lúc xuất model — chạy lại "
            "scripts/export_clip_onnx.py. Tạm bỏ qua đường ONNX."
        )
        return None

    import numpy as np

    cau_hinh = meta["image_preprocess"]
    pixel_values = tien_xu_ly_anh(image, cau_hinh["size"], cau_hinh["mean"], cau_hinh["std"])
    image_emb = session.run(None, {"pixel_values": pixel_values})[0][0]

    logits = float(meta["logit_scale"]) * meta["text_embeddings"] @ image_emb
    exp = np.exp(logits - logits.max())
    probs = exp / exp.sum()

    ket_qua: dict[str, float] = {}
    for prob, code in zip(probs.tolist(), meta["owner_codes"], strict=True):
        ket_qua[code] = max(ket_qua.get(code, 0.0), float(prob))
    return ket_qua


# --- Đường torch (máy dev) -------------------------------------------------


def _load_torch() -> tuple[Any, Any] | None:
    """Nạp CLIP bản đầy đủ. ``None`` nếu máy không có torch."""
    global _torch_model, _torch_processor, _torch_failed
    if _torch_failed:
        return None
    if _torch_model is not None and _torch_processor is not None:
        return _torch_model, _torch_processor

    try:
        import torch  # noqa: F401  (kiểm tra có sẵn trước khi nạp transformers)
        from transformers import CLIPModel, CLIPProcessor
    except ImportError:
        logger.info("Chưa cài torch/transformers — bỏ qua đường torch của tầng T0.5.")
        _torch_failed = True
        return None

    name = get_settings().clip_model_name
    try:
        _torch_model = CLIPModel.from_pretrained(name)
        _torch_processor = CLIPProcessor.from_pretrained(name)
        _torch_model.eval()
    except (OSError, ValueError) as exc:
        logger.warning("Không nạp được model local '%s': %s. Bỏ qua tầng T0.5.", name, exc)
        _torch_failed = True
        return None

    logger.info("Đã nạp T0.5 dạng torch: %s", name)
    return _torch_model, _torch_processor


def _diem_torch(image: Image.Image, prompts: list[str], owner_codes: list[str]) -> dict[str, float] | None:
    loaded = _load_torch()
    if loaded is None:
        return None
    model, processor = loaded

    import torch

    inputs = processor(text=prompts, images=image, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)[0]

    ket_qua: dict[str, float] = {}
    for prob, code in zip(probs.tolist(), owner_codes, strict=True):
        ket_qua[code] = max(ket_qua.get(code, 0.0), float(prob))
    return ket_qua


# --- Dùng chung ------------------------------------------------------------


def _bam_prompt(prompts: list[str]) -> str:
    return hashlib.sha256("\n".join(prompts).encode("utf-8")).hexdigest()


def runtime_dang_dung() -> str:
    """``"onnx"`` · ``"torch"`` · ``""`` — đường nào đang nạp sẵn trong bộ nhớ."""
    if _onnx_session is not None:
        return "onnx"
    if _torch_model is not None:
        return "torch"
    return ""


def is_loaded() -> bool:
    """Model đã nạp sẵn trong bộ nhớ chưa — **không kích hoạt việc tải model**.

    Trang Vận hành dùng hàm này. Dùng nhầm hàm có tác dụng phụ ở một endpoint
    chỉ đọc sẽ khiến request đầu tiên treo vài phút để tải model về.
    """
    return runtime_dang_dung() != ""


def warm_up() -> bool:
    """Nạp model ngay (tải về nếu chưa có). Gọi chủ động khi khởi động server."""
    settings = get_settings()
    if not settings.local_model_enabled:
        return False
    if settings.clip_runtime in {"auto", "onnx"} and _load_onnx() is not None:
        return True
    if settings.clip_runtime in {"auto", "torch"}:
        return _load_torch() is not None
    return False


def _prompts_for(category: CategoryOption) -> list[str]:
    """Sinh các câu mô tả tiếng Anh để CLIP chấm độ khớp với ảnh."""
    if category.hint:
        return [p.strip() for p in category.hint.split("|") if p.strip()]
    return [f"a photo of {category.name}"]


def classify_image_local(image_bytes: bytes, categories: list[CategoryOption]) -> VisionResult | None:
    """Chấm ảnh bằng CLIP. Trả về ``None`` khi không dùng được model local.

    Kết quả trả về vẫn có thể có ``confidence`` thấp — người gọi
    (:mod:`src.services.classifier`) là nơi quyết định chấp nhận hay leo tầng.
    """
    settings = get_settings()
    if not settings.local_model_enabled:
        return None

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except (OSError, ValueError):
        return None

    prompts: list[str] = []
    owner: list[CategoryOption] = []
    for category in categories:
        for prompt in _prompts_for(category):
            prompts.append(prompt)
            owner.append(category)
    if not prompts:
        return None

    best_by_code: dict[str, float] | None = None
    duong = ""
    if settings.clip_runtime in {"auto", "onnx"}:
        best_by_code = _diem_onnx(image, prompts)
        duong = "onnx"
    if best_by_code is None and settings.clip_runtime in {"auto", "torch"}:
        best_by_code = _diem_torch(image, prompts, [c.code for c in owner])
        duong = "torch"
    if not best_by_code:
        return None

    top_code = max(best_by_code, key=lambda c: best_by_code[c])
    top_category = next(c for c in categories if c.code == top_code)
    confidence = best_by_code[top_code]

    suspect_hazardous = any(
        best_by_code.get(c.code, 0.0) > 0.15 for c in categories if c.is_hazardous
    ) or top_category.is_hazardous

    return VisionResult(
        item_name=top_category.name,
        category_code=top_code,
        confidence=confidence,
        reason=f"Model local CLIP khớp cao nhất với nhóm {top_category.name}",
        quality_issue="",
        suspect_hazardous=suspect_hazardous,
        model=f"{settings.clip_model_name} ({duong})",
        provider="local_clip",
        # Chạy trên máy mình nên chi phí bằng 0, và đây là con số ĐO ĐƯỢC
        # chứ không phải ước tính — khác với các model free tier.
        usage=Usage(cost_usd=0.0, price_known=True),
        raw_text="",
    )
