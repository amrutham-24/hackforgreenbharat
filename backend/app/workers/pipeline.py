"""
Event Processing Pipeline (MVP Worker Mode)

Steps:
1. Ingest raw event
2. Classify (LLM or rule-based)
3. Store RAG document + create embedding
4. Recalculate company score
5. Evaluate alert rules
6. Publish live update via Redis pubsub
"""
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ESGEvent, RAGDocument
from app.services.classifier import classify_event
from app.services.scoring import recalculate_company_score
from app.services.alerts import evaluate_alerts_for_event
from app.services.rag import upsert_document
from app.db.redis import redis_client

logger = logging.getLogger(__name__)


async def process_event(db: AsyncSession, event: ESGEvent):
    try:
        classification = await classify_event(event.title, event.description or "")
        event.category = classification.get("category", event.category or "governance")
        event.subcategory = classification.get("subcategory", "")
        event.severity = classification.get("severity", 5)
        event.confidence = classification.get("confidence", 0.7)
        event.sentiment = classification.get("sentiment", "negative")
        event.classification_json = classification
        event.is_processed = True
        await db.flush()

        rag_doc = RAGDocument(
            tenant_id=event.tenant_id,
            company_id=event.company_id,
            event_id=event.id,
            title=event.title,
            content=f"{event.title}. {event.description or ''}",
            source_url=event.source_url or "",
        )
        db.add(rag_doc)
        await db.flush()

        await upsert_document(
            doc_id=rag_doc.id,
            text=rag_doc.content,
            metadata={
                "tenant_id": event.tenant_id,
                "company_id": event.company_id,
                "title": event.title,
                "source_url": event.source_url or "",
                "ts": event.event_date.isoformat() if event.event_date else "",
                "text": rag_doc.content[:500],
            },
        )

        new_score = await recalculate_company_score(db, event.company_id, event.tenant_id)

        await evaluate_alerts_for_event(db, event, new_score, event.tenant_id)

        live_update = {
            "type": "score_update",
            "company_id": event.company_id,
            "tenant_id": event.tenant_id,
            "score": {
                "overall": new_score.overall,
                "environmental": new_score.environmental,
                "social": new_score.social,
                "governance": new_score.governance,
                "risk_level": new_score.risk_level,
            },
            "event": {
                "id": event.id,
                "title": event.title,
                "category": event.category,
                "severity": event.severity,
                "sentiment": event.sentiment,
            },
        }
        try:
            await redis_client.publish("esg:live", json.dumps(live_update))
        except Exception as e:
            logger.warning(f"Redis publish failed (non-critical): {e}")

        logger.info(f"Processed event {event.id} for company {event.company_id}")
        return new_score

    except Exception as e:
        logger.error(f"Pipeline failed for event {event.id}: {e}")
        raise
