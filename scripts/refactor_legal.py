import os
from pathlib import Path

BASE_DIR = Path("packages/agents/legal")

replacements = {
    "contract_analysis": [
        ("ContractReviewAgent", "ContractAnalysisAgent"),
        ("contract-review-1", "contract-analysis-1"),
        ("Contract Review", "Contract Analysis")
    ],
    "legal_research": [
        ("ComplianceAuditorAgent", "LegalResearchAgent"),
        ("compliance-auditor-1", "legal-research-1"),
        ("Compliance Auditor", "Legal Research")
    ],
    "litigation_support": [
        ("DisputeResolutionAgent", "LitigationSupportAgent"),
        ("dispute-resolution-1", "litigation-support-1"),
        ("Dispute Resolution", "Litigation Support")
    ],
    "policy_drafting": [
        ("LegalPolicyAgent", "PolicyDraftingAgent"),
        ("legal-policy-1", "policy-drafting-1"),
        ("Legal Policy", "Policy Drafting")
    ],
    "risk_assessment": [
        ("MADueDiligenceAgent", "RiskAssessmentAgent"),
        ("ma-due-diligence-1", "risk-assessment-1"),
        ("M&A Due Diligence", "Risk Assessment")
    ]
}

def process_dir(agent_dir_name, rules):
    d = BASE_DIR / agent_dir_name
    for f in [d / "agent.py", d / "config.yaml", d / "__init__.py"]:
        if f.exists():
            content = f.read_text(encoding="utf-8")
            for old, new in rules:
                content = content.replace(old, new)
            f.write_text(content, encoding="utf-8")
            print(f"Updated {f}")

for agent, rules in replacements.items():
    process_dir(agent, rules)

# Now update vertical manager
vm_agent = BASE_DIR / "vertical_manager" / "agent.py"
vm_content = vm_agent.read_text(encoding="utf-8")

vm_replacements = [
    ('"contract_review": ["contract-review-1"]', '"contract_analysis": ["contract-analysis-1"]'),
    ('"compliance_audit": ["compliance-auditor-1"]', '"legal_research": ["legal-research-1"]'),
    ('"dispute_resolution": ["dispute-resolution-1"]', '"litigation_support": ["litigation-support-1"]'),
    ('"ma_due_diligence": ["ma-due-diligence-1", "compliance-auditor-1"]', '"risk_assessment": ["risk-assessment-1", "legal-research-1"]'),
    ('"policy_drafting": ["legal-policy-1"]', '"policy_drafting": ["policy-drafting-1"]'),
    ('"general_legal": ["contract-review-1", "compliance-auditor-1"]', '"general_legal": ["contract-analysis-1", "legal-research-1"]'),
]

for old, new in vm_replacements:
    vm_content = vm_content.replace(old, new)

vm_agent.write_text(vm_content, encoding="utf-8")
print(f"Updated {vm_agent}")
