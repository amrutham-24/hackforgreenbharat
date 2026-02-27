# Green Bharat ESG Intelligence - Backend API

Real-Time ESG Risk Intelligence Platform backend built with FastAPI, PostgreSQL, Redis, and AI-powered risk analysis.

## Architecture

```
app/
├── api/routers/      # REST & WebSocket endpoints
│   ├── auth.py       # JWT authentication
│   ├── companies.py  # Company CRUD + scores + events
│   ├── watchlists.py # User watchlists
│   ├── alerts.py     # Alert rules & deliveries
│   ├── chat.py       # RAG-powered AI chat
│   ├── ingest.py     # Event ingestion pipeline
│   └── websocket.py  # Real-time WebSocket updates
├── core/
│   ├── auth.py       # JWT, password hashing, multi-tenant auth
│   └── config.py     # Pydantic settings from environment
├── db/
│   ├── models.py     # SQLAlchemy 2.0 models (9 tables)
│   ├── session.py    # Async engine & session
│   └── redis.py      # Redis client
├── schemas/          # Pydantic v2 request/response schemas
├── services/
│   ├── scoring.py    # ESG risk scoring engine
│   ├── classifier.py # LLM/rule-based ESG classifier
│   ├── rag.py        # RAG retrieval + answer generation
│   └── alerts.py     # Alert evaluation & delivery
├── workers/
│   ├── pipeline.py   # MVP sequential processing pipeline
│   └── kafka_scaffold.py  # Kafka topic definitions & consumer stubs
└── main.py           # FastAPI application entry
```

## Key Features

- **Multi-Tenant Isolation**: All queries enforce tenant_id from JWT
- **Risk Scoring Engine**: Recency decay, category weights, repetition factor
- **ESG Classification**: LLM-powered (OpenAI) with rule-based fallback
- **RAG Chat**: Vector retrieval (Pinecone/local) + citation-backed answers
- **Real-Time Updates**: Redis PubSub → WebSocket broadcast
- **Alert System**: Configurable rules with Slack + email delivery

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/auth/login` | Authenticate and get JWT |
| GET | `/v1/auth/me` | Get current user |
| GET | `/v1/companies` | List companies (with search) |
| GET | `/v1/companies/{id}` | Get company details |
| GET | `/v1/companies/{id}/scores` | Score time series |
| GET | `/v1/companies/{id}/events` | Event history |
| POST | `/v1/watchlists` | Create watchlist |
| POST | `/v1/watchlists/{id}/items` | Add company to watchlist |
| DELETE | `/v1/watchlists/{id}/items/{cid}` | Remove from watchlist |
| POST | `/v1/alerts/rules` | Create alert rule |
| GET | `/v1/alerts/rules` | List alert rules |
| GET | `/v1/alerts/deliveries` | List alert deliveries |
| POST | `/v1/chat` | AI chat with citations |
| POST | `/v1/ingest/events` | Ingest ESG event |
| WS | `/v1/ws/live` | Real-time score updates |

## Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Redis 7+

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy env and configure
cp .env.example .env
# Edit .env with your database URL, Redis URL, API keys

# Run migrations
alembic upgrade head

# Seed demo data
python -m scripts.seed

# Start API server
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
# From project root (parent directory)
docker compose up -d postgres redis
docker compose up api
```

### Running Tests

```bash
pytest tests/ -v
```

## Environment Variables

See `.env.example` for all configuration options. Key variables:

- `DATABASE_URL` - PostgreSQL connection string (async)
- `REDIS_URL` - Redis connection string
- `JWT_SECRET_KEY` - Secret for JWT signing (change in production!)
- `OPENAI_API_KEY` - OpenAI API key for LLM classification & chat
- `PINECONE_API_KEY` - Pinecone for vector storage (optional, local mock available)
- `CORS_ORIGINS` - Allowed frontend origins

## Demo Credentials

- Email: `demo@greenbharat.ai`
- Password: `demo123`
