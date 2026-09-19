# Track Atlas

An AI-powered knowledge platform for everything track & field.

Track Atlas is a Retrieval-Augmented Generation (RAG) application that allows anyone to search and interact with a curated library of track & field documents using natural language.

The goal of this project is to explore modern AI engineering techniques including Retrieval-Augmented Generation, vector databases, embeddings, prompt engineering, and full-stack application development.

## How it works

```
knowledge-base/*.pdf|docx|html
  -> scripts/load_documents.py   extract + clean text
  -> scripts/chunker.py          800-token chunks, 100-token overlap
  -> scripts/embedder.py         all-MiniLM-L6-v2 embeddings (384-dim)
  -> scripts/faiss_store.py      FAISS inner-product index in storage/
  -> scripts/retriever.py        top-k semantic search for a question
  -> scripts/generator.py        local LLM via Ollama, answers from context only
  -> backend/main.py             FastAPI /ask and /health
  -> frontend                    Next.js chat UI with citations
```

## Install

Requirements: Python 3.10+, Node.js 20+, and [Ollama](https://ollama.com) for the local LLM.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # or backend/requirements.txt without the test tooling

ollama pull llama3.2:3b

cd frontend && npm install && cd ..
```

## Usage

1. Build the vector index from the documents in `knowledge-base/`:

   ```bash
   python -m scripts.build_index
   ```

   The index is written to `storage/` (git-ignored). Re-run it whenever documents change.
   Use `--knowledge-base` / `--storage` to point at other directories.

2. Start the API:

   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

   - `GET /health` reports whether the index loaded and how many chunks it holds.
   - `POST /ask` with `{"question": "...", "k": 5}` returns an answer plus the source chunks it was grounded in.

3. Start the UI:

   ```bash
   cd frontend && npm run dev
   ```

   Open http://localhost:3000 and ask a question. Set `NEXT_PUBLIC_API_URL` if the API is not on `http://localhost:8000`.

On CPU-only machines a single answer from `llama3.2:3b` can take a couple of minutes; a smaller model (`TRACK_ATLAS_LLM_MODEL=llama3.2:1b`) is noticeably faster.

## Configuration

Settings live in `config.py` and can be overridden with environment variables prefixed with `TRACK_ATLAS_` or a `.env` file:

| Variable | Default | Purpose |
| --- | --- | --- |
| `TRACK_ATLAS_KNOWLEDGE_BASE_DIR` | `knowledge-base` | Documents to index |
| `TRACK_ATLAS_STORAGE_DIR` | `storage` | Where the FAISS index is stored |
| `TRACK_ATLAS_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformer model |
| `TRACK_ATLAS_LLM_MODEL` | `llama3.2:3b` | Ollama model used for answers |
| `TRACK_ATLAS_OLLAMA_HOST` | `http://localhost:11434` | Ollama endpoint |
| `TRACK_ATLAS_TOP_K` | `5` | Chunks retrieved per question |
| `TRACK_ATLAS_CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins |

## Tests

```bash
pytest          # backend + RAG unit tests
ruff check .    # Python lint
cd frontend && npm run lint && npm run build
```

## Contributing

Coming soon.

## License

Unlicensed
