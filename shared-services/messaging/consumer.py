"""Kafka message consumer with deserialization and handler routing.

Agents subscribe to specific topics and register handler functions.
The consumer deserializes messages into typed Pydantic models and
routes them to the appropriate handler.
"""

from __future__ import annotations

import json
import os
import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from dotenv import load_dotenv

from messaging.schemas import MASMessage
from messaging.topics import TOPIC_REGISTRY

load_dotenv()
logger = structlog.get_logger()

# Type alias for message handlers
MessageHandler = Callable[[MASMessage], Awaitable[None]]


class MessageConsumer:
    """Typed Kafka message consumer with handler routing.

    Usage:
        ```python
        consumer = MessageConsumer(group_id="healthcare-vm-group")

        async def handle_task(message: TaskAssignedMessage):
            print(f"Received task: {message.task_id}")

        consumer.register_handler("task.assigned", handle_task)
        await consumer.start()
        # Consumer runs in the background, dispatching to handlers
        ```
    """

    def __init__(
        self,
        bootstrap_servers: str | None = None,
        group_id: str = "mas-consumer",
        auto_offset_reset: str = "latest",
    ) -> None:
        self._bootstrap_servers = bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self._group_id = group_id
        self._auto_offset_reset = auto_offset_reset
        self._consumer: Any = None
        self._handlers: dict[str, list[MessageHandler]] = {}
        self._running = False
        self._log = logger.bind(component="message_consumer", group_id=group_id)

    def register_handler(
        self,
        topic_name: str,
        handler: MessageHandler,
    ) -> None:
        """Register a handler function for a specific topic.

        Multiple handlers can be registered for the same topic.
        They will be called sequentially in registration order.

        Args:
            topic_name: Must be a registered topic in TOPIC_REGISTRY.
            handler: Async function that accepts a MASMessage subclass.
        """
        if topic_name not in TOPIC_REGISTRY:
            raise ValueError(
                f"Unknown topic '{topic_name}'. "
                f"Valid topics: {list(TOPIC_REGISTRY.keys())}"
            )
        if topic_name not in self._handlers:
            self._handlers[topic_name] = []
        self._handlers[topic_name].append(handler)
        self._log.info(
            "handler_registered",
            topic=topic_name,
            handler=handler.__name__,
        )

    async def start(self) -> None:
        """Start consuming messages from registered topics."""
        if not self._handlers:
            raise RuntimeError("No handlers registered. Call register_handler() first.")

        topics = list(self._handlers.keys())

        try:
            from confluent_kafka import Consumer

            conf = {
                'bootstrap.servers': self._bootstrap_servers,
                'group.id': self._group_id,
                'auto.offset.reset': self._auto_offset_reset,
                'enable.auto.commit': True,
                'auto.commit.interval.ms': 5000,
            }
            if os.getenv("KAFKA_SASL_USERNAME"):
                conf.update({
                    'security.protocol': 'SASL_SSL',
                    'sasl.mechanisms': 'PLAIN',
                    'sasl.username': os.getenv("KAFKA_SASL_USERNAME"),
                    'sasl.password': os.getenv("KAFKA_SASL_PASSWORD"),
                })

            self._consumer = Consumer(conf)
            self._consumer.subscribe(topics)
            self._running = True
            self._log.info("consumer_started", topics=topics)

            # Main consumption loop running in executor to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            
            def poll_messages():
                while self._running:
                    msg = self._consumer.poll(1.0)
                    if msg is None:
                        continue
                    if msg.error():
                        self._log.error("consumer_error", error=msg.error())
                        continue
                    # Schedule the dispatch coroutine in the main loop
                    asyncio.run_coroutine_threadsafe(
                        self._dispatch(msg.topic(), json.loads(msg.value().decode('utf-8'))), 
                        loop
                    )

            await loop.run_in_executor(None, poll_messages)

        except ImportError:
            self._log.warning(
                "confluent_kafka_not_installed",
                message="Running in stub mode — no messages will be consumed.",
            )

    async def _dispatch(self, topic: str, payload: dict[str, Any]) -> None:
        """Deserialize and route a message to registered handlers."""
        handlers = self._handlers.get(topic, [])
        if not handlers:
            self._log.warning("no_handler_for_topic", topic=topic)
            return

        # Deserialize into base MASMessage (handlers can cast to specific types)
        try:
            message = MASMessage.model_validate(payload)
        except Exception as e:
            self._log.error(
                "message_deserialization_failed",
                topic=topic,
                error=str(e),
            )
            return

        self._log.debug(
            "dispatching_message",
            topic=topic,
            message_id=message.message_id,
            handler_count=len(handlers),
        )

        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                self._log.error(
                    "handler_error",
                    topic=topic,
                    handler=handler.__name__,
                    message_id=message.message_id,
                    error=str(e),
                    exc_info=True,
                )

    async def stop(self) -> None:
        """Stop the consumer gracefully."""
        self._running = False
        if self._consumer is not None:
            self._consumer.close()
        self._log.info("consumer_stopped")
