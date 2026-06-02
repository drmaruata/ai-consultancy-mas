"""Execution context models passed to agents during task processing."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskContext(BaseModel):
    """Context for a single task being processed by an agent.

    Created by the CEO Orchestrator or a Vertical Manager when assigning
    a task to an agent. Carries all metadata needed for execution.
    """

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    engagement_id: str | None = None
    """ID of the parent consulting engagement, if applicable."""
    client_id: str | None = None
    vertical: str | None = None
    task_type: str = ""
    """Classification of the task (e.g. 'nabh_gap_analysis', 'contract_review')."""
    description: str = ""
    priority: int = Field(default=5, ge=1, le=10)
    """1 = highest priority, 10 = lowest."""
    deadline: datetime | None = None

    # DAG context
    parent_task_id: str | None = None
    """If this is a sub-task, the parent task ID."""
    depends_on: list[str] = Field(default_factory=list)
    """Task IDs that must complete before this task can start."""

    # Input data
    input_data: dict[str, Any] = Field(default_factory=dict)
    """Arbitrary input payload for the task."""

    # IP Registry hint
    suggested_ip_assets: list[str] = Field(default_factory=list)
    """IP Registry asset IDs suggested for this task."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentContext(BaseModel):
    """Runtime context available to an agent during execution.

    Aggregates the agent's configuration, current task, working memory,
    and references to shared services (KB, IP Registry, message bus).
    """

    agent_id: str
    task: TaskContext

    # Working memory (ephemeral, per-task)
    working_memory: dict[str, Any] = Field(default_factory=dict)
    """Key-value store for intermediate results during task execution."""

    # Retrieved context
    kb_documents: list[dict[str, Any]] = Field(default_factory=list)
    """Relevant KB documents retrieved from semantic memory."""
    ip_assets: list[dict[str, Any]] = Field(default_factory=list)
    """Matching IP Registry assets found during Phase 0 check."""
    episodic_references: list[dict[str, Any]] = Field(default_factory=list)
    """Similar past tasks retrieved from episodic memory."""

    # Token tracking
    tokens_used: int = 0
    token_budget_remaining: int = 0

    # Conversation history (for multi-turn reasoning)
    messages: list[dict[str, str]] = Field(default_factory=list)
    """LLM conversation history: [{'role': 'system'|'user'|'assistant', 'content': '...'}]"""

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the conversation history."""
        self.messages.append({"role": role, "content": content})

    def update_working_memory(self, key: str, value: Any) -> None:
        """Store an intermediate result in working memory."""
        self.working_memory[key] = value

    def track_tokens(self, tokens: int) -> None:
        """Record token usage and decrement remaining budget."""
        self.tokens_used += tokens
        self.token_budget_remaining = max(0, self.token_budget_remaining - tokens)
