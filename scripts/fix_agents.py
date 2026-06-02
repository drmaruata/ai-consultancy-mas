import os

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

agent_template = """from typing import Any
from agent_framework.base import BaseAgent, SuccessResult
from agent_framework.context import AgentContext

class {class_name}(BaseAgent):
    async def plan(self, context: AgentContext) -> dict[str, Any]:
        return {{"steps": ["mock_step_1"]}}

    async def execute(self, context: AgentContext) -> SuccessResult:
        # MVP: Return a static successful output
        return SuccessResult(
            output={{"status": "completed", "deliverable": "{description}"}},
            confidence=0.9
        )
"""

for agent in agents_to_create:
    agent_dir = os.path.join(base_path, agent["dir"])

    # Overwrite agent.py
    with open(os.path.join(agent_dir, "agent.py"), "w", encoding="utf-8") as f:
        f.write(agent_template.format(class_name=agent["class_name"], description=agent["description"]))

print("Added plan method to agents.")
