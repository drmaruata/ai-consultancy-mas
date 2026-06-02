from typing import Any

from agent_framework.base import BaseAgent, SuccessResult
from agent_framework.context import AgentContext


class HealthcareVerticalManager(BaseAgent):
    async def plan(self, context: AgentContext) -> dict[str, Any]:
        return {"steps": ["mock_step_1"]}

    async def execute(self, context: AgentContext) -> SuccessResult:
        # MVP: Return a static successful output
        return SuccessResult(
            output={"status": "completed", "deliverable": "Decomposes healthcare projects into DAGs."},
            confidence=0.9
        )
