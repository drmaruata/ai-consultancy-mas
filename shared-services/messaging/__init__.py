"""
Messaging layer for the AI Consultancy MAS v3.0.

Provides typed Kafka producer/consumer wrappers, a topic registry,
and message schema definitions for all inter-agent communication.
"""

from messaging.consumer import MessageConsumer
from messaging.producer import MessageProducer
from messaging.schemas import (
    AuditLogMessage,
    ClientHealthAlertMessage,
    DeliverableReadyMessage,
    EscalationMessage,
    KBSupersessionMessage,
    MASMessage,
    RegulatoryUpdateMessage,
    TaskAssignedMessage,
    TenderNewMessage,
)
from messaging.topics import TOPIC_REGISTRY, Topic

__all__ = [
    "TOPIC_REGISTRY",
    "AuditLogMessage",
    "ClientHealthAlertMessage",
    "DeliverableReadyMessage",
    "EscalationMessage",
    "KBSupersessionMessage",
    "MASMessage",
    "MessageConsumer",
    "MessageProducer",
    "RegulatoryUpdateMessage",
    "TaskAssignedMessage",
    "TenderNewMessage",
    "Topic",
]
