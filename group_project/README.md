# Bài Tập Nhóm — University Services RAG Chatbot

## Mục Tiêu

Sau khi hoàn thành bài cá nhân, nhóm ngồi lại để xây dựng **1 trong 2 sản phẩm**:

---

## Yêu cầu 1: Sản phẩm nhóm RAG Chatbot

Xây dựng chatbot trả lời câu hỏi về dịch vụ và chính sách đại học liên quan.

**Yêu cầu:**
- Giao diện chat (Streamlit / Gradio / Chainlit)
- Trả lời có citation (dựa trên Task 10)
- Hỗ trợ follow-up questions (conversation memory)
- Hiển thị source documents đã dùng

**Stack gợi ý:**
```
Chainlit/Streamlit → Retrieval (Task 9) → Generation (Task 10) → Display
```

---

## Yêu cầu 2: RAG Evaluation Pipeline

Sử dụng **1 trong 3 framework** sau để evaluate pipeline RAG của nhóm:

### Framework lựa chọn

| Framework | Cài đặt | Đặc điểm |
|-----------|---------|-----------|
| [DeepEval](https://github.com/confident-ai/deepeval) | `pip install deepeval` | Nhiều metric built-in, dễ integrate với pytest |
| [RAGAS](https://github.com/explodinggradients/ragas) | `pip install ragas` | Chuẩn industry cho RAG eval, 3 trục chính |
| [TruLens](https://github.com/truera/trulens) | `pip install trulens` | Dashboard UI, feedback functions mạnh |

### Yêu cầu Evaluation

1. **Tạo Golden Dataset** — tối thiểu 15 cặp Q&A (question, expected_answer, expected_context)
2. **Chạy evaluation** trên toàn bộ golden dataset với các metrics sau:
   - **Faithfulness** — câu trả lời có bám đúng context không?
   - **Answer Relevance** — câu trả lời có đúng câu hỏi không?
   - **Context Recall** — retriever có lấy đủ evidence không?
   - **Context Precision** — trong context lấy về, bao nhiêu % thực sự hữu ích?
3. **So sánh A/B** — chạy eval trên ít nhất 2 config khác nhau (ví dụ: có reranking vs không reranking, hoặc hybrid vs dense-only)
4. **Báo cáo** — bảng điểm + phân tích worst performers + đề xuất cải tiến

Xem code mẫu (DeepEval/RAGAS/TruLens) chi tiết trong `README.md` gốc mục "Yêu cầu 2".

### Deliverable Evaluation

- [x] File `group_project/evaluation/golden_dataset.json` — 15+ cặp Q&A
- [ ] File `group_project/evaluation/eval_pipeline.py` — script chạy evaluation
- [ ] File `group_project/evaluation/results.md` — bảng điểm + phân tích
- [ ] So sánh A/B ít nhất 2 configs

---

## Yêu Cầu Chung

1. **Tích hợp pipeline** từ bài cá nhân của các thành viên
2. **Demo hoạt động được** trong buổi trình bày (chạy local hoặc deploy)
3. **Evaluation pipeline** chạy được và có báo cáo kết quả
4. **Code push lên repository** chung của nhóm
5. **README** mô tả kiến trúc và phân công (điền bên dưới)

---

## Kiến Trúc Hệ Thống

```
┌──────────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                      │
│              User Input → Chat Display → Sources             │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│           Task 10 — Generation + Citation (LLM)              │
│  OpenRouter/GPT-4o-mini │ System Prompt │ Out-of-scope Guard │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│             Task 9 — Retrieval Pipeline (Hybrid)             │
│                                                              │
│  ┌─────────────────┐   ┌──────────────────┐                  │
│  │ Task 5: Semantic │   │ Task 6: Lexical  │                  │
│  │ (ChromaDB+MiniLM)│   │ (BM25+TermExpand)│                  │
│  └────────┬────────┘   └────────┬─────────┘                  │
│           └──────┬──────────────┘                             │
│                  ▼                                           │
│        Task 7: RRF Reranking (k=60)                          │
│                  │                                           │
│     ┌────────────▼────────────┐                              │
│     │ Score < 0.3 → Fallback  │                              │
│     └────────────┬────────────┘                              │
│                  ▼                                           │
│      Task 8: PageIndex (Structural)                          │
└──────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│           Task 4 — Chunking & Indexing                       │
│  RecursiveCharacterTextSplitter (800/100) → ChromaDB         │
│  Embedding: sentence-transformers/all-MiniLM-L6-v2 (384d)   │
└──────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│        Task 1-3 — Data Pipeline                              │
│  Crawl (DUT) → Standardize → Convert to Markdown            │
│  9 Legal docs + 5 News articles                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Phân Công Công Việc

| Thành viên | MSSV | Nhiệm vụ | Trạng thái |
|-----------|------|----------|------------|
| Nguyễn Tiến | 2A202601655 | Frontend & Chatbot Developer (app.py, UI/UX) | ✅ Hoàn thành |
| Trần Tiến Dũng | 2A202601783 | Team Leader & RAG Architect (Task 9-10, Pipeline) | ✅ Hoàn thành |
| Lê Hoàng Việt | 2A202601543 | Evaluation & QA Engineer (Golden Dataset, Eval Pipeline) | 🔄 Đang làm |
| Nguyễn Thiên Tài | 2A202601849 | Data & Retrieval Specialist (Task 1-6, Data Collection) | ✅ Hoàn thành |

---

## Hướng Dẫn Chạy

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Setup API key
cp .env.example .env
# Thêm OPENROUTER_API_KEY vào file .env

# Index dữ liệu (chạy 1 lần)
python -m src.task4_chunking_indexing

# Chạy app
streamlit run app.py
```

---

## Lưu ý

Hãy giữ lại repo này nếu như bạn học track 3 giai đoạn 2, chúng ta sẽ phát triển tiếp dự án lên knowledge graph để khắc phục các câu hỏi hóc búa khi có các câu hỏi khó.
