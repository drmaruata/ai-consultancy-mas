"""Tests for the core Agent Framework — Sprint 0.1 acceptance criteria."""

import pytest

from agent_framework import (
    AgentConfig,
    AgentContext,
    AgentState,
    AgentTier,
    BaseAgent,
    ReasoningMode,
    TaskContext,
    Vertical,
)
from agent_framework.base import (
    AgentResult,
    ErrorResult,
    EscalationResult,
    SuccessResult,
)
from agent_framework.config import (
    EscalationRule,
    GuardrailConfig,
    TokenBudget,
)
from agent_framework.enums import EscalationReason


# ── Test Agent Implementation ────────────────────────────────────────


class MockHealthcareAgent(BaseAgent):
    """A mock Healthcare Clinical AI agent for testing."""

    async def plan(self, context: AgentContext) -> dict:
        return {
            "steps": [
                "Check IP Registry for NABH templates",
                "Analyze client requirements",
                "Generate gap analysis report",
            ]
        }

    async def execute(self, context: AgentContext) -> AgentResult:
        return SuccessResult(
            output={
                "deliverable_text": "NABH Gap Analysis Report: 15 gaps identified.",
                "gaps_found": 15,
            },
            confidence=0.88,
            sources_cited=["NABH_4th_edition", "NMC_Act_2020"],
            tokens_used=2500,
        )


class MockLegalAgent(BaseAgent):
    """A mock Legal agent that tests mandatory disclaimer injection."""

    async def plan(self, context: AgentContext) -> dict:
        return {"steps": ["Analyze contract", "Generate review"]}

    async def execute(self, context: AgentContext) -> AgentResult:
        return SuccessResult(
            output={
                "deliverable_text": "Contract review findings: 3 risk clauses identified.",
            },
            confidence=0.82,
            sources_cited=["Companies_Act_2013"],
            tokens_used=1800,
        )


class MockFailingAgent(BaseAgent):
    """A mock agent that raises an error during execution."""

    async def plan(self, context: AgentContext) -> dict:
        return {"steps": ["Will fail"]}

    async def execute(self, context: AgentContext) -> AgentResult:
        raise RuntimeError("Simulated agent failure")


# ── Tests ────────────────────────────────────────────────────────────


class TestAgentConfig:
    """Test agent configuration validation."""

    def test_valid_config(self):
        config = AgentConfig(
            agent_id="healthcare-clinical-ai",
            name="Clinical AI Agent",
            tier=AgentTier.DOMAIN_SPECIALIST,
            vertical=Vertical.HEALTHCARE,
            reasoning_mode=ReasoningMode.REACT,
            description="Designs CDSS architectures.",
        )
        assert config.agent_id == "healthcare-clinical-ai"
        assert config.tier == AgentTier.DOMAIN_SPECIALIST
        assert config.reasoning_mode == ReasoningMode.REACT

    def test_invalid_agent_id_rejected(self):
        with pytest.raises(Exception):
            AgentConfig(
                agent_id="Invalid ID!",  # Invalid: uppercase + spaces
                name="Test",
                tier=AgentTier.DOMAIN_SPECIALIST,
                vertical=Vertical.ALL,
                reasoning_mode=ReasoningMode.REACT,
            )

    def test_token_budget_defaults(self):
        config = AgentConfig(
            agent_id="test-agent",
            name="Test",
            tier=AgentTier.DOMAIN_SPECIALIST,
            vertical=Vertical.ALL,
            reasoning_mode=ReasoningMode.REACT,
        )
        assert config.token_budget.max_tokens_per_task == 8_000
        assert config.token_budget.overage_threshold_pct == 0.80

    def test_guardrails_defaults(self):
        config = AgentConfig(
            agent_id="test-agent",
            name="Test",
            tier=AgentTier.DOMAIN_SPECIALIST,
            vertical=Vertical.ALL,
            reasoning_mode=ReasoningMode.REACT,
        )
        assert config.guardrails.pii_detection_enabled is True
        assert config.guardrails.require_kb_validity_check is True
        assert config.guardrails.max_confidence_without_source == 0.5


class TestAgentLifecycle:
    """Test the BaseAgent lifecycle and state machine."""

    @pytest.fixture
    def healthcare_config(self) -> AgentConfig:
        return AgentConfig(
            agent_id="healthcare-clinical-ai",
            name="Clinical AI Agent",
            tier=AgentTier.DOMAIN_SPECIALIST,
            vertical=Vertical.HEALTHCARE,
            reasoning_mode=ReasoningMode.PLAN_AND_EXECUTE,
        )

    @pytest.fixture
    def legal_config(self) -> AgentConfig:
        return AgentConfig(
            agent_id="legal-contract-analysis",
            name="Contract Analysis Agent",
            tier=AgentTier.DOMAIN_SPECIALIST,
            vertical=Vertical.LEGAL,
            reasoning_mode=ReasoningMode.PLAN_AND_EXECUTE,
            guardrails=GuardrailConfig(
                mandatory_disclaimer=(
                    "DISCLAIMER: This analysis is for informational purposes only "
                    "and does not constitute legal advice."
                ),
            ),
        )

    @pytest.fixture
    def task(self) -> TaskContext:
        return TaskContext(
            task_type="nabh_gap_analysis",
            description="Perform NABH gap analysis for Apollo Hospital",
            vertical="healthcare",
            priority=3,
        )

    @pytest.mark.asyncio
    async def test_successful_execution(self, healthcare_config, task):
        agent = MockHealthcareAgent(healthcare_config)
        agent.init()

        result = await agent.run(task)

        assert isinstance(result, SuccessResult)
        assert result.confidence == 0.88
        assert "NABH Gap Analysis" in result.output["deliverable_text"]
        assert agent.state == AgentState.COMPLETE

    @pytest.mark.asyncio
    async def test_mandatory_disclaimer_appended(self, legal_config, task):
        agent = MockLegalAgent(legal_config)
        agent.init()

        result = await agent.run(task)

        assert isinstance(result, SuccessResult)
        assert "DISCLAIMER" in result.output["deliverable_text"]
        assert agent.state == AgentState.COMPLETE

    @pytest.mark.asyncio
    async def test_error_handling(self, healthcare_config, task):
        agent = MockFailingAgent(healthcare_config)
        agent.init()

        result = await agent.run(task)

        assert isinstance(result, ErrorResult)
        assert "Simulated agent failure" in result.error
        assert agent.state == AgentState.ERROR

    @pytest.mark.asyncio
    async def test_confidence_capped_without_sources(self, healthcare_config, task):
        """When no sources are cited, confidence should be capped at 0.5."""

        class NoSourceAgent(BaseAgent):
            async def plan(self, ctx):
                return {}

            async def execute(self, ctx):
                return SuccessResult(
                    output={"deliverable_text": "Some output"},
                    confidence=0.95,
                    sources_cited=[],  # No sources
                )

        agent = NoSourceAgent(healthcare_config)
        result = await agent.run(task)

        assert isinstance(result, SuccessResult)
        assert result.confidence == 0.5  # Capped by guardrail


class TestTaskContext:
    """Test task context creation and management."""

    def test_task_context_defaults(self):
        ctx = TaskContext(task_type="test")
        assert ctx.priority == 5
        assert ctx.depends_on == []
        assert ctx.task_id  # Auto-generated UUID

    def test_agent_context_working_memory(self):
        ctx = AgentContext(
            agent_id="test",
            task=TaskContext(task_type="test"),
        )
        ctx.update_working_memory("key1", "value1")
        assert ctx.working_memory["key1"] == "value1"

    def test_agent_context_token_tracking(self):
        ctx = AgentContext(
            agent_id="test",
            task=TaskContext(task_type="test"),
            token_budget_remaining=8000,
        )
        ctx.track_tokens(2000)
        assert ctx.tokens_used == 2000
        assert ctx.token_budget_remaining == 6000


class TestEnums:
    """Test all system enumerations."""

    def test_agent_states(self):
        assert AgentState.IDLE.value == "idle"
        assert AgentState.COMPLETE.value == "complete"
        assert AgentState.ESCALATED.value == "escalated"

    def test_verticals(self):
        assert len(Vertical) == 5  # all, healthcare, logistics, legal, edtech

    def test_agent_tiers(self):
        assert AgentTier.ORCHESTRATION.value == "tier_0"
        assert AgentTier.DOMAIN_SPECIALIST.value == "tier_4"
