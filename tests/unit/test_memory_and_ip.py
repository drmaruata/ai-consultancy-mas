"""Tests for the Memory Architecture & KB Validity Engine — Sprint 0.2."""

from datetime import datetime, timedelta, timezone

import pytest

from memory import (
    WorkingMemory,
    EpisodicMemory,
    EpisodicRecord,
    SemanticMemory,
    SemanticDocument,
    ProceduralMemory,
    PromptTemplate,
)
from ip_registry import IPRegistry, IPAsset
from kb_validity import KBValidityEngine


class TestWorkingMemory:
    """Test ephemeral per-task working memory."""

    def test_message_management(self):
        wm = WorkingMemory(max_tokens=100)
        wm.add_message("system", "You are an agent.")
        wm.add_message("user", "Hello.")
        
        assert wm.message_count == 2
        assert wm.get_last_message() == {"role": "user", "content": "Hello."}
        assert wm.estimated_tokens > 0

    def test_scratchpad(self):
        wm = WorkingMemory()
        wm.set("key1", "value1")
        assert wm.get("key1") == "value1"
        assert wm.has("key1") is True
        
        wm.delete("key1")
        assert wm.has("key1") is False

    def test_summarization_trigger(self):
        # 100 token max, summarize at 75%
        wm = WorkingMemory(max_tokens=100, summarize_at_pct=0.75)
        
        # Add ~80 tokens worth of text (320 chars)
        long_text = "A" * 320
        wm.add_message("user", long_text)
        
        assert wm.utilization_pct >= 0.75
        assert wm.should_summarize() is True

    def test_compression(self):
        wm = WorkingMemory(max_tokens=1000)
        wm.add_message("system", "System prompt")
        wm.add_message("user", "Message 1")
        wm.add_message("assistant", "Message 2")
        
        wm.compress("Compressed summary")
        
        messages = wm.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "assistant"
        assert "Compressed summary" in messages[1]["content"]


class TestEpisodicMemory:
    """Test long-term structured logs."""

    @pytest.mark.asyncio
    async def test_store_and_search_local(self):
        em = EpisodicMemory() # Local stub mode
        
        record = EpisodicRecord(
            agent_id="agent-1",
            task_id="task-1",
            action_type="execute",
            quality_score=0.9,
            metadata={"task_type": "analysis"}
        )
        
        await em.store(record)
        assert em.local_store_size == 1
        
        results = await em.find_similar(agent_id="agent-1", task_type="analysis")
        assert len(results) == 1
        assert results[0].task_id == "task-1"

    @pytest.mark.asyncio
    async def test_agent_performance(self):
        em = EpisodicMemory()
        
        # Add 3 records
        await em.store_batch([
            EpisodicRecord(agent_id="agent-1", task_id="t1", action_type="execute", quality_score=1.0, duration_ms=1000, tokens_used=100),
            EpisodicRecord(agent_id="agent-1", task_id="t2", action_type="execute", quality_score=0.8, duration_ms=2000, tokens_used=200),
            EpisodicRecord(agent_id="agent-1", task_id="t3", action_type="escalate", quality_score=None, duration_ms=500, tokens_used=50),
        ])
        
        metrics = await em.get_agent_performance("agent-1")
        assert metrics["total_tasks"] == 3
        assert metrics["avg_quality_score"] == 0.9 # (1.0 + 0.8) / 2
        assert metrics["escalation_count"] == 1
        assert metrics["total_tokens"] == 350


class TestSemanticMemoryAndValidity:
    """Test vector DB memory and KB decay engine."""

    @pytest.mark.asyncio
    async def test_ingest_and_search_local(self):
        sm = SemanticMemory()
        
        doc = SemanticDocument(
            title="Test Doc",
            content="Some health guidelines",
            vertical="healthcare",
            domain="Guidelines",
            current_confidence=0.9
        )
        await sm.ingest(doc)
        
        results = await sm.search("health", vertical="healthcare", min_confidence=0.8)
        assert len(results) == 1
        assert results[0].document.title == "Test Doc"
        
        # Filtered by confidence
        results_high = await sm.search("health", min_confidence=0.95)
        assert len(results_high) == 0

    @pytest.mark.asyncio
    async def test_supersession(self):
        sm = SemanticMemory()
        doc = SemanticDocument(title="Old", content="Old", vertical="v", domain="d")
        doc_id = await sm.ingest(doc)
        
        await sm.mark_superseded(doc_id, superseded_by="new-id")
        
        updated_doc = await sm.get_document(doc_id)
        assert updated_doc.current_confidence == 0.0
        assert updated_doc.superseded_by == "new-id"

    def test_decay_engine_calculation(self):
        sm = SemanticMemory()
        engine = KBValidityEngine(sm)
        
        now = datetime.now(timezone.utc)
        ninety_days_ago = now - timedelta(days=90)
        
        doc = SemanticDocument(
            title="Fast Decay Doc",
            content="...",
            vertical="v",
            domain="d",
            decay_rate="fast",
            validity_days=365,
            initial_confidence=1.0,
            ingested_at=ninety_days_ago
        )
        
        # For 'fast' decay and validity 365, half_life is max(30, 365/4) = 91.25 days
        # At 90 days, confidence should be roughly half (0.5)
        confidence = engine.calculate_current_confidence(doc, now)
        assert 0.45 < confidence < 0.55


class TestProceduralMemory:
    """Test procedural memory prompts and formatting."""

    def test_register_and_format_prompt(self):
        pm = ProceduralMemory()
        
        template = PromptTemplate(
            name="test_prompt",
            version="v1.0",
            system_prompt="Hello {name}. Your tier is {tier}.",
            required_inputs=["name", "tier"]
        )
        pm.register_prompt(template)
        
        formatted = pm.format_prompt("test_prompt", {"name": "Apollo", "tier": "premium"})
        assert formatted == "Hello Apollo. Your tier is premium."
        
    def test_missing_inputs_raises_error(self):
        pm = ProceduralMemory()
        template = PromptTemplate(
            name="test_prompt",
            version="v1.0",
            system_prompt="Hello {name}.",
            required_inputs=["name"]
        )
        pm.register_prompt(template)
        
        with pytest.raises(ValueError, match="Missing required inputs"):
            pm.format_prompt("test_prompt", {})


class TestIPRegistry:
    """Test IP Registry functionality."""

    @pytest.mark.asyncio
    async def test_register_and_search(self):
        registry = IPRegistry()
        
        asset = IPAsset(
            name="NABH Template",
            vertical="healthcare",
            asset_type="template",
            tags=["NABH", "compliance"]
        )
        
        await registry.register(asset)
        
        results = await registry.search(vertical="healthcare", tags=["NABH"])
        assert len(results) == 1
        assert results[0].name == "NABH Template"

    @pytest.mark.asyncio
    async def test_usage_scoring(self):
        registry = IPRegistry()
        asset = IPAsset(name="Test", vertical="v", asset_type="t")
        asset_id = await registry.register(asset)
        
        assert asset.reusability_score == 0.0
        
        # Record usage
        await registry.record_usage(asset_id)
        
        results = await registry.search()
        assert results[0].times_used == 1
        assert results[0].reusability_score > 0.0
