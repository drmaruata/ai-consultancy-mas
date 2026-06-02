"""KB Validity Decay Engine.

Implements the decay logic for Semantic Memory documents.
Documents have a natural half-life based on their domain (fast/medium/slow).
When a document's confidence drops below thresholds, agents are prevented
from citing it without verification.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime

import structlog

from memory.semantic import SemanticDocument, SemanticMemory

logger = structlog.get_logger()


class KBValidityEngine:
    """Computes and updates confidence decay for KB documents.

    Uses a logarithmic decay curve based on the document's 'validity_days'
    and 'decay_rate'.

    Decay Profiles:
        - fast (e.g. daily legal amendments): half-life of ~90 days
        - medium (e.g. annual budget guidelines): half-life of ~180 days
        - slow (e.g. foundational acts): half-life of ~365 days

    Usage:
        ```python
        engine = KBValidityEngine(semantic_memory)
        await engine.run_decay_sweep()
        ```
    """

    def __init__(self, semantic_memory: SemanticMemory) -> None:
        self._memory = semantic_memory
        self._log = logger.bind(component="kb_validity_engine")

    def calculate_current_confidence(self, doc: SemanticDocument, current_time: datetime | None = None) -> float:
        """Calculate a document's current confidence score based on age and decay rate."""
        if doc.superseded_by:
            return 0.0

        if current_time is None:
            current_time = datetime.now(UTC)

        age_days = (current_time - doc.ingested_at).total_seconds() / 86400.0
        if age_days < 0:
            return doc.initial_confidence

        # Exponential decay: C(t) = C(0) * (0.5 ^ (t / half_life))
        half_life_days = self._get_half_life(doc.decay_rate, doc.validity_days)

        decay_factor = math.pow(0.5, age_days / half_life_days)
        new_confidence = doc.initial_confidence * decay_factor

        # Round to 4 decimal places
        return round(max(0.0, min(1.0, new_confidence)), 4)

    def _get_half_life(self, decay_rate: str, validity_days: int) -> float:
        """Determine the half-life in days based on the decay rate."""
        # Typically validity_days is the absolute expiration (if confidence hits near 0)
        # We set the half-life such that at validity_days, confidence is ~0.1
        if decay_rate == "fast":
            return max(30.0, validity_days / 4.0)
        elif decay_rate == "medium":
            return max(90.0, validity_days / 3.0)
        elif decay_rate == "slow":
            return max(180.0, validity_days / 2.0)
        else:
            return max(90.0, validity_days / 3.0)

    async def update_document(self, doc: SemanticDocument, current_time: datetime | None = None) -> bool:
        """Calculate new confidence and update it in semantic memory if changed."""
        new_confidence = self.calculate_current_confidence(doc, current_time)

        # Only update if changed by more than 0.01 (1%) to avoid excessive writes
        if abs(new_confidence - doc.current_confidence) >= 0.01:
            success = await self._memory.update_confidence(doc.doc_id, new_confidence)
            if success:
                doc.current_confidence = new_confidence
                doc.last_validated_at = current_time or datetime.now(UTC)
            return success
        return False
