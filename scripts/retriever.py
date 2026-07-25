from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self, vector_store):
        """Initializes the Retriever with a vector store and a SentenceTransformer model.
        Args:
            vector_store (VectorStore): An instance of the VectorStore class for storing and searching embeddings
        """
        self.vector_store = vector_store
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_query(self, query):
        """Embeds a query using the SentenceTransformer model.
        Args:
            query (str): The query string to be embedded.
        Returns:
            list: The embedding of the query as a list of floats."""
        return self.model.encode(
            query,
            normalize_embeddings=True
        ).tolist()

    def retrieve(self, query, k=5):
        """Retrieves the most similar chunks to the query from the vector store.
        Args:
            query (str): The query string to search for.
            k (int): The number of similar chunks to return.
        Returns:
            list: A list of the most similar chunks from the vector store."""
        query_embedding = self.embed_query(query)
        return self.vector_store.search(query_embedding, k)