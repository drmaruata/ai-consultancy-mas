"""Tests for the Messaging layer — Sprint 0.1 acceptance criteria."""

import pytest

from messaging import (
    TOPIC_REGISTRY,
    TaskAssignedMessage,
    DeliverableReadyMessage,
    ClientHealthAlertMessage,
    EscalationMessage,
    KBSupersessionMessage,
    RegulatoryUpdateMessage,
    TenderNewMessage,
    AuditLogMessage,
    MessageProducer,
)


class TestTopicRegistry:
    """Test the Kafka topic registry."""

    def test_all_required_topics_exist(self):
        required_topics = [
            "task.assigned",
            "task.completed",
            "task.failed",
            "deliverable.ready",
            "deliverable.approved",
            "deliverable.rejected",
            "client.health.alert",
            "regulatory.update.healthcare",
            "regulatory.update.logistics",
            "regulatory.update.legal",
            "regulatory.update.edtech",
            "kb.supersession",
            "mas.health.report",
            "escalation.required",
            "tender.new",
            "tender.bid.generated",
            "affiliate.event",
            "market.intelligence.digest",
            "audit.log",
        ]
        for topic in required_topics:
            assert topic in TOPIC_REGISTRY, f"Missing topic: {topic}"

    def test_audit_log_has_long_retention(self):
        audit_topic = TOPIC_REGISTRY["audit.log"]
        assert audit_topic.retention_hours == 8760  # 365 days

    def test_audit_log_has_more_partitions(self):
        audit_topic = TOPIC_REGISTRY["audit.log"]
        assert audit_topic.partitions == 12

    def test_topic_count(self):
        """Ensure we have the expected number of topics."""
        assert len(TOPIC_REGISTRY) >= 19


class TestMessageSchemas:
    """Test typed message serialization/deserialization."""

    def test_task_assigned_message(self):
        msg = TaskAssignedMessage(
            source_agent_id="ceo-orchestrator",
            target_agent_id="healthcare-vm",
            task_id="task-123",
            vertical="healthcare",
            task_type="nabh_gap_analysis",
            description="Run NABH gap analysis for Apollo Hospital",
            priority=3,
        )
        assert msg.source_agent_id == "ceo-orchestrator"
        assert msg.target_agent_id == "healthcare-vm"
        assert msg.priority == 3
        assert msg.message_id  # Auto-generated
        assert msg.schema_version == 1

        # Serialize to JSON
        payload = msg.model_dump(mode="json")
        assert isinstance(payload, dict)
        assert payload["vertical"] == "healthcare"

    def test_deliverable_ready_message(self):
        msg = DeliverableReadyMessage(
            source_agent_id="healthcare-clinical-ai",
            task_id="task-123",
            vertical="healthcare",
            deliverable_type="nabh_gap_analysis",
            content_location="deliverables/task-123/report.pdf",
            suggested_qa_tier="class_b",
            confidence=0.88,
            sources_cited=["NABH_4th_edition"],
        )
        assert msg.suggested_qa_tier == "class_b"
        assert len(msg.sources_cited) == 1

    def test_client_health_alert_message(self):
        msg = ClientHealthAlertMessage(
            source_agent_id="ops-hr-agent",
            client_id="client-456",
            client_name="Apollo Hospital",
            current_chs=58.5,
            previous_chs=72.0,
        )
        assert msg.current_chs < msg.threshold
        assert msg.alert_type == "chs_drop"

    def test_escalation_message(self):
        msg = EscalationMessage(
            source_agent_id="finance-agent",
            task_id="task-789",
            escalation_reason="pricing_anomaly",
            description="Computed price is 3.1x base rate, exceeding 2.5x threshold.",
            urgency="high",
        )
        assert msg.urgency == "high"

    def test_kb_supersession_message(self):
        msg = KBSupersessionMessage(
            source_agent_id="legal-regulatory-watch",
            superseded_doc_id="doc-old",
            superseded_doc_title="BNS 2023 v1.0",
            new_doc_id="doc-new",
            new_doc_title="BNS 2023 v1.1 (Amendment)",
            vertical="legal",
            reason="Amendment notification from MCA portal",
        )
        assert msg.vertical == "legal"

    def test_tender_new_message(self):
        msg = TenderNewMessage(
            source_agent_id="tender-bidding-agent",
            tender_id="GEM-2026-HC-001",
            portal="gem",
            title="AI-Powered CDSS for District Hospitals",
            vertical_match=["healthcare"],
            eligibility_met=True,
        )
        assert msg.portal == "gem"
        assert msg.eligibility_met is True

    def test_audit_log_message(self):
        msg = AuditLogMessage(
            source_agent_id="healthcare-clinical-ai",
            execution_id="exec-001",
            task_id="task-123",
            agent_id="healthcare-clinical-ai",
            action="task_completed",
            result_state="complete",
            tokens_used=2500,
            elapsed_ms=4500,
        )
        assert msg.action == "task_completed"
        assert msg.tokens_used == 2500


class TestMessageProducer:
    """Test the Kafka producer (in stub mode without Kafka running)."""

    @pytest.mark.asyncio
    async def test_producer_lifecycle(self):
        producer = MessageProducer(bootstrap_servers="localhost:9094")
        await producer.start()  # Runs in stub mode
        await producer.stop()

    @pytest.mark.asyncio
    async def test_publish_validates_topic(self):
        producer = MessageProducer()
        await producer.start()

        with pytest.raises(ValueError, match="Unknown topic"):
            msg = TaskAssignedMessage(
                source_agent_id="test",
                target_agent_id="test",
                task_id="test",
                vertical="healthcare",
                task_type="test",
            )
            await producer.publish("nonexistent.topic", msg)

        await producer.stop()

    @pytest.mark.asyncio
    async def test_publish_valid_message(self):
        producer = MessageProducer()
        await producer.start()

        msg = TaskAssignedMessage(
            source_agent_id="ceo-orchestrator",
            target_agent_id="healthcare-vm",
            task_id="task-123",
            vertical="healthcare",
            task_type="nabh_gap_analysis",
        )
        # Should succeed in stub mode (no actual Kafka)
        await producer.publish("task.assigned", msg)
        await producer.stop()
