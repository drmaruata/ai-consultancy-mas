"""Legal Project Upstash Workflow.

This defines the parallel DAG orchestrating the Legal Vertical Domain Specialists.
It handles KB Validity Supersession logic (halting if a regulatory circular drops)
and executes the domain specialists in parallel based on the Vertical Manager's routing.
"""

import asyncio
import os
import uuid
import yaml
from typing import Any, Dict, List, Optional, Union

import structlog
from upstash_workflow import AsyncWorkflowContext
from upstash_workflow.fastapi import Serve

from verticals.legal.vertical_manager.agent import LegalVerticalManager
from verticals.legal.contract_analysis.agent import ContractAnalysisAgent
from verticals.legal.legal_research.agent import LegalResearchAgent
from verticals.legal.litigation_support.agent import LitigationSupportAgent
from verticals.legal.policy_drafting.agent import PolicyDraftingAgent
from verticals.legal.risk_assessment.agent import RiskAssessmentAgent
from verticals.legal.regulatory_watch.agent import RegulatoryWatchAgent
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


async def execute_legal_dag(context: AsyncWorkflowContext, project_input: dict) -> dict:
    """The durable workflow orchestrating the legal DAG."""

    # 1. KB Validity Supersession Check
    async def _check_kb_validity() -> dict:
        # Simulate checking if a major regulatory circular dropped recently
        # In production, this reads from the Semantic Memory metadata
        return {"valid": True, "superseded_domains": []}

    kb_status = await context.run("kb_validity_check", _check_kb_validity)
    
    if not kb_status.get("valid"):
        return {
            "status": "HALTED",
            "reason": f"KB Supersession detected in domains: {kb_status.get('superseded_domains')}. Workflow halted pending manual review."
        }

    # 2. Vertical Manager decomposition
    async def _decompose() -> dict:
        agent = _load_agent(LegalVerticalManager, "legal/vertical_manager")
        task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="decompose_legal_project",
            input_data=project_input,
        )
        result = await agent.run(task)
        return result.output if hasattr(result, "output") else {}

    dag_plan = await context.run("vertical_manager_decompose", _decompose)
    parallel_agents = dag_plan.get("dag", {}).get("parallel_agents", [])

    # QA Loop: Max 2 retries
    max_retries = 2
    qa_attempts = 0
    final_output = None

    while qa_attempts <= max_retries:
        qa_attempts += 1

        # 3. Parallel Execution of Domain Specialists
        async def _execute_specialists() -> dict:
            tasks = []
            keys = []
            
            # Map Agent IDs to their classes and directories
            agent_map = {
                "contract-analysis-1": (ContractAnalysisAgent, "legal/contract_analysis"),
                "legal-research-1": (LegalResearchAgent, "legal/legal_research"),
                "litigation-support-1": (LitigationSupportAgent, "legal/litigation_support"),
                "policy-drafting-1": (PolicyDraftingAgent, "legal/policy_drafting"),
                "risk-assessment-1": (RiskAssessmentAgent, "legal/risk_assessment"),
                "regulatory-watch-legal-1": (RegulatoryWatchAgent, "legal/regulatory_watch"),
            }

            for agent_id in parallel_agents:
                if agent_id in agent_map:
                    agent_cls, agent_dir = agent_map[agent_id]
                    agent_instance = _load_agent(agent_cls, agent_dir)
                    task = TaskContext(
                        task_id=str(uuid.uuid4()), 
                        task_type=f"execute_{agent_id}", 
                        input_data=dag_plan
                    )
                    tasks.append(agent_instance.run(task))
                    keys.append(agent_id)

            if not tasks:
                return {"error": "No valid agents identified for parallel execution."}

            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            output = {}
            for key, res in zip(keys, results):
                if isinstance(res, Exception):
                    output[key] = str(res)
                else:
                    output[key] = res.output if hasattr(res, "output") else "No output"
            return output

        specialist_results = await context.run(f"execute_specialists_attempt_{qa_attempts}", _execute_specialists)

        if "error" in specialist_results:
            return {"status": "FAILED", "reason": specialist_results["error"]}

        # 4. Quality & Compliance Check (Class C checks for Legal outputs)
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

        dag_plan["qa_feedback"] = qa_result.get("issues", [])

    if not final_output:
        return {
            "status": "ESCALATED",
            "reason": "QA failed 3 times (max 2 retries exceeded). Systemic failure detected.",
            "last_qa_result": qa_result
        }

    return {
        "status": "COMPLETED",
        "deliverables": final_output
    }


def attach_legal_routes(serve: Serve):
    """Attach the workflow to the Upstash Serve instance."""

    @serve.post("/api/workflow/legal-project")
    async def legal_project_workflow(context: AsyncWorkflowContext) -> None:
        """Endpoint called by Upstash QStash."""
        project_input = {"project_type": "contract_analysis", "vertical": "legal", "client_id": "C-999"}
        await execute_legal_dag(context, project_input)
