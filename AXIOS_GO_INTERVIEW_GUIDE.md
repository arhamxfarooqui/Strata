# AXIOS-GO: Complete Interview Preparation Guide

> **Purpose**: This document is an exhaustive, code-level deep-dive into the AXIOS-GO project. It covers every architectural decision, every file, every data flow, and every system design tradeoff — so you can confidently answer any interview question about this project.

---

## Table of Contents

1. [Project Overview & Philosophy](#1-project-overview--philosophy)
2. [Complete Tech Stack Breakdown](#2-complete-tech-stack-breakdown)
3. [Repository Structure — File-by-File](#3-repository-structure--file-by-file)
4. [Backend Architecture Deep Dive](#4-backend-architecture-deep-dive)
5. [Database Schema & GORM Models](#5-database-schema--gorm-models)
6. [Authentication System (JWT)](#6-authentication-system-jwt)
7. [Complete REST API Reference](#7-complete-rest-api-reference)
8. [AI Intelligence Layer](#8-ai-intelligence-layer)
9. [Shadow Memory Engine](#9-shadow-memory-engine)
10. [The Upsolve Pipeline (Background Processing)](#10-the-upsolve-pipeline-background-processing)
11. [RabbitMQ Integration](#11-rabbitmq-integration)
12. [Cron Job System](#12-cron-job-system)
13. [Redis Caching Strategy](#13-redis-caching-strategy)
14. [Axios Rating Algorithm](#14-axios-rating-algorithm)
15. [External API Integrations](#15-external-api-integrations)
16. [Frontend Architecture](#16-frontend-architecture)
17. [The "Wrapped" Feature (Spotify-Style)](#17-the-wrapped-feature-spotify-style)
18. [Docker & Infrastructure](#18-docker--infrastructure)
19. [Security Considerations](#19-security-considerations)
20. [System Design Tradeoffs & Decisions](#20-system-design-tradeoffs--decisions)
21. [What I Would Improve (Critical for Interviews)](#21-what-i-would-improve-critical-for-interviews)
22. [Potential Interview Questions & Answers](#22-potential-interview-questions--answers)

---

## 1. Project Overview & Philosophy

### What is AXIOS-GO?

AXIOS-GO is a **production-grade, AI-driven platform** designed to centralize technical growth for developers. It bridges three domains:

- **Competitive Programming (CP)** — via Codeforces integration
- **Software Engineering (Dev)** — via GitHub integration
- **AI/ML Research** — via curated resources and HuggingFace

### Core Philosophy: "Decoupled Agentic Architecture"

The system is NOT a simple CRUD app. It's designed as an **Agentic Engine** — a "Second Brain" for developers that:

1. **Reasons** — Uses multi-model AI (DeepSeek for planning, Groq for execution) to decompose complex tasks
2. **Plans** — The AI Orchestrator breaks user prompts into atomic sub-tasks routed to domain-specific sub-agents
3. **Remembers** — The "Shadow Memory" system persistently tracks user proficiency (1-10) in technical concepts and injects that context into every AI call

### The "Wing" System

The platform is organized into **Wings** — specialized domains:

| Wing ID | Domain | Primary Focus |
|---------|--------|---------------|
| `CP` | Competitive Programming | Codeforces sync, upsolving, mock contests |
| `Dev` / `Web` | Software Engineering | Repo health, PR review, resume generation |
| `ML` | Machine Learning | Concept lab, curated resources |
| `App` | App Development | Planned for Phase 2 |
| `FOSS` | Open Source | Planned for Phase 2 |
| `InfoSec` | Cybersecurity | Planned for Phase 2 |

### Why "AXIOS"?

It's not the JavaScript HTTP library — it's the name of the technical club/platform. The name represents a "technical nexus" for cross-disciplinary excellence.

---

## 2. Complete Tech Stack Breakdown

### Backend

| Technology | Version | Purpose | Why This Choice? |
|------------|---------|---------|------------------|
| **Go** | 1.25.1 | Primary language | High concurrency via goroutines, type safety, fast compilation |
| **Gin** | v1.11.0 | HTTP framework | Fastest Go HTTP framework, middleware support, JSON binding |
| **GORM** | v1.31.1 | ORM | Auto-migration, struct-based schema, PostgreSQL JSON support |
| **PostgreSQL** | (via Docker/local) | Primary database | JSONB support for Wing arrays, relational integrity |
| **Redis** | (via Docker) | Caching layer | Sub-millisecond reads for leaderboard caching |
| **RabbitMQ** | 3-management-alpine | Message queue | Decouples heavy API calls from request lifecycle |
| **robfig/cron** | v3.0.1 | Job scheduler | Cron-expression based scheduling for background tasks |
| **golang-jwt** | v5.3.0 | Authentication | Industry-standard JWT with HS256 signing |
| **bcrypt** | (golang.org/x/crypto) | Password hashing | Adaptive cost factor, resistant to rainbow tables |
| **godotenv** | v1.5.1 | Config management | Loads `.env` files for local development |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.2.0 | UI framework |
| **Vite** | 7.2.4 | Build tool / Dev server |
| **TypeScript** | 5.9.3 | Type safety |
| **Tailwind CSS** | 3.4.17 | Utility-first styling |
| **Framer Motion** | 12.26.2 | Animations & transitions |
| **Three.js** | 0.182.0 | 3D visualizations |
| **React Three Fiber** | 9.5.0 | React renderer for Three.js |
| **Recharts** | 3.6.0 | Data visualization charts |
| **Shadcn/UI** | (via Radix) | Premium UI components |
| **Axios** (HTTP client) | 1.13.2 | API calls to backend |
| **React Router** | 7.12.0 | Client-side routing |
| **react-markdown** | 10.1.0 | Rendering AI markdown responses |
| **react-activity-calendar** | 3.0.5 | GitHub-style heatmaps |

### AI Providers

| Provider | Model | Use Case | API Style |
|----------|-------|----------|-----------|
| **DeepSeek** | `deepseek-reasoner` | CP reasoning, Orchestrator planning | OpenAI-compatible |
| **Groq** | `qwen/qwen3-32b` | Dev wing (fast) | OpenAI-compatible |
| **Groq** | `meta-llama/llama-4-scout-17b-16e-instruct` | ML wing | OpenAI-compatible |
| **Groq** | `llama-3.3-70b-versatile` | Global fallback | OpenAI-compatible |
| **HuggingFace** | `Meta-Llama-3-8B-Instruct` | Legacy/alternative roadmap | OpenAI-compatible |

### Infrastructure

| Tool | Purpose |
|------|---------|
| **Docker Compose** | Containerizes Redis + RabbitMQ |
| **Git** | Version control |

---

## 3. Repository Structure — File-by-File

```
AXIOS-GO/
├── README.md                    # Project overview with Mermaid diagrams
├── ARCHITECTURE.md              # Deep technical architecture doc
├── USE_CASES.md                 # User journey & use case documentation
├── docker-compose.yml           # Redis + RabbitMQ containers
├── server.log / server_err.log  # Backend logs
├── vite.log / vite_err.log      # Frontend dev server logs
│
├── backend/
│   ├── main.go                  # Application entry point & bootstrap
│   ├── go.mod                   # Go module definition & dependencies
│   ├── go.sum                   # Dependency checksums
│   ├── .env.example             # Environment variable template
│   ├── .env                     # Actual secrets (gitignored)
│   │
│   ├── database/
│   │   └── db.go                # PostgreSQL connection + GORM AutoMigrate
│   │
│   ├── models/
│   │   ├── user.go              # User model (handles, ratings, wings)
│   │   ├── shadow_memory.go     # AI proficiency tracking model
│   │   ├── upsolve_task.go      # Failed CF problem tracking model
│   │   └── resource.go          # Curated learning resource model
│   │
│   ├── controllers/
│   │   ├── auth.go              # Register + Login endpoints
│   │   ├── user.go              # Profile + Stats refresh
│   │   ├── ai.go                # CodeSensei, Roadmap, Orchestrator, Analysis
│   │   ├── cp.go                # Upsolve queue, sync, mock contest
│   │   ├── dev.go               # First issues, health audit, PR review, resume
│   │   ├── ml.go                # ML curation endpoint
│   │   ├── leaderboard.go       # Global + wing-specific leaderboards
│   │   └── resource.go          # CRUD for learning resources
│   │
│   ├── services/
│   │   ├── ai_common.go         # Generic OpenAI-compatible HTTP client
│   │   ├── multi_provider.go    # Wing-based AI routing + fallback logic
│   │   ├── orchestrator.go      # DeepSeek task decomposition engine
│   │   ├── shadow.go            # Shadow Memory CRUD + context formatting
│   │   ├── fetcher.go           # Codeforces + GitHub API fetchers
│   │   ├── github.go            # GitHub advanced ops (health, PR diff, commits)
│   │   ├── huggingface.go       # HuggingFace Inference API client
│   │   ├── roadmap.go           # 12-week roadmap generation via AI
│   │   ├── rabbitmq.go          # RabbitMQ connection + publish logic
│   │   ├── redis.go             # Redis connection initialization
│   │   └── sync_logic.go        # Codeforces upsolve sync business logic
│   │
│   ├── middleware/
│   │   └── auth.go              # JWT Bearer token validation middleware
│   │
│   ├── routes/
│   │   └── routes.go            # All route definitions & grouping
│   │
│   ├── workers/
│   │   ├── cron.go              # Scheduled jobs (4h upsolve, 24h rating)
│   │   └── cf_worker.go         # RabbitMQ consumer for CF sync
│   │
│   └── utils/
│       ├── jwt.go               # JWT generation & validation
│       └── rating.go            # Axios Rating calculation formula
│
└── frontend/
    ├── package.json             # NPM dependencies
    ├── vite.config.ts           # Vite configuration
    ├── tailwind.config.js       # Tailwind CSS configuration
    ├── index.html               # SPA entry point
    │
    └── src/
        ├── App.tsx              # Root component + React Router
        ├── main.tsx             # React DOM render
        ├── index.css            # Global styles
        ├── App.css              # App-level styles
        │
        ├── context/
        │   └── AuthContext.tsx   # Global auth state (React Context API)
        │
        ├── hooks/
        │   └── useWrappedData.ts # Custom hook for Wrapped feature data
        │
        ├── lib/
        │   └── utils.ts         # Tailwind CN utility
        │
        ├── pages/
        │   ├── Home.tsx         # Landing page with 3D hero + feature grid
        │   ├── Register.tsx     # Multi-field registration form
        │   ├── Login.tsx        # Login form
        │   ├── Dashboard.tsx    # User dashboard (stats, AI coach, analysis)
        │   ├── Leaderboard.tsx  # Global + wing leaderboards
        │   ├── Resources.tsx    # Resource hub with filters
        │   ├── AILab.tsx        # AI Assistant + Roadmap generator
        │   ├── Wrapped.tsx      # Spotify-style CF Wrapped
        │   └── WingPage.tsx     # Dynamic wing router (CP/Dev/ML)
        │
        ├── components/
        │   ├── Navbar.tsx       # Navigation bar
        │   ├── AICoach.tsx      # Chat interface for CodeSensei
        │   ├── AIRoadmap.tsx    # 12-week roadmap display
        │   ├── Analysis.tsx     # Profile analysis component
        │   ├── CPRoadmap.tsx    # CP-specific roadmap
        │   ├── StaticRoadmap.tsx # Pre-built roadmap display
        │   ├── WingRoadmaps.tsx # Wing roadmap selector
        │   ├── WrappedCarousel.tsx # Wrapped card carousel
        │   │
        │   ├── wings/
        │   │   ├── CPWing.tsx   # CP Wing UI (upsolve, mock, sensei)
        │   │   ├── DevWing.tsx  # Dev Wing UI (health, PR, resume, issues)
        │   │   └── MLWing.tsx   # ML Wing UI (curated resources)
        │   │
        │   ├── 3d/
        │   │   ├── HeroScene.tsx       # Landing page 3D scene
        │   │   ├── RoadmapBackground.tsx # Roadmap page 3D bg
        │   │   └── WrappedBackground.tsx # Wrapped page 3D bg
        │   │
        │   ├── Cards/           # Wrapped feature cards (13 cards)
        │   │   ├── WelcomeCard.tsx
        │   │   ├── TotalStatsCard.tsx
        │   │   ├── RatingJourneyCard.tsx
        │   │   ├── ProblemDifficultyCard.tsx
        │   │   ├── TopicsCard.tsx
        │   │   ├── BestContestCard.tsx
        │   │   ├── LanguageCard.tsx
        │   │   ├── PracticeRatingCard.tsx
        │   │   ├── PercentileCard.tsx
        │   │   ├── NightOwlCard.tsx
        │   │   ├── ActivityHeatmapCard.tsx
        │   │   ├── FinalCard.tsx
        │   │   └── WrapperCard.tsx
        │   │
        │   └── ui/              # Shadcn/UI primitives (Button, Card, etc.)
        │
        └── assets/              # Static assets
```

---

## 4. Backend Architecture Deep Dive

### Application Bootstrap Sequence

When `main.go` runs, the following happens in order:

```
1. database.Connect()       → Loads .env, builds DSN, connects PostgreSQL, runs AutoMigrate
2. services.InitRedis()     → Connects to Redis at localhost:6379
3. services.InitRabbitMQ()  → Connects to RabbitMQ, declares "codeforces_sync" queue
4. workers.StartCronJobs()  → Registers 2 cron jobs (4h upsolve + 24h rating)
5. go workers.StartCFConsumer() → Spawns goroutine to consume RabbitMQ messages
6. gin.Default()            → Creates Gin engine with logger + recovery middleware
7. CORS middleware          → Inline middleware allowing all origins (*)
8. routes.SetupRoutes(r)    → Registers all API route groups
9. r.Run(":8081")           → Starts HTTP server on port 8081
```

> **Key Interview Point**: The `go workers.StartCFConsumer()` uses a goroutine to run the RabbitMQ consumer concurrently with the HTTP server. This is a common Go pattern for running background workers alongside an API server in a single binary.

### Layered Architecture

```
┌──────────────────────────────────────┐
│           Controllers Layer          │  ← HTTP request/response handling
│  (auth, user, ai, cp, dev, ml, etc.)│     Input validation via Gin binding
├──────────────────────────────────────┤
│           Middleware Layer           │  ← Cross-cutting concerns
│         (JWT Auth, CORS)            │     Runs before controller logic
├──────────────────────────────────────┤
│            Services Layer            │  ← Business logic & external APIs
│  (multi_provider, orchestrator,     │     No HTTP awareness
│   fetcher, github, shadow, etc.)    │
├──────────────────────────────────────┤
│            Workers Layer             │  ← Background processing
│     (cron jobs, MQ consumers)       │     Runs independently
├──────────────────────────────────────┤
│            Models Layer              │  ← Data structures (GORM schemas)
│  (User, ShadowMemory, UpsolveTask)  │     Defines DB schema
├──────────────────────────────────────┤
│          Database Layer              │  ← Connection management
│       (PostgreSQL via GORM)         │     AutoMigrate on startup
└──────────────────────────────────────┘
```

### Why This Architecture?

1. **Controllers don't contain business logic** — they only handle HTTP concerns (binding, status codes, JSON responses)
2. **Services are reusable** — the same `SyncUserUpsolves()` function is called by both the cron worker and the RabbitMQ consumer
3. **Workers are decoupled** — they don't depend on the HTTP server; they can be scaled independently
4. **Models are pure data** — no methods, just struct definitions with GORM tags

---

## 5. Database Schema & GORM Models

### Model 1: User (`models/user.go`)

```go
type User struct {
    gorm.Model                          // ID, CreatedAt, UpdatedAt, DeletedAt (soft delete)
    Name             string             // Full name
    Email            string             // Unique index — used for login
    Password         string             // bcrypt hash, json:"-" (never exposed in API)
    CollegeID        string             // Institutional identifier
    CodeforcesHandle string             // e.g., "tourist"
    CodechefHandle   string             // Optional
    GithubHandle     string             // e.g., "torvalds"
    KaggleHandle     string             // Optional
    CTFHandle        string             // Optional (TryHackMe)
    Wings            []string           // JSON array in Postgres: ["CP", "ML"]
    CodeforcesRating int                // Cached, refreshed via /api/user/refresh
    CodechefRating   int                // Cached
    TotalSolved      int                // CF problems solved (deduplicated)
    GithubRepos      int                // Public repo count
    AxiosRating      int                // Computed unified score (default: 0)
    IsAdmin          bool               // Lightweight admin flag (default: false)
}
```

> **Interview Key Points**:
> - `Password` has `json:"-"` tag — it's **never serialized** in API responses
> - `Wings` uses `gorm:"serializer:json"` — GORM serializes the Go `[]string` as a JSON array in PostgreSQL
> - `Email` has `gorm:"uniqueIndex"` — database-level unique constraint
> - `gorm.Model` provides `ID`, `CreatedAt`, `UpdatedAt`, `DeletedAt` (soft deletes)

### Model 2: ShadowMemory (`models/shadow_memory.go`)

```go
type ShadowMemory struct {
    gorm.Model
    UserID      uint      // FK to User, indexed
    Domain      string    // Wing ID: "CP", "ML", "Web", etc.
    Concept     string    // e.g., "Dynamic Programming", "SQL Injection"
    Proficiency int       // 1-10 scale (1 = weakness, 10 = mastery, default: 5)
    LastNotedAt time.Time // When the AI last evaluated this concept
}
```

> **Interview Key Point**: This is the "memory" that makes the AI personalized. Before every AI call, the system queries `WHERE user_id = ? AND domain = ? ORDER BY proficiency ASC LIMIT 3` to get the user's **top 3 weakest concepts**, then injects them into the LLM's system prompt. This is what makes CodeSensei say "I notice you struggle with Segment Trees" — it's not hallucinating, it's reading from a database.

### Model 3: UpsolveTask (`models/upsolve_task.go`)

```go
type UpsolveTask struct {
    gorm.Model
    UserID      uint   // FK to User, indexed
    ProblemURL  string // e.g., "https://codeforces.com/contest/1234/problem/A"
    ProblemName string // e.g., "Beautiful Matrix"
    ContestID   int    // For deduplication
    Rating      int    // Codeforces difficulty rating
    Tags        string // JSON string: '["dp","graphs"]' (text field, not relation)
    Status      string // "pending" (default), "solved", "skipped"
}
```

> **Interview Key Point**: `Tags` is stored as a `text` field containing a JSON string array, not as a separate relation. This was a deliberate Phase 1 decision to keep the schema simple and avoid join overhead for what is essentially display-only data.

### Model 4: Resource (`models/resource.go`)

```go
type Resource struct {
    gorm.Model
    Title           string // Resource name
    Description     string // Brief description
    Link            string // URL (kept for backwards compatibility)
    Type            string // "Paper", "Video", "repo", "pdf", "article"
    Year            int    // Publication year
    Subject         string // Topic area
    WingID          string // Scoped to wing: "CP", "ML", "Web", etc. (indexed)
    SubmittedByID   uint   // User who contributed (0 = admin/seeded)
    Upvotes         int    // Community curation (default: 0)
    DifficultyLevel string // "beginner", "intermediate", "advanced"
}
```

### Entity Relationship Diagram

```
┌──────────┐       ┌───────────────┐
│   USER   │──1:N──│ UPSOLVE_TASK  │
│          │       │               │
│ id       │       │ user_id (FK)  │
│ name     │       │ problem_url   │
│ email    │       │ status        │
│ ...      │       │ rating        │
└──────┬───┘       └───────────────┘
       │
       ├──1:N──┌───────────────┐
       │       │ SHADOW_MEMORY │
       │       │               │
       │       │ user_id (FK)  │
       │       │ domain        │
       │       │ concept       │
       │       │ proficiency   │
       │       └───────────────┘
       │
       └──1:N──┌───────────────┐
               │   RESOURCE    │
               │               │
               │ submitted_by  │
               │ wing_id       │
               │ upvotes       │
               └───────────────┘
```

---

## 6. Authentication System (JWT)

### Registration Flow

```
Client                    Server
  │                         │
  │  POST /api/auth/register│
  │  {name, email, password,│
  │   college_id, wings,    │
  │   codeforces_handle,    │
  │   github_handle, ...}   │
  │─────────────────────────▶
  │                         │
  │                   1. Validate input (Gin ShouldBindJSON)
  │                   2. bcrypt.GenerateFromPassword(password, DefaultCost)
  │                   3. Create User in PostgreSQL
  │                   4. If email exists → 400 "Email already exists"
  │                         │
  │  200 {message: "ok"}    │
  │◀─────────────────────────
```

### Login Flow

```
Client                    Server
  │                         │
  │  POST /api/auth/login   │
  │  {email, password}      │
  │─────────────────────────▶
  │                         │
  │                   1. Find user by email (DB.Where)
  │                   2. bcrypt.CompareHashAndPassword
  │                   3. utils.GenerateToken(user.ID)
  │                      → HS256 signed JWT, 24h expiry
  │                   4. Return token + user object
  │                         │
  │  200 {token, user}      │
  │◀─────────────────────────
```

### JWT Token Structure

```go
type Claims struct {
    UserID uint `json:"user_id"`  // Custom claim
    jwt.RegisteredClaims          // Embedded: ExpiresAt, etc.
}
```

- **Algorithm**: HS256 (HMAC-SHA256)
- **Secret**: `JWT_SECRET` env variable (falls back to `"insecure-default-change-me"` with a warning)
- **Expiry**: 24 hours from issuance
- **Payload**: Only contains `user_id` — minimal for security

### Auth Middleware (`middleware/auth.go`)

Every protected route passes through `AuthMiddleware()`:

1. Extracts `Authorization` header
2. Splits on space to get `Bearer <token>`
3. Calls `utils.ValidateToken(token)` — parses and verifies signature + expiry
4. On success: sets `user_id` in Gin context via `c.Set("user_id", claims.UserID)`
5. On failure: returns `401 Unauthorized` and calls `c.Abort()`

> **Interview Key Point**: The middleware uses `c.Set()` / `c.Get()` to pass the authenticated user ID to downstream handlers. This is Gin's context-based request scoping — NOT a global variable.

---

## 7. Complete REST API Reference

### Public Routes (No Auth Required)

| Method | Endpoint | Controller | Description |
|--------|----------|------------|-------------|
| `POST` | `/api/auth/register` | `Register` | Create new user account |
| `POST` | `/api/auth/login` | `Login` | Authenticate & get JWT |
| `GET` | `/api/public/leaderboard` | `GetOverallLeaderboard` | Global ranking by Axios Rating |
| `GET` | `/api/public/leaderboard/wing?wing=cp` | `GetWingLeaderboard` | Wing-specific ranking |
| `GET` | `/api/public/resources?subject=&year=&wing=` | `GetResources` | Filterable resource list |
| `POST` | `/api/public/resources` | `CreateResource` | Add resource (TODO: needs auth) |

### Protected Routes (JWT Required)

#### User Routes

| Method | Endpoint | Controller | Description |
|--------|----------|------------|-------------|
| `GET` | `/api/user/profile` | `GetProfile` | Get authenticated user's profile |
| `POST` | `/api/user/refresh` | `RefreshStats` | Sync Codeforces + GitHub stats from external APIs |

#### AI Routes

| Method | Endpoint | Controller | Description |
|--------|----------|------------|-------------|
| `POST` | `/api/ai/codesensei` | `CodeSensei` | Chat with AI mentor (wing-specific persona) |
| `POST` | `/api/ai/roadmap` | `GenerateRoadmap` | Generate 12-week personalized roadmap |
| `GET` | `/api/ai/analysis` | `GetProfileAnalysis` | AI-generated profile analysis |
| `POST` | `/api/ai/analyze` | `AnalyzeWithOrchestrator` | Full orchestrator decomposition |

#### CP Wing Routes

| Method | Endpoint | Controller | Description |
|--------|----------|------------|-------------|
| `GET` | `/api/wings/cp/upsolves` | `GetUpsolveQueue` | Get user's pending upsolve problems |
| `POST` | `/api/wings/cp/upsolves/:id/status` | `UpdateUpsolveStatus` | Mark task as "solved" or "skipped" |
| `POST` | `/api/wings/cp/mock` | `GenerateMockContest` | Generate 4-problem mock contest |
| `POST` | `/api/wings/cp/sync` | `SyncUpsolves` | Trigger manual CF sync via RabbitMQ |

#### Dev Wing Routes

| Method | Endpoint | Controller | Description |
|--------|----------|------------|-------------|
| `GET` | `/api/wings/dev/first-issues?language=Go,Python` | `GetGoodFirstIssues` | Find open "good first issue" on GitHub |
| `GET` | `/api/wings/dev/health` | `GetDevHealth` | Health audit for top 3 repos |
| `POST` | `/api/wings/dev/review` | `ReviewPullRequest` | AI review of a GitHub PR diff |
| `POST` | `/api/wings/dev/resume` | `GenerateResumeBullets` | STAR-method resume bullets from commits |

#### ML Wing Routes

| Method | Endpoint | Controller | Description |
|--------|----------|------------|-------------|
| `GET` | `/api/wings/ml/curate` | `GetMLCuration` | Weakness-targeted resource curation |

---

## 8. AI Intelligence Layer

### Multi-Provider Routing (`services/multi_provider.go`)

This is one of the most architecturally significant parts of the system. The `MultiCall()` function routes AI requests to different providers based on the wing:

```
Wing Input → Provider Selection → API Call → Fallback (if failed) → Response
```

**Routing Table:**

| Wing | Primary Provider | Model | Persona Name |
|------|-----------------|-------|--------------|
| `CP` | DeepSeek | `deepseek-reasoner` | "Logic Engine (CodeSensei)" |
| `Dev`/`Web` | Groq | `qwen/qwen3-32b` | "Architect (Dev Wing)" |
| `ML` | Groq | `llama-4-scout-17b-16e-instruct` | "Concept Lab (Scout)" |
| Default | DeepSeek | `deepseek-reasoner` | "AXIOS Core (DeepSeek)" |

**Fallback Logic (Critical for Interviews):**

```
1. Try primary provider for the wing
2. If API key is missing → fallback to whichever key exists
3. If primary call fails (e.g., 402 Insufficient Balance):
   - DeepSeek failed → Try Groq (llama-3.3-70b-versatile)
   - Groq failed → Try DeepSeek (deepseek-reasoner)
4. Append "(Groq Fallback)" or "(DeepSeek Fallback)" to persona name
5. If all fail → return error
```

> **Interview Key Point**: This is a **multi-model routing strategy with automatic failover**. The reason for multiple providers is: DeepSeek excels at deep reasoning (critical for CP logic hints) but is slower. Groq excels at fast inference (important for Dev/ML real-time responses). The fallback ensures **high availability** — if one provider's API goes down or runs out of credits, the system degrades gracefully rather than failing entirely.

### The Generic AI Client (`services/ai_common.go`)

All AI providers (DeepSeek, Groq, HuggingFace) use the same OpenAI-compatible chat completion API format. The `CallOpenAICompatible()` function is a universal HTTP client:

```go
func CallOpenAICompatible(url, apiKey, model, system, prompt string) (string, error)
```

It constructs:
```json
{
  "model": "deepseek-reasoner",
  "messages": [
    {"role": "system", "content": "You are CodeSensei..."},
    {"role": "user", "content": "How do I optimize this DP?"}
  ]
}
```

And sends it with `Authorization: Bearer <apiKey>` to the provider's endpoint.

### Response Sanitization

DeepSeek's `deepseek-reasoner` model returns `<think>...</think>` blocks containing its internal reasoning chain. These are stripped from responses before returning to the user:

```go
re := regexp.MustCompile(`(?s)<think>.*?</think>\n*`)
response = re.ReplaceAllString(response, "")
```

> **Interview Key Point**: This regex uses `(?s)` flag (dot matches newline) to handle multi-line think blocks. This is important because raw reasoning tokens would confuse users and waste bandwidth.

### AI Orchestrator (`services/orchestrator.go`)

The Orchestrator is the "brain" that handles complex, multi-domain requests. When a user asks something like *"How do I build a graph visualization in React while improving my BFS skills?"*, the Orchestrator:

1. **Loads Shadow Memory context** — fetches the user's weakest concepts
2. **Calls DeepSeek** with a strict system prompt that demands JSON output
3. **Parses the decomposition plan** — a JSON object with `sub_tasks` and `summary`
4. **Executes each sub-task** via `MultiCall()` with domain-specific sub-agents

**Orchestrator System Prompt (Exact):**
```
You are the AXIOS-GO Routing Orchestrator — an internal AI planner, NOT a user-facing chatbot.
Your only job is to analyze the user's request and break it into 1-3 atomic sub-tasks...
```

**Output Schema:**
```json
{
  "sub_tasks": [
    {
      "description": "Explain BFS traversal with hints for graph problems",
      "target_wing": "CP",
      "action_type": "concept_nudge"
    },
    {
      "description": "Review React component architecture for graph visualization",
      "target_wing": "Web",
      "action_type": "code_review"
    }
  ],
  "summary": "User wants to combine CP graph skills with frontend visualization"
}
```

**JSON Parsing Robustness:**
The orchestrator includes multiple sanitization steps because LLMs sometimes wrap JSON in markdown:
```go
rawText = strings.TrimPrefix(rawText, "```json")
rawText = strings.TrimPrefix(rawText, "```")
rawText = strings.TrimSuffix(rawText, "```")
// Also extracts first { to last } to handle any preamble text
```

### Persona-Locked System Prompts

Each wing has a **personality-locked AI agent** that refuses to answer off-topic questions:

- **CodeSensei (CP)**: *"You STRICTLY ONLY answer questions regarding data structures, algorithms, math, and competitive programming logic. If the user asks about FOSS, web development... you MUST decline and aggressively steer the conversation back to competitive programming."*

- **The Architect (Dev)**: *"You STRICTLY ONLY answer questions regarding software development, system architecture, Go, React, databases, CI/CD, and GitHub workflows."*

> **Interview Key Point**: This is called **persona locking** — it prevents users from "jailbreaking" a CP mentor into writing web code or vice versa. Each sub-agent stays in its lane.

---

## 9. Shadow Memory Engine

### What It Does

Shadow Memory is a **persistent proficiency tracking system**. It stores how good a user is at specific technical concepts on a 1-10 scale.

### How It Works (`services/shadow.go`)

**Reading (Before Every AI Call):**
```go
func GetWeakConcepts(userID uint, domain string) ([]models.ShadowMemory, error)
// Returns top 3 weakest concepts: ORDER BY proficiency ASC LIMIT 3
```

**Writing (After AI Interactions):**
```go
func UpdateProficiency(userID uint, domain string, concept string, score int) error
// Upsert: creates if new, updates if exists
// Clamps score to [1, 10]
```

**Formatting for AI Context:**
```go
func FormatContextString(concepts []models.ShadowMemory) string
// Output: "User's known weak concepts: Dynamic Programming (Score: 3/10), Segment Trees (Score: 4/10)"
```

### The Learning Loop

```
User interacts with CodeSensei about DP
        ↓
Orchestrator reads Shadow Memory: "DP proficiency = 3/10"
        ↓
AI tailors response: "I notice you struggle with state transitions in DP..."
        ↓
User solves the problem successfully
        ↓
Shadow Memory updates: DP proficiency → 5/10
        ↓
Next interaction: AI adjusts difficulty level upward
```

> **Interview Key Point**: Shadow Memory is what makes AXIOS-GO an **agentic** system rather than a simple chatbot. The AI has **persistent state** about the user across sessions. This is conceptually similar to how recommendation engines track user preferences, but applied to educational proficiency.

---

## 10. The Upsolve Pipeline (Background Processing)

### What is Upsolving?

In competitive programming, "upsolving" means going back to solve problems you failed during a contest. AXIOS-GO automates the tracking of these failed problems.

### Complete Data Flow

```
Step 1: CRON TRIGGER (Every 4 hours)
    workers/cron.go → syncCodeforcesUpsolves()
    ↓
Step 2: FETCH ALL USERS WITH CF HANDLES
    database.DB.Where("codeforces_handle != ''").Find(&users)
    ↓
Step 3: FOR EACH USER → CALL SYNC LOGIC
    services.SyncUserUpsolves(&user)
    ↓
Step 4: FETCH LAST 20 SUBMISSIONS FROM CODEFORCES API
    GET https://codeforces.com/api/user.status?handle={handle}&from=1&count=20
    ↓
Step 5: FILTER NON-OK VERDICTS
    Skip: "OK" (accepted), "TESTING" (still judging)
    Keep: "WRONG_ANSWER", "TIME_LIMIT_EXCEEDED", "RUNTIME_ERROR", etc.
    ↓
Step 6: DEDUPLICATION CHECK
    database.DB.Where("user_id = ? AND problem_url = ?", ...).First(&existing)
    If already exists → skip
    ↓
Step 7: CREATE UPSOLVE TASK
    Insert new row with status = "pending"
    ↓
Step 8: USER SEES PROBLEM IN UPSOLVE QUEUE
    GET /api/wings/cp/upsolves → returns all pending tasks
    ↓
Step 9: USER SOLVES OR SKIPS
    POST /api/wings/cp/upsolves/:id/status → {status: "solved"}
```

### Manual Sync via RabbitMQ

Users can also trigger a sync manually via `POST /api/wings/cp/sync`:

```
User clicks "Sync Now"
    ↓
Controller calls services.PublishCFSync(userID, handle)
    ↓
Message published to RabbitMQ "codeforces_sync" queue
    ↓
Returns 202 Accepted immediately (async)
    ↓
Background goroutine (cf_worker.go) consumes message
    ↓
Calls services.SyncUserUpsolves(&user) — same logic as cron
    ↓
On success: d.Ack(false) — remove from queue
On failure: d.Nack(false, true) — requeue for retry
```

> **Interview Key Point**: The manual sync uses `202 Accepted` (not `200 OK`) because the work is asynchronous. The client gets an immediate response and the actual processing happens in the background via RabbitMQ. This is a textbook example of the **async task queue pattern**.

---

## 11. RabbitMQ Integration

### Connection & Queue Declaration (`services/rabbitmq.go`)

```go
func InitRabbitMQ() {
    // Connect to RabbitMQ at amqp://guest:guest@localhost:5672/
    // Declare a durable queue: "codeforces_sync"
    //   - durable: true (survives broker restart)
    //   - delete when unused: false
    //   - exclusive: false (multiple consumers allowed)
}
```

### Message Format

```go
type CFSyncPayload struct {
    UserID   uint   `json:"user_id"`
    CFHandle string `json:"cf_handle"`
}
```

### Publishing (`services/rabbitmq.go`)

```go
func PublishCFSync(userID uint, cfHandle string) error {
    // 1. Marshal payload to JSON
    // 2. Publish with DeliveryMode: amqp.Persistent (survives restart)
    // 3. Uses 5-second context timeout
}
```

### Consuming (`workers/cf_worker.go`)

```go
func StartCFConsumer() {
    // 1. auto-ack = false (manual acknowledgment for reliability)
    // 2. For each message:
    //    - Unmarshal payload
    //    - Find user in DB
    //    - Call SyncUserUpsolves
    //    - On success: Ack (remove from queue)
    //    - On failure: Nack with requeue=true (retry)
    //    - On invalid JSON: Nack with requeue=false (discard)
}
```

> **Interview Key Points**:
> - **Manual ACK**: We use `auto-ack: false` so messages aren't lost if the worker crashes mid-processing
> - **Requeue on transient failure**: If the Codeforces API is temporarily down, the message goes back to the queue for retry
> - **Discard on permanent failure**: Invalid JSON payloads are discarded (`Nack(false, false)`)
> - **Graceful degradation**: If RabbitMQ isn't running, `InitRabbitMQ()` logs a warning but doesn't crash the server

---

## 12. Cron Job System

### Implementation (`workers/cron.go`)

Uses `robfig/cron/v3` with standard cron expressions:

| Job | Schedule | Function | Description |
|-----|----------|----------|-------------|
| CF Upsolve Sync | `0 */4 * * *` (every 4 hours) | `syncCodeforcesUpsolves()` | Fetch failed problems for all users |
| Global Rating Sync | `0 0 * * *` (midnight daily) | `SyncGlobalRatings()` | Refresh all user stats & recalculate Axios Rating |

### Global Rating Sync Flow

```
1. Fetch ALL users from database
2. For each user:
   a. FetchCodeforcesStats(handle) → update CodeforcesRating
   b. FetchCodeforcesSolved(handle) → update TotalSolved
   c. FetchGithubStats(handle) → update GithubRepos
   d. CalculateAxiosRating(cfRating, cfSolved, githubRepos, 0)
   e. Save to database
   f. Sleep 500ms (rate limit respect)
```

> **Interview Key Point**: The `time.Sleep(500ms)` between users is intentional — it prevents hitting Codeforces' rate limit (which is approximately 1 request per second for the public API). Similarly, the CF upsolve sync has a `time.Sleep(1s)` between users. This is a simple but effective rate-limiting strategy.

---

## 13. Redis Caching Strategy

### Current Usage

Redis is currently used for **leaderboard caching** only:

```go
// In GetOverallLeaderboard:
// 1. Try cache first
cached, err := services.RedisClient.Get(Ctx, "global_leaderboard").Result()
// Cache hit → return immediately

// 2. Cache miss → query DB
database.DB.Order("axios_rating desc").Limit(limit).Find(&users)

// 3. Populate cache with 5-minute TTL
services.RedisClient.Set(Ctx, "global_leaderboard", jsonData, 5*time.Minute)
```

### Cache Key: `global_leaderboard`
- **TTL**: 5 minutes
- **Invalidation**: Time-based (not event-based)
- **Format**: JSON-serialized `[]models.User`

### Graceful Degradation

```go
if services.RedisClient != nil {
    // Use cache
}
// If Redis is down, falls through to DB query — no crash
```

> **Interview Key Point**: The caching strategy is **read-through with TTL-based invalidation**. In a production system, you'd want **write-through invalidation** (clear cache when ratings are updated) to prevent stale data. The 5-minute TTL is a reasonable tradeoff for Phase 1.

---

## 14. Axios Rating Algorithm

### Formula (`utils/rating.go`)

```
AxiosRating = (CF_Rating × 0.5) + (CF_Solved × 5) + (GitHub_Repos × 20) + (GitHub_PRs × 50)
```

### Breakdown

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Codeforces Rating × 0.5 | Base metric | Measures algorithmic depth |
| Problems Solved × 5 | Consistency | Rewards volume of practice |
| GitHub Repos × 20 | Engineering output | Measures project creation |
| GitHub PRs × 50 | Quality (highest weight) | Measures contribution quality |

### Edge Cases Handled

```go
// Unrated CF users (rating = 0 or -1)
if normalizedCF <= 0 {
    normalizedCF = 0
}

// Result is rounded to nearest integer
return int(math.Round(score))
```

> **Interview Key Point**: GitHub PRs have the highest weight (50 points each) because the algorithm is designed to incentivize **quality contributions** over quantity. A single meaningful PR to an open-source project is valued more than creating 2 empty repos. In Phase 1, PRs are simulated (placeholder = 0) since the PR tracking integration isn't complete.

---

## 15. External API Integrations

### Codeforces API

| Endpoint | Usage | Service Function |
|----------|-------|-----------------|
| `user.info?handles={handle}` | Fetch rating | `FetchCodeforcesStats()` |
| `user.status?handle={handle}` | Fetch submissions | `FetchCodeforcesDetails()` / `SyncUserUpsolves()` |
| `problemset.problems` | Global problemset | `GenerateMockContest()` (in controller) |

**Key Implementation Details:**
- `FetchCodeforcesDetails()` returns a `DetailedStats` struct with: `TotalSolved`, `MaxRating`, `TopTags` (map), `EasyCount` (<1200), `MediumCount` (1200-1600), `HardCount` (>1600)
- Deduplication is done via a `solved` map keyed by `"{contestId}{index}"` (e.g., `"1234A"`)
- Error handling checks for `status: "FAILED"` in CF API responses

### GitHub API

| Endpoint | Usage | Service Function |
|----------|-------|-----------------|
| `users/{handle}` | Public repo count | `FetchGithubStats()` |
| `users/{handle}/repos?sort=updated` | Repo list + languages | `FetchGithubLanguages()` / `FetchUserRepos()` |
| `repos/{owner}/{repo}/readme` | README check | `CalculateProjectHealth()` |
| `repos/{owner}/{repo}/commits?since=` | Recent activity | `CalculateProjectHealth()` |
| `repos/{owner}/{repo}` | Repo metadata | `CalculateProjectHealth()` |
| `search/issues?q=label:"good first issue"` | Open issues | `FetchGoodFirstIssues()` |
| `repos/{owner}/{repo}/pulls/{num}` | PR diff | `FetchPRDiff()` |
| `repos/{owner}/{repo}/commits?per_page=10` | Commit messages | `FetchRecentCommits()` |

**Key Implementation Details:**
- All GitHub requests go through `executeGitHubRequest()` which injects `GITHUB_TOKEN` if available (for higher rate limits)
- PR diff uses `Accept: application/vnd.github.v3.diff` header to get raw diff format
- Diff is truncated to 8000 chars before sending to AI to save tokens

### Project Health Score Calculation

```
Base Score: 50 points (every project starts at 50)
+ 20 points: Has README (GET /readme returns 200)
+ 20 points: Active in last 30 days (commits exist since now - 30 days)
+ 10 points: Low issue count (open_issues < 5)
= Max 100 points
```

### Mock Contest Generation

The `GenerateMockContest` endpoint creates a personalized 4-problem contest:

1. Fetches ALL user's solved problems from Codeforces
2. Fetches the global problemset (`problemset.problems`)
3. Filters: `ContestID >= 2050` (recent contests only) AND `unsolved` AND `rating ± 200 of target`
4. Randomly shuffles and picks 4 problems

> **Interview Key Point**: The `ContestID >= 2050` filter ensures problems are from recent contests (2025+), making mock contests feel fresh and relevant.

---

## 16. Frontend Architecture

### SPA Routing

```tsx
<Routes>
  <Route path="/"           element={<Home />} />
  <Route path="/register"   element={<Register />} />
  <Route path="/login"      element={<Login />} />
  <Route path="/dashboard"  element={<Dashboard />} />
  <Route path="/leaderboard" element={<Leaderboard />} />
  <Route path="/resources"  element={<Resources />} />
  <Route path="/ai-lab"     element={<AILab />} />
  <Route path="/wrapped"    element={<Wrapped />} />
  <Route path="/wings/:wing_id" element={<WingPage />} />
</Routes>
```

### State Management

Uses **React Context API** (not Redux) for authentication state:

```tsx
interface AuthContextType {
    user: User | null;
    login: (token: string, user: User) => void;
    logout: () => void;
    isAuthenticated: boolean;
}
```

- **Persistence**: Token and user stored in `localStorage`
- **Hydration**: On app load, `useEffect` checks localStorage and restores session
- **Why not Redux?**: The app only has one global state concern (auth). Context API is sufficient and avoids boilerplate.

### 3D Visualizations

Three.js scenes are used for immersive backgrounds:

| Component | Location | Purpose |
|-----------|----------|---------|
| `HeroScene.tsx` | Landing page | Animated 3D particles/geometry |
| `RoadmapBackground.tsx` | Roadmap page | Subtle 3D background |
| `WrappedBackground.tsx` | Wrapped page | Dynamic 3D background |

These use **React Three Fiber** (`@react-three/fiber`) and **Drei** (`@react-three/drei`) for declarative Three.js rendering within React.

### Design System

- **Theme**: Dark mode glassmorphism with neon accents (`#A855F7` purple, `#22D3EE` cyan)
- **Components**: Shadcn/UI (built on Radix UI primitives) for accessible, styled components
- **Animations**: Framer Motion for page transitions, hover effects, loading states
- **Typography**: System fonts with `font-mono` for data displays

### Key Frontend Patterns

1. **Wing Page Dynamic Routing**: `/wings/:wing_id` resolves to `<CPWing />`, `<DevWing />`, or `<MLWing />` based on URL parameter
2. **Dashboard Tabs**: Overview, Analysis, and AI Coach tabs — all in one page, lazy-loaded via Radix Tabs
3. **API Calls**: All use `axios` HTTP client with `Bearer ${token}` header from localStorage
4. **Markdown Rendering**: AI responses are rendered using `react-markdown` for rich formatting

---

## 17. The "Wrapped" Feature (Spotify-Style)

### Concept

A "Codeforces Wrapped" — similar to Spotify Wrapped — that gives users a visual year-in-review of their competitive programming journey.

### Data Pipeline (`hooks/useWrappedData.ts`)

1. Fetches ALL submissions for a user from Codeforces API
2. Filters by selected year (or all time)
3. Computes analytics:
   - Total problems solved & attempts
   - Rating journey (max, min, current)
   - Problem difficulty distribution (Easy/Medium/Hard)
   - Top tags (most solved topics)
   - Best contest performance
   - Preferred programming language
   - Average problem rating
   - Night owl analysis (late-night submissions)
   - Activity heatmap data
   - Percentile estimation

### Card Carousel (13 Cards)

The data is presented as a **swipeable card carousel** (like Spotify Wrapped stories):

| Card # | Component | Content |
|--------|-----------|---------|
| 1 | `WelcomeCard` | Handle + year intro |
| 2 | `TotalStatsCard` | Total solved, attempts, success rate |
| 3 | `RatingJourneyCard` | Rating graph |
| 4 | `ProblemDifficultyCard` | Easy/Medium/Hard breakdown |
| 5 | `TopicsCard` | Top 5 problem tags |
| 6 | `BestContestCard` | Highest rating change in a contest |
| 7 | `LanguageCard` | Most used programming language |
| 8 | `PracticeRatingCard` | Average problem difficulty attempted |
| 9 | `PercentileCard` | Estimated global percentile |
| 10 | `NightOwlCard` | Late-night submission stats |
| 11 | `ActivityHeatmapCard` | GitHub-style activity heatmap |
| 12 | `FinalCard` | Summary + motivational message |
| 13 | `WrapperCard` | Shareable summary card |

---

## 18. Docker & Infrastructure

### Docker Compose (`docker-compose.yml`)

```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    container_name: axios_redis
    ports: ["6379:6379"]
    restart: unless-stopped

  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: axios_rabbitmq
    ports:
      - "5672:5672"    # AMQP protocol
      - "15672:15672"  # Management UI (guest/guest)
    restart: unless-stopped
```

### Running the Project

```bash
# 1. Start infrastructure
docker-compose up -d

# 2. Start backend
cd backend
cp .env.example .env  # Fill in API keys
go run main.go        # Runs on :8081

# 3. Start frontend
cd frontend
npm install
npm run dev           # Runs on :5173
```

### Environment Variables Required

| Variable | Required | Purpose |
|----------|----------|---------|
| `DB_HOST` | Yes | PostgreSQL host |
| `DB_USER` | Yes | PostgreSQL user |
| `DB_PASSWORD` | Yes | PostgreSQL password |
| `DB_NAME` | Yes | Database name (default: "axios") |
| `DB_PORT` | Yes | PostgreSQL port (default: 5432) |
| `GROQ_API_KEY` | Yes | Groq inference API key |
| `DEEPSEEK_API_KEY` | Yes | DeepSeek reasoning API key |
| `JWT_SECRET` | Yes | Secret for JWT signing |
| `GITHUB_TOKEN` | Recommended | GitHub PAT for higher rate limits |
| `HF_TOKEN` | Optional | HuggingFace API token |
| `PORT` | Optional | Server port (default: 8081) |

---

## 19. Security Considerations

### What's Done Well

1. **Password hashing**: bcrypt with `DefaultCost` (10 rounds) — resistant to brute force
2. **JWT with expiry**: 24-hour tokens prevent indefinite session hijacking
3. **Password never exposed**: `json:"-"` tag on User.Password
4. **SQL injection prevention**: GORM uses parameterized queries (`Where("email = ?", input.Email)`)
5. **Input validation**: Gin's `binding:"required,email"` tags on request structs
6. **CORS**: Explicit header setting (though currently allows all origins)

### Known Limitations (Good to Mention in Interviews)

1. **CORS allows `*`**: Should be restricted to frontend domain in production
2. **No rate limiting**: API endpoints are unprotected against brute force
3. **No HTTPS**: Running on plain HTTP (needs TLS in production)
4. **JWT secret fallback**: Falls back to hardcoded default if env var is missing
5. **No refresh tokens**: Only access tokens with 24h expiry; no silent refresh
6. **Resource creation is public**: `POST /api/public/resources` has a TODO for auth
7. **No RBAC**: Only a boolean `IsAdmin` flag, no role-based access control

---

## 20. System Design Tradeoffs & Decisions

### Why Go over Node.js/Python?

| Factor | Go | Node.js | Python |
|--------|-----|---------|--------|
| Concurrency | Goroutines (lightweight) | Event loop (single-threaded) | Threading (GIL limited) |
| Type Safety | Compile-time | Runtime (TypeScript helps) | Runtime |
| Performance | Compiled binary | V8 interpreted | Interpreted |
| Deployment | Single binary | node_modules | virtualenv |

**Go was chosen for**: High concurrency (goroutines for workers), type safety, single binary deployment, and excellent HTTP performance with Gin.

### Why PostgreSQL over MongoDB?

- **Relational data**: Users → UpsolveTask is a natural 1:N relationship
- **JSONB support**: Wings are stored as JSON arrays, getting best of both worlds
- **ACID compliance**: Critical for financial-like operations (rating calculations)
- **GORM support**: Excellent Go ORM with auto-migration

### Why RabbitMQ over Redis Pub/Sub?

- **Persistence**: RabbitMQ messages survive broker restart (durable queue + persistent delivery)
- **Acknowledgment**: Manual ACK ensures messages aren't lost if worker crashes
- **Requeue**: Failed messages can be requeued for retry — Redis Pub/Sub drops messages
- **Backpressure**: RabbitMQ naturally handles backpressure; Redis doesn't

### Why Multiple AI Providers?

- **Cost optimization**: DeepSeek is cheaper for reasoning but slower; Groq is faster but costlier
- **Availability**: If one provider is down, the other is the fallback
- **Specialization**: DeepSeek-reasoner is better at multi-step logic (CP); Groq's Llama is better at code review (Dev)

### Tags as Text vs. Relation

`UpsolveTask.Tags` stores JSON as a text field instead of a many-to-many relation:
- **Pros**: Simple schema, no join tables, easy serialization
- **Cons**: Can't query "all problems with tag X" efficiently
- **Decision**: Phase 1 only needs tags for display, not querying

---

## 21. What I Would Improve (Critical for Interviews)

Interviewers love when you can critique your own work. Here's what to say:

### Backend Improvements

1. **Add request rate limiting** using Redis token buckets
2. **Implement refresh tokens** (JWT access token + longer-lived refresh token)
3. **Add structured logging** (replace `fmt.Println` with `zap` or `logrus`)
4. **Write unit tests** — currently no test files exist
5. **Add graceful shutdown** handling for the HTTP server and RabbitMQ consumer
6. **Use database transactions** for operations that update multiple tables
7. **Implement proper error types** instead of `fmt.Errorf` everywhere
8. **Add OpenAPI/Swagger documentation** for the REST API
9. **Move CORS to a proper middleware** (e.g., `gin-contrib/cors`) instead of inline
10. **Add health check endpoints** (`/healthz`, `/readyz`) for container orchestration

### Architecture Improvements

1. **Event sourcing for Shadow Memory** — instead of overwriting proficiency scores, store events
2. **WebSocket support** for real-time AI streaming responses (currently synchronous)
3. **Circuit breaker pattern** for external API calls (Codeforces, GitHub)
4. **Distributed tracing** (OpenTelemetry) for debugging cross-service issues
5. **Separate worker process** — currently the API server and workers share the same binary

### Frontend Improvements

1. **Add error boundaries** for graceful crash handling
2. **Implement optimistic UI updates** for better perceived performance
3. **Add service worker** for offline support
4. **Code splitting** with React.lazy for faster initial load
5. **State management upgrade** — Context API is fine for auth but add Zustand/Jotai for complex state

---

## 22. Potential Interview Questions & Answers

### Architecture & System Design

**Q: Why did you choose Go for the backend?**
> Go was chosen for three reasons: (1) **Goroutines** — we run background workers (cron jobs, RabbitMQ consumers) concurrently with the HTTP server in a single binary, which Go handles natively. (2) **Performance** — the Gin framework is one of the fastest HTTP frameworks available, critical for low-latency AI proxy calls. (3) **Type safety** — compile-time type checking prevents entire categories of runtime errors.

**Q: How does your system handle a spike in Codeforces sync requests?**
> Manual syncs go through RabbitMQ. Even if 1000 users hit "sync" simultaneously, the messages queue up and the consumer processes them sequentially with rate-limit-aware delays. The user gets a `202 Accepted` immediately, so the UI never blocks. If the consumer crashes, messages are requeued automatically because we use manual ACK.

**Q: Explain the data flow when a user asks the AI a question.**
> 1. Frontend sends POST to `/api/ai/codesensei` with the message and wing. 2. Controller validates JWT, loads user from DB. 3. Constructs a context string with user stats. 4. Selects the persona-locked system prompt based on wing. 5. Calls `MultiCall()` which routes to the appropriate AI provider. 6. If the primary provider fails, it falls back to the alternative. 7. Response is sanitized (removes `<think>` blocks). 8. Returns JSON with `response` and `persona` fields.

**Q: What's the difference between the Orchestrator and MultiCall?**
> `MultiCall` is a **single-turn AI call** — one prompt in, one response out, routed to the right provider. The `Orchestrator` is a **multi-step planner** — it takes a complex query, calls DeepSeek to decompose it into 1-3 atomic sub-tasks, then executes each sub-task via separate `MultiCall` invocations. Think of MultiCall as a function call and the Orchestrator as a workflow engine.

**Q: How would you scale this to 100,000 users?**
> (1) **Separate the workers** into their own service/container. (2) **Horizontal scaling** — run multiple API server instances behind a load balancer. (3) **Redis cluster** for caching instead of single-node. (4) **Database read replicas** for leaderboard queries. (5) **RabbitMQ clustering** with multiple consumers for parallel processing. (6) **CDN** for frontend static assets. (7) **Rate limiting** at the API gateway level.

---

### Database & Data Modeling

**Q: Why did you use GORM instead of raw SQL?**
> GORM provides auto-migration (schema stays in sync with struct definitions), type-safe queries (no string-based SQL), and built-in soft deletes. The tradeoff is less control over complex queries, but for Phase 1, all our queries are simple CRUD + ordering, which GORM handles perfectly.

**Q: Why is `Wings` stored as a JSON array instead of a separate table?**
> Wings are a fixed, small set (6 values). A join table would be overkill — it would add query complexity for no benefit. GORM's `serializer:json` stores it as a PostgreSQL JSONB column, which we can even query with `@>` operator for the wing leaderboard.

**Q: How does the wing leaderboard query work?**
> For PostgreSQL JSONB arrays, we use the containment operator: `WHERE wings @> '["Competitive Programming"]'`. GORM translates `database.DB.Where("wings @> ?", '[\"Competitive Programming\"]')` into this. It checks if the JSON array contains the specified element.

**Q: Explain soft deletes in your system.**
> `gorm.Model` includes a `DeletedAt` field. When you call `DB.Delete(&user)`, GORM doesn't run `DELETE FROM users` — it sets `DeletedAt = NOW()`. All subsequent queries automatically add `WHERE deleted_at IS NULL`. This means we never lose data and can always "undelete" records.

---

### AI & Machine Learning

**Q: Why multiple AI providers instead of just one?**
> (1) **Specialization**: DeepSeek-reasoner excels at multi-step logical reasoning (critical for CP hints), while Groq's Llama models are faster for straightforward tasks like code review. (2) **Availability**: If one provider goes down or runs out of credits (which happened with DeepSeek's 402 errors), the system automatically falls back. (3) **Cost**: We route fast, simple queries to cheaper/faster providers and reserve expensive reasoning models for complex tasks.

**Q: How does Shadow Memory make the AI personalized?**
> Before every AI call, we query the user's Shadow Memory for their weakest concepts in the relevant domain. This produces a string like "User struggles with: Dynamic Programming (3/10), Segment Trees (4/10)". This string is prepended to the system prompt, so the AI's response is specifically tailored to address those weaknesses. It's essentially **context injection** — the AI behaves differently for each user based on their persistent proficiency profile.

**Q: What prevents the AI from giving full solutions in CP?**
> Persona locking. The system prompt explicitly says: "You STRICTLY ONLY provide nudges. Do NOT write full solution code." Additionally, the orchestrator's system prompt enforces `action_type: "concept_nudge"` for CP and InfoSec tasks. The user never has direct access to the AI — every interaction is mediated through our persona-locked system prompts.

**Q: How do you handle AI response sanitization?**
> DeepSeek's reasoner model includes `<think>...</think>` blocks containing its chain-of-thought reasoning. We strip these using a regex `(?s)<think>.*?</think>\n*` before returning responses. We also handle JSON sanitization for the orchestrator — stripping markdown code fences and extracting JSON between the first `{` and last `}`.

---

### Security

**Q: How do you handle authentication?**
> JWT with HS256 signing. On login, we generate a token containing only the `user_id` claim with a 24-hour expiry. The token is sent in the `Authorization: Bearer <token>` header. Our middleware validates the signature and expiry, then sets the user ID in Gin's context for downstream handlers. Passwords are hashed with bcrypt using the default cost factor of 10.

**Q: What security improvements would you make for production?**
> (1) Restrict CORS to specific frontend domain. (2) Add rate limiting using Redis token buckets. (3) Implement refresh tokens for silent session extension. (4) Enable HTTPS with TLS certificates. (5) Move JWT secret to a secrets manager (Vault, AWS Secrets Manager). (6) Add RBAC instead of boolean `IsAdmin`. (7) Implement CSRF protection. (8) Add input sanitization for XSS prevention.

---

### Background Processing

**Q: Why RabbitMQ over a simple goroutine?**
> A goroutine would lose the task if the server crashes. RabbitMQ provides: (1) **Durability** — messages survive broker restart. (2) **Acknowledgment** — we manually ACK after successful processing, so failed tasks are automatically requeued. (3) **Decoupling** — we could move the worker to a separate process/container without changing the publisher. (4) **Observability** — the RabbitMQ management UI shows queue depth, consumer status, and message rates.

**Q: How do your cron jobs handle rate limits?**
> Two strategies: (1) **Sleep between users** — `time.Sleep(1 * time.Second)` for CF sync, `time.Sleep(500ms)` for rating sync. (2) **Batch size** — we fetch only the last 20 submissions per user, not the entire history. This keeps the number of API calls predictable: `N_users × 1 request` per cron run.

**Q: What happens if the cron job takes longer than 4 hours?**
> `robfig/cron` doesn't prevent overlapping executions by default. If the job takes longer than the interval, a new instance starts concurrently. To fix this, we could use `cron.New(cron.WithChain(cron.SkipIfStillRunning(logger)))` — a built-in middleware that skips a job if the previous run is still active.

---

### Frontend

**Q: Why React Context instead of Redux?**
> We only have one piece of global state — the authentication context. Redux would add significant boilerplate (actions, reducers, store configuration) for a single boolean and user object. Context API is built into React, has zero dependencies, and is perfectly suited for this use case. If we added more complex state (e.g., real-time notifications), we'd consider Zustand or Jotai.

**Q: How does the Wrapped feature work?**
> It's entirely client-side — no backend involved. The `useWrappedData` custom hook fetches all submissions from the Codeforces API directly, then computes 12+ analytics metrics in the browser: rating journey, problem difficulty distribution, top topics, night owl analysis, etc. The results are displayed as a Spotify Wrapped-style card carousel using Framer Motion animations and Three.js 3D backgrounds.

**Q: Why Three.js on the landing page?**
> It creates a premium first impression — animated 3D particle fields immediately signal that this isn't a basic CRUD app. We use React Three Fiber for declarative rendering and Drei for pre-built abstractions. The 3D scenes are lightweight (no heavy models) and render at 60fps. They're also wrapped in error boundaries so the app still works if WebGL isn't supported.

---

### General Software Engineering

**Q: How do you handle errors in external API calls?**
> Multiple layers: (1) **HTTP-level**: Check `resp.StatusCode` — handle 403 (rate limit), 404 (not found), etc. (2) **API-level**: Codeforces returns `{status: "FAILED", comment: "..."}` — we check this. (3) **Parse-level**: JSON decode errors are caught. (4) **Business-level**: Empty results are handled (e.g., "no user data found"). Errors propagate up via Go's explicit error returns, and controllers translate them into appropriate HTTP status codes.

**Q: What testing strategy would you implement?**
> (1) **Unit tests**: For `CalculateAxiosRating()`, `FormatContextString()`, JWT utilities. (2) **Integration tests**: For controllers using `httptest` — test actual HTTP requests against test handlers. (3) **Mock external APIs**: Create interfaces for `CFClient`, `GitHubClient`, etc., and use mock implementations in tests. (4) **E2E tests**: Cypress or Playwright for critical flows (register → login → sync → view upsolves).

**Q: Walk me through the codebase organization decisions.**
> We follow a **feature-based** organization where each layer has a clear responsibility: `controllers/` handle HTTP, `services/` contain business logic, `models/` define data structures, `workers/` run background tasks, and `utils/` hold shared utilities. This is a standard Go project layout, not over-engineered with interfaces or DI frameworks (which would be premature for Phase 1), but organized enough that any file's purpose is immediately clear from its package name.

---

## Quick Reference: Key Numbers to Remember

| Metric | Value |
|--------|-------|
| Total backend files | ~28 Go files |
| Total frontend components | ~30+ TSX files |
| API endpoints | 25+ |
| GORM models | 4 (User, ShadowMemory, UpsolveTask, Resource) |
| AI providers | 3 (DeepSeek, Groq, HuggingFace) |
| Cron jobs | 2 (4h upsolve, 24h rating) |
| Docker services | 2 (Redis, RabbitMQ) |
| Frontend pages | 9 |
| Wrapped cards | 13 |
| JWT expiry | 24 hours |
| Leaderboard cache TTL | 5 minutes |
| CF API fetch limit | Last 20 submissions |
| Mock contest problems | 4 per contest |
| Axios Rating formula components | 4 (CF rating, CF solved, GH repos, GH PRs) |

---

> **Final Interview Tip**: When discussing this project, always lead with the **why** before the **what**. Don't say "I used RabbitMQ" — say "I needed to decouple heavy Codeforces API calls from the request lifecycle to keep the API responsive, so I introduced RabbitMQ as an async task queue." This shows system design thinking, not just tool familiarity.

---

*Document generated from a complete source code analysis of every file in the AXIOS-GO repository.*
