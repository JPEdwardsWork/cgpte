# Post-Campaign Analysis Platform (OpenAI Edition)

This implementation adapts the provided architecture spec to an **OpenAI-native** stack (replacing Claude orchestration), and adds an **admin interface** for multi-client project/reporting stream setup.

## What is implemented in this repo

- **Admin UI (`/admin`)** to create:
  - clients (tenants)
  - projects per client
  - reporting streams per project
- **REST APIs** for client/project/stream setup and strategy docs.
- **OpenAI orchestration service abstraction** with a deterministic dry-run mode when no API key is configured.
- **Multi-tenant data model scaffolding** for clients, projects, reporting streams, strategy documents, and insight requests/responses.

## OpenAI-Native AI Layer Changes

Original spec sections that relied on Claude are mapped as follows:

- Claude orchestration → `OpenAIOrchestrator` (`gpt-4.1-mini` default, configurable via `POSTCAMPAIGN_OPENAI_MODEL`)
- Claude RAG summarization hooks → strategy document list + source citation placeholders
- Claude narrative generation for reporting → OpenAI-compatible service abstraction (ready for extension)

## API Surface

- `GET /health`
- `GET /admin`
- `POST /admin/clients`
- `POST /admin/projects`
- `POST /admin/streams`
- `GET /api/v1/clients`
- `GET /api/v1/clients/{client_id}/projects`
- `GET /api/v1/projects/{project_id}/streams`
- `POST /api/v1/strategy-documents`
- `POST /api/v1/insights`

## Run locally

```bash
pip install fastapi uvicorn jinja2 python-multipart
uvicorn post_campaign_platform.app:app --reload
```

Then open `http://localhost:8000/admin`.

## Next steps to reach full reference architecture

1. Replace `InMemoryStore` with PostgreSQL + row-level security by `client_id`.
2. Add MCP connector services for each ad platform.
3. Add asynchronous ingestion and normalization workers.
4. Integrate vector store (ChromaDB or pgvector) for strategy docs and learnings.
5. Add auth/RBAC and optimization approval workflow.
6. Add report generation service and queue-based execution.
