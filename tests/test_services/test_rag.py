"""Test truy hồi quy định và node advise."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Building, KnowledgeChunk, KnowledgeDoc, WasteCategory
from src.services import rag


@pytest.fixture
def kho_quy_dinh(db_session: Session) -> dict[str, int]:
    """Hai toà, mỗi toà một nội quy khác nhau, cộng một tài liệu dùng chung."""
    s1 = Building(code="S1", name="Toà S1")
    s2 = Building(code="S2", name="Toà S2")
    db_session.add_all([s1, s2])
    db_session.flush()

    doc_s1 = KnowledgeDoc(building_id=s1.id, title="Nội quy toà S1", doc_type="building_rule", source="noi-quy-s1")
    doc_s2 = KnowledgeDoc(building_id=s2.id, title="Nội quy toà S2", doc_type="building_rule", source="noi-quy-s2")
    doc_chung = KnowledgeDoc(building_id=None, title="Danh mục rác nguy hại", doc_type="hazard", source="danh-muc")
    db_session.add_all([doc_s1, doc_s2, doc_chung])
    db_session.flush()

    db_session.add_all(
        [
            KnowledgeChunk(
                doc_id=doc_s1.id,
                section="Mục 4.2",
                content="Rác tái chế của toà S1 thu gom thứ Ba, thứ Năm, thứ Bảy khung 18:00-20:00 tại thùng xanh dương.",
            ),
            KnowledgeChunk(
                doc_id=doc_s2.id,
                section="Mục 3.1",
                content="Rác tái chế của toà S2 thu gom thứ Ba và thứ Sáu khung 17:00-19:00.",
            ),
            KnowledgeChunk(
                doc_id=doc_chung.id,
                section="Pin và ắc quy",
                content="Pin và ắc quy chứa kim loại nặng, không làm thủng, không đốt, mang tới điểm thu gom tầng hầm.",
                meta={"needs_verification": False},
            ),
        ]
    )
    db_session.commit()
    return {"s1": s1.id, "s2": s2.id}


def test_truy_hoi_dung_quy_dinh_cua_toa_dang_hoi(db_session: Session, kho_quy_dinh: dict[str, int]) -> None:
    ket_qua = rag.retrieve(db_session, "rác tái chế thu gom lúc mấy giờ", building_id=kho_quy_dinh["s1"])

    assert ket_qua, "Phải truy hồi được ít nhất một đoạn"
    tieu_de = {c.doc_title for c in ket_qua}
    assert "Nội quy toà S1" in tieu_de
    assert "Nội quy toà S2" not in tieu_de, "Trộn quy định toà khác vào là trả lời sai"


def test_tai_lieu_dung_chung_van_duoc_lay_kem(db_session: Session, kho_quy_dinh: dict[str, int]) -> None:
    ket_qua = rag.retrieve(db_session, "pin cũ bỏ ở đâu", building_id=kho_quy_dinh["s1"])

    assert any(c.doc_title == "Danh mục rác nguy hại" for c in ket_qua)


def test_xep_hang_dua_doan_lien_quan_nhat_len_dau(db_session: Session, kho_quy_dinh: dict[str, int]) -> None:
    ket_qua = rag.retrieve(db_session, "pin ắc quy có làm thủng được không", building_id=kho_quy_dinh["s1"])

    assert ket_qua[0].section == "Pin và ắc quy"
    assert ket_qua[0].score > 0


def test_khong_co_tai_lieu_khop_thi_tra_ve_rong(db_session: Session, kho_quy_dinh: dict[str, int]) -> None:
    assert rag.retrieve(db_session, "zzzzz qqqqq", building_id=kho_quy_dinh["s1"]) == []


def test_nguon_tra_ve_du_thong_tin_de_ve_chip(db_session: Session, kho_quy_dinh: dict[str, int]) -> None:
    nguon = rag.retrieve(db_session, "rác tái chế", building_id=kho_quy_dinh["s1"])[0].as_source_dict()

    assert {"doc_title", "section", "quote", "chunk_id", "score"} <= set(nguon)
    assert nguon["quote"], "Chip nguồn bấm vào phải hiện được nguyên văn đoạn trích"


def test_bo_dau_van_khop_tu_khoa() -> None:
    assert rag.tokenize("Thùng rác tái chế") == ["thung", "rac", "tai", "che"]


def test_advise_khong_goi_duoc_model_thi_lui_ve_huong_dan_chuan(
    db_session: Session, kho_quy_dinh: dict[str, int], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Trạng thái suy giảm một phần: vẫn trả lời được, và nói rõ là đang suy giảm."""
    from src.services.vision import VisionUnavailableError

    def khong_co_key():
        raise VisionUnavailableError("Chưa cấu hình API key", code="VISION-401")

    monkeypatch.setattr("src.services.vision.get_vision_client", khong_co_key)

    category = db_session.scalar(select(WasteCategory).where(WasteCategory.code == "recyclable_paper"))
    ket_qua = rag.advise(
        db_session,
        item_name="Hộp sữa giấy",
        category=category,
        building_id=kho_quy_dinh["s1"],
        query="rác tái chế thu gom lúc nào",
    )

    assert ket_qua.advice, "Suy giảm không có nghĩa là im lặng"
    assert ket_qua.generated_by == "template"
    assert ket_qua.degraded is True
    assert ket_qua.sources, "Vẫn phải chỉ ra được nguồn"


def test_advise_khong_truy_hoi_duoc_thi_bao_suy_giam(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    from src.services.vision import VisionUnavailableError

    monkeypatch.setattr(
        "src.services.vision.get_vision_client",
        lambda: (_ for _ in ()).throw(VisionUnavailableError("khong co key")),
    )
    category = db_session.scalar(select(WasteCategory).where(WasteCategory.code == "organic"))

    ket_qua = rag.advise(db_session, item_name="Vỏ chuối", category=category, building_id=None)

    assert ket_qua.degraded is True
    assert "hướng dẫn chung" in ket_qua.degraded_note or "danh mục" in ket_qua.degraded_note
