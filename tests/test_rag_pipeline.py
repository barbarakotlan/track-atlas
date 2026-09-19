from scripts.rag_pipeline import NO_CONTEXT_ANSWER, RAGPipeline


class FakeRetriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.calls = []

    def retrieve(self, query, k=None):
        self.calls.append((query, k))
        return self.chunks


class FakeGenerator:
    def generate_answer(self, question, chunks):
        return f"answer to {question} from {len(chunks)} chunk(s)"


def make_chunk(text="Rule 1: no false starts.", chunk_id=0, score=0.9):
    return {
        "text": text,
        "metadata": {"file_name": "rules.pdf", "chunk_id": chunk_id},
        "score": score,
    }


def test_ask_returns_answer_and_sources():
    retriever = FakeRetriever([make_chunk()])
    pipeline = RAGPipeline(retriever, FakeGenerator())

    result = pipeline.ask("What is a false start?", k=3)

    assert result["answer"] == "answer to What is a false start? from 1 chunk(s)"
    assert result["sources"] == [
        {
            "file_name": "rules.pdf",
            "chunk_id": 0,
            "score": 0.9,
            "excerpt": "Rule 1: no false starts.",
        }
    ]
    assert retriever.calls == [("What is a false start?", 3)]


def test_ask_without_matches_skips_generation():
    pipeline = RAGPipeline(FakeRetriever([]), FakeGenerator())

    assert pipeline.ask("anything") == {"answer": NO_CONTEXT_ANSWER, "sources": []}


def test_long_excerpts_are_truncated():
    pipeline = RAGPipeline(FakeRetriever([make_chunk(text="x" * 500)]), FakeGenerator())

    excerpt = pipeline.ask("q")["sources"][0]["excerpt"]

    assert excerpt.endswith("...")
    assert len(excerpt) == 303
