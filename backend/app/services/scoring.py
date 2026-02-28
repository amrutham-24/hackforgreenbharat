"""
ESG Risk Scoring Engine

Score updates based on:
- Event severity (1-10)
- Category weight (E=0.35, S=0.30, G=0.35)
- Confidence factor
- Recency decay (exponential, half-life 14 days)
- Repetition factor (more events in same category = higher impact)
"""
import math
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ESGScore, ESGEvent, Company

CATEGORY_WEIGHTS = {"environmental": 0.35, "social": 0.30, "governance": 0.35}
HALF_LIFE_DAYS = 14
BASE_SCORE = 75.0


def recency_decay(event_date: datetime, now: Optional[datetime] = None) -> float:
    now = now or datetime.now(timezone.utc)
    if event_date.tzinfo is None:
        event_date = event_date.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    days_ago = max((now - event_date).total_seconds() / 86400, 0)
    return math.exp(-0.693 * days_ago / HALF_LIFE_DAYS)


def compute_event_impact(severity: int, confidence: float, decay: float, repetition_factor: float) -> float:
    return severity * confidence * decay * repetition_factor


def risk_level_from_score(score: float) -> str:
    if score >= 80:
        return "low"
    elif score >= 60:
        return "medium"
    elif score >= 40:
        return "high"
    return "critical"


async def recalculate_company_score(
    db: AsyncSession, company_id: str, tenant_id: str
) -> ESGScore:
    now = datetime.now(timezone.utc)
    lookback = now - timedelta(days=90)

    result = await db.execute(
        select(ESGEvent).where(
            ESGEvent.company_id == company_id,
            ESGEvent.tenant_id == tenant_id,
            ESGEvent.event_date >= lookback,
            ESGEvent.is_processed == True,
        )
    )
    events = result.scalars().all()

    category_impacts = {"environmental": [], "social": [], "governance": []}

    cat_counts = {"environmental": 0, "social": 0, "governance": 0}
    for e in events:
        cat = e.category.lower() if e.category else "governance"
        if cat in cat_counts:
            cat_counts[cat] += 1

    for event in events:
        cat = event.category.lower() if event.category else "governance"
        if cat not in category_impacts:
            continue
        decay = recency_decay(event.event_date, now)
        rep_factor = 1.0 + 0.1 * (cat_counts.get(cat, 1) - 1)
        impact = compute_event_impact(event.severity, event.confidence, decay, rep_factor)
        category_impacts[cat].append(impact)

    e_impact = sum(category_impacts["environmental"])
    s_impact = sum(category_impacts["social"])
    g_impact = sum(category_impacts["governance"])

    max_impact = 50.0
    e_score = max(0, BASE_SCORE - min(e_impact, max_impact))
    s_score = max(0, BASE_SCORE - min(s_impact, max_impact))
    g_score = max(0, BASE_SCORE - min(g_impact, max_impact))

    overall = (
        e_score * CATEGORY_WEIGHTS["environmental"]
        + s_score * CATEGORY_WEIGHTS["social"]
        + g_score * CATEGORY_WEIGHTS["governance"]
    )

    score = ESGScore(
        tenant_id=tenant_id,
        company_id=company_id,
        overall=round(overall, 2),
        environmental=round(e_score, 2),
        social=round(s_score, 2),
        governance=round(g_score, 2),
        risk_level=risk_level_from_score(overall),
        recorded_at=now,
    )
    db.add(score)
    await db.flush()
    return score
