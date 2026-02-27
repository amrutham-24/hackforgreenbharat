"""
Alert Rules Engine

Evaluates scored events against user-defined rules and sends notifications.
Supports: score_drop, severity_gte, category_match
Channels: slack (webhook), email (mock)
"""
import json
import logging
from typing import List, Optional
from datetime import datetime, timezone
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AlertRule, AlertDelivery, ESGEvent, ESGScore
from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def evaluate_alerts_for_event(
    db: AsyncSession, event: ESGEvent, new_score: Optional[ESGScore], tenant_id: str
):
    result = await db.execute(
        select(AlertRule).where(
            AlertRule.tenant_id == tenant_id,
            AlertRule.is_active == True,
        )
    )
    rules = result.scalars().all()

    for rule in rules:
        if rule.company_id and rule.company_id != event.company_id:
            continue

        triggered = False
        if rule.condition_type == "severity_gte":
            triggered = event.severity >= rule.threshold
        elif rule.condition_type == "category_match":
            triggered = event.category == rule.category_filter
        elif rule.condition_type == "score_drop" and new_score:
            prev_result = await db.execute(
                select(ESGScore)
                .where(
                    ESGScore.company_id == event.company_id,
                    ESGScore.tenant_id == tenant_id,
                    ESGScore.id != new_score.id,
                )
                .order_by(ESGScore.recorded_at.desc())
                .limit(1)
            )
            prev_score = prev_result.scalar_one_or_none()
            if prev_score:
                drop = prev_score.overall - new_score.overall
                triggered = drop >= rule.threshold

        if triggered:
            for channel in (rule.channels or ["email"]):
                await _deliver_alert(db, rule, event, channel, tenant_id)


async def _deliver_alert(
    db: AsyncSession, rule: AlertRule, event: ESGEvent, channel: str, tenant_id: str
):
    payload = {
        "rule_name": rule.name,
        "event_title": event.title,
        "event_severity": event.severity,
        "event_category": event.category,
        "company_id": event.company_id,
        "message": f"Alert: {rule.name} triggered by event '{event.title}' (severity: {event.severity})",
    }

    if channel == "slack":
        await _send_slack(payload)
    elif channel == "email":
        await _send_email(payload)

    delivery = AlertDelivery(
        tenant_id=tenant_id,
        rule_id=rule.id,
        event_id=event.id,
        channel=channel,
        status="sent",
        payload=payload,
    )
    db.add(delivery)
    await db.flush()


async def _send_slack(payload: dict):
    settings = get_settings()
    if not settings.SLACK_WEBHOOK_URL:
        logger.info(f"[MOCK SLACK] {payload['message']}")
        return
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                settings.SLACK_WEBHOOK_URL,
                json={"text": payload["message"]},
                timeout=10,
            )
    except Exception as e:
        logger.error(f"Slack delivery failed: {e}")


async def _send_email(payload: dict):
    logger.info(f"[MOCK EMAIL] To: alert-recipient | Subject: {payload['rule_name']} | Body: {payload['message']}")
