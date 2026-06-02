import os

import yaml

agents_to_create = [
    {
        "dir": "business_ops/ops_hr",
        "class_name": "OpsHrAgent",
        "agent_id": "ops-hr-1",
        "name": "Ops & HR Agent",
        "description": "Calculates CHS and manages vendor SLAs.",
    },
    {
        "dir": "business_ops/account_growth",
        "class_name": "AccountGrowthAgent",
        "agent_id": "account-growth-1",
        "name": "Account Growth Agent",
        "description": "Generates retainer proposals to rescue accounts or cross-sell.",
    }
]

base_path = "h:/ai-healthcare-consultancy/packages/agents"

agent_template = """from typing import Any
from agent_framework.base import BaseAgent, SuccessResult
from agent_framework.context import AgentContext

class {class_name}(BaseAgent):
    async def plan(self, context: AgentContext) -> dict[str, Any]:
        return {{"steps": ["analyze_client_data", "generate_proposal"]}}

    async def execute(self, context: AgentContext) -> SuccessResult:
        return SuccessResult(
            output={{"status": "completed", "deliverable": "{description}"}},
            confidence=0.9
        )
"""

config_template = {
    "agent_id": "",
    "name": "",
    "tier": "tier_1",
    "vertical": "all",
    "reasoning_mode": "plan_and_execute",
    "token_budget": {
        "max_tokens_per_task": 15000,
        "hard_cap_pct": 1.0,
        "overage_threshold_pct": 0.8
    },
    "guardrails": {
        "require_kb_validity_check": False,
        "blocked_output_patterns": [],
        "mandatory_disclaimer": "",
        "max_confidence_without_source": 0.9,
        "pii_detection_enabled": True
    },
    "escalation_rules": []
}

for agent in agents_to_create:
    agent_dir = os.path.join(base_path, agent["dir"])
    os.makedirs(agent_dir, exist_ok=True)

    with open(os.path.join(agent_dir, "agent.py"), "w", encoding="utf-8") as f:
        f.write(agent_template.format(class_name=agent["class_name"], description=agent["description"]))

    conf = config_template.copy()
    conf["agent_id"] = agent["agent_id"]
    conf["name"] = agent["name"]

    with open(os.path.join(agent_dir, "config.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(conf, f, sort_keys=False)

print("Sprint 2.1 Agents Scaffolded.")
