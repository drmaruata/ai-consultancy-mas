"""Tests for the LLM Router — Sprint 0.1 acceptance criteria."""

import pytest
from pydantic import SecretStr

from llm_router import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    LLMRouter,
    LLMRouterConfig,
    ProviderConfig,
)
from llm_router.router import LLMBudgetExceededError


class TestLLMModels:
    """Test LLM request/response models."""

    def test_request_defaults(self):
        req = LLMRequest(
            messages=[{"role": "user", "content": "Hello"}],
            agent_id="test-agent",
        )
        assert req.temperature == 0.3
        assert req.max_tokens == 4096
        assert req.preferred_provider is None
        assert req.require_air_gapped is False

    def test_response_cost_estimation(self):
        resp = LLMResponse(
            content="Test response",
            provider=LLMProvider.ANTHROPIC,
            model="claude-sonnet-4-20250514",
            input_tokens=1000,
            output_tokens=500,
        )
        cost = resp.estimated_cost_usd
        assert cost > 0
        # Anthropic: (1000/1000 * 0.003) + (500/1000 * 0.015) = 0.003 + 0.0075 = 0.0105
        assert abs(cost - 0.0105) < 0.001

    def test_gemini_is_cheapest(self):
        """Verify Gemini cost model is significantly cheaper."""
        anthropic_resp = LLMResponse(
            content="Test",
            provider=LLMProvider.ANTHROPIC,
            model="claude-sonnet-4-20250514",
            input_tokens=1000,
            output_tokens=1000,
        )
        gemini_resp = LLMResponse(
            content="Test",
            provider=LLMProvider.GEMINI,
            model="gemini-2.5-pro",
            input_tokens=1000,
            output_tokens=1000,
        )
        assert gemini_resp.estimated_cost_usd < anthropic_resp.estimated_cost_usd

    def test_local_provider_is_free(self):
        resp = LLMResponse(
            content="Test",
            provider=LLMProvider.LOCAL,
            model="llama-3",
            input_tokens=5000,
            output_tokens=2000,
        )
        assert resp.estimated_cost_usd == 0.0


class TestProviderConfig:
    """Test provider configuration."""

    def test_valid_anthropic_config(self):
        config = ProviderConfig(
            provider=LLMProvider.ANTHROPIC,
            api_key=SecretStr("sk-ant-test"),
            default_model="claude-sonnet-4-20250514",
            rate_limit_rpm=1000,
        )
        assert config.provider == LLMProvider.ANTHROPIC
        assert config.enabled is True


class TestLLMRouterConfig:
    """Test router configuration."""

    def test_default_priority_chain(self):
        config = LLMRouterConfig()
        assert config.priority_chain == [
            LLMProvider.ANTHROPIC,
            LLMProvider.OPENAI,
            LLMProvider.GEMINI,
        ]

    def test_get_provider_config(self):
        config = LLMRouterConfig(
            providers=[
                ProviderConfig(
                    provider=LLMProvider.ANTHROPIC,
                    api_key=SecretStr("test"),
                    default_model="claude-sonnet-4-20250514",
                ),
            ]
        )
        pc = config.get_provider_config(LLMProvider.ANTHROPIC)
        assert pc is not None
        assert pc.default_model == "claude-sonnet-4-20250514"

        pc_missing = config.get_provider_config(LLMProvider.OPENAI)
        assert pc_missing is None

    def test_disabled_provider_not_returned(self):
        config = LLMRouterConfig(
            providers=[
                ProviderConfig(
                    provider=LLMProvider.ANTHROPIC,
                    api_key=SecretStr("test"),
                    default_model="claude-sonnet-4-20250514",
                    enabled=False,
                ),
            ]
        )
        assert config.get_provider_config(LLMProvider.ANTHROPIC) is None


class TestLLMRouter:
    """Test the LLM Router logic."""

    @pytest.fixture
    def router_config(self) -> LLMRouterConfig:
        return LLMRouterConfig(
            providers=[
                ProviderConfig(
                    provider=LLMProvider.ANTHROPIC,
                    api_key=SecretStr("test-key"),
                    default_model="claude-sonnet-4-20250514",
                ),
                ProviderConfig(
                    provider=LLMProvider.OPENAI,
                    api_key=SecretStr("test-key"),
                    default_model="gpt-4o",
                ),
            ],
            global_daily_budget_usd=50.0,
        )

    def test_provider_chain_resolution_default(self, router_config):
        router = LLMRouter(router_config)
        request = LLMRequest(
            messages=[{"role": "user", "content": "Hello"}],
        )
        chain = router._resolve_provider_chain(request)
        assert chain[0] == LLMProvider.ANTHROPIC
        assert chain[1] == LLMProvider.OPENAI
        assert chain[2] == LLMProvider.GEMINI

    def test_provider_chain_with_preferred(self, router_config):
        router = LLMRouter(router_config)
        request = LLMRequest(
            messages=[{"role": "user", "content": "Hello"}],
            preferred_provider=LLMProvider.OPENAI,
        )
        chain = router._resolve_provider_chain(request)
        assert chain[0] == LLMProvider.OPENAI  # Preferred first
        assert LLMProvider.ANTHROPIC in chain  # Others as fallback

    def test_air_gapped_forces_local(self, router_config):
        router = LLMRouter(router_config)
        request = LLMRequest(
            messages=[{"role": "user", "content": "Hello"}],
            require_air_gapped=True,
        )
        chain = router._resolve_provider_chain(request)
        assert chain == [LLMProvider.LOCAL]

    def test_rate_limit_check(self, router_config):
        router = LLMRouter(router_config)
        provider = router_config.providers[0]
        # Should pass initially
        assert router._check_rate_limit(provider) is True

    def test_cache_set_and_get(self, router_config):
        router = LLMRouter(router_config)
        response = LLMResponse(
            content="Cached content",
            provider=LLMProvider.ANTHROPIC,
            model="claude-sonnet-4-20250514",
        )
        router._set_cached("test-key", response)
        cached = router._get_cached("test-key")
        assert cached is not None
        assert cached.content == "Cached content"
        assert cached.cached is True

    def test_cache_miss(self, router_config):
        router = LLMRouter(router_config)
        assert router._get_cached("nonexistent") is None
