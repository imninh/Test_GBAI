"""Test định tuyến **nhà cung cấp theo từng tầng**.

Ba nguồn miễn phí đang dùng có ba kiểu hạn mức khác nhau (Gemini tính theo số
request và rất ít, NVIDIA tính theo credit, CLIP local thì $0), nên trộn chúng
theo tầng là cách để cạn quota một nơi không làm đứng cả sản phẩm. Đo ngày
01/08/2026: bản deploy chỉ chạy 2/4 tầng đúng vì cả hệ thống dùng chung một
provider và nó hết quota.

Các test ở đây **không gọi mạng** — chỉ kiểm phần chọn provider/model và kiểu
client được dựng ra.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

import pytest

from src.config import get_settings, reset_settings_cache
from src.services.vision import (
    GeminiClient,
    OpenAICompatibleClient,
    get_tier_model,
    get_vision_client,
    provider_status,
)


@pytest.fixture(autouse=True)
def _cau_hinh_sach() -> Iterator[None]:
    """Cấu hình đọc qua ``lru_cache`` nên phải xoá cache quanh mỗi test."""
    reset_settings_cache()
    yield
    reset_settings_cache()


def _tron_ba_nha_cung_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cấu hình khuyến nghị: T1 NVIDIA · T2 Gemini · advise Gemini lite."""
    monkeypatch.setenv("VISION_PROVIDER", "gemini")
    monkeypatch.setenv("VISION_PROVIDER_T1", "nvidia")
    monkeypatch.setenv("VISION_PROVIDER_T2", "gemini")
    monkeypatch.setenv("VISION_PROVIDER_TEXT", "gemini")
    for ten in ("VISION_MODEL_T1", "VISION_MODEL_T2", "TEXT_MODEL"):
        monkeypatch.setenv(ten, "")
    monkeypatch.setenv("NVIDIA_API_KEY", "khoa-gia-nvidia")
    monkeypatch.setenv("GEMINI_API_KEY", "khoa-gia-gemini")
    reset_settings_cache()


# --- Chọn provider và model ----------------------------------------------


def test_moi_tang_doc_nha_cung_cap_cua_rieng_no(monkeypatch: pytest.MonkeyPatch) -> None:
    _tron_ba_nha_cung_cap(monkeypatch)
    settings = get_settings()

    assert settings.resolve_provider("t1") == "nvidia"
    assert settings.resolve_provider("t2") == "gemini"
    assert settings.resolve_provider("text") == "gemini"


def test_model_mac_dinh_lay_theo_provider_cua_chinh_tang_do(monkeypatch: pytest.MonkeyPatch) -> None:
    """Chỗ dễ sai nhất: T1 phải lấy model mặc định của NVIDIA, không của Gemini."""
    _tron_ba_nha_cung_cap(monkeypatch)

    assert get_tier_model("t1") == "meta/llama-3.2-11b-vision-instruct"
    assert get_tier_model("t2") == "gemini-flash-latest"
    assert get_tier_model("text") == "gemini-flash-lite-latest"


def test_khong_khai_rieng_thi_lui_ve_provider_chung(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VISION_PROVIDER", "openai")
    for ten in ("VISION_PROVIDER_T1", "VISION_PROVIDER_T2", "VISION_PROVIDER_TEXT"):
        monkeypatch.setenv(ten, "")
    for ten in ("VISION_MODEL_T1", "VISION_MODEL_T2", "TEXT_MODEL"):
        monkeypatch.setenv(ten, "")
    reset_settings_cache()

    settings = get_settings()

    assert settings.resolve_models() == ("gpt-4o-mini", "gpt-4o", "gpt-4o-mini")
    assert settings.resolve_provider("t2") == "openai"


def test_ten_model_khai_thang_trong_env_thi_thang(monkeypatch: pytest.MonkeyPatch) -> None:
    _tron_ba_nha_cung_cap(monkeypatch)
    monkeypatch.setenv("VISION_MODEL_T1", "model-tu-chon")
    reset_settings_cache()

    assert get_tier_model("t1") == "model-tu-chon"


def test_api_key_tra_dung_theo_ten_nha_cung_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    _tron_ba_nha_cung_cap(monkeypatch)
    settings = get_settings()

    assert settings.api_key_for("nvidia") == "khoa-gia-nvidia"
    assert settings.api_key_for("gemini") == "khoa-gia-gemini"
    assert settings.api_key_for("local_only") == ""


# --- Client dựng theo tầng ------------------------------------------------


def test_client_cua_hai_tang_la_hai_nha_cung_cap_khac_nhau(monkeypatch: pytest.MonkeyPatch) -> None:
    _tron_ba_nha_cung_cap(monkeypatch)

    client_t1 = get_vision_client("t1")
    client_t2 = get_vision_client("t2")

    assert isinstance(client_t1, OpenAICompatibleClient)
    assert client_t1.provider_name == "nvidia"
    assert isinstance(client_t2, GeminiClient)


def test_khong_truyen_tang_thi_mac_dinh_la_t1(monkeypatch: pytest.MonkeyPatch) -> None:
    """Giữ tương thích với chỗ gọi cũ."""
    _tron_ba_nha_cung_cap(monkeypatch)

    assert getattr(get_vision_client(), "provider_name", "") == "nvidia"


# --- Trang Vận hành -------------------------------------------------------


def test_provider_status_liet_ke_tung_tang(monkeypatch: pytest.MonkeyPatch) -> None:
    _tron_ba_nha_cung_cap(monkeypatch)

    status = provider_status()
    theo_tang = {t["tier"]: t for t in status["tiers"]}  # type: ignore[union-attr]

    assert set(theo_tang) == {"t1", "t2", "text"}
    assert theo_tang["t1"]["provider"] == "nvidia"
    assert theo_tang["t2"]["provider"] == "gemini"
    assert theo_tang["t1"]["has_api_key"] is True
    assert status["single_provider"] is False, "Ba tầng khác nhà cung cấp mà vẫn báo là một"


def test_provider_status_khong_bao_gio_lo_gia_tri_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _tron_ba_nha_cung_cap(monkeypatch)

    dump = json.dumps(provider_status(), ensure_ascii=False)

    assert "khoa-gia-nvidia" not in dump
    assert "khoa-gia-gemini" not in dump


def test_thieu_key_cua_mot_tang_thi_bao_ngay_tren_trang_van_hanh(monkeypatch: pytest.MonkeyPatch) -> None:
    """Trước đây chỉ có một cờ ``has_api_key`` chung → thiếu key ở một tầng bị lấp."""
    _tron_ba_nha_cung_cap(monkeypatch)
    monkeypatch.setenv("NVIDIA_API_KEY", "")
    reset_settings_cache()

    theo_tang = {t["tier"]: t for t in provider_status()["tiers"]}  # type: ignore[union-attr]

    assert theo_tang["t1"]["has_api_key"] is False
    assert theo_tang["t2"]["has_api_key"] is True
