import asyncio
import logging
import uuid
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
load_dotenv()

from verticals.legal.regulatory_watch.agent import RegulatoryWatchAgent
from agent_framework.base import AgentConfig
from agent_framework.context import AgentContext, TaskContext
from memory.semantic import SemanticMemory, SemanticDocument
from packages.services.data_pipelines.regulatory_scraper import trigger_regulatory_scraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestSprint3.1")

class MockRequest:
    pass

class MockBackgroundTasks:
    pass

async def test_regulatory_pipeline():
    logger.info("Starting Sprint 3.1 Regulatory Pipeline E2E Test")
    
    # 1. Setup Semantic Memory with a mock "Old Law"
    memory = SemanticMemory()
    old_doc_id = "SEBI/HO/CFD/PoD2/CIR/P/2023/120"
    
    old_doc = SemanticDocument(
        doc_id=old_doc_id,
        title="Old SEBI Circular",
        content="24-hour reporting window",
        vertical="legal",
        domain="compliance",
        current_confidence=1.0
    )
    
    # We await ingest, but since upstash might not be connected locally, it uses _local_store fallback if not set.
    # However, since the user is using Upstash, this will attempt upsert.
    await memory.ingest(old_doc)
    logger.info(f"Ingested old document: {old_doc_id} with confidence 1.0")

    # 2. Trigger the Scraper (reads the mock JSON)
    logger.info("Triggering Regulatory Scraper...")
    scraper_result = await trigger_regulatory_scraper(MockRequest(), MockBackgroundTasks())
    
    if scraper_result.get("status") != "success":
        logger.error("Scraper failed to process the mock JSON.")
        return
        
    logger.info(f"Scraper processed document: {scraper_result.get('document')}")

    # 3. Trigger Regulatory Watch Agent manually 
    # (In a real system, the Kafka Consumer would trigger this agent, but for testing we invoke it directly)
    logger.info("Instantiating Regulatory Watch Agent...")
    config = AgentConfig(
        agent_id="regulatory-watch-test",
        name="Regulatory Watch Agent",
        tier="tier_4",
        vertical="legal",
        reasoning_mode="react"
    )
    agent = RegulatoryWatchAgent(config)
    
    # The payload from the scraper
    task = TaskContext(
        task_id=str(uuid.uuid4()),
        task_type="process_regulatory_update",
        input_data={
            "document_id": "SEBI/HO/CFD/PoD2/CIR/P/2026/001",
            "supersedes": old_doc_id,
            "summary": "This circular mandates real-time API-based reporting of material events."
        }
    )
    
    logger.info("Executing Regulatory Watch Agent...")
    result = await agent.run(task)
    
    # 4. Assertions
    logger.info(f"Agent Execution State: {agent.state.value}")
    
    if hasattr(result, "output"):
        alert_msg = result.output.get("alert_to_vertical_manager")
        logger.info(f"Generated Alert:\n{alert_msg}")
        
        # Verify the BaseAgent.report() hook injected the disclaimer!
        deliverable = result.output.get("alert_to_vertical_manager", "")
        if "MANDATORY DISCLAIMER:" in deliverable:
            logger.info("✅ SUCCESS: Mandatory legal disclaimer was injected successfully.")
        else:
            logger.error("❌ FAILED: Mandatory legal disclaimer was NOT injected.")
    else:
        logger.error("❌ FAILED: Agent result did not have an output.")
        
    # Verify the old document confidence is now 0.0
    logger.info("Waiting 2 seconds for Upstash Vector DB consistency...")
    await asyncio.sleep(2)
    
    updated_doc = await memory.get_document(old_doc_id)
    if updated_doc:
        logger.info(f"Old document current_confidence: {updated_doc.current_confidence}")
        if updated_doc.current_confidence == 0.0:
            logger.info("✅ SUCCESS: Upstash Vector DB successfully dropped confidence to 0.0.")
        else:
            logger.error(f"❌ FAILED: Expected confidence 0.0, got {updated_doc.current_confidence}")
    else:
        logger.error("Could not retrieve old document from Semantic Memory.")

if __name__ == "__main__":
    asyncio.run(test_regulatory_pipeline())
