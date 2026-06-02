import os

import yaml

agents_to_create = [
    {
        "dir": "healthcare/vertical_manager",
        "class_name": "HealthcareVerticalManager",
        "agent_id": "vertical-manager-1",
        "name": "Healthcare Vertical Manager",
        "description": "Decomposes healthcare projects into DAGs.",
    },
    {
        "dir": "healthcare/clinical_ai",
        "class_name": "ClinicalAIAgent",
        "agent_id": "clinical-ai-1",
        "name": "Clinical AI Agent",
        "description": "Designs CDSS architectures.",
    },
    {
        "dir": "healthcare/regulatory_compliance",
        "class_name": "RegulatoryComplianceAgent",
        "agent_id": "regulatory-compliance-1",
        "name": "Regulatory Compliance Agent",
        "description": "Performs ABDM/NABH gap analysis.",
    },
    {
        "dir": "healthcare/ehr_integration",
        "class_name": "EHRIntegrationAgent",
        "agent_id": "ehr-integration-1",
        "name": "EHR Integration Agent",
        "description": "Maps FHIR and HL7 data models.",
    },
    {
        "dir": "shared_services/quality_compliance",
        "class_name": "QualityComplianceAgent",
        "agent_id": "quality-compliance-1",
        "name": "Quality & Compliance Agent",
        "description": "Tiered QA pipeline for deliverables.",
    }
]

base_path = "h:/ai-healthcare-consultancy/packages/agents"

agent_template = """from agent_framework.base import BaseAgent, SuccessResult
from agent_framework.context import TaskContext

class {class_name}(BaseAgent):
    async def execute(self, context: TaskContext) -> SuccessResult:
        # MVP: Return a static successful output
        return SuccessResult(
            output={{"status": "completed", "deliverable": "{description}"}},
            confidence=0.9
        )
"""

config_template = {
    "agent_id": "",
    "name": "",
    "tier": "tier_1",
    "vertical": "healthcare",
    "reasoning_mode": "plan_and_execute",
    "token_budget": {
        "max_tokens_per_task": 20000,
        "hard_cap_pct": 1.0,
        "overage_threshold_pct": 0.8
    },
    "guardrails": {
        "require_kb_validity_check": True,
        "blocked_output_patterns": [],
        "mandatory_disclaimer": "",
        "max_confidence_without_source": 0.8,
        "pii_detection_enabled": True
    },
    "escalation_rules": []
}

for agent in agents_to_create:
    agent_dir = os.path.join(base_path, agent["dir"])
    os.makedirs(agent_dir, exist_ok=True)

    # Create agent.py
    with open(os.path.join(agent_dir, "agent.py"), "w", encoding="utf-8") as f:
        f.write(agent_template.format(class_name=agent["class_name"], description=agent["description"]))

    # Create config.yaml
    conf = config_template.copy()
    conf["agent_id"] = agent["agent_id"]
    conf["name"] = agent["name"]

    if "quality_compliance" in agent["dir"]:
        conf["vertical"] = "all"

    with open(os.path.join(agent_dir, "config.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(conf, f, sort_keys=False)

print("Scaffolding complete.")
