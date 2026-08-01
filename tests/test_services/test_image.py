"""Test tiền xử lý ảnh — phần khẳng định EXIF đã sạch là bắt buộc.

Đây là test có giá trị pháp lý với đề: nó chứng minh ảnh gửi đi không còn
toạ độ GPS, chứ không phải chỉ nói suông trong tài liệu.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from src.services.image import has_exif, phash_distance, preprocess_image


def _image_with_exif(size: tuple[int, int] = (1200, 900)) -> bytes:
    """Tạo ảnh JPEG có EXIF: GPS, thời gian chụp, model điện thoại."""
    img = Image.new("RGB", size, (120, 160, 130))
    exif = img.getexif()
    exif[271] = "Apple"  # Make
    exif[272] = "iPhone 13"  # Model
    exif[306] = "2026:07:28 14:22:03"  # DateTime
    exif[34853] = {  # GPSInfo — 10.776900, 106.700900
        1: "N",
        2: (10.0, 46.0, 36.84),
        3: "E",
        4: (106.0, 42.0, 3.24),
    }
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif.tobytes())
    return buf.getvalue()


@pytest.fixture
def media_dir(tmp_path: Path) -> str:
    return str(tmp_path / "media")


def test_anh_da_xu_ly_khong_con_exif(media_dir: str) -> None:
    result = preprocess_image(_image_with_exif(), media_dir=media_dir)

    assert result.exif_stripped is True
    assert has_exif(result.stored_path) is False, "Ảnh gửi đi vẫn còn EXIF — không được phép"


def test_ghi_lai_cac_truong_da_xoa_cho_man_quyen_rieng_tu(media_dir: str) -> None:
    result = preprocess_image(_image_with_exif(), media_dir=media_dir)

    labels = {r.label_vi for r in result.removed_fields}
    assert "Toạ độ GPS" in labels
    assert "Model điện thoại" in labels
    # Giá trị trước khi xoá phải đọc được để dựng bảng đối chiếu ở spec 4.5.
    gps = next(r for r in result.removed_fields if r.label_vi == "Toạ độ GPS")
    assert gps.value_before.startswith("10.7")


def test_nen_ve_512px_va_giam_dung_luong(media_dir: str) -> None:
    raw = _image_with_exif(size=(3024, 4032))
    result = preprocess_image(raw, media_dir=media_dir)

    assert max(result.width, result.height) == 512
    assert result.bytes_size < result.original_bytes_size
    assert result.original_width == 3024


def test_phash_on_dinh_va_phan_biet_duoc_anh_khac(media_dir: str) -> None:
    same_a = preprocess_image(_image_with_exif(), media_dir=media_dir)
    same_b = preprocess_image(_image_with_exif(), media_dir=media_dir)

    noise = Image.effect_noise((600, 600), 90).convert("RGB")
    buf = io.BytesIO()
    noise.save(buf, format="JPEG")
    other = preprocess_image(buf.getvalue(), media_dir=media_dir)

    assert phash_distance(same_a.phash, same_b.phash) == 0
    assert phash_distance(same_a.phash, other.phash) > 6


def test_giu_anh_goc_rieng_va_dat_han_luu_tru(media_dir: str) -> None:
    result = preprocess_image(_image_with_exif(), media_dir=media_dir)

    assert result.original_path != result.stored_path
    assert Path(result.original_path).exists()
    assert result.expires_at is not None


def test_file_khong_phai_anh_thi_bao_loi_ro_rang(media_dir: str) -> None:
    with pytest.raises(ValueError, match="Không đọc được file ảnh"):
        preprocess_image(b"day khong phai anh", media_dir=media_dir)
