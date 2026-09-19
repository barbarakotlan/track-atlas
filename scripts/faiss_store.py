import json
from pathlib import Path

import faiss
import numpy as np

INDEX_FILE = "faiss.index"
DOCUMENTS_FILE = "documents.json"
METADATA_FILE = "index_metadata.json"


class VectorStore:

    def __init__(self, dimension, embedding_model=None):
        """Initalizes the FAISS index.
        Args:
            dimension (int): The dimension of the embeddings.
            embedding_model (str | None): The model the embeddings come from.
        """
        self.dimension = dimension
        self.embedding_model = embedding_model
        self.index = faiss.IndexFlatIP(dimension)
        self.documents = []

    def __len__(self):
        return len(self.documents)

    def add_documents(self, chunks):
        """Adds embedded chunks to the vector store.
        Args:
            chunks (list): A list of dictionaries containing the embedded chunks.
        """
        if not chunks:
            return

        embeddings = np.array(
            [chunk['embedding'] for chunk in chunks],
            dtype='float32'
        )

        self.index.add(embeddings)
        self.documents.extend(chunks)

    def search(self, query_embedding, k=5):
        """Finds the most similar chunks to the query embedding.
        Args:
            query_embedding (list): The embedding of the query.
            k (int): The number of similar chunks to return.
        Returns:
            list: The most similar chunks, each with its similarity score.
        """
        if not self.documents:
            return []

        query = np.array(
            [query_embedding],
            dtype='float32'
        )

        scores, indices = self.index.search(query, min(k, len(self.documents)))
        results = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue
            document = self.documents[index]
            results.append({
                "text": document["text"],
                "metadata": document["metadata"],
                "score": float(score),
            })

        return results

    def save(self, directory):
        """Saves the FAISS index and documents to disk.
        Args:
            directory (str): The directory where the index and documents will be saved.
        """
        directory_path = Path(directory)
        directory_path.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(directory_path / INDEX_FILE))

        with open(directory_path / DOCUMENTS_FILE, "w") as f:
            json.dump(self.documents, f)

        with open(directory_path / METADATA_FILE, "w") as f:
            json.dump(
                {
                    "embedding_model": self.embedding_model,
                    "dimension": self.index.d,
                    "chunks": len(self.documents),
                },
                f,
            )

    def load(self, directory):
        """Loads the FAISS index and documents from disk.
        Args:
            directory (str): The directory where the index and documents are saved.
        """
        directory_path = Path(directory)

        if not self.exists(directory_path):
            raise FileNotFoundError(
                f"No index found in {directory_path.resolve()}. "
                "Run `python -m scripts.build_index` first."
            )

        index = faiss.read_index(str(directory_path / INDEX_FILE))
        metadata = self.read_metadata(directory_path)
        indexed_model = metadata.get("embedding_model")

        if self.embedding_model and indexed_model and indexed_model != self.embedding_model:
            raise ValueError(
                f"The index in {directory_path.resolve()} was built with embedding model "
                f"'{indexed_model}' but '{self.embedding_model}' is configured. "
                "Rebuild it with `python -m scripts.build_index`."
            )

        if index.d != self.dimension:
            raise ValueError(
                f"The index in {directory_path.resolve()} has dimension {index.d} but "
                f"{self.dimension} is configured. Rebuild it with `python -m scripts.build_index`."
            )

        self.index = index
        self.embedding_model = indexed_model or self.embedding_model

        with open(directory_path / DOCUMENTS_FILE, "r") as f:
            self.documents = json.load(f)

    @staticmethod
    def exists(directory):
        """Checks whether a saved index exists in the given directory.
        Args:
            directory (str | Path): The directory to check.
        Returns:
            bool: True when both the index and the documents file are present.
        """
        directory_path = Path(directory)
        return (
            (directory_path / INDEX_FILE).is_file()
            and (directory_path / DOCUMENTS_FILE).is_file()
        )

    @staticmethod
    def read_metadata(directory):
        """Reads the metadata saved alongside an index.
        Args:
            directory (str | Path): The directory holding the index.
        Returns:
            dict: The saved metadata, empty when the index predates it.
        """
        metadata_path = Path(directory) / METADATA_FILE
        if not metadata_path.is_file():
            return {}

        with open(metadata_path, "r") as f:
            return json.load(f)
