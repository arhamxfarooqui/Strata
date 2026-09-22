# Strata — AI Tutoring Platform Backend

> Same philosophy, Python-native architecture.

Strata is an AI-powered tutoring platform for competitive programmers (and beyond) that tracks per-user skill gaps and serves targeted conceptual hints — never raw solutions.

---

## Architecture — The 4 Pillars

### 1. Skill-Gap-Aware Conceptual Tutor (Anti-Cheat)

The **Shadow Memory** system persists per-user proficiency profiles in PostgreSQL. Before every AI call, the system:
1. Queries the user's top 3 weakest concepts (with time-decay applied)
2. Injects them into the LLM system prompt
3. Forces the AI to tailor responses to the user's specific gaps

The **Prompt Guard** classifier flags "give me the answer" prompts before they reach the AI. Every query is logged to `query_logs` with:
- Whether the prompt was flagged
- Whether the response leaked a code solution (≥8-line code blocks)
- This enables computing the **direct-answer retrieval rate**: `flagged_count / total_count`

### 2. 6-Domain LLM Orchestration Engine

Complex queries are decomposed into atomic sub-tasks by DeepSeek-Reasoner, then each sub-task is routed to a domain-specific handler:

| Domain | Handler | AI Provider | Persona |
|--------|---------|-------------|---------|
| CP | `competitive_programming.py` | DeepSeek | CodeSensei |
| Web Dev | `web_dev.py` | Groq (Qwen) | The Architect |
| ML | `machine_learning.py` | Groq (Llama) | Concept Lab Scout |
| DSA | `dsa.py` | DeepSeek | Structure Sensei |
| Systems | `systems.py` | Groq (Qwen) | Systems Architect |
| InfoSec | `infosec.py` | Groq (Llama) | Red Team Analyst |

Each routing decision is logged to `routing_logs` for accuracy benchmarking.

### 3. Redis Cache-Aside Layer

The leaderboard uses a **cache-aside** pattern with parameterized keys:
- Cache key: `leaderboard:{wing}:{page}:{limit}`
- TTL: 5 minutes
- **Write-through invalidation**: When ratings change (via `/api/user/refresh` or the daily cron), all `leaderboard:*` keys are purged

Built-in instrumentation tracks hits, misses, cache latency, and DB latency. Access via `GET /api/metrics/cache`.

### 4. Fault-Tolerant Celery + RabbitMQ Pipeline

Background tasks use **Celery** with **RabbitMQ** as the broker:

| Task | Schedule | Retries | Backoff |
|------|----------|---------|---------|
| CF Upsolve Sync | Every 4 hours | 5 | Exponential + jitter |
| Global Rating Sync | Daily midnight | 3 | Exponential |

- `acks_late=True` ensures at-least-once delivery
- `reject_on_worker_lost=True` requeues tasks if a worker crashes
- Idempotency via `(user_id, problem_url)` deduplication

---

## Stack

| Component | Technology |
|-----------|------------|
| API | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Cache | Redis |
| Task Queue | Celery + RabbitMQ |
| Migrations | Alembic |
| AI Providers | Groq, DeepSeek, HuggingFace |
| Auth | JWT (HS256) + bcrypt |
| HTTP Client | httpx (async) |

---

## Quick Start

### 1. Copy environment file
```bash
cp .env.example .env
# Fill in your API keys
```

### 2. Start with Docker Compose
```bash
docker-compose up -d
```

### 3. Run migrations
```bash
docker-compose exec api alembic upgrade head
```

### 4. Verify
```bash
curl http://localhost:8081/health
# → {"status": "ok", "service": "strata"}
```

### 5. Start your existing frontend
```bash
cd ../frontend && npm run dev
# → Frontend at localhost:5173 connects to Strata at localhost:8081
```

---

## API Routes

### Public
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/auth/register` | Register |
| POST | `/api/auth/login` | Login → JWT |
| GET | `/api/public/leaderboard` | Global ranking (cached) |
| GET | `/api/public/leaderboard/wing` | Wing ranking (cached) |
| GET | `/api/public/resources` | Resource list |
| POST | `/api/public/resources` | Create resource |

### Protected (JWT Required)
| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/user/profile` | Get profile |
| POST | `/api/user/refresh` | Sync stats |
| POST | `/api/ai/codesensei` | Chat with AI mentor |
| POST | `/api/ai/roadmap` | 12-week roadmap |
| GET | `/api/ai/analysis` | Profile analysis |
| POST | `/api/ai/analyze` | Orchestrator decomposition |
| GET | `/api/wings/cp/upsolves` | Upsolve queue |
| POST | `/api/wings/cp/upsolves/:id/status` | Mark solved/skipped |
| POST | `/api/wings/cp/mock` | Mock contest |
| POST | `/api/wings/cp/sync` | Async CF sync (202) |
| GET | `/api/wings/dev/first-issues` | Good first issues |
| GET | `/api/wings/dev/health` | Repo health audit |
| POST | `/api/wings/dev/review` | AI PR review |
| POST | `/api/wings/dev/resume` | STAR resume bullets |
| GET | `/api/wings/ml/curate` | Weakness-targeted resources |

### Internal
| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/health` | Health check |
| GET | `/api/metrics/cache` | Cache instrumentation |

---

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

---

## Project Structure

```
strata/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Async SQLAlchemy
│   ├── models/              # 6 ORM models
│   ├── schemas/             # Pydantic request/response
│   ├── api/                 # Route modules
│   ├── services/            # Business logic + AI orchestration
│   │   └── domain_handlers/ # 6 domain-specific AI handlers
│   ├── cache/               # Redis cache-aside + invalidation
│   ├── tasks/               # Celery workers + beat schedule
│   ├── middleware/          # JWT auth dependency
│   └── utils/              # JWT generation
├── alembic/                 # Database migrations
├── tests/                   # Pytest suite
├── docker-compose.yml       # Full stack
├── Dockerfile
├── requirements.txt
└── .env.example
```
