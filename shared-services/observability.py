"""Observability & OpenTelemetry setup for MAS v4.0.

Provides standard tracing for all agent calls and router steps.
"""

import os
from contextlib import contextmanager
from typing import Iterator

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize OpenTelemetry
resource = Resource.create({"service.name": "mas-agent-system", "service.version": "4.0.0"})
provider = TracerProvider(resource=resource)

# Setup OTLP Exporter if configured (e.g. to Axiom or Grafana)
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if otlp_endpoint:
    headers = None
    otlp_token = os.getenv("OTEL_EXPORTER_OTLP_HEADERS")
    if otlp_token:
        headers = {k: v for k, v in [h.split("=") for h in otlp_token.split(",")]}
    
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, headers=headers)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


@contextmanager
def agent_trace(agent_name: str, agent_layer: int, task_id: str) -> Iterator[trace.Span]:
    """Context manager for tracing agent execution."""
    with tracer.start_as_current_span(f"{agent_name}.run") as span:
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("agent.layer", agent_layer)
        span.set_attribute("task.id", task_id)
        yield span
