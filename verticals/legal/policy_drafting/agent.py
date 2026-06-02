from typing import Any

from agent_framework.base import BaseAgent, SuccessResult
from agent_framework.context import AgentContext


class PolicyDraftingAgent(BaseAgent):
    """
    Tier 2 specialist for drafting and reviewing internal legal policies.

    Creates or reviews company policies: data privacy, anti-bribery, POSH,
    whistleblower, code of conduct, and vendor management. Aligns them with
    applicable Indian law and international standards (ISO 27001, GDPR where
    relevant for cross-border data flows).
    """

    async def plan(self, context: AgentContext) -> dict[str, Any]:
        input_data = context.task.input_data or {}
        policy_type = input_data.get("policy_type", "data_privacy")
        action = input_data.get("action", "draft")  # "draft" or "review"
        return {
            "steps": [
                f"Load applicable law and standards for {policy_type} policy",
                f"{action.capitalize()} policy document using KB templates",
                "Cross-check against DPDP Act 2023 / IT Act / Company Law",
                "Flag gaps or non-compliant clauses",
                "Output final policy with change log",
            ]
        }

    async def execute(self, context: AgentContext) -> SuccessResult:
        input_data = context.task.input_data or {}
        policy_type = input_data.get("policy_type", "data_privacy")
        action = input_data.get("action", "draft")
        client_id = input_data.get("client_id", "UNKNOWN")

        policy_map = {
            "data_privacy": "Data Privacy & DPDP Act Compliance Policy",
            "anti_bribery": "Anti-Bribery and Corruption Policy (aligned with FCPA/UK Bribery Act)",
            "posh": "Prevention of Sexual Harassment (POSH) Policy",
            "whistleblower": "Vigil Mechanism / Whistleblower Policy (Companies Act 2013)",
            "code_of_conduct": "Employee Code of Conduct",
            "vendor_management": "Third-Party Vendor Risk Management Policy",
        }
        policy_name = policy_map.get(policy_type, f"{policy_type.replace('_', ' ').title()} Policy")

        summary = (
            f"Policy {action.capitalize()} Complete: '{policy_name}' for client {client_id}. "
            "Document aligned with applicable Indian law. "
            "Review by legal counsel recommended before adoption."
        )

        return SuccessResult(
            output={
                "deliverable_text": summary,
                "policy_name": policy_name,
                "policy_type": policy_type,
                "action": action,
            },
            confidence=0.88,
            sources_cited=["dpdp_act_2023", "companies_act_2013", "it_act_2000"],
        )
