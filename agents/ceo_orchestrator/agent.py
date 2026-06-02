"""CEO Orchestrator Agent (Layer 0)."""

from typing import Any

from agent_framework.base import (
    AgentResult,
    BaseAgent,
    EscalationResult,
    SuccessResult,
)
from agent_framework.context import AgentContext
from agent_framework.enums import EscalationReason
from messaging.producer import MessageProducer
from messaging.schemas import MASMessage


class TaskAssignedMessage(MASMessage):
    """Message payload for task.assigned."""
    topic: str = "task.assigned"
    target_agent_id: str
    task_id: str
    vertical: str
    task_type: str


class CEOOrchestratorAgent(BaseAgent):
    """Layer 0 Agent: Coordinates execution across the entire MAS."""

    def __init__(self, agent_id: str, producer: MessageProducer | None = None) -> None:
        super().__init__(agent_id=agent_id)
        self._producer = producer

    async def plan(self, context: AgentContext) -> dict[str, Any]:
        """Plan the execution for the current task."""
        self._log.info("planning_task", task_type=context.task.task_type)
        if context.task.task_type == "generate_weekly_report":
            return {
                "steps": [
                    {"step": 1, "action": "gather_metrics", "description": "Fetch revenue, CHS, and KB health"},
                    {"step": 2, "action": "synthesize_report", "description": "Format Weekly MAS Health Report"},
                ]
            }
        return {"steps": [{"step": 1, "action": "route_request"}]}

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the CEO task."""
        task_type = context.task.task_type
        if task_type == "generate_weekly_report":
            return await self._generate_health_report(context)
        elif task_type == "route_client_request":
            return await self.route_task(context)
        else:
            return EscalationResult(
                reason=EscalationReason.UNKNOWN_TASK_TYPE,
                description=f"Unknown CEO task type: {task_type}"
            )

    async def route_task(self, context: AgentContext) -> AgentResult:
        """Route task and publish to task.assigned topic."""
        # Stub logic for routing
        target_agent = "healthcare-vertical-manager"
        vertical = "healthcare"
        
        if self._producer:
            msg = TaskAssignedMessage(
                source_agent_id=self.agent_id,
                target_agent_id=target_agent,
                task_id=context.task.id,
                vertical=vertical,
                task_type="route_client_request"
            )
            try:
                await self._producer.publish("task.assigned", msg)
                self._log.info("task_routed", target=target_agent, task_id=context.task.id)
            except Exception as e:
                return EscalationResult(
                    reason=EscalationReason.SYSTEM_ERROR,
                    description=f"Failed to publish routed task: {e}"
                )
                
        return SuccessResult(output={"routed_to": target_agent}, confidence=0.95)

    async def _generate_health_report(self, context: AgentContext) -> SuccessResult:
        """Generates the weekly MAS health report."""
        # TODO: Integrate with LLM Router and Memory to fetch real metrics in Phase 4
        mock_report = """# Weekly MAS Health Report
        
## Revenue Snapshot
- MTD: $120,000
- Active Engagements: 4

## Client Health
- 1 Client requires Account Growth intervention (CHS < 65)

## KB Health
- 0 Documents below confidence threshold
"""
        return SuccessResult(
            output={"report_markdown": mock_report},
            confidence=0.99,
        )
