import os
from pathlib import Path
import yaml

base_dir = Path("packages/agents/edtech")
base_dir.mkdir(parents=True, exist_ok=True)
base_dir.joinpath("__init__.py").write_text('"""EdTech Vertical Agents."""\n', encoding="utf-8")

agents = {
    "vertical_manager": {
        "class_name": "EdTechVerticalManager",
        "name": "EdTech Vertical Manager",
        "tier": "Tier 3",
        "mode": "PLAN_AND_EXECUTE",
    },
    "curriculum_design": {
        "class_name": "CurriculumDesignAgent",
        "name": "Curriculum Design Agent",
        "tier": "Tier 2",
        "mode": "PLAN_AND_EXECUTE",
    },
    "assessment": {
        "class_name": "AssessmentAgent",
        "name": "Assessment Agent",
        "tier": "Tier 2",
        "mode": "PLAN_AND_EXECUTE",
    },
    "adaptive_tutor": {
        "class_name": "AdaptiveTutorAgent",
        "name": "Adaptive Tutor Agent",
        "tier": "Tier 2",
        "mode": "PLAN_AND_EXECUTE",
    },
    "exam_strategist": {
        "class_name": "ExamStrategistAgent",
        "name": "Exam Strategist Agent",
        "tier": "Tier 2",
        "mode": "PLAN_AND_EXECUTE",
    },
    "performance_analytics": {
        "class_name": "PerformanceAnalyticsAgent",
        "name": "Performance Analytics Agent",
        "tier": "Tier 2",
        "mode": "PLAN_AND_EXECUTE",
    },
    "lms_integration": {
        "class_name": "LMSIntegrationAgent",
        "name": "LMS Integration Agent",
        "tier": "Tier 2",
        "mode": "PLAN_AND_EXECUTE",
    }
}

agent_py_template = """from typing import Any
from agent_framework.base import BaseAgent, SuccessResult
from agent_framework.context import AgentContext

class {class_name}(BaseAgent):
    \"\"\"{name}.\"\"\"

    async def plan(self, context: AgentContext) -> dict[str, Any]:
        return {{"steps": ["Initialize", "Execute task", "Complete"]}}

    async def execute(self, context: AgentContext) -> SuccessResult:
        return SuccessResult(
            output={{"deliverable_text": "{name} executed successfully."}},
            confidence=0.90,
            sources_cited=["edtech_kb_v1"],
        )
"""

config_yaml_template = """agent_id: {dir_name}-1
name: {name}
vertical: EDTECH
tier: {tier_mapped}
reasoning_mode: {mode}
token_budget:
  max_tokens_per_task: 16000
  overage_threshold_pct: 0.8
  hard_cap_pct: 1.0
guardrails:
  pii_detection_enabled: true
  blocked_output_patterns:
    - "(?i)guarantee success"
  max_confidence_without_source: 0.6
  require_kb_validity_check: true
"""

for dir_name, meta in agents.items():
    agent_dir = base_dir / dir_name
    agent_dir.mkdir(exist_ok=True)
    
    agent_dir.joinpath("__init__.py").write_text(f'"""{meta["name"]} module."""\n', encoding="utf-8")
    
    # Write agent.py
    agent_dir.joinpath("agent.py").write_text(
        agent_py_template.format(class_name=meta["class_name"], name=meta["name"]), 
        encoding="utf-8"
    )
    
    # Write config.yaml
    tier_mapped = meta["tier"].replace("Tier ", "TIER_")
    agent_dir.joinpath("config.yaml").write_text(
        config_yaml_template.format(
            dir_name=dir_name.replace("_", "-"), 
            name=meta["name"],
            tier_mapped=tier_mapped,
            mode=meta["mode"]
        ),
        encoding="utf-8"
    )
    
    print(f"Scaffolded {dir_name}")

