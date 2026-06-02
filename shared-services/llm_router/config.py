"""Configuration for the LLM Router and individual providers."""

from __future__ import annotations

from pydantic import BaseModel, Field, SecretStr

from llm_router.models import LLMProvider


class ProviderConfig(BaseModel):
    """Configuration for a single LLM provider."""

    provider: LLMProvider
    api_key: SecretStr
    """API key (loaded from environment variables)."""
    base_url: str | None = None
    """Custom API base URL (for local/self-hosted models)."""

    default_model: str
    """Default model to use when no specific model is requested."""
    fallback_model: str | None = None
    """Cheaper/faster model for fallback within the same provider."""

    max_context_tokens: int = 200_000
    """Maximum context window supported by the default model."""
    max_output_tokens: int = 8_192

    rate_limit_rpm: int = 1000
    """Requests per minute rate limit."""
    rate_limit_tpm: int = 400_000
    """Tokens per minute rate limit."""

    enabled: bool = True
    """If False, provider is skipped during routing."""

    # Cost tracking
    input_cost_per_1k_tokens: float = 0.003
    output_cost_per_1k_tokens: float = 0.015


class CacheConfig(BaseModel):
    """Configuration for the response cache."""

    enabled: bool = True
    ttl_seconds: int = Field(default=3600, ge=60, le=86400)
    """Cache TTL in seconds (default: 1 hour)."""
    max_entries: int = Field(default=10_000, ge=100)
    """Maximum number of cached responses."""


class LLMRouterConfig(BaseModel):
    """Top-level configuration for the Multi-LLM Router.

    Example config (from environment / YAML):
        ```yaml
        providers:
          - provider: anthropic
            api_key: ${ANTHROPIC_API_KEY}
            default_model: claude-sonnet-4-20250514
            rate_limit_rpm: 1000
          - provider: openai
            api_key: ${OPENAI_API_KEY}
            default_model: gpt-4o
            rate_limit_rpm: 500
          - provider: gemini
            api_key: ${GEMINI_API_KEY}
            default_model: gemini-2.5-pro
            rate_limit_rpm: 300
        priority_chain:
          - anthropic
          - openai
          - gemini
        ```
    """

    providers: list[ProviderConfig] = Field(default_factory=list)

    priority_chain: list[LLMProvider] = Field(
        default=[LLMProvider.ANTHROPIC, LLMProvider.OPENAI, LLMProvider.GEMINI]
    )
    """Ordered list of providers to try. First available wins."""

    # Routing thresholds
    complexity_threshold_for_premium: float = Field(default=0.7, ge=0.0, le=1.0)
    """Tasks above this complexity use the primary model; below may use cheaper models."""

    # Retry configuration
    max_retries_per_provider: int = Field(default=2, ge=0, le=5)
    retry_delay_seconds: float = Field(default=1.0, ge=0.1, le=30.0)

    # Caching
    cache: CacheConfig = Field(default_factory=CacheConfig)

    # Budget controls
    global_daily_budget_usd: float = Field(default=100.0, ge=0.0)
    """Global daily spending cap across all providers."""
    alert_threshold_pct: float = Field(default=0.80, ge=0.5, le=1.0)
    """Alert when daily spend reaches this fraction of the budget."""

    def get_provider_config(self, provider: LLMProvider) -> ProviderConfig | None:
        """Look up the configuration for a specific provider."""
        for p in self.providers:
            if p.provider == provider and p.enabled:
                return p
        return None
