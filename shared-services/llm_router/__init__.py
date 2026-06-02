"""
Multi-LLM Router for the AI Consultancy MAS v3.0.

Routes LLM requests to the optimal provider based on task complexity,
context length, rate limits, and cost. Implements automatic fallback
chain: Anthropic Claude (primary) → OpenAI → Google Gemini.
"""

from llm_router.config import LLMRouterConfig, ProviderConfig
from llm_router.models import LLMProvider, LLMRequest, LLMResponse
from llm_router.router import LLMRouter

__all__ = [
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "LLMRouter",
    "LLMRouterConfig",
    "ProviderConfig",
]
