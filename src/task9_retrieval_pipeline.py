"""
Task 9 — Retrieval Pipeline Hoàn Chỉnh.
"""

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search

SCORE_THRESHOLD = 0.3
DEFAULT_TOP_K = 5
RERANK_METHOD = "rrf"

# Ngưỡng tối thiểu: nếu best cosine score dưới mức này → coi như ngoài phạm vi
OUT_OF_SCOPE_THRESHOLD = 0.15


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """
    Retrieval pipeline hoàn chỉnh với hybrid search + RRF + PageIndex fallback logic.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả cuối cùng
        score_threshold: Ngưỡng điểm cosine gốc tối thiểu (để trigger fallback)
        use_reranking: Có áp dụng reranking hay không

    Returns:
        List of {
            'content': str,
            'score': float,
            'original_cosine_score': float,  # Điểm cosine gốc
            'metadata': dict,
            'source': str  # 'hybrid' hoặc 'pageindex'
        }
    """
    if not query:
        return []

    # Step 1: Run semantic & lexical search
    dense_results = semantic_search(query, top_k=top_k * 2)
    sparse_results = lexical_search(query, top_k=top_k * 2)

    # Check best raw cosine similarity score for fallback decision
    best_dense_score = dense_results[0]["score"] if dense_results else 0.0

    # Guard: Nếu score quá thấp → câu hỏi ngoài phạm vi hoàn toàn
    if best_dense_score < OUT_OF_SCOPE_THRESHOLD and not sparse_results:
        return []

    # Gắn original_cosine_score từng chunk từ dense_results trước khi merge RRF
    for item in dense_results:
        item["original_cosine_score"] = item.get("score", 0.0)

    # Step 2: Merge using RRF (or skip if reranking disabled)
    if use_reranking and dense_results and sparse_results:
        merged = rerank_rrf([dense_results, sparse_results], top_k=top_k * 2)
    elif dense_results:
        merged = dense_results[:top_k * 2]
    elif sparse_results:
        merged = sparse_results[:top_k * 2]
    else:
        merged = []

    # Gắn source tag và fallback original_cosine_score nếu thiếu (ví dụ từ sparse-only)
    for item in merged:
        item["source"] = "hybrid"
        if "original_cosine_score" not in item:
            item["original_cosine_score"] = 0.0

    # Step 3: Trigger Fallback if raw cosine similarity is below threshold or hybrid results are empty
    if best_dense_score < score_threshold or not merged:
        fallback = pageindex_search(query, top_k=top_k)
        if fallback:
            # Gắn original_cosine_score cho fallback results
            for item in fallback:
                item["original_cosine_score"] = best_dense_score
            return fallback
        # Nếu cả pageindex cũng trống → trả merged (có thể rỗng)

    final_results = merged[:top_k] if merged else []
    return final_results


if __name__ == "__main__":
    test_queries = [
        "Quy chế đào tạo đại học bách khoa",
        "Quy định đồ án tốt nghiệp",
        "xyzabc123nonsense",
        "Thời tiết hôm nay thế nào?",
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        print("-" * 60)
        results = retrieve(q, top_k=3)
        if not results:
            print("  → Ngoài phạm vi hệ thống, không có kết quả.")
        for i, r in enumerate(results, 1):
            cos = r.get('original_cosine_score', 0)
            print(f"  {i}. [RRF:{r['score']:.3f}|Cos:{cos:.3f}] [{r['source']}] {r['content'][:80]}...")
