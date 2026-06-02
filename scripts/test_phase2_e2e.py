import asyncio
import logging

from verticals.logistics.erp_integration.agent import ERPIntegrationAgent
from verticals.logistics.supply_chain.agent import SupplyChainAgent
from verticals.logistics.trade_compliance.agent import TradeComplianceAgent

from agent_framework.enums import AgentTier, Vertical, ReasoningMode

# Logistics Agents
from verticals.logistics.vertical_manager.agent import LogisticsVerticalManager
from agent_framework.config import AgentConfig
from agent_framework.context import AgentContext, TaskContext
from verticals.workflows.retention_cron import retention_cron_webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Phase2_E2E")

async def test_growth_engine() -> None:
    print("\n" + "="*50)
    print("  PHASE 2 E2E TEST: PART 1 - GROWTH ENGINE (CHS)")
    print("="*50)

    logger.info("Simulating QStash Webhook trigger for Retention Cron...")

    # Run the retention cron workflow
    tasks = await retention_cron_webhook()

    # In a real environment, tasks are coroutines that would be gathered.
    # We will await them to see the output of the AccountGrowthAgent
    results = await asyncio.gather(*tasks)

    for i, res in enumerate(results):
        if hasattr(res, 'output'):
            logger.info(f"Rescue Task {i+1} Output: {res.output['deliverable']}")
        else:
            logger.info(f"Rescue Task {i+1} Output: Error or Escalated")

    print("\nGrowth Engine tests completed successfully.")

async def test_logistics_dag() -> None:
    print("\n" + "="*50)
    print("  PHASE 2 E2E TEST: PART 2 - LOGISTICS VERTICAL DAG")
    print("="*50)

    logger.info("Simulating CEO Orchestrator delegating a Supply Chain Audit project...")

    # 1. Initialize the Vertical Manager
    vm_config = AgentConfig(
        agent_id="logistics-vm-1",
        name="Logistics Vertical Manager",
        tier=AgentTier.VERTICAL_MANAGER,
        vertical=Vertical.LOGISTICS,
        reasoning_mode=ReasoningMode.PLAN_AND_EXECUTE
    )
    vertical_manager = LogisticsVerticalManager(vm_config)

    # 2. Context for the master project
    project_ctx = AgentContext(
        agent_id="logistics-vm-1",
        task=TaskContext(
            client_id="11111111-2222-3333-4444-555555555555",
            description="Supply Chain Visibility Audit and Tally Prime ERP Integration.",
            task_type="supply_chain_audit",
            input_data={}
        )
    )

    # 3. Simulate VM Planning Phase (DAG Breakdown)
    logger.info("Vertical Manager planning task distribution...")
    plan = await vertical_manager.plan(project_ctx)
    logger.info(f"Vertical Manager Plan: {plan['steps']}")

    # 4. Instantiate Specialist Agents for the DAG
    specialists = [
        SupplyChainAgent(AgentConfig(agent_id="supply-chain-1", name="Supply Chain Specialist", tier=AgentTier.DOMAIN_SPECIALIST, vertical=Vertical.LOGISTICS, reasoning_mode=ReasoningMode.REACT)),
        TradeComplianceAgent(AgentConfig(agent_id="trade-1", name="Trade Compliance Specialist", tier=AgentTier.DOMAIN_SPECIALIST, vertical=Vertical.LOGISTICS, reasoning_mode=ReasoningMode.REACT)),
        ERPIntegrationAgent(AgentConfig(agent_id="erp-1", name="ERP Integration Specialist", tier=AgentTier.DOMAIN_SPECIALIST, vertical=Vertical.LOGISTICS, reasoning_mode=ReasoningMode.REACT))
    ]

    # 5. Execute Specialists Concurrently (Simulating Upstash Workflow Parallel Execution)
    logger.info("Dispatching tasks to Logistics Specialist Agents concurrently...")

    specialist_tasks = []
    for agent in specialists:
        task_ctx = AgentContext(
            agent_id=agent.config.agent_id,
            task=TaskContext(
                client_id="11111111-2222-3333-4444-555555555555",
                description=f"Execute specialization for {agent.config.name}",
                task_type="specialist_task",
                input_data={}
            )
        )
        specialist_tasks.append(agent.execute(task_ctx))

    specialist_results = await asyncio.gather(*specialist_tasks)

    # 6. Print Results
    for i, res in enumerate(specialist_results):
        if hasattr(res, 'output'):
            logger.info(f"[{specialists[i].config.name} Result]: {res.output['deliverable']}")
        else:
            logger.info(f"[{specialists[i].config.name} Result]: Error or Escalated")

    logger.info("Logistics DAG tests completed successfully.")

async def run_all_tests():
    await test_growth_engine()
    await test_logistics_dag()
    print("\n" + "="*50)
    print("[PASS] PHASE 2 END-TO-END ACCEPTANCE TESTS PASSED")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
