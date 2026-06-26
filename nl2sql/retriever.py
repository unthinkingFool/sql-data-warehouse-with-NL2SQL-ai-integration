# nl2sql/retriever.py
"""
RAG Retriever: Finds the most relevant schema chunks for a given user question.
Uses cosine similarity between the question embedding and stored schema embeddings.
"""

from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from .embedder import CHROMA_DIR, COLLECTION


_model: Optional[SentenceTransformer] = None
_collection: Optional[chromadb.Collection] = None


def _get_resources():
    """Lazy-loads the embedding model and ChromaDB collection."""
    global _model, _collection

    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_collection(name=COLLECTION)

    return _model, _collection


def retrieve_schema_context(question: str, top_k: int = 4) -> str:
    """
    Retrieves the top-k most relevant schema chunks for a given question.

    Args:
        question: The user's English question about the data.
        top_k: Number of schema chunks to retrieve (default: 4).

    Returns:
        A formatted string of relevant schema context to include in the LLM prompt.

    Example:
        >>> ctx = retrieve_schema_context("Who are the top 5 customers by sales?")
        >>> # Returns: facts about fact_sales and dim_customers tables
    """
    model, collection = _get_resources()

    # Embed the question
    question_embedding = model.encode([question]).tolist()

    # Query ChromaDB for top-k similar schema chunks
    results = collection.query(
        query_embeddings=question_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Format retrieved chunks into a readable context block
    context_parts = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        similarity = 1 - dist  # Convert cosine distance → similarity score
        context_parts.append(
            f"[Table: {meta.get('table', 'Unknown')} | Relevance: {similarity:.2f}]\n"
            f"{doc}\n"
        )

    return "\n---\n".join(context_parts)


def retrieve_with_scores(question: str, top_k: int = 6) -> List[Dict[str, Any]]:
    """
    Same as retrieve_schema_context but returns structured data instead of text.
    Useful for debugging retrieval quality.
    """
    model, collection = _get_resources()
    question_embedding = model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=question_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    return [
        {
            "text": doc,
            "table": meta.get("table"),
            "similarity": round(1 - dist, 3)
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
    ]