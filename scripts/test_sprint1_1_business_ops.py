import asyncio
import os
import uuid

import structlog
import yaml

from agents.business_ops.finance_agent.agent import FinanceAgent
from agents.business_ops.sales_agent.agent import SalesAgent
from agent_framework.config import AgentConfig
from agent_framework.context import TaskContext

logger = structlog.get_logger()

async def main():
    logger.info("Starting Business Ops Core Verification (Sprint 1.1)")

    # 1. Load Configurations
    sales_config_path = os.path.join(
        "packages", "agents", "business_ops", "sales_agent", "config.yaml"
    )
    finance_config_path = os.path.join(
        "packages", "agents", "business_ops", "finance_agent", "config.yaml"
    )

    with open(sales_config_path) as f:
        sales_config = AgentConfig(**yaml.safe_load(f))
    with open(finance_config_path) as f:
        finance_config = AgentConfig(**yaml.safe_load(f))

    # 2. Initialize Agents
    sales_agent = SalesAgent(sales_config)
    finance_agent = FinanceAgent(finance_config)
    sales_agent.init()
    finance_agent.init()

    # 3. Create a Hardcoded Lead
    lead_data = {
        "company_name": "Apollo Care Solutions",
        "vertical": "healthcare",
        "budget": 120000,
        "urgency": "medium",
        "region": "US"
    }

    logger.info("Processing inbound lead", company=lead_data["company_name"])

    # 4. Run Sales Agent
    sales_task = TaskContext(
        task_id=str(uuid.uuid4()),
        task_type="process_inbound_lead",
        input_data={"lead": lead_data}
    )

    sales_result = await sales_agent.run(sales_task)

    if not hasattr(sales_result, 'output'):
        logger.error("Sales agent failed or escalated", result=sales_result)
        return

    logger.info("Sales Agent Output", output=sales_result.output)

    # 5. Run Finance Agent (Handoff)
    if sales_result.output.get("next_step") == "finance_pricing_validation":
        finance_payload = sales_result.output.get("finance_payload", {})
        logger.info("Handing off to Finance Agent", payload=finance_payload)

        finance_task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="generate_pricing_and_invoice",
            input_data=finance_payload
        )

        finance_result = await finance_agent.run(finance_task)
        if hasattr(finance_result, 'output'):
            logger.info("Finance Agent Output", output=finance_result.output)
            print("\n--- INVOICE GENERATED ---\n")
            print(finance_result.output["invoice_markdown"])
            print("-------------------------\n")
        else:
            logger.error("Finance agent failed or escalated", result=finance_result)

if __name__ == "__main__":
    asyncio.run(main())
