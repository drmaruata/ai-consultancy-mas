"""CEO Weekly Report Upstash Workflow.

This is a serverless workflow endpoint utilizing Upstash Workflow.
It replaces the Temporal worker. It exposes a FastAPI endpoint
that Upstash QStash calls to drive the state machine.
"""

import os
import uuid

import yaml
from fastapi import FastAPI
from upstash_workflow import AsyncWorkflowContext
from upstash_workflow.fastapi import Serve

from agents.ceo_orchestrator.agent import CEOOrchestratorAgent
from agent_framework.config import AgentConfig
from agent_framework.context import TaskContext

app = FastAPI(title="MAS Workflow Engine", version="1.0.0")

serve = Serve(app)

@serve.post("/api/workflow/ceo-report")
async def generate_ceo_report_workflow(context: AsyncWorkflowContext) -> None:
    """Serverless workflow to generate the CEO Weekly Report."""

    # Define the step function that actually runs the heavy lifting
    async def _run_agent() -> str:
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "agents", "ceo_orchestrator", "config.yaml"
        )
        with open(config_path, encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)

        config = AgentConfig(**config_dict)
        agent = CEOOrchestratorAgent(config)
        agent.init()

        task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="generate_weekly_report",
            input_data={"period": "weekly"},
        )

        result = await agent.run(task)
        if hasattr(result, "output") and "report_markdown" in result.output:
            return result.output["report_markdown"]
        return f"Report generation ended in state: {agent.state.value}"

    # context.run ensures the step is executed deterministically and retried upon failure
    # It acts as a durable execution boundary, similar to Temporal's execute_activity
    report_result = await context.run("generate_ceo_report_step", _run_agent)

    return None
