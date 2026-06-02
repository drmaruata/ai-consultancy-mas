"""Working Memory — ephemeral, per-task context window management.

Working memory is the agent's short-term scratchpad during task execution.
It manages the LLM conversation history, intermediate results, and token
counting with automatic summarization when the context window fills up.

This is entirely in-process and is discarded after task completion.
Important results should be persisted to Episodic Memory before disposal.
"""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger()


class WorkingMemory:
    """Ephemeral context window for a single agent task execution.

    Manages:
    - Conversation history (system/user/assistant messages)
    - Key-value scratchpad for intermediate results
    - Token counting with configurable window limits
    - Automatic context summarization when nearing the window limit

    Usage:
        ```python
        wm = WorkingMemory(max_tokens=16_000)
        wm.add_message("system", "You are a healthcare compliance agent.")
        wm.add_message("user", "Analyze NABH gaps for Apollo Hospital.")
        wm.set("client_profile", {"name": "Apollo", "tier": "premium"})

        # Check before sending to LLM
        if wm.should_summarize():
            summary = wm.get_context_summary()
            wm.compress(summary)
        ```
    """

    def __init__(self, max_tokens: int = 16_000, summarize_at_pct: float = 0.75) -> None:
        self._messages: list[dict[str, str]] = []
        self._scratchpad: dict[str, Any] = {}
        self._max_tokens = max_tokens
        self._summarize_at_pct = summarize_at_pct
        self._estimated_tokens = 0
        self._log = logger.bind(component="working_memory")

    # ── Message Management ───────────────────────────────────────────

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history.

        Args:
            role: One of 'system', 'user', 'assistant'.
            content: The message text.
        """
        if role not in ("system", "user", "assistant"):
            raise ValueError(f"Invalid role '{role}'. Must be 'system', 'user', or 'assistant'.")
        self._messages.append({"role": role, "content": content})
        self._estimated_tokens += self._estimate_tokens(content)

    def get_messages(self) -> list[dict[str, str]]:
        """Return the current conversation history."""
        return list(self._messages)

    def get_last_message(self) -> dict[str, str] | None:
        """Return the most recent message, or None if empty."""
        return self._messages[-1] if self._messages else None

    @property
    def message_count(self) -> int:
        """Number of messages in the conversation history."""
        return len(self._messages)

    # ── Scratchpad ───────────────────────────────────────────────────

    def set(self, key: str, value: Any) -> None:
        """Store an intermediate result in the scratchpad."""
        self._scratchpad[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the scratchpad."""
        return self._scratchpad.get(key, default)

    def has(self, key: str) -> bool:
        """Check if a key exists in the scratchpad."""
        return key in self._scratchpad

    def delete(self, key: str) -> None:
        """Remove a key from the scratchpad."""
        self._scratchpad.pop(key, None)

    def get_all(self) -> dict[str, Any]:
        """Return a copy of the entire scratchpad."""
        return dict(self._scratchpad)

    # ── Token Management ─────────────────────────────────────────────

    @property
    def estimated_tokens(self) -> int:
        """Estimated total tokens in the conversation history."""
        return self._estimated_tokens

    @property
    def tokens_remaining(self) -> int:
        """Estimated tokens remaining before hitting the window limit."""
        return max(0, self._max_tokens - self._estimated_tokens)

    @property
    def utilization_pct(self) -> float:
        """Fraction of the context window currently in use."""
        if self._max_tokens == 0:
            return 1.0
        return self._estimated_tokens / self._max_tokens

    def should_summarize(self) -> bool:
        """Returns True if the context window is filling up and needs compression."""
        return self.utilization_pct >= self._summarize_at_pct

    def compress(self, summary: str) -> None:
        """Replace conversation history with a compressed summary.

        Keeps the system message (if any) and replaces all other messages
        with a single summary message, freeing up context window space.

        Args:
            summary: A concise summary of the conversation so far.
        """
        system_messages = [m for m in self._messages if m["role"] == "system"]
        self._messages = system_messages + [
            {"role": "assistant", "content": f"[Context Summary]\n{summary}"}
        ]
        self._estimated_tokens = sum(
            self._estimate_tokens(m["content"]) for m in self._messages
        )
        self._log.info(
            "context_compressed",
            new_token_estimate=self._estimated_tokens,
            utilization_pct=round(self.utilization_pct, 2),
        )

    def get_context_summary(self) -> str:
        """Generate a plain-text summary of the current conversation.

        This is a simple concatenation — agents should use an LLM call
        for more intelligent summarization in production.
        """
        parts: list[str] = []
        for msg in self._messages:
            if msg["role"] != "system":
                parts.append(f"[{msg['role']}]: {msg['content'][:200]}")
        return "\n".join(parts)

    # ── Lifecycle ────────────────────────────────────────────────────

    def clear(self) -> None:
        """Reset all working memory (messages and scratchpad)."""
        self._messages.clear()
        self._scratchpad.clear()
        self._estimated_tokens = 0

    def snapshot(self) -> dict[str, Any]:
        """Create a serializable snapshot of the working memory.

        Useful for persisting to Episodic Memory before disposal.
        """
        return {
            "messages": list(self._messages),
            "scratchpad": dict(self._scratchpad),
            "estimated_tokens": self._estimated_tokens,
            "message_count": len(self._messages),
        }

    # ── Internal ─────────────────────────────────────────────────────

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token estimate: ~4 characters per token for English text."""
        return max(1, len(text) // 4)
