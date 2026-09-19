import pytest

from scripts.faiss_store import VectorStore


def chunk(text, embedding, chunk_id):
    return {
        "text": text,
        "metadata": {"file_name": "rules.pdf", "chunk_id": chunk_id},
        "embedding": embedding,
    }


def test_search_returns_closest_chunk_with_score():
    store = VectorStore(dimension=2)
    store.add_documents([chunk("first", [1.0, 0.0], 0), chunk("second", [0.0, 1.0], 1)])

    results = store.search([1.0, 0.0], k=1)

    assert len(results) == 1
    assert results[0]["text"] == "first"
    assert results[0]["score"] == pytest.approx(1.0)
    assert "embedding" not in results[0]


def test_search_on_empty_store_returns_nothing():
    assert VectorStore(dimension=2).search([1.0, 0.0]) == []


def test_k_larger_than_store_is_clamped():
    store = VectorStore(dimension=2)
    store.add_documents([chunk("first", [1.0, 0.0], 0)])

    assert len(store.search([1.0, 0.0], k=10)) == 1


def test_save_and_load_round_trip(tmp_path):
    store = VectorStore(dimension=2, embedding_model="model-a")
    store.add_documents([chunk("first", [1.0, 0.0], 0)])
    store.save(tmp_path)

    loaded = VectorStore(dimension=2, embedding_model="model-a")
    loaded.load(tmp_path)

    assert len(loaded) == 1
    assert loaded.search([1.0, 0.0], k=1)[0]["text"] == "first"


def test_load_rejects_a_different_embedding_model(tmp_path):
    store = VectorStore(dimension=2, embedding_model="model-a")
    store.add_documents([chunk("first", [1.0, 0.0], 0)])
    store.save(tmp_path)

    with pytest.raises(ValueError, match="model-a"):
        VectorStore(dimension=2, embedding_model="model-b").load(tmp_path)


def test_load_rejects_a_different_dimension(tmp_path):
    store = VectorStore(dimension=2, embedding_model="model-a")
    store.add_documents([chunk("first", [1.0, 0.0], 0)])
    store.save(tmp_path)

    with pytest.raises(ValueError, match="dimension"):
        VectorStore(dimension=3, embedding_model="model-a").load(tmp_path)


def test_load_missing_index_raises(tmp_path):
    assert not VectorStore.exists(tmp_path)

    with pytest.raises(FileNotFoundError):
        VectorStore(dimension=2).load(tmp_path)
