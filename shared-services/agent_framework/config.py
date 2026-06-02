"""Agent configuration models using Pydantic for validation."""

from __future__ import annotations

from pydantic import BaseModel, Field

from agent_framework.enums import (
    AgentTier,
    EscalationReason,
    QATier,
    ReasoningMode,
    Vertical,
)


class EscalationRule(BaseModel):
    """Defines when and why an agent should escalate to human oversight."""

    reason: EscalationReason
    description: str
    auto_escalate: bool = True
    """If True, escalation happens automatically. If False, agent asks for confirmation."""


class TokenBudget(BaseModel):
    """Per-task and per-cycle token budget configuration."""

    max_tokens_per_task: int = Field(default=8_000, ge=100, le=500_000)
    max_tokens_per_cycle: int = Field(default=100_000, ge=1_000, le=5_000_000)
    overage_threshold_pct: float = Field(default=0.80, ge=0.5, le=1.0)
    """Fraction of budget at which throttling kicks in (default: 80%)."""
    hard_cap_pct: float = Field(default=1.20, ge=1.0, le=2.0)
    """Fraction of budget at which requests are blocked (default: 120%)."""


class CronSchedule(BaseModel):
    """Cron-based proactive execution schedule for an agent."""

    expression: str
    """Standard 5-field cron expression (e.g. '0 6 * * MON' for Monday 6 AM)."""
    task_description: str
    """Human-readable description of the scheduled task."""
    enabled: bool = True


class GuardrailConfig(BaseModel):
    """Guardrail rules applied to agent outputs before delivery."""

    mandatory_disclaimer: str | None = None
    """Disclaimer text appended to ALL outputs (e.g. Legal vertical)."""
    pii_detection_enabled: bool = True
    """Run PII detection on outputs before delivery."""
    blocked_output_patterns: list[str] = Field(default_factory=list)
    """Regex patterns that, if matched, block the output and trigger escalation."""
    max_confidence_without_source: float = Field(default=0.5, ge=0.0, le=1.0)
    """Maximum confidence score allowed when no KB source is cited."""
    require_kb_validity_check: bool = True
    """If True, agent must check KB validity scores before citing documents."""


class AgentConfig(BaseModel):
    """Complete configuration for a single MAS agent.

    Every agent in the system is instantiated with an AgentConfig
    that defines its identity, behaviour, constraints, and scheduling.

    Example:
        ```python
        config = AgentConfig(
            agent_id="healthcare-clinical-ai",
            name="Clinical AI Agent",
            tier=AgentTier.DOMAIN_SPECIALIST,
            vertical=Vertical.HEALTHCARE,
            reasoning_mode=ReasoningMode.REACT,
            description="Designs CDSS and bioinformatics pipeline architectures.",
            token_budget=TokenBudget(max_tokens_per_task=16_000),
            guardrails=GuardrailConfig(
                blocked_output_patterns=[r"(?i)diagnos(e|is|ing)\\s+patient"],
            ),
        )
        ```
    """

    agent_id: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9\-]+$",
        min_length=3,
        max_length=64,
        description="Unique identifier for the agent (kebab-case).",
    )
    name: str = Field(..., min_length=1, max_length=128)
    tier: AgentTier
    vertical: Vertical
    reasoning_mode: ReasoningMode
    description: str = ""

    # System prompt and tools
    system_prompt_path: str | None = None
    """Path to the versioned system prompt file (procedural memory)."""
    tools: list[str] = Field(default_factory=list)
    """List of tool identifiers this agent has access to."""

    # Behavioural constraints
    token_budget: TokenBudget = Field(default_factory=TokenBudget)
    escalation_rules: list[EscalationRule] = Field(default_factory=list)
    guardrails: GuardrailConfig = Field(default_factory=GuardrailConfig)

    # Scheduling
    cron_schedules: list[CronSchedule] = Field(default_factory=list)

    # QA classification
    default_qa_tier: QATier = QATier.CLASS_B
    """Default QA tier for deliverables produced by this agent."""

    # Feature flags
    ip_registry_check_enabled: bool = True
    """If True, agent checks IP Registry before executing bespoke work."""
    self_improvement_enabled: bool = True
    """If True, agent performance is tracked by the Self-Improvement Engine."""
