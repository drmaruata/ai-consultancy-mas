"""Data models for LLM requests, responses, and provider identifiers."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class LLMProvider(StrEnum):
    """Supported LLM providers.

    Priority order (confirmed):
        1. ANTHROPIC (primary)
        2. OPENAI (secondary fallback)
        3. GEMINI (tertiary fallback)
        4. LOCAL (Phase 5 — air-gapped deployments)
    """

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    LOCAL = "local"


class LLMRequest(BaseModel):
    """Unified request model for all LLM providers.

    The router translates this into provider-specific API calls.
    """

    messages: list[dict[str, str]]
    """Conversation history: [{'role': 'system'|'user'|'assistant', 'content': '...'}]"""
    model: str | None = None
    """Specific model override (e.g. 'claude-sonnet-4-20250514'). If None, router selects."""
    max_tokens: int = Field(default=4_096, ge=1, le=200_000)
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)

    # Routing hints
    preferred_provider: LLMProvider | None = None
    """Force a specific provider. If None, router uses priority chain."""
    require_air_gapped: bool = False
    """If True, only route to LOCAL provider (Phase 5)."""
    task_complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    """Hint for routing: 0.0 = trivial, 1.0 = extremely complex."""
    context_length_estimate: int = Field(default=0, ge=0)
    """Estimated total context length in tokens (for provider selection)."""

    # Budget tracking
    agent_id: str = ""
    task_id: str = ""

    # Caching
    cache_key: str | None = None
    """If set, response is cached and reused for identical requests (TTL: 1 hour)."""

    # Structured output
    response_format: dict[str, Any] | None = None
    """JSON schema for structured output (provider-dependent support)."""


class LLMResponse(BaseModel):
    """Unified response model from any LLM provider."""

    content: str
    """The generated text response."""
    provider: LLMProvider
    """Which provider actually served the request."""
    model: str
    """Specific model that generated the response."""

    # Token usage
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    # Metadata
    latency_ms: int = 0
    cached: bool = False
    fallback_used: bool = False
    """True if the response came from a fallback provider."""
    original_provider: LLMProvider | None = None
    """If fallback_used, the provider that was originally tried."""

    # Structured output
    parsed_output: dict[str, Any] | None = None
    """Parsed JSON if response_format was requested and parsing succeeded."""

    @property
    def estimated_cost_usd(self) -> float:
        """Rough cost estimate based on provider and token counts.

        These are approximate rates and should be updated periodically.
        """
        rates: dict[str, tuple[float, float]] = {
            # (input_per_1k, output_per_1k)
            "anthropic": (0.003, 0.015),
            "openai": (0.005, 0.015),
            "gemini": (0.00035, 0.00105),
            "local": (0.0, 0.0),
        }
        input_rate, output_rate = rates.get(self.provider.value, (0.01, 0.03))
        return (self.input_tokens / 1000 * input_rate) + (
            self.output_tokens / 1000 * output_rate
        )
