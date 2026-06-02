"""Multi-LLM Router — intelligent request routing with automatic fallback.

Routes LLM requests to the optimal provider (Anthropic → OpenAI → Gemini)
based on task complexity, context length, rate limits, and cost. Handles
provider failures with automatic fallback and implements response caching.
"""

from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from typing import Any

import httpx
import structlog

from llm_router.config import LLMRouterConfig, ProviderConfig
from llm_router.models import LLMProvider, LLMRequest, LLMResponse

logger = structlog.get_logger()


class LLMProviderError(Exception):
    """Raised when an LLM provider returns an error."""

    def __init__(self, provider: LLMProvider, status_code: int, message: str) -> None:
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"{provider.value} error ({status_code}): {message}")


class LLMRateLimitError(LLMProviderError):
    """Raised when an LLM provider rate limit is hit."""
    pass


class LLMBudgetExceededError(Exception):
    """Raised when the daily spending budget is exceeded."""
    pass


class LLMRouter:
    """Intelligent multi-provider LLM router with fallback and caching.

    Usage:
        ```python
        config = LLMRouterConfig(providers=[...])
        router = LLMRouter(config)

        request = LLMRequest(
            messages=[{"role": "user", "content": "Analyze NABH compliance..."}],
            agent_id="healthcare-regulatory",
            task_id="task-123",
        )
        response = await router.complete(request)
        print(response.content)
        ```
    """

    def __init__(self, config: LLMRouterConfig, supabase_client: Any = None, producer: Any = None) -> None:
        self._config = config
        self._http_client = httpx.AsyncClient(timeout=120.0)
        self._cache: dict[str, tuple[LLMResponse, float]] = {}
        self._daily_spend: float = 0.0
        self._daily_spend_reset: float = 0.0
        self._rate_counters: dict[str, list[float]] = defaultdict(list)
        self._log = logger.bind(component="llm_router")
        self._supabase = supabase_client
        self._producer = producer

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Route an LLM request to the best available provider.

        Steps:
            1. Check response cache
            2. Check daily budget
            3. Determine provider chain (preferred → priority fallbacks)
            4. Try each provider in order
            5. Cache successful response
            6. Track spending (and update Supabase tasks.token_spend)
            7. Alert if overrun via Redpanda
        """
        # 1. Check cache
        if request.cache_key:
            cached = self._get_cached(request.cache_key)
            if cached:
                self._log.debug("cache_hit", cache_key=request.cache_key)
                return cached

        # 2. Check daily budget
        self._reset_daily_spend_if_needed()
        if self._daily_spend >= self._config.global_daily_budget_usd:
            raise LLMBudgetExceededError(
                f"Daily spend ${self._daily_spend:.2f} exceeds "
                f"budget ${self._config.global_daily_budget_usd:.2f}"
            )

        # 3. Determine provider chain
        chain = self._resolve_provider_chain(request)
        if not chain:
            raise LLMProviderError(
                LLMProvider.ANTHROPIC, 500, "No enabled providers available"
            )

        # 4. Try each provider
        last_error: Exception | None = None
        original_provider = chain[0]

        for i, provider in enumerate(chain):
            provider_config = self._config.get_provider_config(provider)
            if not provider_config:
                continue

            if not self._check_rate_limit(provider_config):
                self._log.warning("rate_limit_precheck_skip", provider=provider.value)
                continue

            try:
                response = await self._call_provider(request, provider_config)
                response.fallback_used = i > 0
                if i > 0:
                    response.original_provider = original_provider

                # 5. Cache
                if request.cache_key:
                    self._set_cached(request.cache_key, response)

                # 6. Track spending
                self._daily_spend += response.estimated_cost_usd
                
                # Update task.token_spend in Supabase
                if self._supabase and request.task_id:
                    try:
                        self._supabase.rpc("increment_token_spend", {
                            "p_task_id": request.task_id,
                            "p_amount": response.estimated_cost_usd
                        }).execute()
                    except Exception as e:
                        self._log.error("supabase_update_failed", error=str(e))

                # 7. Overrun Check
                overrun_threshold = self._config.global_daily_budget_usd * self._config.alert_threshold_pct
                if self._daily_spend >= overrun_threshold:
                    self._log.warning(
                        "daily_budget_alert",
                        spend=round(self._daily_spend, 4),
                        budget=self._config.global_daily_budget_usd,
                    )
                    if self._producer:
                        from messaging.schemas import MASMessage
                        class CostOverrunMessage(MASMessage):
                            topic: str = "cost.overrun"
                            spend: float
                            budget: float
                        
                        try:
                            msg = CostOverrunMessage(
                                source_agent_id="llm-router",
                                spend=self._daily_spend,
                                budget=self._config.global_daily_budget_usd
                            )
                            # Publish to a general alert topic or a specific one
                            await self._producer.publish("mas.health.report", msg)
                        except Exception as e:
                            self._log.error("cost_overrun_publish_failed", error=str(e))

                self._log.info(
                    "llm_request_complete",
                    provider=response.provider.value,
                    model=response.model,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    latency_ms=response.latency_ms,
                    cost_usd=round(response.estimated_cost_usd, 6),
                    fallback=response.fallback_used,
                    agent_id=request.agent_id,
                    task_id=request.task_id,
                )

                return response

            except LLMRateLimitError as e:
                last_error = e
                self._log.warning(
                    "provider_rate_limited",
                    provider=provider.value,
                    error=str(e),
                )
                continue

            except LLMProviderError as e:
                last_error = e
                self._log.warning(
                    "provider_error",
                    provider=provider.value,
                    status_code=e.status_code,
                    error=str(e),
                )
                continue

            except Exception as e:
                last_error = e
                self._log.error(
                    "provider_unexpected_error",
                    provider=provider.value,
                    error=str(e),
                    exc_info=True,
                )
                continue

        # All providers failed
        raise LLMProviderError(
            original_provider,
            500,
            f"All providers in chain {[p.value for p in chain]} failed. "
            f"Last error: {last_error}",
        )

    async def _call_provider(
        self, request: LLMRequest, config: ProviderConfig
    ) -> LLMResponse:
        """Make an API call to a specific LLM provider.

        Translates the unified LLMRequest into provider-specific format
        and parses the response back into the unified LLMResponse.
        """
        start_time = time.monotonic()
        model = request.model or config.default_model

        if config.provider == LLMProvider.ANTHROPIC:
            return await self._call_anthropic(request, config, model, start_time)
        elif config.provider == LLMProvider.OPENAI:
            return await self._call_openai(request, config, model, start_time)
        elif config.provider == LLMProvider.GEMINI:
            return await self._call_gemini(request, config, model, start_time)
        elif config.provider == LLMProvider.LOCAL:
            return await self._call_local(request, config, model, start_time)
        else:
            raise LLMProviderError(
                config.provider, 500, f"Unknown provider: {config.provider}"
            )

    async def _call_anthropic(
        self,
        request: LLMRequest,
        config: ProviderConfig,
        model: str,
        start_time: float,
    ) -> LLMResponse:
        """Call Anthropic Claude API."""
        base_url = config.base_url or "https://api.anthropic.com"

        # Separate system message from conversation
        system_content = ""
        messages = []
        for msg in request.messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                messages.append(msg)

        payload: dict[str, Any] = {
            "model": model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "messages": messages,
        }
        if system_content:
            payload["system"] = system_content

        headers = {
            "x-api-key": config.api_key.get_secret_value(),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        response = await self._http_client.post(
            f"{base_url}/v1/messages",
            json=payload,
            headers=headers,
        )

        if response.status_code == 429:
            raise LLMRateLimitError(LLMProvider.ANTHROPIC, 429, "Rate limited")
        if response.status_code != 200:
            raise LLMProviderError(
                LLMProvider.ANTHROPIC, response.status_code, response.text[:500]
            )

        data = response.json()
        latency_ms = int((time.monotonic() - start_time) * 1000)

        return LLMResponse(
            content=data["content"][0]["text"],
            provider=LLMProvider.ANTHROPIC,
            model=data.get("model", model),
            input_tokens=data.get("usage", {}).get("input_tokens", 0),
            output_tokens=data.get("usage", {}).get("output_tokens", 0),
            total_tokens=(
                data.get("usage", {}).get("input_tokens", 0)
                + data.get("usage", {}).get("output_tokens", 0)
            ),
            latency_ms=latency_ms,
        )

    async def _call_openai(
        self,
        request: LLMRequest,
        config: ProviderConfig,
        model: str,
        start_time: float,
    ) -> LLMResponse:
        """Call OpenAI ChatGPT API."""
        base_url = config.base_url or "https://api.openai.com"

        payload: dict[str, Any] = {
            "model": model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "messages": request.messages,
        }
        if request.response_format:
            payload["response_format"] = request.response_format

        headers = {
            "Authorization": f"Bearer {config.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

        response = await self._http_client.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            headers=headers,
        )

        if response.status_code == 429:
            raise LLMRateLimitError(LLMProvider.OPENAI, 429, "Rate limited")
        if response.status_code != 200:
            raise LLMProviderError(
                LLMProvider.OPENAI, response.status_code, response.text[:500]
            )

        data = response.json()
        usage = data.get("usage", {})
        latency_ms = int((time.monotonic() - start_time) * 1000)

        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            provider=LLMProvider.OPENAI,
            model=data.get("model", model),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            latency_ms=latency_ms,
        )

    async def _call_gemini(
        self,
        request: LLMRequest,
        config: ProviderConfig,
        model: str,
        start_time: float,
    ) -> LLMResponse:
        """Call Google Gemini API via OpenAI-compatible endpoint."""
        base_url = config.base_url or "https://generativelanguage.googleapis.com/v1beta/openai"

        payload: dict[str, Any] = {
            "model": model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "messages": request.messages,
        }

        headers = {
            "Authorization": f"Bearer {config.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

        response = await self._http_client.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers=headers,
        )

        if response.status_code == 429:
            raise LLMRateLimitError(LLMProvider.GEMINI, 429, "Rate limited")
        if response.status_code != 200:
            raise LLMProviderError(
                LLMProvider.GEMINI, response.status_code, response.text[:500]
            )

        data = response.json()
        usage = data.get("usage", {})
        latency_ms = int((time.monotonic() - start_time) * 1000)

        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            provider=LLMProvider.GEMINI,
            model=data.get("model", model),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            latency_ms=latency_ms,
        )

    async def _call_local(
        self,
        request: LLMRequest,
        config: ProviderConfig,
        model: str,
        start_time: float,
    ) -> LLMResponse:
        """Call local/air-gapped LLM via OpenAI-compatible API (vLLM/Ollama).

        Placeholder for Phase 5 — air-gapped deployments.
        """
        raise LLMProviderError(
            LLMProvider.LOCAL,
            501,
            "Local LLM provider not yet implemented (Phase 5)",
        )

    # ── Provider Chain Resolution ────────────────────────────────────

    def _resolve_provider_chain(self, request: LLMRequest) -> list[LLMProvider]:
        """Determine the ordered list of providers to try for a request."""
        if request.require_air_gapped:
            return [LLMProvider.LOCAL]

        if request.preferred_provider:
            chain = [request.preferred_provider]
            # Add remaining priority providers as fallbacks
            for p in self._config.priority_chain:
                if p != request.preferred_provider:
                    chain.append(p)
            return chain

        return list(self._config.priority_chain)

    # ── Rate Limiting ────────────────────────────────────────────────

    def _check_rate_limit(self, config: ProviderConfig) -> bool:
        """Pre-check if the provider is within rate limits.

        Uses a sliding window counter for requests per minute.
        """
        now = time.monotonic()
        key = config.provider.value
        # Clean old entries (> 60 seconds)
        self._rate_counters[key] = [
            t for t in self._rate_counters[key] if now - t < 60.0
        ]
        if len(self._rate_counters[key]) >= config.rate_limit_rpm:
            return False
        self._rate_counters[key].append(now)
        return True

    # ── Caching ──────────────────────────────────────────────────────

    def _get_cached(self, cache_key: str) -> LLMResponse | None:
        """Retrieve a cached response if it exists and hasn't expired."""
        if not self._config.cache.enabled:
            return None
        key = self._hash_cache_key(cache_key)
        entry = self._cache.get(key)
        if entry is None:
            return None
        response, cached_at = entry
        if time.monotonic() - cached_at > self._config.cache.ttl_seconds:
            del self._cache[key]
            return None
        cached_response = response.model_copy()
        cached_response.cached = True
        return cached_response

    def _set_cached(self, cache_key: str, response: LLMResponse) -> None:
        """Store a response in the cache."""
        if not self._config.cache.enabled:
            return
        # Evict oldest entries if over max
        while len(self._cache) >= self._config.cache.max_entries:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        key = self._hash_cache_key(cache_key)
        self._cache[key] = (response, time.monotonic())

    @staticmethod
    def _hash_cache_key(key: str) -> str:
        """Create a short hash for cache lookup."""
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    # ── Budget ───────────────────────────────────────────────────────

    def _reset_daily_spend_if_needed(self) -> None:
        """Reset the daily spend counter at midnight UTC."""
        now = time.time()
        # Reset every 86400 seconds (24 hours)
        if now - self._daily_spend_reset >= 86400:
            self._daily_spend = 0.0
            self._daily_spend_reset = now

    # ── Lifecycle ────────────────────────────────────────────────────

    async def close(self) -> None:
        """Clean up HTTP client resources."""
        await self._http_client.aclose()
