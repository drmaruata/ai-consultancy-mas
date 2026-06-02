"""Upstash Workflow server entry point for the MAS.

This runs the FastAPI app that serves Upstash Workflow webhooks,
replacing the Temporal worker.
"""

import logging

import uvicorn

from verticals.workflows.ceo_weekly_report import app, serve
from verticals.workflows.healthcare_project import attach_healthcare_routes
from verticals.workflows.legal_project import attach_legal_routes

attach_healthcare_routes(serve)
attach_legal_routes(serve)

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Upstash Workflow Webhook Server for MAS on port 8000...")
    # In production, this would be deployed to a serverless platform like Vercel,
    # AWS Lambda, or a long-running container via Docker.
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
