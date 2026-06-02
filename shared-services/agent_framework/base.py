"""Base Agent class — the foundation for all 43 agents in the MAS.

Every agent inherits from BaseAgent and implements the abstract lifecycle
methods. The base class handles state management, guardrail enforcement,
token budget tracking, escalation logic, and audit logging.

Architecture:
    Plan-and-Execute (Tier 0–3):
        Phase 0: IP Registry Check → Plan → Execute → Reflect
    ReAct (Tier 4):
        Reason → Act → Observe → loop until done
"""

from __future__ import annotations

import abc
import re
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from agent_framework.config import AgentConfig
from agent_framework.context import AgentContext, TaskContext
from agent_framework.enums import (
    AgentState,
    EscalationReason,
    ReasoningMode,
)

logger = structlog.get_logger()


class AgentResult(abc.ABC):
    """Base class for agent execution results."""
    pass


class SuccessResult(AgentResult):
    """Successful task completion."""

    def __init__(
        self,
        output: dict[str, Any],
        confidence: float,
        sources_cited: list[str] | None = None,
        ip_assets_used: list[str] | None = None,
        tokens_used: int = 0,
    ) -> None:
        self.output = output
        self.confidence = confidence
        self.sources_cited = sources_cited or []
        self.ip_assets_used = ip_assets_used or []
        self.tokens_used = tokens_used


class EscalationResult(AgentResult):
    """Task requires human oversight escalation."""

    def __init__(
        self,
        reason: EscalationReason,
        description: str,
        partial_output: dict[str, Any] | None = None,
    ) -> None:
        self.reason = reason
        self.description = description
        self.partial_output = partial_output or {}


class ErrorResult(AgentResult):
    """Task failed with an error."""

    def __init__(self, error: str, recoverable: bool = False) -> None:
        self.error = error
        self.recoverable = recoverable


class BaseAgent(abc.ABC):
    """Abstract base class for all MAS agents.

    Lifecycle:
        1. `init()` — One-time setup (load system prompt, register tools)
        2. `run(task)` — Main entry point, manages the full lifecycle
            a. Phase 0: IP Registry check (Plan-and-Execute only)
            b. `plan(context)` — Generate execution plan
            c. `execute(context)` — Carry out the plan
            d. `reflect(context, result)` — Self-evaluate quality
            e. Guardrail checks (PII, disclaimers, blocked patterns)
        3. Result is either SuccessResult, EscalationResult, or ErrorResult

    Subclasses MUST implement:
        - `plan(context) -> dict`
        - `execute(context) -> AgentResult`

    Subclasses MAY override:
        - `init()` for custom setup
        - `reflect(context, result)` for custom self-evaluation
        - `check_ip_registry(context)` for custom IP lookups
    """

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.state = AgentState.IDLE
        self._log = logger.bind(
            agent_id=config.agent_id,
            agent_name=config.name,
            tier=config.tier.value,
            vertical=config.vertical.value,
        )

    # ── Lifecycle Hooks ──────────────────────────────────────────────

    def init(self) -> None:
        """One-time initialization. Override for custom setup (e.g. loading tools)."""
        self._log.info("agent_initialized")

    async def run(self, task: TaskContext) -> AgentResult:
        """Main entry point — runs the full agent lifecycle for a task.

        This method manages the state machine, guardrail checks, token
        budget enforcement, and audit logging. Subclasses should NOT
        override this method — implement `plan()` and `execute()` instead.
        """
        execution_id = str(uuid.uuid4())
        started_at = datetime.now(UTC)

        context = AgentContext(
            agent_id=self.config.agent_id,
            task=task,
            token_budget_remaining=self.config.token_budget.max_tokens_per_task,
        )

        self._log.info(
            "task_started",
            execution_id=execution_id,
            task_id=task.task_id,
            task_type=task.task_type,
        )

        try:
            # ── Phase 0: IP Registry Check (Plan-and-Execute only) ───
            if self.config.reasoning_mode == ReasoningMode.PLAN_AND_EXECUTE:
                self.state = AgentState.PLANNING
                if self.config.ip_registry_check_enabled:
                    ip_matches = await self.check_ip_registry(context)
                    context.ip_assets = ip_matches
                    if ip_matches:
                        self._log.info(
                            "ip_registry_hits",
                            count=len(ip_matches),
                            asset_ids=[a.get("id") for a in ip_matches],
                        )

            # ── KB Validity Pre-check ────────────────────────────────
            if self.config.guardrails.require_kb_validity_check:
                await self._preload_kb_documents(context)

            # ── Planning ─────────────────────────────────────────────
            self.state = AgentState.PLANNING
            plan = await self.plan(context)
            context.update_working_memory("plan", plan)
            self._log.info("plan_generated", plan_summary=str(plan)[:200])

            # ── Execution ────────────────────────────────────────────
            self.state = AgentState.EXECUTING
            result = await self.execute(context)

            # ── Token budget check ───────────────────────────────────
            if isinstance(result, SuccessResult):
                self._check_token_budget(context, result)

            # ── Guardrail enforcement ────────────────────────────────
            if isinstance(result, SuccessResult):
                result = await self._enforce_guardrails(result)

            # ── Reflection ───────────────────────────────────────────
            self.state = AgentState.REFLECTING
            reflection = await self.reflect(context, result)
            self._log.info("reflection_complete", reflection=str(reflection)[:200])

            # ── Reporting ────────────────────────────────────────────
            if isinstance(result, SuccessResult):
                result = await self.report(context, result)

            # ── Set final state ──────────────────────────────────────
            if isinstance(result, SuccessResult):
                self.state = AgentState.COMPLETE
            elif isinstance(result, EscalationResult):
                self.state = AgentState.ESCALATED
            else:
                self.state = AgentState.ERROR

            return result

        except Exception as e:
            self.state = AgentState.ERROR
            self._log.error("agent_execution_failed", error=str(e), exc_info=True)
            return ErrorResult(error=str(e), recoverable=False)

        finally:
            elapsed_ms = int(
                (datetime.now(UTC) - started_at).total_seconds() * 1000
            )
            self._log.info(
                "task_completed",
                execution_id=execution_id,
                task_id=task.task_id,
                final_state=self.state.value,
                elapsed_ms=elapsed_ms,
                tokens_used=context.tokens_used,
            )
            # Audit log entry (to be persisted to Supabase by the messaging layer)
            await self._emit_audit_log(execution_id, task, context, elapsed_ms)

    # ── Abstract Methods (subclasses MUST implement) ─────────────────

    @abc.abstractmethod
    async def plan(self, context: AgentContext) -> dict[str, Any]:
        """Generate an execution plan for the current task.

        For Plan-and-Execute agents: returns a structured plan with steps.
        For ReAct agents: returns the initial reasoning about the task.

        Returns:
            A dictionary containing the plan or initial reasoning.
        """

    @abc.abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the task according to the plan.

        This is where the core agent logic lives — LLM calls, tool usage,
        data processing, and deliverable generation.

        Returns:
            SuccessResult, EscalationResult, or ErrorResult.
        """

    # ── Optional Overrides ───────────────────────────────────────────

    async def reflect(
        self, context: AgentContext, result: AgentResult
    ) -> dict[str, Any]:
        """Self-evaluate the quality of the execution result.

        Default implementation logs basic metrics. Override for
        custom quality scoring, improvement suggestions, etc.

        Returns:
            A dictionary with reflection metadata (quality score, notes).
        """
        reflection: dict[str, Any] = {
            "agent_id": self.config.agent_id,
            "task_id": context.task.task_id,
            "result_type": type(result).__name__,
            "tokens_used": context.tokens_used,
        }
        if isinstance(result, SuccessResult):
            reflection["confidence"] = result.confidence
            reflection["sources_count"] = len(result.sources_cited)
        return reflection

    async def report(self, context: AgentContext, result: SuccessResult) -> SuccessResult:
        """Final output generation hook.
        
        Applies strict vertical-specific formatting and disclaimers.
        """
        from agent_framework.enums import Vertical
        
        if self.config.vertical == Vertical.LEGAL:
            disclaimer = "MANDATORY DISCLAIMER: This AI-generated analysis is not legal advice and should not be relied upon as such. Always consult a qualified attorney before taking any legal action."
            
            if "deliverable_text" in result.output:
                result.output["deliverable_text"] += f"\n\n---\n{disclaimer}"
            elif "deliverable" in result.output:
                result.output["deliverable"] += f"\n\n---\n{disclaimer}"
            else:
                # Fallback: inject into the first string field found
                for k, v in result.output.items():
                    if isinstance(v, str):
                        result.output[k] += f"\n\n---\n{disclaimer}"
                        break

        return result

    async def check_ip_registry(
        self, context: AgentContext
    ) -> list[dict[str, Any]]:
        """Look up matching IP assets for the current task.

        Default implementation returns empty list. Override to integrate
        with the actual IP Registry service.

        Returns:
            List of matching IP asset records.
        """
        # TODO: Integrate with IP Registry service in Sprint 0.2
        return []

    # ── Internal Methods ─────────────────────────────────────────────

    async def _preload_kb_documents(self, context: AgentContext) -> None:
        """Retrieve relevant KB documents and check validity scores.

        Documents below the 0.7 confidence threshold will cap the
        agent's output confidence, preventing hallucination of stale data.
        """
        # TODO: Integrate with Memory/KB service in Sprint 0.2
        self._log.debug("kb_preload_skipped", reason="not_yet_integrated")

    def _check_token_budget(
        self, context: AgentContext, result: SuccessResult
    ) -> None:
        """Verify token usage against budget thresholds."""
        budget = self.config.token_budget
        usage_pct = context.tokens_used / budget.max_tokens_per_task

        if usage_pct >= budget.hard_cap_pct:
            self._log.warning(
                "token_budget_hard_cap_exceeded",
                tokens_used=context.tokens_used,
                budget=budget.max_tokens_per_task,
                usage_pct=round(usage_pct, 2),
            )
        elif usage_pct >= budget.overage_threshold_pct:
            self._log.warning(
                "token_budget_throttle_threshold",
                tokens_used=context.tokens_used,
                budget=budget.max_tokens_per_task,
                usage_pct=round(usage_pct, 2),
            )

    async def _enforce_guardrails(self, result: SuccessResult) -> AgentResult:
        """Apply all configured guardrails to the output.

        Checks:
            1. Blocked output patterns (regex)
            2. Mandatory disclaimers (Legal vertical)
            3. Confidence cap when no sources cited
            4. PII detection (stub — to be integrated)
        """
        guardrails = self.config.guardrails
        output_text = str(result.output)

        # 1. Check blocked patterns
        for pattern in guardrails.blocked_output_patterns:
            if re.search(pattern, output_text):
                self._log.warning(
                    "guardrail_blocked_pattern_matched",
                    pattern=pattern,
                )
                return EscalationResult(
                    reason=EscalationReason.LOW_CONFIDENCE,
                    description=f"Output matched blocked pattern: {pattern}",
                    partial_output=result.output,
                )

        # 2. Append mandatory disclaimer
        if guardrails.mandatory_disclaimer:
            if "deliverable_text" in result.output:
                result.output["deliverable_text"] += (
                    f"\n\n---\n{guardrails.mandatory_disclaimer}"
                )

        # 3. Cap confidence when no sources cited
        if not result.sources_cited:
            max_conf = guardrails.max_confidence_without_source
            if result.confidence > max_conf:
                self._log.info(
                    "confidence_capped_no_sources",
                    original=result.confidence,
                    capped_to=max_conf,
                )
                result.confidence = max_conf

        # 4. PII detection (stub)
        if guardrails.pii_detection_enabled:
            # TODO: Integrate with anonymizer pipeline in Sprint 0.2
            pass

        return result

    async def _emit_audit_log(
        self,
        execution_id: str,
        task: TaskContext,
        context: AgentContext,
        elapsed_ms: int,
    ) -> None:
        """Publish an audit log entry for this execution.

        Will be persisted to the `audit_log` table in Supabase
        via the messaging layer.
        """
        # TODO: Publish to Kafka `audit.log` topic in Sprint 0.1
        self._log.debug(
            "audit_log_entry",
            execution_id=execution_id,
            task_id=task.task_id,
            agent_id=self.config.agent_id,
            state=self.state.value,
            tokens_used=context.tokens_used,
            elapsed_ms=elapsed_ms,
        )
