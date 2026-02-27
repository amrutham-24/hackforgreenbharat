# Green Bharat - Real-Time ESG Risk Intelligence Platform

A Bloomberg-like ESG intelligence dashboard that detects environmental, social, and governance risks in near real-time, updates scores live, and explains score changes with evidence-backed conversational AI.

Built for **Hack for Green Bharat** hackathon.

---

## Architecture

```
green-bharath/
├── frontend/          # Next.js 16 (App Router) + TypeScript + TailwindCSS
├── backend/           # FastAPI + PostgreSQL + Redis + AI services
├── docker-compose.yml # Local dev: Postgres + Redis + API + Web
└── README.md          # This file
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Live ESG Scorecards** | Real-time overall + E/S/G scores with risk level indicators |
| **Risk Trend Charts** | 30-day interactive area charts with category breakdowns |
| **Event Timeline** | Filterable timeline with severity, category, and date range filters |
| **AI Chat Assistant** | RAG-powered Q&A with citation-backed answers (e.g., "Why did the score change?") |
| **Watchlists** | Per-user company watchlists for focused monitoring |
| **Alert Rules** | Configurable alert rules with Slack and email delivery |
| **Real-Time Updates** | WebSocket-based live score and event broadcasting |
| **Multi-Tenant** | Full tenant isolation with JWT-based authentication |

## Tech Stack

### Frontend (`/frontend`)
- **Framework**: Next.js 16 (App Router) + TypeScript
- **Styling**: TailwindCSS v4 + Radix UI primitives
- **State**: Zustand
- **Charts**: Recharts
- **Icons**: Lucide React
- **Real-Time**: Native WebSocket client

### Backend (`/backend`)
- **API**: FastAPI + Uvicorn + Pydantic v2
- **Database**: PostgreSQL (SQLAlchemy 2.0 + Alembic)
- **Cache/PubSub**: Redis
- **Vector Store**: Pinecone (with local mock fallback)
- **LLM**: OpenAI-compatible (with rule-based fallback)
- **Auth**: JWT with multi-tenant isolation

### Azure Services
- **Azure App Service** (Linux) - API + Web hosting
- **Azure Database for PostgreSQL** (Flexible Server)
- **Azure Cache for Redis**
- **Azure Resource Group** - `green-bharath-rg` in Central India

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/auth/login` | Authenticate and get JWT |
| `GET` | `/v1/auth/me` | Get current user profile |
| `GET` | `/v1/companies?query=` | List/search companies |
| `GET` | `/v1/companies/{id}` | Company details |
| `GET` | `/v1/companies/{id}/scores?range=30d` | Score time series |
| `GET` | `/v1/companies/{id}/events?range=30d&severity_gte=` | Event history with filters |
| `POST` | `/v1/watchlists` | Create watchlist |
| `POST` | `/v1/watchlists/{id}/items` | Add company to watchlist |
| `DELETE` | `/v1/watchlists/{id}/items/{company_id}` | Remove from watchlist |
| `POST` | `/v1/alerts/rules` | Create alert rule |
| `GET` | `/v1/alerts/rules` | List alert rules |
| `GET` | `/v1/alerts/deliveries` | Alert delivery history |
| `POST` | `/v1/chat` | AI chat with citations |
| `POST` | `/v1/ingest/events` | Ingest ESG event (secured) |
| `WS` | `/v1/ws/live` | Real-time score/event updates |

## Risk Scoring Engine

The scoring engine computes ESG scores based on:

- **Event severity** (1-10 scale)
- **Category weights** (Environmental: 35%, Social: 30%, Governance: 35%)
- **Confidence factor** from classification
- **Recency decay** (exponential, 14-day half-life)
- **Repetition factor** (more events in same category = higher impact)

Risk levels: `low` (>=80) | `medium` (>=60) | `high` (>=40) | `critical` (<40)

## RAG Chat System

1. Events are classified via LLM (or rule-based fallback)
2. Documents are embedded and stored in Pinecone (or local vector mock)
3. User queries retrieve top-K evidence docs filtered by tenant + company
4. LLM generates answers with inline citations `[1]`, `[2]`
5. "Explain last change" uses score delta + supporting evidence

## Quick Start (Local Development)

### Prerequisites
- **Node.js 22+** and **Python 3.12+**
- **Docker** (for PostgreSQL + Redis)

### 1. Start Database Services

```bash
docker compose up -d postgres redis
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your configuration

# Run migrations (creates all tables)
alembic upgrade head

# Seed demo data (20 companies, events, scores)
python -m scripts.seed

# Start API server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install

cp .env.example .env.local
# Edit .env.local if API is not on localhost:8000

npm run dev
```

### 4. Open Dashboard

Visit **http://localhost:3000** and log in with:

| Field | Value |
|-------|-------|
| Email | `demo@greenbharat.ai` |
| Password | `demo123` |

## Docker Compose (Full Stack)

```bash
docker compose up
```

This starts: PostgreSQL, Redis, Backend API (port 8000), Frontend (port 3000).

## Azure Deployment

The platform is deployed to Azure using:

```bash
# Login to Azure
az login

# Create resources (resource group, app service plan, web apps)
# See backend/scripts/deploy-azure.ps1 for full script

az group create --name green-bharath-rg --location centralindia
az appservice plan create --name green-bharath-plan --resource-group green-bharath-rg --sku B1 --is-linux
az webapp create --resource-group green-bharath-rg --plan green-bharath-plan --name greenbharat-api --runtime "PYTHON:3.12"
az webapp create --resource-group green-bharath-rg --plan green-bharath-plan --name greenbharat-web --runtime "NODE:22-lts"
```

**Live URLs:**
- API: `https://greenbharat-api.azurewebsites.net`
- Web: `https://greenbharat-web.azurewebsites.net`

## Project Structure

### Backend (`/backend`)
```
backend/
├── app/
│   ├── api/routers/       # REST + WebSocket endpoints
│   │   ├── auth.py        # JWT authentication
│   │   ├── companies.py   # Companies + scores + events
│   │   ├── watchlists.py  # Watchlist CRUD
│   │   ├── alerts.py      # Alert rules + deliveries
│   │   ├── chat.py        # RAG-powered AI chat
│   │   ├── ingest.py      # Event ingestion pipeline
│   │   └── websocket.py   # Real-time WebSocket
│   ├── core/              # Auth + config
│   ├── db/                # Models + sessions + Redis
│   ├── schemas/           # Pydantic v2 schemas
│   ├── services/          # Scoring, classifier, RAG, alerts
│   ├── workers/           # Pipeline + Kafka scaffolding
│   └── main.py            # FastAPI app
├── migrations/            # Alembic migrations
├── scripts/               # Seed + deploy scripts
├── tests/                 # Pytest test suite
├── requirements.txt
├── Dockerfile
└── .env.example
```

### Frontend (`/frontend`)
```
frontend/
├── app/                   # Next.js App Router pages
│   ├── dashboard/         # Main ESG dashboard
│   ├── company/[id]/      # Company detail view
│   ├── watchlist/[id]/    # Watchlist management
│   ├── alerts/            # Alert rules + history
│   ├── settings/          # Account settings
│   └── login/             # Authentication
├── components/
│   ├── dashboard/         # Scorecard, chart, timeline, sidebar
│   ├── chat/              # AI chat panel with citations
│   └── ui/                # Reusable UI components
├── stores/                # Zustand state management
├── lib/                   # API client, WebSocket, utilities
├── types/                 # TypeScript type definitions
├── package.json
├── Dockerfile
└── .env.example
```

## Demo Data

The seed script creates:
- **1 tenant** (Green Bharat Demo)
- **1 user** (demo@greenbharat.ai / demo123)
- **20 Indian companies** (Tata Steel, Reliance, Infosys, Adani Green, HDFC Bank, etc.)
- **8-20 ESG events per company** with realistic titles and descriptions
- **31 days of score history** per company
- **1 watchlist** with 5 companies
- **1 alert rule** (severity >= 7)

## Environment Variables

### Backend (`.env`)
| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL async connection string | Yes |
| `DATABASE_URL_SYNC` | PostgreSQL sync connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | Yes |
| `OPENAI_API_KEY` | OpenAI API key for LLM features | No (fallback to rule-based) |
| `PINECONE_API_KEY` | Pinecone vector store key | No (fallback to local mock) |
| `CORS_ORIGINS` | Allowed frontend origins | Yes |

### Frontend (`.env.local`)
| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend build check
cd frontend
npm run build
```

## License

Built for the Hack for Green Bharat hackathon.
