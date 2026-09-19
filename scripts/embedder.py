"""
This module provides utilities for creating embeddings for document chunks using SentenceTransformer models.
"""
from functools import cache

from sentence_transformers import SentenceTransformer

from config import settings


@cache
def get_model(model_name=None):
    """Loads (and caches) the SentenceTransformer model used for embeddings.
    Args:
        model_name (str | None): Model to load, defaults to the configured model.
    Returns:
        SentenceTransformer: The loaded model.
    """
    return SentenceTransformer(model_name or settings.embedding_model)


def embed_query(query, model_name=None):
    """Embeds a single query string.
    Args:
        query (str): The query string to embed.
        model_name (str | None): Model to use, defaults to the configured model.
    Returns:
        list: The embedding of the query as a list of floats.
    """
    return get_model(model_name).encode(query, normalize_embeddings=True).tolist()


def create_embeddings(chunks, model_name=None):
    """Creates embeddings for a list of text chunks using the SentenceTransformer model.
    Args:
        chunks (list): A list of chunk dictionaries, each containing text and metadata.
        model_name (str | None): Model to use, defaults to the configured model.
    Returns:
        list: A list of chunk dictionaries, each containing text, metadata, and the corresponding embedding.
    """
    if not chunks:
        return []

    texts = [chunk["text"] for chunk in chunks]
    embeddings = get_model(model_name).encode(texts, normalize_embeddings=True)
    embedded_chunks = []

    for chunk, embedding in zip(chunks, embeddings):
        embedded_chunk = {
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "embedding": embedding.tolist()
        }
        embedded_chunks.append(embedded_chunk)
    return embedded_chunks
