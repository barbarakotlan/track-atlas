import pytest

from scripts.chunker import chunk_document


def make_document(text):
    return {"text": text, "metadata": {"file_name": "rules.pdf"}}


def test_short_document_becomes_single_chunk():
    chunks = chunk_document(make_document("a short sentence"), chunk_size=50, overlap=10)

    assert len(chunks) == 1
    assert chunks[0]["text"] == "a short sentence"
    assert chunks[0]["metadata"] == {"file_name": "rules.pdf", "chunk_id": 0}


def test_long_document_is_split_with_overlap():
    text = " ".join(f"word{i}" for i in range(400))

    chunks = chunk_document(make_document(text), chunk_size=100, overlap=20)

    assert len(chunks) > 1
    assert [chunk["metadata"]["chunk_id"] for chunk in chunks] == list(range(len(chunks)))
    assert chunks[1]["text"].split()[0] in chunks[0]["text"]


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        chunk_document(make_document("text"), chunk_size=10, overlap=10)
