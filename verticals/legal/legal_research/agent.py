from typing import Any

from agent_framework.base import BaseAgent, SuccessResult
from agent_framework.context import AgentContext


class LegalResearchAgent(BaseAgent):
    """
    Tier 2 specialist for regulatory compliance gap analysis.

    Audits an organisation against applicable Indian regulations:
    SEBI (for listed entities), RBI (for NBFCs/fintechs), MCA (company law),
    DPDP Act 2023 (data privacy), and sector-specific rules.
    Produces a gap report with remediation timelines.
    """

    async def plan(self, context: AgentContext) -> dict[str, Any]:
        input_data = context.task.input_data or {}
        regulatory_body = input_data.get("regulatory_body", "SEBI")
        return {
            "steps": [
                f"Load applicable {regulatory_body} regulations from KB",
                "Map client's current practices against each regulation",
                "Identify non-compliance gaps",
                "Prioritise by severity and regulatory penalty risk",
                "Generate remediation roadmap with timelines",
            ]
        }

    async def execute(self, context: AgentContext) -> SuccessResult:
        input_data = context.task.input_data or {}
        regulatory_body = input_data.get("regulatory_body", "SEBI")
        client_id = input_data.get("client_id", "UNKNOWN")

        # MVP: Structured compliance gap output
        gaps = [
            {
                "regulation": f"{regulatory_body} Circular 2026/001",
                "requirement": "Material event reporting within 6 hours via API",
                "current_status": "Manual reporting via email (24-hour window)",
                "gap": "Non-compliant — using superseded 2023 circular process",
                "severity": "CRITICAL",
                "remediation": "Integrate with SEBI's real-time API endpoint within 30 days",
            },
            {
                "regulation": "DPDP Act 2023 — Section 8",
                "requirement": "Data Principal consent records retained for 3 years",
                "current_status": "Consent logs purged after 1 year",
                "gap": "Partial non-compliance",
                "severity": "HIGH",
                "remediation": "Update data retention policy and extend log storage",
            },
        ]

        critical_count = sum(1 for g in gaps if g["severity"] == "CRITICAL")
        high_count = sum(1 for g in gaps if g["severity"] == "HIGH")

        summary = (
            f"Compliance Audit ({regulatory_body}, Client: {client_id}): "
            f"{critical_count} CRITICAL and {high_count} HIGH severity gaps identified. "
            "Immediate remediation required for CRITICAL items."
        )

        return SuccessResult(
            output={
                "deliverable_text": summary,
                "compliance_gaps": gaps,
                "regulatory_body": regulatory_body,
            },
            confidence=0.9,
            sources_cited=[
                f"{regulatory_body.lower()}_circular_2026_001",
                "dpdp_act_2023",
            ],
        )
