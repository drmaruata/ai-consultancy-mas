"""
Memory Architecture for the AI Consultancy MAS v3.0.

Implements the four-layer memory model:
- Working Memory: Ephemeral, per-task context window
- Episodic Memory: Long-term structured logs (Supabase)
- Semantic Memory: Vector DB with validity metadata (Weaviate)
- Procedural Memory: Versioned system prompts and workflows
"""

from memory.episodic import EpisodicMemory, EpisodicRecord
from memory.procedural import ProceduralMemory, PromptTemplate
from memory.semantic import SemanticDocument, SemanticMemory, SemanticSearchResult
from memory.working import WorkingMemory

__all__ = [
    "EpisodicMemory",
    "EpisodicRecord",
    "ProceduralMemory",
    "PromptTemplate",
    "SemanticDocument",
    "SemanticMemory",
    "SemanticSearchResult",
    "WorkingMemory",
]
