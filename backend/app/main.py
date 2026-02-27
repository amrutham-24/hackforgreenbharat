import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.routers import auth, companies, watchlists, alerts, chat, ingest, websocket

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("ESG Risk Intelligence Platform starting...")
    yield
    logging.info("Shutting down...")


app = FastAPI(
    title="Green Bharat ESG Risk Intelligence API",
    description="Real-time ESG risk scoring, classification, and RAG-powered chat",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(watchlists.router)
app.include_router(alerts.router)
app.include_router(chat.router)
app.include_router(ingest.router)
app.include_router(websocket.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "esg-api"}
