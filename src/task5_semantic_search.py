"""
Task 5 — Semantic Search Module.
"""

from .task4_chunking_indexing import get_collection, get_embedding_model


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity trong ChromaDB.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index
        }
        Sorted by score descending.
    """
    if not query:
        return []

    try:
        model = get_embedding_model()
        query_vector = model.encode(query).tolist()

        collection = get_collection()
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k * 2, max(collection.count(), 1)),
            include=["documents", "metadatas", "distances"],
        )

        if not results or not results["documents"] or not results["documents"][0]:
            return []

        output = []
        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            # ChromaDB cosine space returns cosine distance in [0, 2]
            score = max(0.0, 1.0 - float(dist))
            output.append({
                "content": doc,
                "score": round(score, 4),
                "metadata": meta
            })

        output.sort(key=lambda x: x["score"], reverse=True)
        return output[:top_k]
    except Exception as e:
        print(f"Error in semantic_search: {e}")
        return []


if __name__ == "__main__":
    results = semantic_search("quy chế đào tạo bách khoa", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
