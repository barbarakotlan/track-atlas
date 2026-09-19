from config import settings
from scripts.embedder import embed_query


class Retriever:
    def __init__(self, vector_store, model_name=None):
        """Initializes the Retriever with a vector store and a SentenceTransformer model.
        Args:
            vector_store (VectorStore): An instance of the VectorStore class for storing and searching embeddings
            model_name (str | None): Embedding model to use, defaults to the configured model.
        """
        self.vector_store = vector_store
        self.model_name = model_name or settings.embedding_model

    def embed_query(self, query):
        """Embeds a query using the SentenceTransformer model.
        Args:
            query (str): The query string to be embedded.
        Returns:
            list: The embedding of the query as a list of floats."""
        return embed_query(query, self.model_name)

    def retrieve(self, query, k=None):
        """Retrieves the most similar chunks to the query from the vector store.
        Args:
            query (str): The query string to search for.
            k (int | None): The number of similar chunks to return.
        Returns:
            list: A list of the most similar chunks from the vector store."""
        query_embedding = self.embed_query(query)
        return self.vector_store.search(query_embedding, k or settings.top_k)
