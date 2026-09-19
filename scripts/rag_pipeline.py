NO_CONTEXT_ANSWER = "I do not have enough information to answer this question."


class RAGPipeline:
    def __init__(self, retriever, generator):
        """Initializes the RAGPipeline with a retriever and a generator.
        Args:
            retriever (Retriever): An instance of the Retriever class for retrieving relevant documents.
            generator (Generator): An instance of the Generator class for generating answers based on retrieved documents.
        """
        self.retriever = retriever
        self.generator = generator

    def ask(self, question, k=None):
        """Asks a question, retrieves relevant chunks and generates a grounded answer.
        Args:
            question (str): The question to be answered.
            k (int | None): The number of relevant chunks to retrieve.
        Returns:
            dict: The generated answer and the sources it was grounded in."""
        chunks = self.retriever.retrieve(question, k=k)
        if not chunks:
            return {"answer": NO_CONTEXT_ANSWER, "sources": []}

        answer = self.generator.generate_answer(question, chunks)
        return {"answer": answer, "sources": [self.to_source(chunk) for chunk in chunks]}

    @staticmethod
    def to_source(chunk):
        """Converts a retrieved chunk into a citation payload.
        Args:
            chunk (dict): A retrieved chunk with text, metadata and score.
        Returns:
            dict: The file name, chunk id, similarity score and an excerpt.
        """
        metadata = chunk.get("metadata", {})
        text = chunk["text"]
        return {
            "file_name": metadata.get("file_name", "unknown"),
            "chunk_id": metadata.get("chunk_id"),
            "score": chunk.get("score"),
            "excerpt": text[:300] + ("..." if len(text) > 300 else ""),
        }
