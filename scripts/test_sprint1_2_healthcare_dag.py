import asyncio
import logging

from upstash_workflow import AsyncWorkflowContext


# Mock context to run the DAG locally without the Upstash backend for testing
class MockContext(AsyncWorkflowContext):
    def __init__(self):
        self.step_results = {}

    async def run(self, step_name: str, func, *args, **kwargs):
        logging.info(f"[Workflow Step] {step_name} started.")
        result = await func()
        logging.info(f"[Workflow Step] {step_name} completed.")
        return result

async def run_test():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # We will temporarily modify the QA agent to ALWAYS fail to test the 3-strike escalation rule.
    import agents.shared_services.quality_compliance.agent as qa_module
    from agent_framework.base import SuccessResult
    from verticals.workflows.healthcare_project import execute_healthcare_dag

    class FailingQAAgent(qa_module.QualityComplianceAgent):
        async def execute(self, context):
            return SuccessResult(
                output={"pass": False, "issues": ["Syntax error in FHIR mapping", "Missing CDSS model accuracy metric"]},
                confidence=0.9
            )

    # Override the loaded class
    qa_module.QualityComplianceAgent = FailingQAAgent

    context = MockContext()
    project_input = {"project_type": "NABH_Pre_Assessment", "vertical": "healthcare"}

    logging.info("Starting Healthcare DAG execution test...")
    result = await execute_healthcare_dag(context, project_input)

    logging.info(f"Final Workflow Result: {result}")

    assert result["status"] == "ESCALATED", "Workflow should have escalated after max retries."
    assert "QA failed 3 times" in result["reason"], "Escalation reason should mention max retries."
    logging.info("Test passed: 3-strike QA escalation rule works perfectly.")

if __name__ == "__main__":
    asyncio.run(run_test())
