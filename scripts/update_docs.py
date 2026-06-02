import os
from pathlib import Path

docs = [Path("AGENTS.md"), Path("README.md")]

replacements = [
    ("Contract Review Agent", "Contract Analysis Agent"),
    ("Compliance Auditor Agent", "Legal Research Agent"),
    ("Legal Policy Agent", "Policy Drafting Agent"),
    ("Dispute Resolution Agent", "Litigation Support Agent"),
    ("M&A Due Diligence Agent", "Risk Assessment Agent"),
    ("Contract Review", "Contract Analysis"),
    ("Compliance Auditor", "Legal Research"),
    ("Legal Policy", "Policy Drafting"),
    ("Dispute Resolution", "Litigation Support"),
    ("M&A Due Diligence", "Risk Assessment"),
]

for doc in docs:
    if doc.exists():
        content = doc.read_text(encoding="utf-8")
        for old, new in replacements:
            content = content.replace(old, new)
        doc.write_text(content, encoding="utf-8")
        print(f"Updated {doc}")
