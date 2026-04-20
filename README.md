# Multi-Team RAG Chatbot

This repository is a scalable scaffold for a RAG-based chatbot system where each team starts isolated and can later be unified into a multi-tenant platform.

The current design keeps team-specific configuration in `backend/app/teams/<team_name>` while shared RAG services live under `backend/app/services`. This allows Cloud, Dayforce, and future teams to own separate prompts, Milvus collections, and runtime settings without duplicating core retrieval or generation logic.

## Architecture

- `frontend`: React chat UI with a team selector.
- `backend`: Flask API layer and shared RAG orchestration stubs.
- `docker`: Dockerfiles for backend and frontend services.
- `docker-compose.yml`: Local stack with frontend and backend. The backend connects to your already-running Milvus stack.

## Request Flow

1. User selects a team in the frontend.
2. Frontend sends `POST /chat` with `{ "team": "cloud", "query": "..." }`.
3. Backend resolves team configuration through `team_router_service.get_team_config`.
4. Backend uses shared RAG service placeholders:
   - query rewriting
   - embedding generation
   - Milvus collection search
   - reranking
   - LLM answer generation
5. Backend returns an answer and lightweight metadata.

## How To Add A New Team

1. Create a new folder under `backend/app/teams`, for example:

   ```text
   backend/app/teams/security/
   ```

2. Add a `config.py` file:

   ```python
   collection_name = "security_collection"

   settings = {
       "top_k": 5,
       "enable_query_rewrite": True,
       "enable_rerank": True,
   }
   ```

3. Add a `prompt_template.txt` file with the team's assistant instructions.

4. Add the team name to `ALLOWED_TEAMS` in `backend/app/services/team_router_service.py`.

5. Create or migrate that team's Milvus collection using your ingestion pipeline.

## How To Run

From the project root:

```bash
docker compose up --build
```

Expected local services:

- Frontend: `http://localhost:3101`
- Backend: `http://localhost:8101`
- Existing Milvus: `localhost:19530`
- Existing Ollama LLM on VM: `http://192.168.28.100:11434` using `llama3`

Docker backend note:

- When running inside Docker, the backend uses `host.docker.internal:19530` to reach your existing Milvus container published on the host.
- When running locally with `python app.py`, the backend uses `localhost:19530` from `backend/.env`.
- The backend calls Ollama through `OLLAMA_BASE_URL`. For laptop-to-VM testing, set it to the VM address, for example `http://192.168.28.100:11434`.

## Future-Proofing Notes

This scaffold intentionally separates:

- tenant or team routing
- prompt ownership
- vector collection ownership
- shared RAG pipeline services
- API contracts

That separation makes it easier to later replace folder-based team config with database-backed tenant config, centralized auth, per-tenant quotas, shared observability, hybrid search, advanced reranking, and unified admin tooling.

The files are placeholders by design. Production logic should add authentication, authorization, validation, tracing, retry handling, local ingestion pipelines, Milvus schema management, and integration tests.
