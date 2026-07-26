from rag_pipeline import RAGPipeline
from retriever import Retriever
from generator import Generator
from faiss_store import VectorStore

vector_store = VectorStore(dimension=384)

retriever = Retriever(vector_store)
generator = Generator()

rag = RAGPipeline(retriever, generator)

answer = rag.ask("What are the false start rules?")

print(answer)