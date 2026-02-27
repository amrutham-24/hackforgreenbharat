# Green Bharat ESG Intelligence - Frontend

Real-Time ESG Risk Intelligence Dashboard built with Next.js 16, TypeScript, TailwindCSS, and Zustand.

## Features

- **Bloomberg-like Dashboard**: Left sidebar + main panel + AI chat panel
- **Live ESG Scorecards**: Real-time score rings (Overall, E, S, G) with risk level
- **Risk Trend Charts**: 30-day interactive area charts with Recharts
- **Event Timeline**: Filterable timeline with severity, category, and date filters
- **AI Chat Panel**: RAG-powered assistant with citation-backed answers
- **Watchlists**: Per-user company watchlists
- **Alerts**: Configurable alert rules and delivery history
- **Real-Time Updates**: WebSocket client for live score changes

## Tech Stack

- Next.js 16 (App Router)
- TypeScript
- TailwindCSS v4
- Zustand (state management)
- Recharts (data visualization)
- Lucide React (icons)
- Radix UI primitives

## Pages

| Route | Description |
|-------|-------------|
| `/login` | Authentication page |
| `/dashboard` | Main ESG dashboard |
| `/company/[id]` | Company detail with scores, events, chart |
| `/watchlist/[id]` | User watchlists |
| `/alerts` | Alert rules and delivery history |
| `/settings` | Account and organization settings |

## Setup

### Prerequisites
- Node.js 22+

### Local Development

```bash
# Install dependencies
npm install

# Copy env and configure
cp .env.example .env.local

# Start development server
npm run dev
```

### Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)

### Docker

```bash
# From project root
docker compose up web
```

## Demo Credentials

- Email: `demo@greenbharat.ai`
- Password: `demo123`
