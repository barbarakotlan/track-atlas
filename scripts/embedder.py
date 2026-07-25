"""
This module provides utilities for creating embeddings for document chunks using SentenceTransformer models.
"""
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embeddings(chunks):
    """Creates embeddings for a list of text chunks using the SentenceTransformer model.
    Args:
        chunks (list): A list of chunk dictionaries, each containing text and metadata.
    Returns:
        list: A list of chunk dictionaries, each containing text, metadata, and the corresponding embedding.
    """
    if not chunks:
        return []

    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True)
    embedded_chunks = []

    for chunk, embedding in zip(chunks, embeddings):
        embedded_chunk = {
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "embedding": embedding.tolist()
        }
        embedded_chunks.append(embedded_chunk)
    return embedded_chunks
