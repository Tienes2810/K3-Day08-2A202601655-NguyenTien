"""
Task 6 — Lexical Search Module (BM25).
"""

import re
from pathlib import Path
from .task4_chunking_indexing import load_documents, chunk_documents

_bm25_index = None
_corpus_chunks = []

# Từ điển đồng nghĩa / dịch Anh-Việt đơn giản cho RAG trường đại học
TERM_MAPPING = {
    "tuition": "học phí",
    "fee": "học phí thanh toán",
    "payment": "thanh toán học phí",
    "policy": "quy chế quy định",
    "scholarship": "học bổng khuyến khích",
    "eligibility": "điều kiện xét học bổng",
    "library": "thư viện tài liệu",
    "study": "học tập",
    "room": "phòng học nhóm",
    "accommodation": "ký túc xá chỗ ở",
    "registration": "đăng ký học phần",
    "course": "học phần tín chỉ",
}


def _tokenize(text: str) -> list[str]:
    """Tokenize cho tiếng Việt / tiếng Anh và mở rộng từ đồng nghĩa."""
    text_lower = text.lower()

    # Mở rộng từ khóa Anh -> Việt
    expanded_terms = []
    for en_word, vi_phrase in TERM_MAPPING.items():
        if en_word in text_lower:
            expanded_terms.extend(vi_phrase.split())

    text_clean = re.sub(r"[^\w\s]", " ", text_lower)
    tokens = [w for w in text_clean.split() if w.strip()]
    tokens.extend(expanded_terms)
    return tokens


def get_bm25_corpus():
    global _bm25_index, _corpus_chunks
    if _bm25_index is None or not _corpus_chunks:
        docs = load_documents()
        _corpus_chunks = chunk_documents(docs)
        if not _corpus_chunks:
            return None, []

        tokenized_corpus = [_tokenize(c["content"]) for c in _corpus_chunks]
        try:
            from rank_bm25 import BM25Okapi
            _bm25_index = BM25Okapi(tokenized_corpus)
        except ImportError:
            _bm25_index = None

    return _bm25_index, _corpus_chunks


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}
        Sorted by score descending. Trả [] rỗng nếu không có kết quả liên quan.
    """
    if not query:
        return []

    bm25, corpus = get_bm25_corpus()
    if not corpus:
        return []

    tokenized_query = _tokenize(query)

    if bm25 is not None and tokenized_query:
        scores = bm25.get_scores(tokenized_query)
    else:
        scores = []
        for c in corpus:
            content_lower = c["content"].lower()
            sc = sum(1.0 for q in tokenized_query if q in content_lower)
            scores.append(sc)

    # CHỈ trả về kết quả có score > 0 (thực sự match keyword)
    scored_items = []
    for idx, sc in enumerate(scores):
        if sc > 0:
            scored_items.append({
                "content": corpus[idx]["content"],
                "score": float(round(sc, 4)),
                "metadata": corpus[idx]["metadata"]
            })

    scored_items.sort(key=lambda x: x["score"], reverse=True)
    return scored_items[:top_k]


if __name__ == "__main__":
    results = lexical_search("scholarship eligibility", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
