"""
Kafka Mode Scaffolding

Topics:
- raw_events: Ingested events before processing
- normalized: Events after normalization
- classified: Events after ESG classification
- scored_updates: Final scored updates for live distribution

This is scaffolding only. MVP uses the sequential pipeline worker.
"""

TOPICS = {
    "raw_events": {
        "description": "Raw ingested ESG events",
        "partitions": 6,
        "replication_factor": 3,
    },
    "normalized": {
        "description": "Normalized events with consistent schema",
        "partitions": 6,
        "replication_factor": 3,
    },
    "classified": {
        "description": "Events after LLM/rule-based classification",
        "partitions": 6,
        "replication_factor": 3,
    },
    "scored_updates": {
        "description": "Score updates ready for live distribution",
        "partitions": 6,
        "replication_factor": 3,
    },
}


class KafkaProducerStub:
    """Stub for Kafka producer. Replace with confluent_kafka or aiokafka in production."""

    async def send(self, topic: str, key: str, value: dict):
        raise NotImplementedError("Kafka mode not implemented. Use MVP worker mode.")


class KafkaConsumerStub:
    """Stub for Kafka consumer. Replace with confluent_kafka or aiokafka in production."""

    async def consume(self, topic: str, group_id: str):
        raise NotImplementedError("Kafka mode not implemented. Use MVP worker mode.")


class RawEventsConsumer(KafkaConsumerStub):
    """Consumes from raw_events, normalizes, produces to normalized."""
    pass


class NormalizedConsumer(KafkaConsumerStub):
    """Consumes from normalized, classifies, produces to classified."""
    pass


class ClassifiedConsumer(KafkaConsumerStub):
    """Consumes from classified, scores, produces to scored_updates."""
    pass


class ScoredUpdatesConsumer(KafkaConsumerStub):
    """Consumes from scored_updates, publishes to WebSocket via Redis."""
    pass
