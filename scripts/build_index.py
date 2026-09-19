"""Builds the FAISS index for the knowledge base."""
import argparse
from pathlib import Path

from config import settings
from scripts.chunker import chunk_document
from scripts.embedder import create_embeddings
from scripts.faiss_store import VectorStore
from scripts.load_documents import load_all_documents


def build_index(knowledge_base_path, storage_path):
    """Loads, chunks and embeds every document in the knowledge base and saves the index.

    Args:
        knowledge_base_path (Path): Directory containing the source documents.
        storage_path (Path): Directory the FAISS index and documents are written to.
    Returns:
        VectorStore: The vector store that was saved to disk.
    """
    documents = load_all_documents(Path(knowledge_base_path))

    if not documents:
        raise ValueError(f"No supported documents found in {knowledge_base_path}")

    chunks = []
    for document in documents:
        chunks.extend(
            chunk_document(
                document,
                chunk_size=settings.chunk_size,
                overlap=settings.chunk_overlap,
            )
        )

    embedded_chunks = create_embeddings(chunks)

    vector_store = VectorStore(dimension=settings.embedding_dimension)
    vector_store.add_documents(embedded_chunks)
    vector_store.save(storage_path)

    print(
        f"Indexed {len(documents)} document(s) into {len(embedded_chunks)} chunks "
        f"at {Path(storage_path).resolve()}"
    )

    return vector_store


def main():
    parser = argparse.ArgumentParser(description="Build the Track Atlas vector index.")
    parser.add_argument(
        "--knowledge-base",
        type=Path,
        default=settings.knowledge_base_dir,
        help="Directory containing the documents to index.",
    )
    parser.add_argument(
        "--storage",
        type=Path,
        default=settings.storage_dir,
        help="Directory to write the FAISS index and documents to.",
    )
    args = parser.parse_args()

    build_index(args.knowledge_base, args.storage)


if __name__ == "__main__":
    main()
