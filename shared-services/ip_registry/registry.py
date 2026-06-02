"""IP Registry — centralized store for reusable templates and accelerators.

The IP Registry manages the metadata for reusable assets like document templates,
workflow blueprints, and product accelerators. It tracks how often assets are
used and computes a reusability score to identify highly valuable IP.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class IPAsset(BaseModel):
    """A reusable IP asset (template, accelerator, blueprint)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    vertical: str
    asset_type: str
    """'template', 'accelerator', 'product', 'workflow_blueprint'"""
    description: str = ""
    reusability_score: float = 0.0
    times_used: int = 0
    source_engagement_id: str | None = None
    deliverable_path: str = ""
    """Path or URI to the actual asset content (e.g. Supabase Storage)."""
    tags: list[str] = Field(default_factory=list)
    status: str = "active"
    """'active', 'deprecated', 'draft'"""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class IPRegistry:
    """Manages reusable IP assets.

    Provides:
    - Registering new IP assets extracted from engagements
    - Searching available assets for reuse
    - Tracking usage to compute reusability scores

    Usage:
        ```python
        registry = IPRegistry(supabase_client=client)

        # Search for a template
        assets = await registry.search(
            vertical="healthcare",
            asset_type="template",
            tags=["NABH"],
        )

        # Record usage
        if assets:
            await registry.record_usage(assets[0].id)
        ```
    """

    def __init__(self, supabase_client: Any = None) -> None:
        self._client = supabase_client
        self._log = logger.bind(component="ip_registry")
        self._local_store: dict[str, IPAsset] = {}

    async def register(self, asset: IPAsset) -> str:
        """Register a new IP asset."""
        if self._client:
            try:
                data = asset.model_dump(mode="json")
                self._client.table("ip_registry").insert(data).execute()
                self._log.info(
                    "ip_asset_registered",
                    asset_id=asset.id,
                    name=asset.name,
                )
                return asset.id
            except Exception as e:
                self._log.error("ip_register_failed", error=str(e))

        self._local_store[asset.id] = asset
        self._log.debug(
            "ip_asset_registered_locally",
            asset_id=asset.id,
        )
        return asset.id

    async def search(
        self,
        vertical: str | None = None,
        asset_type: str | None = None,
        tags: list[str] | None = None,
        status: str = "active",
        limit: int = 10,
    ) -> list[IPAsset]:
        """Search for reusable IP assets."""
        if self._client:
            try:
                query = (
                    self._client.table("ip_registry")
                    .select("*")
                    .eq("status", status)
                )
                if vertical:
                    query = query.eq("vertical", vertical)
                if asset_type:
                    query = query.eq("asset_type", asset_type)
                if tags:
                    query = query.contains("tags", tags)

                result = query.order("reusability_score", desc=True).limit(limit).execute()
                return [IPAsset.model_validate(row) for row in result.data]
            except Exception as e:
                self._log.error("ip_search_failed", error=str(e))

        # Local fallback
        matches = []
        for asset in self._local_store.values():
            if asset.status != status:
                continue
            if vertical and asset.vertical != vertical:
                continue
            if asset_type and asset.asset_type != asset_type:
                continue
            if tags and not all(t in asset.tags for t in tags):
                continue
            matches.append(asset)

        matches.sort(key=lambda a: a.reusability_score, reverse=True)
        return matches[:limit]

    async def record_usage(self, asset_id: str) -> bool:
        """Record that an asset was used and update its reusability score.

        The reusability score is a normalized heuristic (0-1) combining
        usage count and recency (simplified here as log(count)).
        """
        import math

        if self._client:
            try:
                # Fetch current usage
                result = self._client.table("ip_registry").select("times_used").eq("id", asset_id).execute()
                if not result.data:
                    return False

                new_count = result.data[0]["times_used"] + 1
                # Simple logarithmic scoring, maxing out around 100 uses
                new_score = min(1.0, math.log10(new_count + 1) / 2.0)

                self._client.table("ip_registry").update({
                    "times_used": new_count,
                    "reusability_score": new_score,
                    "updated_at": datetime.now(UTC).isoformat(),
                }).eq("id", asset_id).execute()

                self._log.info(
                    "ip_usage_recorded",
                    asset_id=asset_id,
                    new_count=new_count,
                    new_score=round(new_score, 3),
                )
                return True
            except Exception as e:
                self._log.error("ip_record_usage_failed", error=str(e))

        # Local fallback
        if asset_id in self._local_store:
            asset = self._local_store[asset_id]
            asset.times_used += 1
            asset.reusability_score = min(1.0, math.log10(asset.times_used + 1) / 2.0)
            asset.updated_at = datetime.now(UTC)
            return True

        return False
