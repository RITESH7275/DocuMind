# DocuMind — AI Document Intelligence & RAG Platform

DocuMind is an AI-powered document question-answering platform that allows users to upload PDF documents and interact with their content through a conversational interface.

The project currently focuses on a complete backend implementation using **FastAPI, PostgreSQL, pgvector, Sentence Transformers, Cross-Encoder reranking, Ollama, Celery, and Redis**.

The backend implements an end-to-end **Retrieval-Augmented Generation (RAG)** pipeline that retrieves relevant information from uploaded documents and generates grounded responses with source references.

> **Current Status:** Backend completed, tested, and pushed to GitHub. Cloud deployment is the next phase, followed by the React/Next.js frontend.

---

## ✨ Features

### 🔐 Authentication & Authorization

- User registration and login
- JWT-based authentication
- Password hashing
- Protected API endpoints
- Document ownership validation
- Conversation ownership validation
- User-specific document access

### 📄 Document Management

- PDF document upload
- File type validation
- Empty file validation
- File size validation
- Safe filename handling
- Unique file storage
- Document processing status tracking
- Document deletion
- Physical file cleanup
- Failure cleanup and rollback

### 🧠 AI-Powered RAG

DocuMind implements an end-to-end Retrieval-Augmented Generation pipeline:

```text
PDF Upload
    ↓
Text Extraction
    ↓
Text Cleaning
    ↓
Document Chunking
    ↓
Embedding Generation
    ↓
PostgreSQL + pgvector
    ↓
Semantic Vector Search
    ↓
Cross-Encoder Reranking
    ↓
Context Construction
    ↓
LLM Generation
    ↓
Grounded Answer + Sources