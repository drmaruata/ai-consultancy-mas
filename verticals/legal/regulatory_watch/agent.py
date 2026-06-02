import json
import logging
from typing import Any

from agent_framework.base import BaseAgent, AgentConfig, SuccessResult
from agent_framework.context import AgentContext
from messaging.producer import MessageProducer
from messaging.schemas import KBSupersessionMessage
from memory.semantic import SemanticMemory

logger = logging.getLogger(__name__)

class RegulatoryWatchAgent(BaseAgent):
    """
    Monitors regulatory updates (SEBI, RBI, MCA).
    Consumes regulatory.update.legal events from the scraper.
    Publishes kb.supersession events and directly updates Semantic Memory.
    Alerts the Legal Vertical Manager about the update.
    """

    async def plan(self, context: AgentContext) -> dict[str, Any]:
        """Reason about the incoming regulatory update."""
        input_data = context.task.input_data or {}
        document_id = input_data.get("document_id", "UNKNOWN")
        supersedes = input_data.get("supersedes")
        
        plan = {
            "step_1": f"Analyze new circular {document_id}",
            "step_2": f"If supersedes exists ({supersedes}), publish kb.supersession and zero out confidence in Vector DB.",
            "step_3": "Alert Vertical Manager to review impacted active projects."
        }
        return plan

    async def execute(self, context: AgentContext) -> SuccessResult:
        """Process the update, update KB, and alert Manager."""
        input_data = context.task.input_data or {}
        supersedes = input_data.get("supersedes")
        new_doc_id = input_data.get("document_id")
        summary = input_data.get("summary", "No summary provided.")

        memory = SemanticMemory()
        
        if supersedes:
            logger.info(f"Processing supersession: {new_doc_id} supersedes {supersedes}")
            # 1. Update Upstash Vector DB confidence to 0.0 directly
            await memory.mark_superseded(doc_id=supersedes, superseded_by=new_doc_id)
            
            # 2. Publish kb.supersession event to Kafka
            producer = MessageProducer()
            await producer.start()
            try:
                event = KBSupersessionMessage(
                    source_agent_id=self.config.agent_id,
                    superseded_doc_id=supersedes,
                    superseded_doc_title="Old Document",
                    new_doc_id=new_doc_id,
                    new_doc_title="New Regulatory Update",
                    vertical="legal",
                    reason="Superseded by new regulatory circular"
                )
                await producer.publish(
                    topic_name="kb.supersession",
                    message=event,
                    key=supersedes
                )
                logger.info(f"Published kb.supersession event for {supersedes}")
            finally:
                await producer.stop()

        # 3. Formulate the alert for the Vertical Manager
        alert_message = (
            f"URGENT REGULATORY UPDATE: Document {new_doc_id} has been published.\n"
            f"Summary: {summary}\n"
            f"Impact: Supersedes {supersedes if supersedes else 'None'}.\n"
            f"Action Required: Vertical Manager must cross-reference this with active legal tasks."
        )
        
        return SuccessResult(
            output={
                "alert_to_vertical_manager": alert_message,
                "supersession_processed": bool(supersedes)
            },
            confidence=1.0,
            sources_cited=[new_doc_id]
        )
