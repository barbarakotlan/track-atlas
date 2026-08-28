import faiss
import json
import numpy as np
from pathlib import Path

class VectorStore:

    def __init__(self, dimension):
        """Initalizes the FAISS index.
        Args:
            dimension (int): The dimension of the embeddings.
        """
        self.index = faiss.IndexFlatIP(dimension)
        self.documents = []

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
            list: A list of the most similar chunks.
        """
        query = np.array(
            [query_embedding],
            dtype='float32'
        )

        distances, indices = self.index.search(query, k)
        results = []

        for index in indices[0]:
            if index != -1:
                results.append(self.documents[index])

        return results

    def save(self, directory):
        """Saves the FAISS index and documents to disk.
        Args:
            directory (str): The directory where the index and documents will be saved.
        """
        directory_path = Path(directory)
        directory_path.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(directory_path / "faiss.index"))

        with open(directory_path / "documents.json", "w") as f:
            json.dump(self.documents, f)

    def load(self, directory):
        """Loads the FAISS index and documents from disk.
        Args:
            directory (str): The directory where the index and documents are saved.
        """
        directory_path = Path(directory)

        self.index = faiss.read_index(str(directory_path / "faiss.index"))

        with open(directory_path / "documents.json", "r") as f:
            self.documents = json.load(f)
