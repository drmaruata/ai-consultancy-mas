import os
from pathlib import Path
import json

base = Path("knowledge_bases")

kb_files = {
    "legal": [
        "bns_2023.md",
        "companies_act_2013.md",
        "sebi_lodr.md",
        "rbi_master_directions.md",
        "dpdp_act_2023.md"
    ],
    "healthcare": [
        "abdm_standards.md",
        "nqas_guidelines.md"
    ]
}

for vertical, files in kb_files.items():
    dir_path = base / vertical
    dir_path.mkdir(parents=True, exist_ok=True)
    for filename in files:
        file_path = dir_path / filename
        title = filename.replace("_", " ").replace(".md", "").title()
        
        # Create a placeholder document
        content = f"# {title}\n\nThis is a seeded knowledge base document for {title}."
        file_path.write_text(content, encoding="utf-8")
        print(f"Created {file_path}")

