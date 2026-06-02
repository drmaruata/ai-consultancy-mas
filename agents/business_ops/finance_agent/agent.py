"""Finance Agent."""

import uuid
from datetime import UTC, datetime
from typing import Any

from agent_framework.base import (
    AgentResult,
    BaseAgent,
    EscalationResult,
    SuccessResult,
)
from agent_framework.context import AgentContext
from agent_framework.enums import EscalationReason


class FinanceAgent(BaseAgent):
    """Layer 1 Agent: Handles pricing and invoicing."""

    async def plan(self, context: AgentContext) -> dict[str, Any]:
        """Plan the execution for the current task."""
        self._log.info("planning_finance_task", task_type=context.task.task_type)
        if context.task.task_type == "generate_pricing_and_invoice":
            return {
                "steps": [
                    {"step": 1, "action": "calculate_pricing", "description": "Apply dynamic pricing engine rules"},
                    {"step": 2, "action": "check_threshold", "description": "Escalate if price > 2.5x base rate"},
                    {"step": 3, "action": "generate_invoice", "description": "Output structured Markdown/HTML invoice"},
                ]
            }
        return {"steps": []}

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the Finance task."""
        task_type = context.task.task_type
        if task_type == "generate_pricing_and_invoice":
            return await self._process_pricing_and_invoice(context)
        else:
            return EscalationResult(
                reason=EscalationReason.UNKNOWN_TASK_TYPE,
                description=f"Unknown Finance task type: {task_type}"
            )

    async def _process_pricing_and_invoice(self, context: AgentContext) -> AgentResult:
        """Calculates dynamic pricing and generates invoice."""
        payload = context.task.input_data
        lead_data = payload.get("lead", {})
        complexity = payload.get("complexity", 1.0)

        # 1. Calculate Pricing
        base_rate = 10000.0  # Base standard rate
        urgency_factor = 1.5 if lead_data.get("urgency", "low").lower() == "high" else 1.0
        geography_factor = 1.2 if lead_data.get("region", "US") == "US" else 1.0
        competitive_discount = 0.95
        client_tier_factor = 1.0

        final_price = base_rate * complexity * urgency_factor * geography_factor * competitive_discount * client_tier_factor

        # 2. Check threshold for escalation
        if final_price > (base_rate * 2.5):
            return EscalationResult(
                reason=EscalationReason.PRICING_ANOMALY,
                description=f"Computed price (${final_price:,.2f}) exceeds 2.5x base rate (${base_rate:,.2f}). Human review required."
            )

        # 3. Generate Invoice (Markdown)
        invoice_id = f"INV-{str(uuid.uuid4())[:8].upper()}"
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")

        invoice_md = f"""# INVOICE {invoice_id}
**Date:** {date_str}
**Client:** {lead_data.get("company_name", "Valued Client")}

## Services Provided
- AI Consultancy & Architecture Integration

## Pricing Breakdown
| Item | Amount |
|------|--------|
| Base Services | ${base_rate:,.2f} |
| Complexity & Tier Adjustments | ${(final_price - base_rate):,.2f} |
| **Total Due** | **${final_price:,.2f}** |

*Payment due within 30 days.*
"""

        return SuccessResult(
            output={
                "invoice_id": invoice_id,
                "final_price": final_price,
                "invoice_markdown": invoice_md,
            },
            confidence=0.95,
        )
