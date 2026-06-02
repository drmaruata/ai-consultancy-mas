"""Sales Agent."""

from typing import Any

from agent_framework.base import (
    AgentResult,
    BaseAgent,
    EscalationResult,
    SuccessResult,
)
from agent_framework.context import AgentContext
from agent_framework.enums import EscalationReason


class SalesAgent(BaseAgent):
    """Layer 1 Agent: Handles lead qualification and proposal generation."""

    async def plan(self, context: AgentContext) -> dict[str, Any]:
        """Plan the execution for the current task."""
        self._log.info("planning_sales_task", task_type=context.task.task_type)
        if context.task.task_type == "process_inbound_lead":
            return {
                "steps": [
                    {"step": 1, "action": "qualify_lead", "description": "Score lead based on vertical, budget, and urgency"},
                    {"step": 2, "action": "generate_proposal", "description": "Draft proposal based on IP registry assets"},
                    {"step": 3, "action": "handoff_finance", "description": "Send proposal to Finance Agent for pricing validation"},
                ]
            }
        return {"steps": []}

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the Sales task."""
        task_type = context.task.task_type
        if task_type == "process_inbound_lead":
            return await self._process_lead(context)
        else:
            return EscalationResult(
                reason=EscalationReason.UNKNOWN_TASK_TYPE,
                description=f"Unknown Sales task type: {task_type}"
            )

    async def _process_lead(self, context: AgentContext) -> AgentResult:
        """Qualifies lead and generates proposal."""
        lead_data = context.task.input_data.get("lead", {})

        # 1. Qualify Lead
        score = self._qualify_lead(lead_data)
        if score < 50:
            return EscalationResult(
                reason=EscalationReason.TASK_FAILED,
                description=f"Lead unqualified. Score: {score}. Reason: Low budget or poor fit."
            )

        # 2. Generate Proposal
        proposal_content = f"# Proposal for {lead_data.get('company_name', 'Client')}\n\n"
        proposal_content += "Based on your needs in the Healthcare vertical, we propose a strategic AI integration plan.\n"

        # 3. Handoff to Finance (In a full MAS, this sends a message to the Finance Agent)
        # For Sprint 1.1, we output the proposal and the qualification score.

        return SuccessResult(
            output={
                "qualification_score": score,
                "status": "qualified",
                "proposal_markdown": proposal_content,
                "next_step": "finance_pricing_validation",
                "finance_payload": {
                    "lead": lead_data,
                    "complexity": 1.5 if score > 80 else 1.0,
                }
            },
            confidence=0.9,
        )

    def _qualify_lead(self, lead_data: dict[str, Any]) -> int:
        """Simple lead scoring heuristic for Sprint 1.1."""
        score = 0
        if lead_data.get("vertical", "").lower() == "healthcare":
            score += 40

        budget = lead_data.get("budget", 0)
        if budget > 100000:
            score += 40
        elif budget > 50000:
            score += 20

        urgency = lead_data.get("urgency", "low").lower()
        if urgency == "high":
            score += 20

        return score
