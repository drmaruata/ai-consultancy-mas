"""Healthcare Project Upstash Workflow.

This defines the parallel DAG orchestrating the Healthcare Vertical Domain Specialists.
It enforces the hard limit of 2 QA retries before escalating to human oversight.
"""

import asyncio
import os
import uuid
import yaml
from typing import Any, Dict, List, Optional, Union

import structlog
from upstash_workflow import AsyncWorkflowContext
from upstash_workflow.fastapi import Serve

from verticals.healthcare.clinical_ai.agent import ClinicalAIAgent
from verticals.healthcare.ehr_integration.agent import EHRIntegrationAgent
from verticals.healthcare.regulatory_compliance.agent import RegulatoryComplianceAgent
from verticals.healthcare.vertical_manager.agent import HealthcareVerticalManager
from agents.shared_services.quality_compliance.agent import QualityComplianceAgent
from agent_framework.config import AgentConfig
from agent_framework.context import TaskContext


def _load_agent(agent_class: type, agent_dir: str) -> Any:
    """Helper to load agent config and instantiate."""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "agents", agent_dir, "config.yaml"
    )
    with open(config_path, encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)
    config = AgentConfig(**config_dict)
    agent = agent_class(config)
    agent.init()
    return agent


async def execute_healthcare_dag(context: AsyncWorkflowContext, project_input: dict) -> dict:
    """The durable workflow orchestrating the healthcare DAG."""

    # 1. Vertical Manager decomposition
    async def _decompose() -> dict:
        agent = _load_agent(HealthcareVerticalManager, "healthcare/vertical_manager")
        task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="decompose_project",
            input_data=project_input,
        )
        result = await agent.run(task)
        return result.output if hasattr(result, "output") else {}

    dag_plan = await context.run("vertical_manager_decompose", _decompose)

    # QA Loop: Max 2 retries
    max_retries = 2
    qa_attempts = 0
    final_output = None

    while qa_attempts <= max_retries:
        qa_attempts += 1

        # 2. Parallel Execution of Domain Specialists
        # In a real Upstash setup we'd use context.call to invoke other endpoints or `asyncio.gather` inside a single step
        # Since Upstash Python SDK currently uses step functions sequentially, we will wrap the parallel execution in one durable step.

        async def _execute_specialists() -> dict:
            reg_agent = _load_agent(RegulatoryComplianceAgent, "healthcare/regulatory_compliance")
            clin_agent = _load_agent(ClinicalAIAgent, "healthcare/clinical_ai")
            ehr_agent = _load_agent(EHRIntegrationAgent, "healthcare/ehr_integration")

            # Create tasks
            reg_task = TaskContext(task_id=str(uuid.uuid4()), task_type="regulatory_analysis", input_data=dag_plan)
            clin_task = TaskContext(task_id=str(uuid.uuid4()), task_type="cdss_architecture", input_data=dag_plan)
            ehr_task = TaskContext(task_id=str(uuid.uuid4()), task_type="fhir_mapping", input_data=dag_plan)

            # Execute in parallel
            results = await asyncio.gather(
                reg_agent.run(reg_task),
                clin_agent.run(clin_task),
                ehr_agent.run(ehr_task),
                return_exceptions=True
            )

            return {
                "regulatory": results[0].output if not isinstance(results[0], Exception) and hasattr(results[0], "output") else str(results[0]),
                "clinical": results[1].output if not isinstance(results[1], Exception) and hasattr(results[1], "output") else str(results[1]),
                "ehr": results[2].output if not isinstance(results[2], Exception) and hasattr(results[2], "output") else str(results[2]),
            }

        specialist_results = await context.run(f"execute_specialists_attempt_{qa_attempts}", _execute_specialists)

        # 3. Quality & Compliance Check
        async def _run_qa() -> dict:
            qa_agent = _load_agent(QualityComplianceAgent, "shared_services/quality_compliance")
            qa_task = TaskContext(
                task_id=str(uuid.uuid4()),
                task_type="validate_deliverables",
                input_data=specialist_results,
            )
            result = await qa_agent.run(qa_task)
            return result.output if hasattr(result, "output") else {"pass": False, "issues": ["QA Agent Failed"]}

        qa_result = await context.run(f"qa_check_attempt_{qa_attempts}", _run_qa)

        if qa_result.get("pass", False):
            final_output = specialist_results
            break

        # If QA fails, we loop again up to max_retries.
        # In a real system, we'd feed `qa_result["issues"]` back into the specialist input.
        dag_plan["qa_feedback"] = qa_result.get("issues", [])

    # If it failed 3 times (1 initial + 2 retries)
    if not final_output:
        # Publish escalation event (simulated by returning escalation state)
        return {
            "status": "ESCALATED",
            "reason": "QA failed 3 times (max 2 retries exceeded). Systemic failure detected.",
            "last_qa_result": qa_result
        }

    return {
        "status": "COMPLETED",
        "deliverables": final_output
    }


def attach_healthcare_routes(serve: Serve):
    """Attach the workflow to the Upstash Serve instance."""

    @serve.post("/api/workflow/healthcare-project")
    async def healthcare_project_workflow(context: AsyncWorkflowContext) -> None:
        """Endpoint called by Upstash QStash."""
        # For this test, we use a static input. In prod, it comes from context.request
        project_input = {"project_type": "NABH_Pre_Assessment", "vertical": "healthcare"}
        await execute_healthcare_dag(context, project_input)
