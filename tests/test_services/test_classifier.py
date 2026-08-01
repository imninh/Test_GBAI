"""Test định tuyến 4 tầng và hàng rào an toàn.

Các test ở đây là bằng chứng cho tiêu chí an toàn AI của đề: hệ thống phải
**từ chối trả lời** đúng lúc, và phải **leo tầng khi nghi rác nguy hại** chứ
không chỉ khi confidence thấp.
"""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from src.db.models import Classification, Media
from src.services import classifier, safety
from src.services.classifier import TIER_T0_CACHE, TIER_T1, TIER_T2, classify_waste
from tests.conftest import FakeVisionClient, make_result


@pytest.fixture(autouse=True)
def _tat_model_local(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tắt tầng T0.5 trong đa số test để tách bạch hành vi của T1/T2."""
    monkeypatch.setattr(classifier, "classify_image_local", lambda *a, **k: None)


def _dung_model_gia(monkeypatch: pytest.MonkeyPatch, *results) -> FakeVisionClient:
    fake = FakeVisionClient(results=list(results))
    monkeypatch.setattr(classifier, "get_vision_client", lambda: fake)
    monkeypatch.setattr(classifier, "get_tier_models", lambda: ("model-t1", "model-t2", "model-text"))
    return fake


# --- Luồng bình thường ---------------------------------------------------


def test_anh_ro_thi_dung_o_t1_va_tra_loi(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _dung_model_gia(monkeypatch, make_result(confidence=0.91))

    outcome = classify_waste(db_session, image_bytes=b"fake-image", image_phash="a1b2c3d4e5f60718")

    assert outcome.refused is False
    assert outcome.tier == TIER_T1
    assert outcome.category_code == "recyclable_paper"
    assert outcome.confidence_level == "chac_chan"
    assert len(fake.calls) == 1, "Ảnh rõ mà vẫn gọi T2 là đốt tiền"


def test_hoi_bang_chu_khong_can_anh(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _dung_model_gia(monkeypatch, make_result(item_name="Ly trà sữa", category_code="recyclable_plastic"))

    outcome = classify_waste(db_session, text_query="ly trà sữa có màng nhựa dán miệng")

    assert outcome.refused is False
    assert outcome.category_code == "recyclable_plastic"
    assert fake.calls[0][0] == "text"


# --- Leo tầng T1 → T2 ----------------------------------------------------


def test_confidence_thap_thi_leo_len_t2(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _dung_model_gia(
        monkeypatch,
        make_result(confidence=0.41),
        make_result(confidence=0.93),
    )

    outcome = classify_waste(db_session, image_bytes=b"anh", image_phash="1111222233334444")

    assert outcome.tier == TIER_T2
    assert "dưới ngưỡng" in outcome.escalation_reason
    assert len(fake.calls) == 2
    assert outcome.refused is False


def test_nghi_nguy_hai_thi_leo_t2_du_confidence_cao(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Đây là điều kiện escalate mà đa số nhóm bỏ sót — CLAUDE.md mục 4."""
    fake = _dung_model_gia(
        monkeypatch,
        make_result(item_name="Cục pin", category_code="hazardous", confidence=0.95, suspect_hazardous=True),
        make_result(item_name="Pin lithium", category_code="hazardous", confidence=0.96, suspect_hazardous=True),
    )

    outcome = classify_waste(db_session, image_bytes=b"anh-pin", image_phash="aaaabbbbccccdddd")

    assert len(fake.calls) == 2, "Nghi rác nguy hại mà không kiểm lại bằng model mạnh hơn"
    assert outcome.escalation_reason.startswith("Nghi rác nguy hại")
    assert outcome.tier == TIER_T2


def test_t2_loi_thi_giu_ket_qua_t1_chu_khong_nang_do_tin_cay(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    from src.services.vision import VisionUnavailableError

    fake = FakeVisionClient(results=[make_result(confidence=0.41)])
    monkeypatch.setattr(classifier, "get_vision_client", lambda: fake)
    monkeypatch.setattr(classifier, "get_tier_models", lambda: ("model-t1", "model-t2", "model-text"))

    original = fake.classify_image
    calls = {"n": 0}

    def flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return original(*args, **kwargs)
        raise VisionUnavailableError("Model quá tải", code="VISION-429")

    fake.classify_image = flaky  # type: ignore[method-assign]

    outcome = classify_waste(db_session, image_bytes=b"anh", image_phash="9999888877776666")

    assert outcome.refused is True, "T2 lỗi mà vẫn trả lời với confidence dưới ngưỡng là sai"
    assert any(n.node == "classify_waste_t2" and n.status == "error" for n in outcome.nodes)


# --- Từ chối trả lời -----------------------------------------------------


def test_duoi_nguong_nhom_nguy_hai_thi_tu_choi_tra_loi(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    _dung_model_gia(
        monkeypatch,
        make_result(item_name="Chai nước tẩy bồn cầu", category_code="hazardous", confidence=0.52),
        make_result(item_name="Chai nước tẩy bồn cầu", category_code="hazardous", confidence=0.58),
    )

    outcome = classify_waste(db_session, image_bytes=b"anh-toi", image_phash="0f0f0f0f0f0f0f0f")

    assert outcome.refused is True
    assert outcome.refusal_reason == safety.RefusalReason.NGHI_NGUY_HAI
    assert outcome.category is None, "Từ chối mà vẫn chốt nhãn là mâu thuẫn"
    assert outcome.guess_item_name == "Chai nước tẩy bồn cầu", "Vẫn phải hiện phỏng đoán gần nhất"
    assert outcome.safety_warning == "", "Từ chối thì không được kèm hướng dẫn xử lý"


def test_model_doan_ra_hoa_chat_thi_len_luon_danh_sach_chan_cung(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Chặn cứng chạy trên cả tên món model đoán ra, không chỉ câu người dùng gõ."""
    _dung_model_gia(
        monkeypatch,
        make_result(item_name="Chai hoá chất tẩy rửa", category_code="hazardous", confidence=0.95, suspect_hazardous=True),
        make_result(item_name="Chai hoá chất tẩy rửa", category_code="hazardous", confidence=0.97, suspect_hazardous=True),
    )

    outcome = classify_waste(db_session, image_bytes=b"anh", image_phash="0e0e0e0e0e0e0e0e")

    assert outcome.refused is True
    assert outcome.refusal_reason == safety.RefusalReason.CHAN_CUNG
    assert outcome.hard_block is not None and outcome.hard_block.code == "hoa_chat"


def test_anh_toi_thi_noi_ro_ly_do_la_anh_toi(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    _dung_model_gia(
        monkeypatch,
        make_result(category_code="other", confidence=0.30, quality_issue="anh_toi"),
        make_result(category_code="other", confidence=0.33, quality_issue="anh_toi"),
    )

    outcome = classify_waste(db_session, image_bytes=b"anh", image_phash="1234123412341234")

    assert outcome.refusal_reason == safety.RefusalReason.ANH_TOI
    assert "tối" in outcome.refusal_label_vi


def test_khong_goi_duoc_model_thi_tu_choi_chu_khong_vo_500(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    from src.services.vision import VisionUnavailableError

    def khong_co_key():
        raise VisionUnavailableError("Chưa cấu hình API key", code="VISION-401")

    monkeypatch.setattr(classifier, "get_vision_client", khong_co_key)
    monkeypatch.setattr(classifier, "get_tier_models", lambda: ("t1", "t2", "text"))

    outcome = classify_waste(db_session, image_bytes=b"anh", image_phash="5555555555555555")

    assert outcome.refused is True
    assert outcome.refusal_reason == safety.RefusalReason.MODEL_LOI
    assert "API key" in outcome.refusal_headline_vi


# --- Danh sách chặn cứng -------------------------------------------------


def test_chan_cung_theo_cau_hoi_thi_khong_goi_model_nao(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _dung_model_gia(monkeypatch)  # không nạp kết quả nào — gọi là hỏng test

    outcome = classify_waste(db_session, text_query="mình có mấy cái kim tiêm cũ bỏ đâu")

    assert outcome.refused is True
    assert outcome.refusal_reason == safety.RefusalReason.CHAN_CUNG
    assert outcome.hard_block is not None
    assert outcome.hard_block.code == "vat_sac_nhon_y_te"
    assert fake.calls == [], "Danh sách chặn cứng phải chặn TRƯỚC khi tốn tiền gọi model"


def test_chan_cung_bo_qua_confidence_cua_model(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    _dung_model_gia(monkeypatch, make_result(item_name="Bình gas mini", category_code="other", confidence=0.99))

    outcome = classify_waste(db_session, image_bytes=b"anh", image_phash="7777777777777777")

    assert outcome.refused is True
    assert outcome.hard_block is not None
    assert outcome.hard_block.code == "binh_gas"


def test_tu_khoa_khong_dau_van_bat_duoc() -> None:
    assert safety.check_hard_block("thuoc tru sau") is not None
    assert safety.check_hard_block("Thuốc trừ sâu còn nửa chai") is not None
    assert safety.check_hard_block("hộp sữa giấy") is None


# --- Tầng T0: cache pHash ------------------------------------------------


def test_anh_trung_thi_tra_ve_tu_cache_khong_goi_model(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _dung_model_gia(monkeypatch, make_result(confidence=0.91))
    phash = "abcdabcdabcdabcd"

    db_session.add(Media(uploader_id=1, stored_path="x.jpg", phash=phash))
    db_session.flush()
    media = db_session.query(Media).one()
    category = classifier._category_by_code(db_session, "recyclable_paper")
    db_session.add(
        Classification(
            media_id=media.id,
            item_name="Hộp sữa giấy tráng nhôm",
            predicted_category_id=category.id,
            confidence=0.91,
            tier=TIER_T1,
        )
    )
    db_session.commit()

    outcome = classify_waste(db_session, image_bytes=b"anh", image_phash=phash)

    assert outcome.tier == TIER_T0_CACHE
    assert outcome.cost_usd == 0.0
    assert outcome.category_code == "recyclable_paper"
    assert fake.calls == [], "Trúng cache mà vẫn gọi model là mất ý nghĩa của tầng T0"


def test_anh_khac_han_thi_khong_dinh_cache(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    _dung_model_gia(monkeypatch, make_result(confidence=0.88))

    db_session.add(Media(uploader_id=1, stored_path="x.jpg", phash="0000000000000000"))
    db_session.flush()
    media = db_session.query(Media).one()
    category = classifier._category_by_code(db_session, "organic")
    db_session.add(
        Classification(media_id=media.id, predicted_category_id=category.id, confidence=0.9, tier=TIER_T1)
    )
    db_session.commit()

    outcome = classify_waste(db_session, image_bytes=b"anh", image_phash="ffffffffffffffff")

    assert outcome.tier == TIER_T1


# --- Ngưỡng và mức hiển thị ---------------------------------------------


def test_nhom_nguy_hai_luon_dung_nguong_cao_hon(db_session: Session) -> None:
    hazardous = classifier._category_by_code(db_session, "hazardous")
    thuong = classifier._category_by_code(db_session, "other")

    assert safety.min_confidence_for(hazardous) >= 0.80
    assert safety.min_confidence_for(hazardous) > safety.min_confidence_for(thuong)


def test_ba_muc_hien_thi_do_tin_cay() -> None:
    assert safety.confidence_level(0.95, 0.60) == "chac_chan"
    assert safety.confidence_level(0.66, 0.60) == "kha_chac"
    assert safety.confidence_level(0.40, 0.60) == "duoi_nguong"


def test_canh_bao_an_toan_lay_tu_csdl_khong_do_llm_sinh(db_session: Session) -> None:
    hazardous = classifier._category_by_code(db_session, "hazardous")

    warning = safety.safety_warning_for(hazardous)

    assert "KHÔNG bỏ vào thùng rác thường" in warning
    assert safety.safety_warning_for(classifier._category_by_code(db_session, "organic")) == ""


def test_moi_buoc_deu_sinh_so_lieu_cho_man_agent_run(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    _dung_model_gia(monkeypatch, make_result(confidence=0.91))

    outcome = classify_waste(db_session, image_bytes=b"anh", image_phash="abab abab".replace(" ", "") + "abababab")

    nodes = {n.node for n in outcome.nodes}
    assert {"safety_precheck", "cache_lookup", "classify_waste", "safety_check"} <= nodes
    assert any(n.llm_calls == 1 for n in outcome.nodes)
    assert outcome.latency_ms >= 0


# --- Ảnh nhiều món rác ---------------------------------------------------


def test_nhieu_vat_thi_leo_t2_du_confidence_cao(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CLAUDE.md mục 4 liệt kê "nhiều vật" là một trong ba điều kiện leo T2.

    Điều kiện này từng bị bỏ sót: model tự tin 0,85 trên một ảnh có ba món
    khác nhóm thì vẫn đi thẳng ra kết quả, không kiểm lại lần nào.
    """
    fake = _dung_model_gia(
        monkeypatch,
        make_result(confidence=0.85, quality_issue="nhieu_vat"),
        make_result(confidence=0.88, quality_issue="nhieu_vat"),
    )

    classify_waste(db_session, image_bytes=b"anh-nhieu-mon", image_phash="1111222233334444")

    assert len(fake.calls) == 2, "Ảnh nhiều món mà không kiểm lại bằng model mạnh hơn"


def test_nhieu_mon_khac_nhom_thi_tu_choi_chu_khong_gan_mot_nhan(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ca thật gặp trên bản deploy 01/08: ảnh có chai nhựa + bình thuỷ tinh +
    chuột máy tính, model trả về "Nhựa tái chế" với độ tin cậy 0,85.

    Một nhãn duy nhất ở đây là **câu trả lời sai** — thuỷ tinh và rác điện tử
    đi đường khác nhựa. Phải chuyển người, bất kể confidence cao đến đâu.
    """
    nhieu_mon = [
        {"name": "Chai nhựa", "category_code": "recyclable_plastic", "confidence": 0.9},
        {"name": "Bình thuỷ tinh", "category_code": "recyclable_glass", "confidence": 0.8},
        {"name": "Chuột máy tính", "category_code": "hazardous", "confidence": 0.7},
    ]
    _dung_model_gia(
        monkeypatch,
        make_result(category_code="recyclable_plastic", confidence=0.85, quality_issue="nhieu_vat", items=nhieu_mon),
        make_result(category_code="recyclable_plastic", confidence=0.85, quality_issue="nhieu_vat", items=nhieu_mon),
    )

    outcome = classify_waste(db_session, image_bytes=b"anh-ba-mon", image_phash="5555666677778888")

    assert outcome.refused, "Ba món khác nhóm mà vẫn chốt một nhãn duy nhất"
    assert outcome.refusal_reason == safety.RefusalReason.NHIEU_VAT.value
    # Phỏng đoán vẫn giữ lại để hiện trên màn "chưa chắc chắn", nhưng không
    # được kèm hướng dẫn xử lý.
    assert outcome.guess_item_name


def test_nhieu_mon_cung_mot_nhom_thi_van_tra_loi_binh_thuong(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Không được khắt khe quá: ba cái chai nhựa vẫn chỉ là nhựa tái chế."""
    cung_nhom = [
        {"name": "Chai nước suối", "category_code": "recyclable_plastic", "confidence": 0.9},
        {"name": "Chai nước ngọt", "category_code": "recyclable_plastic", "confidence": 0.9},
    ]
    _dung_model_gia(
        monkeypatch,
        make_result(category_code="recyclable_plastic", confidence=0.92, quality_issue="nhieu_vat", items=cung_nhom),
        make_result(category_code="recyclable_plastic", confidence=0.93, quality_issue="nhieu_vat", items=cung_nhom),
    )

    outcome = classify_waste(db_session, image_bytes=b"anh-may-chai", image_phash="9999aaaabbbbcccc")

    assert not outcome.refused
    assert outcome.category is not None and outcome.category.code == "recyclable_plastic"
