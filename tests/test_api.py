import pytest
from fastapi.testclient import TestClient

from backend import main
from scripts.generator import GeneratorError


class FakePipeline:
    def __init__(self, error=None):
        self.error = error

    def ask(self, question, k=None):
        if self.error:
            raise self.error
        return {
            "answer": "Use rule 4.",
            "sources": [
                {
                    "file_name": "rules.pdf",
                    "chunk_id": 1,
                    "score": 0.42,
                    "excerpt": "Rule 4 ...",
                }
            ],
        }


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "build_pipeline", lambda: (FakePipeline(), 0))
    original = dict(main.state)
    with TestClient(main.app) as test_client:
        yield test_client
    main.state.update(original)


def test_health_reports_index_state(client):
    main.state.update({"rag": FakePipeline(), "chunks": 12, "error": None})

    body = client.get("/health").json()

    assert body["status"] == "ok"
    assert body["indexed_chunks"] == 12


def test_ask_returns_answer_with_sources(client):
    main.state.update({"rag": FakePipeline(), "chunks": 12, "error": None})

    response = client.post("/ask", json={"question": "Which rule?"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Use rule 4.",
        "sources": [
            {"file_name": "rules.pdf", "chunk_id": 1, "score": 0.42, "excerpt": "Rule 4 ..."}
        ],
    }


def test_health_reports_an_empty_index_as_missing(client):
    main.state.update({"rag": FakePipeline(), "chunks": 0, "error": None})

    assert client.get("/health").json()["status"] == "index_missing"


def test_ask_without_index_returns_503(client):
    main.state.update({"rag": None, "chunks": 0, "error": "No index found."})

    response = client.post("/ask", json={"question": "Which rule?"})

    assert response.status_code == 503
    assert response.json()["detail"] == "No index found."


def test_ask_surfaces_generator_failure(client):
    main.state.update(
        {"rag": FakePipeline(error=GeneratorError("Ollama is down")), "chunks": 1, "error": None}
    )

    response = client.post("/ask", json={"question": "Which rule?"})

    assert response.status_code == 503
    assert response.json()["detail"] == "Ollama is down"


def test_empty_question_is_rejected(client):
    main.state.update({"rag": FakePipeline(), "chunks": 1, "error": None})

    assert client.post("/ask", json={"question": ""}).status_code == 422
