"""Typed message schemas for all Kafka topics.

Every message flowing through the Kafka bus is validated against
these Pydantic models before publishing and after consuming.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class MASMessage(BaseModel):
    """Base message class for all Kafka messages.

    Every message carries a unique ID, timestamp, source agent,
    and correlation ID for distributed tracing.
    """

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_agent_id: str
    """The agent that published this message."""
    correlation_id: str = ""
    """Traces a message back to the originating task/workflow."""
    schema_version: int = 1
    """Message schema version for forward/backward compatibility."""


# ── Task Lifecycle ───────────────────────────────────────────────────


class TaskAssignedMessage(MASMessage):
    """Published when a task is assigned to an agent."""

    target_agent_id: str
    task_id: str
    engagement_id: str | None = None
    client_id: str | None = None
    vertical: str
    task_type: str
    description: str = ""
    priority: int = Field(default=5, ge=1, le=10)
    deadline: datetime | None = None
    input_data: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    suggested_ip_assets: list[str] = Field(default_factory=list)


class TaskCompletedMessage(MASMessage):
    """Published when an agent completes a task."""

    task_id: str
    engagement_id: str | None = None
    result_summary: str = ""
    confidence: float = 0.0
    tokens_used: int = 0
    duration_ms: int = 0
    output_location: str = ""
    """Reference to where the output/deliverable is stored."""


class TaskFailedMessage(MASMessage):
    """Published when an agent fails to complete a task."""

    task_id: str
    error: str
    recoverable: bool = False


# ── Deliverable Pipeline ─────────────────────────────────────────────


class DeliverableReadyMessage(MASMessage):
    """Published when a deliverable is ready for QA review."""

    task_id: str
    engagement_id: str | None = None
    client_id: str | None = None
    vertical: str
    deliverable_type: str
    """E.g. 'nabh_gap_analysis', 'contract_review', 'study_plan'."""
    content_location: str
    """Storage path or ID for the deliverable content."""
    suggested_qa_tier: str = "class_b"
    """Suggested QA tier: 'class_a', 'class_b', 'class_c'."""
    confidence: float = 0.0
    sources_cited: list[str] = Field(default_factory=list)
    ip_assets_used: list[str] = Field(default_factory=list)


class DeliverableApprovedMessage(MASMessage):
    """Published when QA approves a deliverable."""

    task_id: str
    deliverable_id: str
    qa_tier: str
    quality_score: float = 0.0
    review_notes: str = ""


class DeliverableRejectedMessage(MASMessage):
    """Published when QA rejects a deliverable."""

    task_id: str
    deliverable_id: str
    qa_tier: str
    rejection_reasons: list[str] = Field(default_factory=list)
    revision_instructions: str = ""


# ── Client Health ────────────────────────────────────────────────────


class ClientHealthAlertMessage(MASMessage):
    """Published when a client's CHS drops below threshold."""

    client_id: str
    client_name: str
    current_chs: float
    previous_chs: float
    threshold: float = 65.0
    alert_type: str = "chs_drop"
    """'chs_drop', 'payment_overdue', 'engagement_stalled'."""
    recommended_action: str = ""


# ── Regulatory & Knowledge ───────────────────────────────────────────


class RegulatoryUpdateMessage(MASMessage):
    """Published when a regulatory change is detected."""

    vertical: str
    regulation_name: str
    update_type: str
    """'new_regulation', 'amendment', 'supersession', 'circular'."""
    summary: str
    effective_date: datetime | None = None
    source_url: str = ""
    affected_kb_documents: list[str] = Field(default_factory=list)


class KBSupersessionMessage(MASMessage):
    """Published when a KB document is superseded by a newer version."""

    superseded_doc_id: str
    superseded_doc_title: str
    new_doc_id: str | None = None
    new_doc_title: str | None = None
    vertical: str
    reason: str = ""


# ── MAS Health ───────────────────────────────────────────────────────


class MASHealthReportMessage(MASMessage):
    """Weekly MAS Health Report published by CEO Orchestrator."""

    report_period_start: datetime
    report_period_end: datetime
    revenue_snapshot: dict[str, Any] = Field(default_factory=dict)
    agent_performance: dict[str, Any] = Field(default_factory=dict)
    client_health_alerts: list[dict[str, Any]] = Field(default_factory=list)
    kb_health: dict[str, Any] = Field(default_factory=dict)
    market_intelligence_highlights: list[str] = Field(default_factory=list)


# ── Escalation ───────────────────────────────────────────────────────


class EscalationMessage(MASMessage):
    """Published when an agent needs human oversight approval."""

    task_id: str
    engagement_id: str | None = None
    client_id: str | None = None
    escalation_reason: str
    """One of EscalationReason enum values."""
    description: str
    partial_output: dict[str, Any] = Field(default_factory=dict)
    urgency: str = "normal"
    """'low', 'normal', 'high', 'critical'."""


# ── Tender Pipeline ──────────────────────────────────────────────────


class TenderNewMessage(MASMessage):
    """Published when a new government tender is detected."""

    tender_id: str
    portal: str
    """'gem', 'eprocure', 'state_health', 'state_education'."""
    title: str
    description: str = ""
    deadline: datetime | None = None
    estimated_value: float | None = None
    vertical_match: list[str] = Field(default_factory=list)
    eligibility_met: bool = False
    rfp_document_url: str = ""


class TenderBidMessage(MASMessage):
    """Published when a bid package is generated and awaiting approval."""

    tender_id: str
    bid_document_location: str
    technical_score: float = 0.0
    financial_bid_amount: float = 0.0
    requires_human_approval: bool = True


# ── Affiliate ────────────────────────────────────────────────────────


class AffiliateEventMessage(MASMessage):
    """Published for affiliate marketing events."""

    partner_id: str
    event_type: str
    """'click', 'signup', 'conversion', 'payout'."""
    amount: float = 0.0
    currency: str = "INR"
    product: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


# ── Market Intelligence ──────────────────────────────────────────────


class MarketIntelDigestMessage(MASMessage):
    """Weekly market intelligence digest."""

    period_start: datetime
    period_end: datetime
    competitor_updates: list[dict[str, Any]] = Field(default_factory=list)
    funding_announcements: list[dict[str, Any]] = Field(default_factory=list)
    regulatory_pipeline: list[dict[str, Any]] = Field(default_factory=list)
    opportunities: list[dict[str, Any]] = Field(default_factory=list)


# ── Audit ────────────────────────────────────────────────────────────


class AuditLogMessage(MASMessage):
    """Immutable audit trail entry for every agent action."""

    execution_id: str
    task_id: str
    agent_id: str
    action: str
    """'task_started', 'task_completed', 'escalation', 'error', etc."""
    result_state: str
    tokens_used: int = 0
    elapsed_ms: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
