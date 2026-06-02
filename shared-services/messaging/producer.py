"""Kafka message producer with serialization and error handling.

All agents publish messages through this producer, which handles
JSON serialization via Pydantic, delivery confirmations, and
dead-letter queue routing for failed publishes.
"""

from __future__ import annotations

import json
import os
import asyncio
from typing import Any

import structlog
from dotenv import load_dotenv

from messaging.schemas import MASMessage
from messaging.topics import TOPIC_REGISTRY

load_dotenv()
logger = structlog.get_logger()


class MessageProducer:
    """Typed Kafka message producer.

    Wraps the confluent-kafka producer with:
    - Automatic Pydantic → JSON serialization
    - Topic validation against the registry
    - Delivery confirmation logging
    - Dead-letter queue routing on failure

    Usage:
        ```python
        producer = MessageProducer()
        await producer.start()

        message = TaskAssignedMessage(
            source_agent_id="ceo-orchestrator",
            target_agent_id="healthcare-vm",
            task_id="task-123",
            vertical="healthcare",
            task_type="nabh_gap_analysis",
        )
        await producer.publish("task.assigned", message)

        await producer.stop()
        ```
    """

    def __init__(
        self,
        bootstrap_servers: str | None = None,
        client_id: str = "mas-producer",
    ) -> None:
        self._bootstrap_servers = bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self._client_id = client_id
        self._producer: Any = None
        self._started = False
        self._log = logger.bind(component="message_producer")

    async def start(self) -> None:
        """Initialize and start the Kafka producer."""
        try:
            from confluent_kafka import Producer

            conf = {
                'bootstrap.servers': self._bootstrap_servers,
                'client.id': self._client_id,
                'acks': 'all',
                'retries': 3,
                'retry.backoff.ms': 500,
            }
            # For Redpanda/Confluent Cloud, add SASL config here if needed
            if os.getenv("KAFKA_SASL_USERNAME"):
                conf.update({
                    'security.protocol': 'SASL_SSL',
                    'sasl.mechanisms': 'PLAIN',
                    'sasl.username': os.getenv("KAFKA_SASL_USERNAME"),
                    'sasl.password': os.getenv("KAFKA_SASL_PASSWORD"),
                })

            self._producer = Producer(conf)
            self._started = True
            self._log.info("producer_started", servers=self._bootstrap_servers)
        except ImportError:
            self._log.warning(
                "confluent_kafka_not_installed",
                message="Running in stub mode — messages logged but not published.",
            )
            self._started = True  # Allow operation in stub mode

    async def publish(
        self,
        topic_name: str,
        message: MASMessage,
        key: str | None = None,
    ) -> None:
        """Publish a typed message to a Kafka topic.

        Args:
            topic_name: Must be a registered topic in TOPIC_REGISTRY.
            message: A Pydantic message object inheriting from MASMessage.
            key: Optional partition key for ordering guarantees.
        """
        if not self._started:
            raise RuntimeError("Producer not started. Call start() first.")

        # Validate topic
        topic = TOPIC_REGISTRY.get(topic_name)
        if topic is None:
            raise ValueError(
                f"Unknown topic '{topic_name}'. "
                f"Valid topics: {list(TOPIC_REGISTRY.keys())}"
            )

        # Serialize message
        payload = message.model_dump(mode="json")
        payload_bytes = json.dumps(payload).encode("utf-8")
        key_bytes = key.encode("utf-8") if key else message.source_agent_id.encode("utf-8")

        self._log.debug(
            "publishing_message",
            topic=topic_name,
            message_id=message.message_id,
            source_agent=message.source_agent_id,
        )

        try:
            if self._producer is not None:
                loop = asyncio.get_running_loop()
                future = loop.create_future()

                def delivery_report(err, msg):
                    if err is not None:
                        loop.call_soon_threadsafe(future.set_exception, Exception(err))
                    else:
                        loop.call_soon_threadsafe(future.set_result, msg)

                self._producer.produce(
                    topic=topic_name,
                    value=payload_bytes,
                    key=key_bytes,
                    callback=delivery_report
                )
                self._producer.poll(0)
                await future
            else:
                # Stub mode — just log
                self._log.info(
                    "message_published_stub",
                    topic=topic_name,
                    message_id=message.message_id,
                    payload_size=len(payload_bytes),
                )

            self._log.info(
                "message_published",
                topic=topic_name,
                message_id=message.message_id,
            )

        except Exception as e:
            self._log.error(
                "publish_failed",
                topic=topic_name,
                message_id=message.message_id,
                error=str(e),
            )
            # Route to dead-letter queue
            await self._send_to_dlq(topic_name, payload, str(e))

    async def publish_batch(
        self,
        topic_name: str,
        messages: list[MASMessage],
    ) -> int:
        """Publish a batch of messages to a topic.

        Returns:
            Number of successfully published messages.
        """
        success_count = 0
        for message in messages:
            try:
                await self.publish(topic_name, message)
                success_count += 1
            except Exception as e:
                self._log.error(
                    "batch_publish_failed",
                    topic=topic_name,
                    message_id=message.message_id,
                    error=str(e),
                )
        return success_count

    async def _send_to_dlq(
        self,
        original_topic: str,
        payload: dict[str, Any],
        error: str,
    ) -> None:
        """Send a failed message to the dead-letter queue.

        DLQ messages are logged with the original topic and error
        for later investigation and replay.
        """
        self._log.warning(
            "dead_letter_queue",
            original_topic=original_topic,
            error=error,
            payload_size=len(json.dumps(payload)),
        )
        # TODO: Publish to a dedicated DLQ topic for replay

    async def stop(self) -> None:
        """Flush pending messages and stop the producer."""
        if self._producer is not None:
            self._producer.flush()
        self._started = False
        self._log.info("producer_stopped")
