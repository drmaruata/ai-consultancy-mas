import json
import logging
import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Request, BackgroundTasks

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

MOCKS_DIR = Path(__file__).parent.parent.parent.parent / "tests" / "mocks" / "legal"

@router.post("/api/cron/regulatory-scraper")
async def trigger_regulatory_scraper(request: Request, background_tasks: BackgroundTasks):
    """
    Called daily by Upstash QStash.
    Simulates scraping SEBI/RBI portals by reading a mocked JSON file.
    When a new circular is detected, it publishes a Kafka event so the
    Regulatory Watch Agent can process it and issue KB supersession updates.
    """
    logger.info("Triggered daily regulatory scraper cron job")

    # In MVP, we simulate scraping by reading a local mocked file
    mock_file = MOCKS_DIR / "sebi_circular.json"
    
    if not mock_file.exists():
        logger.warning(f"Mock file not found at {mock_file}. Assuming no new updates.")
        return {"status": "no_updates"}

    with open(mock_file, "r", encoding="utf-8") as f:
        new_circular = json.load(f)

    logger.info(f"Detected new regulatory update: {new_circular.get('title')}")

    # Produce an event to Kafka for the Regulatory Watch Agent
    from messaging.producer import MessageProducer
    from messaging.schemas import RegulatoryUpdateMessage
    producer = MessageProducer()
    await producer.start()

    event = RegulatoryUpdateMessage(
        source_agent_id="regulatory_scraper",
        vertical=new_circular.get("vertical", "legal"),
        regulation_name=new_circular.get("title", "Unknown"),
        update_type="circular",
        summary=new_circular.get("content_summary", ""),
        source_url=new_circular.get("document_id", ""),
        affected_kb_documents=[new_circular.get("supersedes")] if new_circular.get("supersedes") else []
    )

    try:
        await producer.publish(
            topic_name=f"regulatory.update.{event.vertical}",
            message=event,
            key=event.source_url
        )
        logger.info(f"Published regulatory.update event for {event.source_url}")
    except Exception as e:
        logger.error(f"Failed to publish regulatory update event: {e}")
    finally:
        await producer.stop()

    return {"status": "success", "published_events": 1, "document": new_circular.get("document_id")}
