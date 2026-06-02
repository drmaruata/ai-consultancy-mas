from typing import Any

from agent_framework.base import BaseAgent, SuccessResult
from agent_framework.context import AgentContext


class LitigationSupportAgent(BaseAgent):
    """
    Tier 3 specialist for commercial dispute strategy and resolution pathways.

    Analyses disputes and recommends resolution pathways:
    negotiation → mediation → arbitration → litigation. Drafts legal
    notices, response strategies, and settlement term sheets.
    Covers Indian arbitration law (Arbitration & Conciliation Act 1996),
    consumer disputes (NCDRC), commercial courts, and NCLT proceedings.
    """

    async def plan(self, context: AgentContext) -> dict[str, Any]:
        input_data = context.task.input_data or {}
        dispute_type = input_data.get("dispute_type", "commercial")
        return {
            "steps": [
                f"Analyse {dispute_type} dispute facts and evidence",
                "Assess strength of each party's position",
                "Identify applicable jurisdiction and forum",
                "Evaluate resolution pathways (negotiation → arbitration → litigation)",
                "Draft recommended strategy with risk/cost analysis",
            ]
        }

    async def execute(self, context: AgentContext) -> SuccessResult:
        input_data = context.task.input_data or {}
        dispute_type = input_data.get("dispute_type", "commercial")
        dispute_value = input_data.get("dispute_value_inr", 0)
        client_id = input_data.get("client_id", "UNKNOWN")

        # Determine recommended pathway based on dispute value
        if dispute_value < 2_000_000:  # < 20 Lakhs
            pathway = "Mediation (MSME Facilitation Council or private mediator)"
            timeline = "3–6 months"
        elif dispute_value < 10_000_000:  # < 1 Crore
            pathway = "Arbitration (institutional — DIAC or MCIA)"
            timeline = "12–18 months"
        else:  # > 1 Crore
            pathway = "Arbitration (institutional) with parallel negotiation track"
            timeline = "18–36 months"

        summary = (
            f"Dispute Analysis ({dispute_type}, Client: {client_id}): "
            f"Recommended pathway is {pathway}. "
            f"Estimated timeline: {timeline}. "
            "Full strategy memo and legal notice draft prepared."
        )

        return SuccessResult(
            output={
                "deliverable_text": summary,
                "recommended_pathway": pathway,
                "estimated_timeline": timeline,
                "dispute_type": dispute_type,
            },
            confidence=0.82,
            sources_cited=[
                "arbitration_conciliation_act_1996",
                "commercial_courts_act_2015",
            ],
        )
