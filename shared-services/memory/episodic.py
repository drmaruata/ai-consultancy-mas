"""Episodic Memory — long-term structured logs of past agent tasks.

Episodic memory records every completed task with its context, quality
score, and outcome. It powers the Self-Improvement Engine by enabling
agents to learn from past experiences and avoid repeating mistakes.

Backed by Supabase (PostgreSQL) for durability and queryability.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class EpisodicRecord(BaseModel):
    """A single episodic memory record — one completed agent action.

    Stored in the `episodic_memory` table in Supabase.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    task_id: str
    client_id: str | None = None
    vertical: str | None = None
    action_type: str
    """One of: 'plan', 'execute', 'reflect', 'escalate'."""
    input_summary: str = ""
    output_summary: str = ""
    quality_score: float | None = None
    tokens_used: int = 0
    duration_ms: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EpisodicMemory:
    """Long-term structured memory for past agent task executions.

    Provides:
    - Recording completed task outcomes
    - Querying similar past tasks for context
    - Computing agent performance trends
    - Feeding the Self-Improvement Engine

    Usage:
        ```python
        memory = EpisodicMemory(supabase_client=client)

        # Record a completed task
        record = EpisodicRecord(
            agent_id="healthcare-clinical-ai",
            task_id="task-123",
            action_type="execute",
            output_summary="Generated NABH gap analysis with 15 findings.",
            quality_score=0.88,
            tokens_used=2500,
            duration_ms=4500,
        )
        await memory.store(record)

        # Find similar past tasks
        similar = await memory.find_similar(
            agent_id="healthcare-clinical-ai",
            task_type="nabh_gap_analysis",
            limit=5,
        )
        ```
    """

    def __init__(self, supabase_client: Any = None) -> None:
        self._client = supabase_client
        self._log = logger.bind(component="episodic_memory")
        # In-memory fallback when Supabase is not connected
        self._local_store: list[EpisodicRecord] = []

    async def store(self, record: EpisodicRecord) -> str:
        """Persist an episodic record to Supabase.

        Args:
            record: The episodic memory record to store.

        Returns:
            The record ID.
        """
        if self._client:
            try:
                data = record.model_dump(mode="json")
                result = self._client.table("episodic_memory").insert(data).execute()
                self._log.info(
                    "episodic_record_stored",
                    record_id=record.id,
                    agent_id=record.agent_id,
                    task_id=record.task_id,
                )
                return record.id
            except Exception as e:
                self._log.error("episodic_store_failed", error=str(e))
                # Fall through to local store

        self._local_store.append(record)
        self._log.debug(
            "episodic_record_stored_locally",
            record_id=record.id,
            store_size=len(self._local_store),
        )
        return record.id

    async def store_batch(self, records: list[EpisodicRecord]) -> int:
        """Store multiple episodic records at once.

        Returns:
            Number of successfully stored records.
        """
        count = 0
        for record in records:
            try:
                await self.store(record)
                count += 1
            except Exception as e:
                self._log.error(
                    "episodic_batch_store_failed",
                    record_id=record.id,
                    error=str(e),
                )
        return count

    async def find_similar(
        self,
        agent_id: str,
        task_type: str | None = None,
        vertical: str | None = None,
        limit: int = 5,
    ) -> list[EpisodicRecord]:
        """Find similar past tasks for context and learning.

        Searches episodic memory for tasks with matching agent, type,
        or vertical. Results are ordered by recency.

        Args:
            agent_id: The agent whose past tasks to search.
            task_type: Optional filter by task type.
            vertical: Optional filter by vertical.
            limit: Maximum number of results.

        Returns:
            List of matching episodic records, most recent first.
        """
        if self._client:
            try:
                query = (
                    self._client.table("episodic_memory")
                    .select("*")
                    .eq("agent_id", agent_id)
                    .order("created_at", desc=True)
                    .limit(limit)
                )
                if task_type:
                    query = query.eq("metadata->>task_type", task_type)
                if vertical:
                    query = query.eq("vertical", vertical)

                result = query.execute()
                return [EpisodicRecord.model_validate(row) for row in result.data]
            except Exception as e:
                self._log.error("episodic_query_failed", error=str(e))

        # Fallback: search local store
        matches = [
            r for r in self._local_store
            if r.agent_id == agent_id
            and (task_type is None or r.metadata.get("task_type") == task_type)
            and (vertical is None or r.vertical == vertical)
        ]
        matches.sort(key=lambda r: r.created_at, reverse=True)
        return matches[:limit]

    async def get_agent_performance(
        self,
        agent_id: str,
        days: int = 30,
    ) -> dict[str, Any]:
        """Compute performance metrics for an agent over a time period.

        Returns:
            Dict with avg_quality_score, total_tasks, avg_duration_ms,
            total_tokens, escalation_count.
        """
        if self._client:
            try:
                from_date = datetime.now(UTC).isoformat()
                result = (
                    self._client.table("episodic_memory")
                    .select("quality_score, tokens_used, duration_ms, action_type")
                    .eq("agent_id", agent_id)
                    .gte("created_at", from_date)
                    .execute()
                )
                rows = result.data
            except Exception as e:
                self._log.error("performance_query_failed", error=str(e))
                rows = []
        else:
            rows = [
                r.model_dump() for r in self._local_store
                if r.agent_id == agent_id
            ]

        if not rows:
            return {
                "agent_id": agent_id,
                "total_tasks": 0,
                "avg_quality_score": 0.0,
                "avg_duration_ms": 0,
                "total_tokens": 0,
                "escalation_count": 0,
            }

        scores = [r["quality_score"] for r in rows if r.get("quality_score") is not None]
        durations = [r["duration_ms"] for r in rows if r.get("duration_ms")]
        tokens = sum(r.get("tokens_used", 0) for r in rows)
        escalations = sum(1 for r in rows if r.get("action_type") == "escalate")

        return {
            "agent_id": agent_id,
            "total_tasks": len(rows),
            "avg_quality_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
            "avg_duration_ms": round(sum(durations) / len(durations)) if durations else 0,
            "total_tokens": tokens,
            "escalation_count": escalations,
        }

    async def get_recent(self, limit: int = 20) -> list[EpisodicRecord]:
        """Get the most recent episodic records across all agents."""
        if self._client:
            try:
                result = (
                    self._client.table("episodic_memory")
                    .select("*")
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute()
                )
                return [EpisodicRecord.model_validate(row) for row in result.data]
            except Exception as e:
                self._log.error("recent_query_failed", error=str(e))

        sorted_records = sorted(self._local_store, key=lambda r: r.created_at, reverse=True)
        return sorted_records[:limit]

    @property
    def local_store_size(self) -> int:
        """Number of records in the local fallback store."""
        return len(self._local_store)
