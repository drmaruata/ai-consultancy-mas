"""
Core Agent Framework for the AI Consultancy MAS v3.0.

Provides base agent classes, lifecycle management, reasoning modes,
and guardrail hooks for all 43 agents in the system.
"""

from agent_framework.base import BaseAgent
from agent_framework.config import AgentConfig
from agent_framework.context import AgentContext, TaskContext
from agent_framework.enums import AgentState, AgentTier, ReasoningMode, Vertical

__all__ = [
    "AgentConfig",
    "AgentContext",
    "AgentState",
    "AgentTier",
    "BaseAgent",
    "ReasoningMode",
    "TaskContext",
    "Vertical",
]
