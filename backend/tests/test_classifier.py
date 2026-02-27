import pytest
from app.services.classifier import _rule_based_classify


def test_environmental_classification():
    result = _rule_based_classify(
        "Carbon emission targets missed",
        "Company exceeded planned emissions by 20%"
    )
    assert result["category"] == "environmental"
    assert 1 <= result["severity"] <= 10
    assert 0 <= result["confidence"] <= 1


def test_social_classification():
    result = _rule_based_classify(
        "Worker safety incident at plant",
        "Workplace accident resulted in injuries to workers"
    )
    assert result["category"] == "social"


def test_governance_classification():
    result = _rule_based_classify(
        "Board independence concerns raised",
        "Proxy firm flagged low board independence and audit issues"
    )
    assert result["category"] == "governance"


def test_high_severity_keywords():
    result = _rule_based_classify(
        "Critical pollution disaster",
        "Major environmental disaster at the facility"
    )
    assert result["severity"] >= 7


def test_positive_sentiment():
    result = _rule_based_classify(
        "Positive improvement in waste management",
        "Company made significant progress in reducing waste"
    )
    assert result["sentiment"] == "positive"


def test_classification_json_schema():
    result = _rule_based_classify("Test event", "Test description")
    required_keys = {"category", "subcategory", "severity", "confidence", "sentiment"}
    assert required_keys.issubset(set(result.keys()))
    assert result["category"] in ("environmental", "social", "governance")
    assert isinstance(result["severity"], int)
    assert isinstance(result["confidence"], float)
