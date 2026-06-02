import json
import logging
import os
import urllib.error
import urllib.request

from agents.business_ops.account_growth.agent import AccountGrowthAgent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Supabase settings
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

from typing import Any, List, Coroutine
async def retention_cron_webhook() -> List[Coroutine[Any, Any, Any]]:
    """
    Called weekly by Upstash QStash.
    1. Makes a batch Supabase RPC call to calculate CHS for all clients.
    2. Iterates over results; if is_alert_triggered is True, triggers Account Growth Agent.
    """
    logger.info("Triggered weekly retention cron batch job")

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.warning("Supabase credentials not found. Mocking CHS calculation.")
        # Mock results
        results = [
            {"client_id": "00000000-0000-0000-0000-000000000001", "previous_chs": 80, "new_chs": 60, "is_alert_triggered": True},
            {"client_id": "00000000-0000-0000-0000-000000000002", "previous_chs": 90, "new_chs": 95, "is_alert_triggered": False}
        ]
    else:
        # Call Supabase RPC natively (no payload needed as it batches all active clients)
        url = f"{SUPABASE_URL}/rest/v1/rpc/calculate_weekly_chs"

        req = urllib.request.Request(url, method="POST")
        req.add_header("apikey", SUPABASE_SERVICE_KEY)
        req.add_header("Authorization", f"Bearer {SUPABASE_SERVICE_KEY}")
        req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                results = json.loads(response.read().decode())
                logger.info(f"Calculated CHS batch for {len(results)} clients.")
        except Exception as e:
            logger.error(f"Failed to calculate CHS via Supabase RPC: {e}")
            return []

    # Check threshold triggers
    triggered_tasks = []
    for row in results:
        client_id = str(row.get("client_id"))
        new_chs = int(row.get("new_chs", 100))
        is_alert_triggered = bool(row.get("is_alert_triggered"))

        if is_alert_triggered:
            logger.warning(f"Alert triggered for client {client_id}! CHS dropped to {new_chs}.")

            from agent_framework.config import AgentConfig
            from agent_framework.enums import AgentTier, Vertical, ReasoningMode
            mock_config = AgentConfig(
                agent_id="account-growth-1",
                name="Account Growth Agent",
                tier=AgentTier.BUSINESS_OPS,
                vertical=Vertical.ALL,
                reasoning_mode=ReasoningMode.PLAN_AND_EXECUTE
            )
            agent = AccountGrowthAgent(mock_config)

            from agent_framework.context import AgentContext, TaskContext
            task_ctx = TaskContext(
                client_id=client_id,
                description=f"Rescue strategy for Client {client_id} due to low CHS ({new_chs})",
                task_type="account_rescue",
                input_data={"chs_score": new_chs, "trigger": "chs_drop"}
            )
            context = AgentContext(
                agent_id="account-growth-1",
                task=task_ctx,
                working_memory={"chs_score": new_chs}
            )

            # Append coroutine to process concurrently later if needed
            triggered_tasks.append(agent.execute(context))
        else:
            logger.info(f"Client {client_id} is healthy (CHS: {new_chs}).")

    return triggered_tasks
