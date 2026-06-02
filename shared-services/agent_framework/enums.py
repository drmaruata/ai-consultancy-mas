"""Enumerations and constants for the MAS agent system."""

from enum import StrEnum


class AgentState(StrEnum):
    """State machine for agent lifecycle.

    Transitions:
        IDLE → PLANNING → EXECUTING → REFLECTING → COMPLETE
                                    ↘ ERROR
                                    ↘ ESCALATED
    """

    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    COMPLETE = "complete"
    ERROR = "error"
    ESCALATED = "escalated"


class ReasoningMode(StrEnum):
    """Reasoning architecture for agents.

    - PLAN_AND_EXECUTE: For Tier 0–3 agents. Includes mandatory Phase 0 IP Registry check.
    - REACT: For Tier 4 domain specialist agents. Reason + Act loop.
    """

    PLAN_AND_EXECUTE = "plan_and_execute"
    REACT = "react"


class AgentTier(StrEnum):
    """Agent tier in the MAS hierarchy.

    Tier 0: Orchestration (CEO)
    Tier 1: Business Ops (Sales, Marketing, Finance, Ops, Account Growth, Market Intel, Tender)
    Tier 2: Shared Services (Memory, QA, Self-Improvement)
    Tier 3: Vertical Managers
    Tier 4: Domain Specialists
    """

    ORCHESTRATION = "tier_0"
    BUSINESS_OPS = "tier_1"
    SHARED_SERVICES = "tier_2"
    VERTICAL_MANAGER = "tier_3"
    DOMAIN_SPECIALIST = "tier_4"


class Vertical(StrEnum):
    """Industry verticals served by the MAS."""

    ALL = "all"
    HEALTHCARE = "healthcare"
    LOGISTICS = "logistics"
    LEGAL = "legal"
    EDTECH = "edtech"


class QATier(StrEnum):
    """Quality Assurance classification tiers.

    CLASS_A: Pattern-matched, fast-track (< 2 min)
    CLASS_B: Full LLM validation + domain rules (< 15 min)
    CLASS_C: High-stakes, requires human review gate
    """

    CLASS_A = "class_a"
    CLASS_B = "class_b"
    CLASS_C = "class_c"


class EscalationReason(StrEnum):
    """Reasons an agent may escalate to human oversight."""

    HIGH_VALUE_CONTRACT = "high_value_contract"
    GOVERNMENT_TENDER = "government_tender"
    CLINICAL_RECOMMENDATION = "clinical_recommendation"
    LEGAL_OPINION = "legal_opinion"
    PRICING_ANOMALY = "pricing_anomaly"
    LOW_CONFIDENCE = "low_confidence"
    AGENT_ERROR = "agent_error"
    NOVEL_CLIENT_TYPE = "novel_client_type"
    BEHAVIOUR_CHANGE = "behaviour_change"
    UNKNOWN_TASK_TYPE = "unknown_task_type"
    TASK_FAILED = "task_failed"


class DecayRate(StrEnum):
    """Knowledge base document validity decay rates.

    FAST: 180-day half-life (regulatory docs)
    MEDIUM: 365-day half-life (standards docs)
    SLOW: 730-day half-life (foundational reference)
    """

    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"


class IPAssetType(StrEnum):
    """Categories of intellectual property assets in the IP Registry."""

    TEMPLATE = "template"
    ACCELERATOR = "accelerator"
    PRODUCT = "product"
