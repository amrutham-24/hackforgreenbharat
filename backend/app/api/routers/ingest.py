from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import ESGEvent
from app.core.auth import get_current_user, TokenPayload, require_internal_key
from app.schemas.common import IngestEventRequest
from app.workers.pipeline import process_event

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])


@router.post("/events")
async def ingest_event(
    body: IngestEventRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event = ESGEvent(
        tenant_id=current_user.tenant_id,
        company_id=body.company_id,
        title=body.title,
        description=body.description,
        source_url=body.source_url or "",
        category=body.category or "governance",
        raw_text=body.raw_text or body.description,
        event_date=body.event_date or datetime.now(timezone.utc),
    )
    db.add(event)
    await db.flush()

    new_score = await process_event(db, event)

    return {
        "status": "processed",
        "event_id": event.id,
        "score": {
            "overall": new_score.overall,
            "risk_level": new_score.risk_level,
        },
    }
