# Green Bharat -- Real-Time ESG Risk Intelligence Platform

> A Bloomberg-grade ESG intelligence dashboard purpose-built for the Indian market that detects environmental, social, and governance risks in near real-time, updates composite scores live, and explains every score movement with evidence-backed conversational AI.

**Hack for Green Bharat** | Team Entry

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Our Solution](#our-solution)
3. [What Makes This Unique](#what-makes-this-unique)
4. [How It Works -- End to End](#how-it-works--end-to-end)
5. [Impact and Benefits](#impact-and-benefits)
6. [Key Features](#key-features)
7. [Architecture Overview](#architecture-overview)
8. [Tech Stack](#tech-stack)
9. [Risk Scoring Engine -- Deep Dive](#risk-scoring-engine--deep-dive)
10. [RAG Chat System -- Deep Dive](#rag-chat-system--deep-dive)
11. [Alert and Notification System](#alert-and-notification-system)
12. [Multi-Tenant Security Model](#multi-tenant-security-model)
13. [API Reference](#api-reference)
14. [Real-Time WebSocket Protocol](#real-time-websocket-protocol)
15. [Streaming Pipeline](#streaming-pipeline)
16. [Project Structure](#project-structure)
17. [Quick Start -- Local Development](#quick-start--local-development)
18. [Docker Compose -- Full Stack](#docker-compose--full-stack)
19. [Azure Cloud Deployment](#azure-cloud-deployment)
20. [Demo Data and Seed Script](#demo-data-and-seed-script)
21. [Environment Variables Reference](#environment-variables-reference)
22. [Testing](#testing)
23. [Future Roadmap](#future-roadmap)

---

## Problem Statement

India is home to some of the world's fastest-growing economies, but ESG (Environmental, Social, and Governance) risk visibility remains poor:

- **Fragmented data**: ESG-relevant events are scattered across news feeds, regulatory filings, NGO reports, and social media. No single pane of glass exists for Indian companies.
- **Delayed scoring**: Traditional ESG rating agencies update scores quarterly or annually. A factory pollution incident today may not appear in an ESG rating for months.
- **No explainability**: When a company's ESG score drops, investors and compliance teams cannot understand *why* without manually reading hundreds of source documents.
- **No real-time alerting**: Portfolio managers and sustainability officers learn about critical ESG events after the market has already reacted.
- **No Indian-market focus**: Most ESG tools are built for US/EU markets. Indian companies (Nifty 50, BSE 500) lack dedicated, sector-aware ESG monitoring.

**Result**: Billions of rupees in climate-linked investment risk go unmonitored, greenwashing goes undetected, and sustainable investment in India stalls.

---

## Our Solution

**Green Bharat** is a full-stack, production-grade ESG Risk Intelligence Platform that:

1. **Ingests ESG events in real time** -- news articles, regulatory filings, incident reports, and NGO data are ingested through a streaming pipeline.
2. **Classifies every event automatically** -- an LLM-powered classifier (with intelligent rule-based fallback) categorizes events into Environmental / Social / Governance, assigns severity (1-10), confidence, and sentiment.
3. **Computes composite ESG scores live** -- a custom scoring engine recalculates company scores within seconds of an event, using recency decay, category weighting, and repetition factors.
4. **Pushes updates to every connected user** -- WebSocket-based broadcasting ensures the dashboard reflects new scores and events within seconds, not hours.
5. **Explains every change with AI** -- a RAG (Retrieval-Augmented Generation) chat assistant retrieves the specific evidence documents that caused a score change and generates human-readable answers with inline citations.
6. **Alerts the right people** -- configurable alert rules detect threshold breaches (e.g., "score dropped by 10 points" or "severity >= 8 event") and notify via Slack webhook and email.

---

## What Makes This Unique

| Differentiator | How Green Bharat Does It |
|----------------|--------------------------|
| **Real-time, not quarterly** | Events are classified and scored in seconds via an async pipeline. WebSocket pushes live updates to every connected client. Traditional ESG providers update quarterly. |
| **Explainable AI** | The RAG chat system retrieves *actual source documents* that caused a score change and generates answers with numbered citations `[1]`, `[2]` -- not hallucinated opinions. Users can verify every claim. |
| **India-first** | Seed data includes 20 major Indian companies (Tata Steel, Reliance, Infosys, Adani Green, HDFC Bank, etc.) with Indian-specific event templates (SEBI scrutiny, ₹ crore community programs, Mumbai/Chennai/Delhi facility events). |
| **Multi-tenant from day one** | Every database table carries a `tenant_id`. Every API query is scoped to the authenticated tenant. This is not a single-user prototype -- it is designed for multi-organization SaaS deployment. |
| **Graceful degradation** | No OpenAI key? The classifier falls back to keyword-based rules. No Pinecone? A local in-memory vector store handles RAG retrieval. No Redis? A mock pubsub keeps the app running. The platform works out of the box with zero external API keys. |
| **Kafka-ready streaming** | While the MVP uses a simple sequential pipeline, the codebase includes full Kafka topic definitions (`raw_events` -> `normalized` -> `classified` -> `scored_updates`) and consumer stubs, ready for horizontal scaling. |
| **Production security** | JWT tokens, bcrypt password hashing, CORS enforcement, internal API key protection for the ingestion endpoint, and no hardcoded secrets anywhere. |

---

## How It Works -- End to End

```
                                                     +------------------+
                                                     |   Frontend       |
                                                     |   (Next.js 16)  |
   +-------------+     +---------------+             |                  |
   | News Feed / |     | POST          |   WebSocket | - Dashboard      |
   | Data Source |---->| /v1/ingest/   |------------>| - Score Cards    |
   +-------------+     | events        |   (live)    | - Risk Charts    |
                        +-------+-------+             | - Event Timeline |
                                |                     | - AI Chat Panel  |
                                v                     +--------+---------+
                     +----------+----------+                   |
                     | Event Pipeline      |                   | POST /v1/chat
                     |                     |                   v
                     | 1. Classify (LLM)   |          +--------+---------+
                     | 2. Store RAG Doc    |          | RAG System       |
                     | 3. Create Embedding |          |                  |
                     | 4. Recalc Score     |          | 1. Embed query   |
                     | 5. Evaluate Alerts  |          | 2. Vector search |
                     | 6. Publish to Redis |          | 3. Retrieve docs |
                     +----------+----------+          | 4. LLM answer   |
                                |                     | 5. Return w/     |
                                v                     |    citations     |
                     +----------+----------+          +------------------+
                     | Redis PubSub        |
                     | Channel: esg:live   |
                     +----------+----------+
                                |
                                v
                     +----------+----------+
                     | WebSocket Server    |
                     | /v1/ws/live         |
                     | Broadcasts per-     |
                     | tenant updates      |
                     +---------------------+
```

### Step-by-step flow:

1. **Ingestion**: An external data source (or the seed script) sends a raw ESG event to `POST /v1/ingest/events` with a title, description, company ID, and optional source URL.

2. **Classification**: The pipeline sends the event text to the LLM classifier (OpenAI GPT-4o-mini). The classifier returns structured JSON: `{ category, subcategory, severity, confidence, sentiment }`. If no API key is configured, a keyword-based rule engine handles classification.

3. **RAG Document Storage**: The event text is stored as a RAG document in PostgreSQL. An embedding is created (via OpenAI `text-embedding-3-small` or a local hash-based mock) and upserted to the vector store (Pinecone or local in-memory).

4. **Score Recalculation**: The scoring engine pulls all processed events for the company from the last 90 days. For each event, it computes impact = `severity * confidence * recency_decay * repetition_factor`. Category scores (E, S, G) are derived by subtracting aggregated impact from a base of 75. The overall score is a weighted average (E: 35%, S: 30%, G: 35%).

5. **Alert Evaluation**: All active alert rules for the tenant are checked against the new event and score. If a rule triggers (e.g., severity >= threshold, or score dropped by >= threshold), a delivery is created and sent via Slack webhook / email.

6. **Live Broadcast**: The new score and event summary are published to the `esg:live` Redis channel. The WebSocket server picks up the message and broadcasts it to all connected clients for that tenant.

7. **Dashboard Update**: The frontend WebSocket client receives the update and immediately updates the Zustand store. The score card animates to the new value. The event appears at the top of the timeline. The live feed shows the update in real time.

8. **AI Chat**: At any time, the user can ask the chat assistant "Why did the score change?" or "What environmental risks does this company have?". The system embeds the question, searches the vector store for the most relevant evidence documents (filtered by tenant + company), and generates a contextual answer with inline citations.

---

## Impact and Benefits

### For Investors and Portfolio Managers
- **Proactive risk detection**: Get notified within seconds of a material ESG event, not months later from a rating agency update.
- **Evidence-based decisions**: Every score change is traceable to specific events. The AI chat provides the *why* behind every number.
- **Portfolio-wide monitoring**: Watchlists let investors track their entire holdings. Alert rules ensure nothing slips through.

### For Corporate Sustainability Officers
- **Real-time compliance view**: See your company's ESG posture as the market sees it. Identify emerging risks before they become crises.
- **Benchmarking**: Compare your E, S, G scores against peers in your sector.
- **Audit trail**: Every event, classification, and score change is timestamped and stored.

### For Regulators and Policymakers
- **Market-wide ESG visibility**: Monitor ESG trends across sectors and geographies in real time.
- **Greenwashing detection**: Sudden score improvements without corresponding events can flag suspicious claims.
- **Data-driven policy**: 30-day trend data and event distributions inform evidence-based environmental policy.

### For India's Green Economy Goals
- **Channeling capital to sustainable companies**: Clear, real-time ESG visibility helps investors direct funds to genuinely sustainable businesses.
- **Accountability for polluters**: Immediate scoring impact from environmental incidents creates a financial incentive for compliance.
- **Supporting India's NDC commitments**: Better ESG data supports India's Nationally Determined Contributions under the Paris Agreement.

---

## Key Features

### 1. Bloomberg-like Dashboard Layout
Three-panel design: collapsible left sidebar for navigation and company list, central main panel for scores/charts/events, and right panel for AI chat. Responsive and information-dense.

### 2. Live ESG Score Cards
Animated SVG ring charts showing Overall, Environmental, Social, and Governance scores. Color-coded risk levels (green/amber/orange/red). Updates in real time via WebSocket.

### 3. Risk Trend Charts
30-day area chart (built with Recharts) plotting Overall, E, S, G scores over time. Interactive tooltips. Gradient fills. Dashed lines for sub-categories.

### 4. Filterable Event Timeline
Scrollable timeline of all ESG events. Filter by category (ENV/SOC/GOV), toggle high-severity only. Each event shows title, description snippet, severity badge, sentiment, date, and category icon.

### 5. RAG-Powered AI Chat
Chat panel with:
- Quick-question buttons ("Why did the score change?", "What environmental risks?")
- Typing indicator animation
- Citation badges linking to source documents
- Company-aware context (automatically uses the selected company)

### 6. Watchlists
Create named watchlists. Add/remove companies. View scores at a glance. Click through to company detail pages.

### 7. Alert Rules Engine
- **Condition types**: `severity_gte` (event severity above threshold), `score_drop` (score decreased by at least N points), `category_match` (specific category)
- **Delivery channels**: Slack webhook, email (mock for demo)
- **History**: Full delivery log with timestamps and payloads

### 8. Company Detail Pages
Deep-dive into any company: description, sector, country, ticker, full ESG scorecard, 60-day risk chart, and complete event history.

### 9. Settings and Account
View profile, tenant info, organization details. Sign out.

---

## Architecture Overview

```
+------------------------------------------------------+
|                     FRONTEND                          |
|  Next.js 16 | TypeScript | TailwindCSS | Zustand     |
|  Recharts | Radix UI | Lucide Icons                  |
|  WebSocket Client | Typed API Client                  |
+---+-------------------------------+------------------+
    |  REST API (HTTPS)             |  WebSocket (WSS)
    v                               v
+---+-------------------------------+------------------+
|                      BACKEND                          |
|  FastAPI | Uvicorn | Pydantic v2                      |
|                                                       |
|  +------------+  +------------+  +----------------+   |
|  | Routers    |  | Services   |  | Workers        |   |
|  | - auth     |  | - scoring  |  | - pipeline     |   |
|  | - companies|  | - classify |  | - kafka stubs  |   |
|  | - watchlist|  | - rag      |  +----------------+   |
|  | - alerts   |  | - alerts   |                       |
|  | - chat     |  +------------+                       |
|  | - ingest   |                                       |
|  | - websocket|                                       |
|  +------------+                                       |
+---+------------------+---------------+----------------+
    |                  |               |
    v                  v               v
+---+------+   +------+------+  +-----+--------+
| PostgreSQL|   |    Redis    |  |   Pinecone   |
| (SQLAlch  |   | (PubSub +  |  | (Vector DB)  |
|  2.0 +    |   |  Cache)    |  | or Local     |
|  Alembic) |   +-------------+  | Mock         |
+-----------+                    +--------------+
```

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16.1.6 | React framework with App Router |
| React | 19.2.3 | UI library |
| TypeScript | 5.x | Type safety |
| TailwindCSS | 4.x | Utility-first styling |
| Zustand | 5.x | Lightweight state management |
| Recharts | 3.7 | Data visualization (charts) |
| Radix UI | Latest | Accessible UI primitives (scroll area, slot, dialog) |
| Lucide React | Latest | SVG icon library |
| date-fns | 4.x | Date formatting and manipulation |
| class-variance-authority | 0.7 | Component variant management |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12 | Runtime |
| FastAPI | 0.115 | Async web framework |
| Uvicorn | 0.34 | ASGI server |
| Pydantic | 2.11 | Data validation and serialization |
| SQLAlchemy | 2.0 | Async ORM |
| Alembic | 1.15 | Database migrations |
| Redis | 5.x client | PubSub, caching |
| Pinecone | 6.x client | Vector similarity search |
| OpenAI | 1.82 | LLM classification + RAG generation |
| python-jose | 3.4 | JWT token handling |
| passlib | 1.7 | bcrypt password hashing |
| httpx | 0.28 | Async HTTP client (Slack webhooks) |
| Gunicorn | 23.x | Production WSGI/ASGI server |

### Azure Cloud Services
| Service | Purpose |
|---------|---------|
| Azure App Service (Linux, B1) | Hosts both API and Web applications |
| Azure Database for PostgreSQL (Flexible Server) | Managed relational database |
| Azure Cache for Redis | Managed caching and PubSub |
| Azure Resource Group (`green-bharath-rg`) | Resource organization, Central India region |

---

## Risk Scoring Engine -- Deep Dive

The scoring engine is the mathematical core of the platform, implemented in `backend/app/services/scoring.py`.

### Algorithm

For each company, the engine:

1. **Retrieves all processed events** from the last 90 days.

2. **Computes per-event impact**:
   ```
   impact = severity * confidence * recency_decay * repetition_factor
   ```

3. **Recency decay** uses an exponential decay with a 14-day half-life:
   ```
   decay = e^(-0.693 * days_since_event / 14)
   ```
   An event from today has decay = 1.0. An event from 14 days ago has decay ~ 0.5. An event from 28 days ago has decay ~ 0.25.

4. **Repetition factor** increases impact when multiple events hit the same category:
   ```
   rep_factor = 1.0 + 0.1 * (category_count - 1)
   ```
   A company with 5 environmental incidents gets a 1.4x multiplier on each, reflecting systemic risk.

5. **Category scores** start from a base of 75 and subtract capped aggregate impact:
   ```
   E_score = max(0, 75 - min(total_environmental_impact, 50))
   S_score = max(0, 75 - min(total_social_impact, 50))
   G_score = max(0, 75 - min(total_governance_impact, 50))
   ```

6. **Overall score** is a weighted average:
   ```
   overall = E * 0.35 + S * 0.30 + G * 0.35
   ```

7. **Risk level** is derived from the overall score:
   | Score Range | Risk Level |
   |-------------|------------|
   | >= 80 | Low |
   | >= 60 | Medium |
   | >= 40 | High |
   | < 40 | Critical |

### Why This Approach?

- **Recency decay** ensures old incidents fade naturally, mimicking how markets discount past events.
- **Repetition factor** captures systemic risk -- a company with repeated environmental violations is riskier than one with a single incident.
- **Category weighting** reflects that governance failures (fraud, corruption) and environmental failures (pollution, emissions) tend to have more material financial impact than isolated social incidents.
- **Capped impact** prevents a single extreme event from dominating the entire score.

---

## RAG Chat System -- Deep Dive

The RAG (Retrieval-Augmented Generation) system, implemented in `backend/app/services/rag.py`, ensures the AI assistant never hallucinates -- every claim is backed by retrievable evidence.

### Pipeline

1. **Document Ingestion**: When an ESG event is processed, its text is stored as a `rag_document` in PostgreSQL and also embedded into a vector (1536-dim via OpenAI `text-embedding-3-small`, or a deterministic hash-based mock).

2. **Vector Upsert**: The embedding is upserted to Pinecone (or the local in-memory vector store) with metadata: `tenant_id`, `company_id`, `title`, `source_url`, `ts`, `text`.

3. **Query Processing**: When a user sends a chat message:
   - The message is embedded using the same model.
   - The vector store is queried for the top 5 most similar documents, filtered by `tenant_id` and `company_id`.
   - The latest 2 ESG scores are fetched to compute the score delta.

4. **Answer Generation**: The retrieved documents and score context are assembled into a prompt:
   ```
   Evidence:
   [1] Carbon emission targets missed: The company failed to meet...
   [2] Water pollution incident at Mumbai plant: Regulatory authorities...

   Latest score: 62.5 (delta: -4.30). Risk level: medium.
   ```
   The LLM generates a concise answer citing `[1]`, `[2]`, etc.

5. **Response Format**:
   ```json
   {
     "answer": "The score dropped by 4.3 points primarily due to...",
     "citations": [
       {"idx": 1, "title": "Carbon emission targets missed", "url": "https://...", "ts": "2026-02-15T..."},
       {"idx": 2, "title": "Water pollution incident", "url": "https://...", "ts": "2026-02-20T..."}
     ],
     "used_company_id": "abc-123"
   }
   ```

### Graceful Degradation

- **No OpenAI key**: The system generates a structured summary from the retrieved documents and score delta without LLM generation.
- **No Pinecone key**: A local in-memory vector store with cosine similarity search handles retrieval.
- **No documents found**: The system clearly states that no evidence was found for the query.

---

## Alert and Notification System

Implemented in `backend/app/services/alerts.py`.

### Rule Types

| Condition | Triggers When |
|-----------|---------------|
| `severity_gte` | An event has severity >= threshold (e.g., >= 7) |
| `score_drop` | The company's overall score dropped by >= threshold points |
| `category_match` | An event matches a specific category (e.g., "environmental") |

### Delivery Channels

- **Slack**: Sends a message to a configured webhook URL with the alert details.
- **Email**: Mock implementation logs the alert (production-ready SMTP integration scaffolded).

### Alert Lifecycle

1. User creates a rule via `POST /v1/alerts/rules`.
2. Every time an event is processed, the pipeline calls `evaluate_alerts_for_event`.
3. All active rules for the tenant are checked against the new event and score.
4. For each triggered rule, a delivery record is created in `alert_deliveries` and the notification is sent.
5. Users can view delivery history via `GET /v1/alerts/deliveries`.

---

## Multi-Tenant Security Model

Every table in the database that contains user-facing data includes a `tenant_id` column. The security model works as follows:

1. **Authentication**: Users log in via `POST /v1/auth/login` with email + password. The backend verifies the bcrypt-hashed password and returns a JWT containing `sub` (user ID), `tenant_id`, `email`, and `role`.

2. **Authorization**: Every protected endpoint calls `get_current_user`, which decodes the JWT and extracts the `TokenPayload`. The `tenant_id` is then used in every database query as a mandatory filter.

3. **Data isolation**: Even if a user discovers another tenant's company ID, querying that company will return 404 because the `tenant_id` filter will not match.

4. **WebSocket isolation**: The WebSocket server tracks connections per tenant. Live updates are only broadcast to clients belonging to the same tenant as the event's `tenant_id`.

5. **Internal API protection**: The ingestion endpoint can be further secured with an internal API key for machine-to-machine communication.

---

## API Reference

### Authentication

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| `POST` | `/v1/auth/login` | `{ email, password }` | `{ access_token, user_id, tenant_id, email, full_name }` |
| `GET` | `/v1/auth/me` | -- (Bearer token) | `{ id, email, full_name, role }` |

### Companies

| Method | Endpoint | Query Params | Response |
|--------|----------|--------------|----------|
| `GET` | `/v1/companies` | `?query=tata` (optional search) | `Company[]` |
| `GET` | `/v1/companies/{id}` | -- | `Company` |
| `GET` | `/v1/companies/{id}/scores` | `?range=30d` | `ESGScore[]` (time series) |
| `GET` | `/v1/companies/{id}/events` | `?range=30d&severity_gte=5` | `ESGEvent[]` |

### Watchlists

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| `GET` | `/v1/watchlists` | -- | `Watchlist[]` |
| `POST` | `/v1/watchlists` | `{ name }` | `Watchlist` |
| `GET` | `/v1/watchlists/{id}` | -- | `Watchlist` (with items) |
| `POST` | `/v1/watchlists/{id}/items` | `{ company_id }` | `{ status, id }` |
| `DELETE` | `/v1/watchlists/{id}/items/{company_id}` | -- | `{ status }` |

### Alerts

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| `POST` | `/v1/alerts/rules` | `{ name, condition_type, threshold, channels }` | `AlertRule` |
| `GET` | `/v1/alerts/rules` | -- | `AlertRule[]` |
| `GET` | `/v1/alerts/deliveries` | -- | `AlertDelivery[]` |

### Chat

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| `POST` | `/v1/chat` | `{ message, company_id? }` | `{ answer, citations[], used_company_id }` |

### Ingestion

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| `POST` | `/v1/ingest/events` | `{ company_id, title, description, source_url?, category? }` | `{ status, event_id, score }` |

### Health

| Method | Endpoint | Response |
|--------|----------|----------|
| `GET` | `/health` | `{ status: "ok", service: "esg-api" }` |

---

## Real-Time WebSocket Protocol

**Endpoint**: `WS /v1/ws/live?token=<JWT>`

### Connection

```javascript
const ws = new WebSocket("wss://api.example.com/v1/ws/live?token=eyJ...");
```

### Messages from Server

```json
{
  "type": "score_update",
  "company_id": "abc-123",
  "tenant_id": "tenant-456",
  "score": {
    "overall": 62.5,
    "environmental": 58.3,
    "social": 70.1,
    "governance": 60.2,
    "risk_level": "medium"
  },
  "event": {
    "id": "evt-789",
    "title": "Carbon emission targets missed by 20%",
    "category": "environmental",
    "severity": 8,
    "sentiment": "negative"
  }
}
```

### Keep-alive

Send `"ping"` as text. Server responds with `{ "type": "pong" }`.

---

## Streaming Pipeline

### MVP Mode (Fully Implemented)

Sequential processing within the API request:

```
Ingest -> Classify -> Store RAG Doc -> Embed -> Score -> Alert -> Publish
```

All steps run asynchronously within a single request. Simple, reliable, and sufficient for moderate throughput.

### Kafka Mode (Scaffolded)

For high-throughput production:

```
raw_events (topic) -> RawEventsConsumer -> normalized (topic) -> NormalizedConsumer -> classified (topic) -> ClassifiedConsumer -> scored_updates (topic) -> ScoredUpdatesConsumer -> Redis PubSub
```

Topic definitions, partition counts, and consumer stubs are in `backend/app/workers/kafka_scaffold.py`.

---

## Project Structure

```
green-bharath/
├── README.md                      # This documentation
├── docker-compose.yml             # Full-stack local development
├── .gitignore                     # Root gitignore
│
├── backend/                       # FastAPI Backend
│   ├── app/
│   │   ├── api/routers/           # HTTP + WebSocket endpoints
│   │   │   ├── auth.py            # Login, get current user
│   │   │   ├── companies.py       # List, detail, scores, events
│   │   │   ├── watchlists.py      # CRUD watchlists and items
│   │   │   ├── alerts.py          # Rules and delivery history
│   │   │   ├── chat.py            # RAG-powered AI chat
│   │   │   ├── ingest.py          # Event ingestion + pipeline trigger
│   │   │   └── websocket.py       # Live update broadcasting
│   │   ├── core/
│   │   │   ├── auth.py            # JWT encode/decode, password hashing
│   │   │   └── config.py          # Pydantic settings from environment
│   │   ├── db/
│   │   │   ├── models.py          # 9 SQLAlchemy models
│   │   │   ├── session.py         # Async engine and session factory
│   │   │   └── redis.py           # Redis client with mock fallback
│   │   ├── schemas/
│   │   │   └── common.py          # Pydantic v2 request/response schemas
│   │   ├── services/
│   │   │   ├── scoring.py         # Risk scoring algorithm
│   │   │   ├── classifier.py      # LLM + rule-based ESG classifier
│   │   │   ├── rag.py             # Embedding, vector search, answer gen
│   │   │   └── alerts.py          # Rule evaluation and notification
│   │   ├── workers/
│   │   │   ├── pipeline.py        # MVP sequential processing
│   │   │   └── kafka_scaffold.py  # Kafka topic defs + consumer stubs
│   │   └── main.py                # FastAPI application entry point
│   ├── migrations/                # Alembic database migrations
│   ├── scripts/
│   │   ├── seed.py                # Demo data generator
│   │   └── deploy-azure.ps1       # Azure provisioning script
│   ├── tests/
│   │   ├── test_scoring.py        # Scoring engine unit tests
│   │   └── test_classifier.py     # Classifier validation tests
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Container image
│   ├── .env.example               # Environment variable template
│   └── README.md                  # Backend-specific docs
│
├── frontend/                      # Next.js Frontend
│   ├── app/                       # App Router pages
│   │   ├── login/page.tsx         # Authentication page
│   │   ├── dashboard/             # Main ESG dashboard
│   │   ├── company/[id]/          # Company detail view
│   │   ├── watchlist/[id]/        # Watchlist management
│   │   ├── alerts/                # Alert rules and history
│   │   ├── settings/              # Account settings
│   │   ├── layout.tsx             # Root layout (fonts, metadata)
│   │   ├── page.tsx               # Root redirect (auth check)
│   │   └── globals.css            # Global styles
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── esg-scorecard.tsx   # SVG ring charts for E/S/G/Overall
│   │   │   ├── risk-chart.tsx      # 30-day area chart (Recharts)
│   │   │   ├── event-timeline.tsx  # Filterable event list
│   │   │   ├── company-list.tsx    # Searchable company grid
│   │   │   ├── live-feed.tsx       # Real-time update feed
│   │   │   └── sidebar.tsx         # Navigation + company quick-links
│   │   ├── chat/
│   │   │   └── chat-panel.tsx      # AI assistant with citations
│   │   └── ui/                    # Reusable primitives (Button, Card, etc.)
│   ├── stores/
│   │   ├── auth.ts                # Authentication state (Zustand)
│   │   └── dashboard.ts           # Dashboard data state (Zustand)
│   ├── lib/
│   │   ├── api.ts                 # Typed fetch wrapper for all endpoints
│   │   ├── websocket.ts           # WebSocket client with auto-reconnect
│   │   └── utils.ts               # cn() utility for Tailwind class merging
│   ├── types/
│   │   └── api.ts                 # TypeScript interfaces matching backend
│   ├── package.json
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md
```

---

## Quick Start -- Local Development

### Prerequisites

- **Node.js 22+**
- **Python 3.12+**
- **Docker** (for PostgreSQL + Redis) -- *optional, SQLite fallback available*

### 1. Clone the Repository

```bash
git clone https://github.com/amrutham-24/hackforgreenbharat.git
cd hackforgreenbharat
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env -- at minimum set JWT_SECRET_KEY to a random string
```

### 3. Database Setup

**Option A: Docker (PostgreSQL + Redis)**:
```bash
# From the project root
docker compose up -d postgres redis
# Then in backend/.env set:
# DATABASE_URL=postgresql+asyncpg://esg_user:esg_pass@localhost:5432/esg_db
# DATABASE_URL_SYNC=postgresql://esg_user:esg_pass@localhost:5432/esg_db
# REDIS_URL=redis://localhost:6379/0
```

**Option B: SQLite (no Docker needed)**:
```bash
# In backend/.env set:
# DATABASE_URL=sqlite+aiosqlite:///./esg.db
# DATABASE_URL_SYNC=sqlite:///./esg.db
# REDIS_URL=   (leave empty for mock)
```

### 4. Seed Demo Data

```bash
cd backend
python -m scripts.seed
# Output: Seeded: 1 tenant, 1 user, 20 companies, events, scores, watchlist, alert rule
# Login: demo@greenbharat.ai / demo123
```

### 5. Start Backend

```bash
uvicorn app.main:app --reload --port 8000
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 6. Frontend Setup

```bash
cd frontend
npm install

cp .env.example .env.local
# Ensure NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
# Dashboard at http://localhost:3000
```

### 7. Login

Open **http://localhost:3000** and sign in with:

| Field | Value |
|-------|-------|
| Email | `demo@greenbharat.ai` |
| Password | `demo123` |

---

## Docker Compose -- Full Stack

```bash
docker compose up
```

This starts four services:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Backend API** on port 8000
- **Frontend Web** on port 3000

---

## Azure Cloud Deployment

The platform deploys to Azure using the Azure CLI (`az`). Resources created in the `centralindia` region:

```bash
az login
az group create --name green-bharath-rg --location centralindia

az appservice plan create \
  --name green-bharath-plan \
  --resource-group green-bharath-rg \
  --sku B1 --is-linux

az webapp create \
  --resource-group green-bharath-rg \
  --plan green-bharath-plan \
  --name greenbharat-api \
  --runtime "PYTHON:3.12"

az webapp create \
  --resource-group green-bharath-rg \
  --plan green-bharath-plan \
  --name greenbharat-web \
  --runtime "NODE:22-lts"
```

**Deployed URLs**:
- API: `https://greenbharat-api.azurewebsites.net`
- Web: `https://greenbharat-web.azurewebsites.net`

See `backend/scripts/deploy-azure.ps1` for the full provisioning script including PostgreSQL Flexible Server and Redis Cache.

---

## Demo Data and Seed Script

The seed script (`backend/scripts/seed.py`) creates a complete demo environment:

| Entity | Count | Details |
|--------|-------|---------|
| Tenant | 1 | "Green Bharat Demo" |
| User | 1 | demo@greenbharat.ai / demo123 (admin role) |
| Companies | 20 | Tata Steel, Reliance, Infosys, Adani Green, HDFC Bank, ITC, M&M, Wipro, Bharti Airtel, L&T, JSW Steel, NTPC, Sun Pharma, Coal India, HUL, Asian Paints, Bajaj Finance, Power Grid, UltraTech Cement, Vedanta |
| Events per company | 8-20 | Realistic titles and multi-paragraph descriptions |
| Score history | 31 days per company | Daily score snapshots with natural variation |
| Watchlist | 1 | "My ESG Watchlist" with 5 companies |
| Alert rule | 1 | "High Severity Alert" (severity >= 7) |
| RAG documents | 1 per event | Full text + embeddings in vector store |

Event templates cover all three ESG categories with Indian-specific scenarios:
- **Environmental**: Carbon emission misses, renewable energy commissioning, water pollution, deforestation, zero-waste certification, plastic reduction
- **Social**: Worker safety incidents, gender diversity progress, labor disputes, community programs, data breaches, wellness programs
- **Governance**: Board independence concerns, executive compensation controversy, anti-corruption policies, related-party transactions, ESG committee formation, audit qualifications

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://esg_user:esg_pass@localhost:5432/esg_db` | Yes |
| `DATABASE_URL_SYNC` | PostgreSQL sync connection (for Alembic) | `postgresql://esg_user:esg_pass@localhost:5432/esg_db` | Yes |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | No (mock fallback) |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | `change-me` | Yes (change in prod!) |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` | No |
| `JWT_EXPIRY_MINUTES` | Token expiry time | `1440` (24h) | No |
| `OPENAI_API_KEY` | OpenAI API key for classification + chat | -- | No (rule-based fallback) |
| `OPENAI_MODEL` | LLM model for classification/chat | `gpt-4o-mini` | No |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` | No |
| `PINECONE_API_KEY` | Pinecone vector database key | -- | No (local mock fallback) |
| `PINECONE_INDEX` | Pinecone index name | `esg-rag` | No |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000` | Yes |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook for alerts | -- | No (mock delivery) |
| `INTERNAL_API_KEY` | Key for securing internal endpoints | `change-me-internal-key` | Yes |
| `APP_ENV` | Environment identifier | `development` | No |

### Frontend (`frontend/.env.local`)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` | Yes |

---

## Testing

### Backend Unit Tests

```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v
```

Tests cover:
- **Scoring engine**: Recency decay at 0/14/28 days, impact computation, risk level classification
- **Classifier**: Environmental/social/governance keyword detection, high-severity keyword detection, positive sentiment detection, JSON schema validation

### Frontend Build Verification

```bash
cd frontend
npm run build
```

---

## Future Roadmap

| Phase | Feature | Description |
|-------|---------|-------------|
| Phase 2 | Kafka Streaming | Replace MVP pipeline with full Kafka consumers for horizontal scale |
| Phase 2 | Azure Cognitive Search | Replace Pinecone with Azure AI Search for fully Azure-native stack |
| Phase 2 | SEBI Filing Ingestion | Auto-ingest BRSR (Business Responsibility and Sustainability Reporting) filings |
| Phase 3 | Portfolio Analytics | Aggregate ESG scores across a portfolio of holdings with weighted exposure |
| Phase 3 | Peer Benchmarking | Compare company scores against sector averages and percentiles |
| Phase 3 | Custom Scoring Weights | Let tenants configure their own E/S/G category weights |
| Phase 4 | Mobile App | React Native companion app with push notifications |
| Phase 4 | Regulatory Reporting | Auto-generate ESG compliance reports for SEBI/RBI submissions |
| Phase 4 | Carbon Footprint Calculator | Scope 1/2/3 emissions tracking per company |

---

## License

Built with purpose for the **Hack for Green Bharat** hackathon. Committed to accelerating sustainable investment in India through transparent, real-time ESG intelligence.

---

*Green Bharat -- Because sustainable growth needs real-time visibility.*
