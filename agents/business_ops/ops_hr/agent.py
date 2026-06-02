from typing import Any

from agent_framework.base import BaseAgent, SuccessResult
from agent_framework.context import AgentContext


class OpsHrAgent(BaseAgent):
    async def plan(self, context: AgentContext) -> dict[str, Any]:
        return {"steps": ["analyze_client_data", "generate_proposal"]}

    async def execute(self, context: AgentContext) -> SuccessResult:
        return SuccessResult(
            output={"status": "completed", "deliverable": "Calculates CHS and manages vendor SLAs."},
            confidence=0.9
        )
