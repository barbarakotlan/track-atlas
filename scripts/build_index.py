from pathlib import Path

from load_documents import load_all_documents
from chunker import chunk_document
from embedder import create_embeddings
from faiss_store import VectorStore


def build_index(knowledge_base_path):
    documents = load_all_documents(
        Path(knowledge_base_path)
    )

    chunks = []

    for document in documents:
        chunks.extend(chunk_document(document))

    embedded_chunks = create_embeddings(chunks)

    vector_store = VectorStore(dimension=384)
    vector_store.add_documents(embedded_chunks)

    vector_store.save("storage")

if __name__ == "__main__":  
    build_index("../knowledge-base/ncaa")
