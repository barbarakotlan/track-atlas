import faiss
import numpy as np

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
