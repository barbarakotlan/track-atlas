"""
This module provides utilities for splitting documents into token-based chunks
with configurable size and overlap for retrieval-augmented generation (RAG).
"""
import tiktoken

tokenizer = tiktoken.get_encoding("cl100k_base")

def chunk_document(document, chunk_size=800, overlap=100):
    """Splits a document into chunks of a specified size with a specified overlap.
    Args:
        document (dict): A document object containing text and metadata.
        chunk_size (int): The maximum number of tokens per chunk.
        overlap (int): The number of tokens to overlap between chunks.
    Returns:
        list: A list of chunk dictionaries, each containing text and metadata.
    """
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    text = document["text"]
    metadata = document["metadata"]
    tokens = tokenizer.encode(text)

    chunks = []
    start = 0
    chunk_id = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))

        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens)

        chunks.append({
            "text": chunk_text,
            "metadata": {
                **metadata,
                "chunk_id": chunk_id
            }
        })

        chunk_id += 1
        start += chunk_size - overlap

    return chunks
