"""
ESG Event Classifier using LLM (OpenAI-compatible)

Classifies raw event text into:
- category: environmental | social | governance
- subcategory: specific sub-type
- severity: 1-10
- confidence: 0.0-1.0
- sentiment: positive | negative | neutral
"""
import json
import logging
from typing import Optional
from openai import AsyncOpenAI
from app.core.config import get_settings

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """You are an ESG (Environmental, Social, Governance) event classifier.
Analyze the following event and return a JSON object with these fields:
- category: one of "environmental", "social", "governance"
- subcategory: a specific sub-type (e.g., "carbon_emissions", "labor_rights", "board_diversity")
- severity: integer 1-10 (10 = most severe risk)
- confidence: float 0.0-1.0 (your confidence in the classification)
- sentiment: one of "positive", "negative", "neutral"

Event Title: {title}
Event Description: {description}

Return ONLY valid JSON, no markdown or explanation."""

FALLBACK_CLASSIFICATION = {
    "category": "governance",
    "subcategory": "general",
    "severity": 5,
    "confidence": 0.5,
    "sentiment": "negative",
}


async def classify_event(title: str, description: str) -> dict:
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        return _rule_based_classify(title, description)

    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an ESG classification expert. Return only valid JSON."},
                {"role": "user", "content": CLASSIFICATION_PROMPT.format(title=title, description=description)},
            ],
            temperature=0.1,
            max_tokens=200,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        result["severity"] = max(1, min(10, int(result.get("severity", 5))))
        result["confidence"] = max(0.0, min(1.0, float(result.get("confidence", 0.5))))
        return result
    except Exception as e:
        logger.warning(f"LLM classification failed, using rule-based: {e}")
        return _rule_based_classify(title, description)


def _rule_based_classify(title: str, description: str) -> dict:
    text = (title + " " + description).lower()

    env_keywords = ["emission", "carbon", "pollution", "climate", "waste", "deforest", "water", "biodiversity", "renewable", "energy"]
    social_keywords = ["labor", "worker", "safety", "health", "diversity", "human rights", "community", "discrimination", "wage"]
    gov_keywords = ["board", "corruption", "fraud", "compliance", "audit", "executive", "shareholder", "transparency", "bribery"]

    env_score = sum(1 for k in env_keywords if k in text)
    soc_score = sum(1 for k in social_keywords if k in text)
    gov_score = sum(1 for k in gov_keywords if k in text)

    if env_score >= soc_score and env_score >= gov_score:
        category = "environmental"
    elif soc_score >= gov_score:
        category = "social"
    else:
        category = "governance"

    severity = 5
    high_severity = ["critical", "severe", "major", "disaster", "scandal", "violation", "breach"]
    low_severity = ["minor", "improvement", "positive", "progress", "award"]
    if any(w in text for w in high_severity):
        severity = 8
    elif any(w in text for w in low_severity):
        severity = 3

    sentiment = "negative"
    if any(w in text for w in ["positive", "improvement", "award", "progress", "commitment"]):
        sentiment = "positive"

    return {
        "category": category,
        "subcategory": "general",
        "severity": severity,
        "confidence": 0.7,
        "sentiment": sentiment,
    }
