import json
from pathlib import Path

import faiss
import numpy as np

INDEX_FILE = "faiss.index"
DOCUMENTS_FILE = "documents.json"


class VectorStore:

    def __init__(self, dimension):
        """Initalizes the FAISS index.
        Args:
            dimension (int): The dimension of the embeddings.
        """
        self.dimension = dimension
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

        self.index = faiss.read_index(str(directory_path / INDEX_FILE))
        self.dimension = self.index.d

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
