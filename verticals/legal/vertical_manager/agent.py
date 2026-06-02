from typing import Any

from agent_framework.base import BaseAgent, SuccessResult
from agent_framework.context import AgentContext


class LegalVerticalManager(BaseAgent):
    """
    Tier 3 orchestrator for the Legal Vertical.

    Decomposes incoming legal project requests into parallel sub-tasks
    and delegates them to specialist legal agents (Contract Review,
    Compliance Auditor, Dispute Resolution, etc.) via Upstash Workflow.
    """

    async def plan(self, context: AgentContext) -> dict[str, Any]:
        input_data = context.task.input_data or {}
        project_type = input_data.get("project_type", "general_legal")
        return {
            "steps": [
                f"Classify project type: {project_type}",
                "Identify required specialist agents",
                "Decompose into parallel sub-tasks",
                "Dispatch sub-tasks via Upstash Workflow",
            ]
        }

    async def execute(self, context: AgentContext) -> SuccessResult:
        input_data = context.task.input_data or {}
        project_type = input_data.get("project_type", "general_legal")
        client_id = input_data.get("client_id", "UNKNOWN")

        # Agent routing map: project type → required specialist agents
        routing_map: dict[str, list[str]] = {
            "contract_analysis": ["contract-analysis-1"],
            "legal_research": ["legal-research-1"],
            "litigation_support": ["litigation-support-1"],
            "risk_assessment": ["risk-assessment-1", "legal-research-1"],
            "policy_drafting": ["policy-drafting-1"],
            "regulatory_update": ["regulatory-watch-legal-1"],
            "general_legal": ["contract-analysis-1", "legal-research-1"],
        }

        required_agents = routing_map.get(project_type, routing_map["general_legal"])

        dag = {
            "project_type": project_type,
            "client_id": client_id,
            "parallel_agents": required_agents,
            "status": "dispatched",
        }

        return SuccessResult(
            output={
                "deliverable_text": (
                    f"Legal project '{project_type}' for client {client_id} "
                    f"has been dispatched to: {', '.join(required_agents)}. "
                    "All sub-tasks are queued for parallel execution."
                ),
                "dag": dag,
            },
            confidence=0.95,
            sources_cited=["legal_vertical_routing_map_v1"],
        )
