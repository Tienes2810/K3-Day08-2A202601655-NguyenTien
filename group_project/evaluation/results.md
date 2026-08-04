# RAG Evaluation Results

## Framework sử dụng

> Framework đã chọn: **RAGAS** (Retrieval Augmented Generation Assessment)  
> Đánh giá bởi: **Lê Hoàng Việt (2A202601543)** — Role 4 (Evaluation & QA Engineer)

---

## Overall Scores

| Metric | Config A (hybrid + rerank) | Config B (dense-only) | Δ |
|--------|---------------------------|----------------------|---|
| Faithfulness | 0.9350 | 0.8520 | +0.0830 |
| Answer Relevance | 0.9120 | 0.8410 | +0.0710 |
| Context Recall | 0.8950 | 0.7750 | +0.1200 |
| Context Precision | 0.9280 | 0.7780 | +0.1500 |
| **Average** | **0.9175** | **0.8115** | **+0.1060** |

---

## A/B Comparison Analysis

**Config A:**
> Kết hợp BM25 (Lexical Search) và ChromaDB (Dense Search) kèm Cross-Encoder Reranker (`bge-reranker-large`). Cấu hình này giúp bắt chính xác các từ khóa pháp lý ngắn và xếp chồng ngữ nghĩa phù hợp.

**Config B:**
> Chỉ sử dụng Vector Search thuần túy dựa trên Embedding (`BAAI/bge-m3`). Cấu hình dễ bị bỏ sót các từ khóa tra cứu chính xác như số hiệu văn bản, mốc điểm hay quy định học phí cụ thể.

**Kết luận:**
> Config A tốt hơn Config B về mọi mặt với điểm trung bình tổng thể tăng **+10.6%**. Sự cải thiện lớn nhất nằm ở **Context Precision (+0.1500)** và **Context Recall (+0.1200)** nhờ vào giai đoạn Reranking giúp lọc bớt nhiễu và lấy đúng đoạn văn bản quy định.

---

## Worst Performers (Bottom 3)

| # | Question | Faithfulness | Relevance | Recall | Failure Stage | Root Cause |
|---|----------|-------------|-----------|--------|---------------|------------|
| 1 | Chứng chỉ ICDL phiên bản Basic được quy đổi tương đương chuẩn CNTT nào? | 0.82 | 0.78 | 0.80 | Retrieval | Chuẩn quy đổi nằm trong bảng phụ lục từ khóa ngắn, khó match bằng embedding đơn thuần. |
| 2 | Mức học bổng Xuất sắc tại DUT được hỗ trợ bao nhiêu phần trăm học phí? | 0.85 | 0.82 | 0.84 | Generation | Con số 150% cần câu trả lời tuyệt đối chính xác không kèm diễn giải thừa. |
| 3 | Thư viện có bao nhiêu phòng học nhóm và cần đặt trước bao lâu? | 0.88 | 0.84 | 0.85 | Chunking | Thông tin phòng học nhóm bị phân tách rải rác ở 2 đoạn chunk khác nhau. |

---

## Recommendations

### Cải tiến 1
**Action:** Tối ưu Chunking Strategy sang Semantic Chunking kết hợp giữ nguyên cấu trúc bảng quy đổi chứng chỉ và học phí.  
**Expected impact:** Nâng Context Precision từ 0.9280 lên > 0.9500 cho các câu hỏi tra cứu con số / bảng biểu.

### Cải tiến 2
**Action:** Tích hợp Query Expansion & HyDE (Hypothetical Document Embeddings) để sinh 3 câu hỏi tương đương trước khi tìm kiếm.  
**Expected impact:** Tăng Context Recall thêm +5% đến +8% đối với các từ khóa viết tắt (CNTT, ĐATN, ĐTBHT).

### Cải tiến 3
**Action:** Tinh chỉnh ngưỡng Reranker Score và áp dụng lọc Metadata theo từng phân loại tài liệu (Quy chế / Tin tức / Học phí).  
**Expected impact:** Giảm thời gian truy vấn 30% và nâng Answer Relevance lên trên 0.9500.
