from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings
from scripts.faiss_store import VectorStore
from scripts.generator import Generator, GeneratorError
from scripts.rag_pipeline import RAGPipeline
from scripts.retriever import Retriever

state = {"rag": None, "chunks": 0, "error": None}


def build_pipeline():
    """Loads the vector index and wires up the RAG pipeline.
    Returns:
        tuple: The pipeline and the number of indexed chunks.
    """
    vector_store = VectorStore(
        dimension=settings.embedding_dimension,
        embedding_model=settings.embedding_model,
    )
    vector_store.load(settings.storage_dir)

    pipeline = RAGPipeline(Retriever(vector_store), Generator())
    return pipeline, len(vector_store)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        state["rag"], state["chunks"] = build_pipeline()
    except (FileNotFoundError, ValueError) as error:
        state["error"] = str(error)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    k: int = Field(default=settings.top_k, ge=1, le=20)


class Source(BaseModel):
    file_name: str
    chunk_id: int | None = None
    score: float | None = None
    excerpt: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
async def health():
    return {
        "status": "ok" if state["rag"] and state["chunks"] else "index_missing",
        "indexed_chunks": state["chunks"],
        "model": settings.llm_model,
        "error": state["error"],
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not state["rag"]:
        raise HTTPException(status_code=503, detail=state["error"] or "Index not loaded.")

    try:
        return state["rag"].ask(request.question, k=request.k)
    except GeneratorError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
