from pathlib import Path

from korean_maritime_law_rag.config import load_settings


def test_load_settings_from_yaml(tmp_path: Path):
    cfg_file = tmp_path / "demo.yaml"
    cfg_file.write_text("top_k: 7\nrrf_k: 30\n", encoding="utf-8")
    s = load_settings(cfg_file)
    assert s.top_k == 7
    assert s.rrf_k == 30
    assert s.graph_hops == 1  # 멀티홉 검색의 기본 확장 깊이


def test_load_settings_defaults():
    s = load_settings(None)
    assert s.neo4j_user == "neo4j"
    assert s.rerank is False
    assert s.embedding_cache == Path("data/embeddings/kure-v1-articles.npz")


def test_env_overrides_yaml(tmp_path: Path, monkeypatch):
    cfg_file = tmp_path / "demo.yaml"
    cfg_file.write_text("top_k: 7\n", encoding="utf-8")
    monkeypatch.setenv("MLR_TOP_K", "99")
    s = load_settings(cfg_file)
    assert s.top_k == 99  # env가 yaml보다 우선
