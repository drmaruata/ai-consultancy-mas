"""Upstash Workflow engine definitions for the AI Consultancy MAS.

Each module defines a durable, serverless workflow executed via Upstash Workflow
(QStash-backed). Workflows orchestrate multi-agent DAGs with guaranteed
at-least-once delivery and automatic retry on failure.

Modules:
    healthcare_project  — Healthcare vertical project DAG
    ceo_weekly_report   — CEO weekly intelligence digest workflow
    retention_cron      — Client retention cron trigger
    worker              — Upstash Workflow worker entrypoint
"""
