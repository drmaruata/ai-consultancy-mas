import pytest
from agents.ceo_orchestrator.agent import CEOOrchestratorAgent
from agent_framework.base import EscalationResult, SuccessResult
from agent_framework.context import AgentContext, TaskContext
from agent_framework.config import AgentConfig
from agent_framework.enums import AgentTier, Vertical, ReasoningMode

@pytest.fixture
def ceo_config():
    return AgentConfig(
        agent_id="ceo-1", 
        name="CEO Orchestrator", 
        tier=AgentTier.ORCHESTRATION, 
        vertical=Vertical.ALL,
        reasoning_mode=ReasoningMode.PLAN_AND_EXECUTE
    )

@pytest.mark.asyncio
async def test_ceo_route_to_vertical(ceo_config):
    agent = CEOOrchestratorAgent(config=ceo_config)
    task = TaskContext(task_id="t1", task_type="route_client_request", input_data={"vertical": "logistics"})
    context = AgentContext(agent_id="ceo-1", task=task)
    
    result = await agent.route_task(context)
    assert isinstance(result, SuccessResult)
    assert result.output["routed_to"] == "logistics-vertical-manager"

@pytest.mark.asyncio
async def test_ceo_route_to_specific_agent(ceo_config):
    agent = CEOOrchestratorAgent(config=ceo_config)
    task = TaskContext(task_id="t2", task_type="route_client_request", input_data={"target_agent": "sales-agent"})
    context = AgentContext(agent_id="ceo-1", task=task)
    
    result = await agent.route_task(context)
    assert isinstance(result, SuccessResult)
    assert result.output["routed_to"] == "sales-agent"

@pytest.mark.asyncio
async def test_ceo_route_invalid_payload(ceo_config):
    agent = CEOOrchestratorAgent(config=ceo_config)
    task = TaskContext(task_id="t3", task_type="route_client_request", input_data={})
    context = AgentContext(agent_id="ceo-1", task=task)
    
    result = await agent.route_task(context)
    assert isinstance(result, EscalationResult)
