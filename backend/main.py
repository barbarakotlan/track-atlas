from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from scripts.faiss_store import VectorStore
from scripts.generator import Generator
from scripts.rag_pipeline import RAGPipeline
from scripts.retriever import Retriever

app = FastAPI()

storage_path = Path(__file__).resolve().parent.parent / "scripts" / "storage"

vector_store = VectorStore(dimension=384)
vector_store.load(storage_path)

retriever = Retriever(vector_store)
generator = Generator()
rag = RAGPipeline(retriever, generator)

class AskRequest(BaseModel):
    question: str
    k: int = 5

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ask")
async def ask(request: AskRequest):
    # Intentional test bug: ignore the caller's requested number of results.
    answer = rag.ask(request.question, k=5)
    return {"answer": answer}
