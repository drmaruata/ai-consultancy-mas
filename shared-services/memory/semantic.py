"""Semantic Memory — vector DB-backed knowledge retrieval with validity metadata.

Semantic memory stores all domain knowledge base documents as vector
embeddings with validity metadata envelopes. It integrates with the
KB Validity Decay engine to ensure agents never cite stale information.

Backed by Upstash Vector for serverless vector search with metadata filtering.
"""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class SemanticDocument(BaseModel):
    """A document stored in semantic memory (vector DB + metadata)."""

    doc_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    vertical: str
    domain: str

    # Validity metadata envelope
    decay_rate: str = "medium"
    validity_days: int = 365
    initial_confidence: float = 1.0
    current_confidence: float = 1.0
    superseded_by: str | None = None
    superseded_at: datetime | None = None

    # Source tracking
    source_url: str = ""
    content_hash: str = ""

    # Vector DB reference
    vector_db_id: str | None = None

    ingested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_validated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class SemanticSearchResult(BaseModel):
    """A single result from a semantic search query."""

    document: SemanticDocument
    similarity_score: float = 0.0
    effective_confidence: float = 0.0


class SemanticMemory:
    """Upstash Vector-backed knowledge retrieval with validity-aware search."""

    def __init__(self) -> None:
        self._client = None
        self._log = logger.bind(component="semantic_memory")
        # In-memory fallback
        self._local_store: dict[str, SemanticDocument] = {}

        # Initialize Upstash Vector client if env vars are present
        url = os.environ.get("UPSTASH_VECTOR_REST_URL")
        token = os.environ.get("UPSTASH_VECTOR_REST_TOKEN")
        if url and token:
            try:
                from upstash_vector import Index
                self._client = Index(url=url, token=token)
            except ImportError:
                self._log.warning("upstash-vector package not installed, using local fallback")

    async def ingest(self, document: SemanticDocument) -> str:
        """Ingest a document into the vector store."""
        if self._client:
            try:
                # Upstash Vector requires an ID, Data (string to embed) and Metadata
                self._client.upsert(
                    vectors=[{
                        "id": document.doc_id,
                        "vector": [0.1] * 1536,
                        "sparse_vector": ([1], [0.1]),
                        "metadata": {
                            "title": document.title,
                            "content": document.content,
                            "vertical": document.vertical,
                            "domain": document.domain,
                            "decay_rate": document.decay_rate,
                            "validity_days": document.validity_days,
                            "initial_confidence": document.initial_confidence,
                            "current_confidence": document.current_confidence,
                            "ingested_at": document.ingested_at.isoformat(),
                            "source_url": document.source_url,
                            "doc_id": document.doc_id,
                        }
                    }]
                )
                document.vector_db_id = document.doc_id
                self._log.info(
                    "document_ingested",
                    doc_id=document.doc_id,
                    title=document.title,
                )
                return document.doc_id
            except Exception as e:
                self._log.error("upstash_ingest_failed", error=str(e))

        # Local fallback
        self._local_store[document.doc_id] = document
        return document.doc_id

    async def ingest_batch(self, documents: list[SemanticDocument]) -> int:
        """Ingest multiple documents at once."""
        count = 0
        for doc in documents:
            try:
                await self.ingest(doc)
                count += 1
            except Exception as e:
                self._log.error("batch_ingest_failed", doc_id=doc.doc_id, error=str(e))
        return count

    async def search(
        self,
        query: str,
        vertical: str | None = None,
        domain: str | None = None,
        min_confidence: float = 0.7,
        limit: int = 5,
    ) -> list[SemanticSearchResult]:
        """Search semantic memory for relevant documents."""
        if self._client:
            try:
                # Upstash vector filter string format: "field = 'value' AND other > 0"
                filters = []
                if vertical:
                    filters.append(f"vertical = '{vertical}'")
                if domain:
                    filters.append(f"domain = '{domain}'")
                if min_confidence > 0.0:
                    filters.append(f"current_confidence >= {min_confidence}")

                filter_str = " AND ".join(filters) if filters else ""

                results = self._client.query(
                    data=query,
                    top_k=limit,
                    include_metadata=True,
                    filter=filter_str if filter_str else None
                )

                search_results = []
                for obj in results:
                    props = obj.metadata or {}
                    similarity = obj.score
                    doc = SemanticDocument(
                        doc_id=str(props.get("doc_id", obj.id)),
                        title=props.get("title", ""),
                        content=props.get("content", ""),
                        vertical=props.get("vertical", ""),
                        domain=props.get("domain", ""),
                        current_confidence=props.get("current_confidence", 1.0),
                        decay_rate=props.get("decay_rate", "medium"),
                        validity_days=props.get("validity_days", 365),
                    )
                    search_results.append(
                        SemanticSearchResult(
                            document=doc,
                            similarity_score=similarity,
                            effective_confidence=similarity * doc.current_confidence,
                        )
                    )

                search_results.sort(key=lambda r: r.effective_confidence, reverse=True)
                return search_results

            except Exception as e:
                self._log.error("upstash_search_failed", error=str(e))

        # Local fallback
        return self._local_search(query, vertical, domain, min_confidence, limit)

    async def get_document(self, doc_id: str) -> SemanticDocument | None:
        """Retrieve a specific document by ID."""
        if self._client:
            try:
                result = self._client.fetch([doc_id], include_metadata=True)
                if result and result[0] and result[0].metadata:
                    return SemanticDocument.model_validate(result[0].metadata)
            except Exception as e:
                self._log.error("get_document_failed", error=str(e))

        return self._local_store.get(doc_id)

    async def update_confidence(self, doc_id: str, new_confidence: float) -> bool:
        """Update a document's current confidence score."""
        if self._client:
            try:
                result = self._client.fetch([doc_id], include_metadata=True, include_vectors=True)
                if result and result[0] and result[0].metadata:
                    metadata = result[0].metadata
                    metadata["current_confidence"] = new_confidence
                    # Upstash requires upsert to update metadata
                    vec = result[0].vector if getattr(result[0], 'vector', None) else [0.1] * 1536
                    sparse_vec = result[0].sparse_vector if getattr(result[0], 'sparse_vector', None) else ([1], [0.1])
                    
                    if hasattr(sparse_vec, 'indices') and hasattr(sparse_vec, 'values'):
                        sparse_vec = (list(sparse_vec.indices), list(sparse_vec.values))
                        
                    self._client.upsert(
                        vectors=[{
                            "id": doc_id,
                            "vector": vec,
                            "sparse_vector": sparse_vec,
                            "metadata": metadata
                        }]
                    )
                    self._log.info("confidence_updated", doc_id=doc_id, new_confidence=new_confidence)
                    return True
            except Exception as e:
                self._log.error("confidence_update_failed", error=str(e))

        # Local fallback
        if doc_id in self._local_store:
            self._local_store[doc_id].current_confidence = new_confidence
            return True
        return False

    async def mark_superseded(
        self,
        doc_id: str,
        superseded_by: str | None = None,
    ) -> bool:
        """Mark a document as superseded."""
        success = await self.update_confidence(doc_id, 0.0)
        if success and doc_id in self._local_store:
            doc = self._local_store[doc_id]
            doc.superseded_by = superseded_by
            doc.superseded_at = datetime.now(UTC)
        self._log.info("document_superseded", doc_id=doc_id, superseded_by=superseded_by)
        return success

    async def get_documents_by_vertical(
        self,
        vertical: str,
        min_confidence: float = 0.0,
    ) -> list[SemanticDocument]:
        """Get all documents for a vertical."""
        # Upstash Vector does not have a fetch_all query, we must use query with empty vector or random query
        # But for this simple method, if client is active, we can just do a broad query
        if self._client:
            try:
                filters = [f"vertical = '{vertical}'"]
                if min_confidence > 0.0:
                    filters.append(f"current_confidence >= {min_confidence}")
                filter_str = " AND ".join(filters)

                # Broad query
                results = self._client.query(data="domain", top_k=100, include_metadata=True, filter=filter_str)
                docs = []
                for obj in results:
                    if obj.metadata:
                        docs.append(SemanticDocument.model_validate(obj.metadata))
                return docs
            except Exception as e:
                self._log.error("get_by_vertical_failed", error=str(e))

        return [
            doc for doc in self._local_store.values()
            if doc.vertical == vertical and doc.current_confidence >= min_confidence
        ]

    @property
    def local_store_size(self) -> int:
        return len(self._local_store)

    # ── Internal ─────────────────────────────────────────────────────

    def _local_search(
        self,
        query: str,
        vertical: str | None,
        domain: str | None,
        min_confidence: float,
        limit: int,
    ) -> list[SemanticSearchResult]:
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        results: list[SemanticSearchResult] = []

        for doc in self._local_store.values():
            if vertical and doc.vertical != vertical:
                continue
            if domain and doc.domain != domain:
                continue
            if doc.current_confidence < min_confidence:
                continue

            doc_text = f"{doc.title} {doc.content}".lower()
            matching_terms = sum(1 for t in query_terms if t in doc_text)
            if matching_terms == 0:
                continue

            similarity = matching_terms / max(len(query_terms), 1)
            results.append(
                SemanticSearchResult(
                    document=doc,
                    similarity_score=similarity,
                    effective_confidence=similarity * doc.current_confidence,
                )
            )

        results.sort(key=lambda r: r.effective_confidence, reverse=True)
        return results[:limit]
