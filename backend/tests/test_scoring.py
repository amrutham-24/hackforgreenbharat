import pytest
from datetime import datetime, timezone, timedelta
from app.services.scoring import recency_decay, compute_event_impact, risk_level_from_score


def test_recency_decay_now():
    now = datetime.now(timezone.utc)
    decay = recency_decay(now, now)
    assert abs(decay - 1.0) < 0.01


def test_recency_decay_14_days():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=14)
    decay = recency_decay(past, now)
    assert abs(decay - 0.5) < 0.05


def test_recency_decay_28_days():
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=28)
    decay = recency_decay(past, now)
    assert abs(decay - 0.25) < 0.05


def test_compute_event_impact():
    impact = compute_event_impact(severity=8, confidence=0.9, decay=1.0, repetition_factor=1.0)
    assert abs(impact - 7.2) < 0.01


def test_risk_level_low():
    assert risk_level_from_score(85) == "low"


def test_risk_level_medium():
    assert risk_level_from_score(65) == "medium"


def test_risk_level_high():
    assert risk_level_from_score(45) == "high"


def test_risk_level_critical():
    assert risk_level_from_score(30) == "critical"
