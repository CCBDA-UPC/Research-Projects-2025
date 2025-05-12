import os
from dotenv import load_dotenv

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

load_dotenv()

# Setup Tracing Provider
trace.set_tracer_provider(TracerProvider())
tracer_provider = trace.get_tracer_provider()

# Configure OTLP exporter for Dynatrace
otlp_exporter = OTLPSpanExporter(
    endpoint= f"{os.getenv('DYNATRACE_OTLP_ENDPOINT')}/v1/traces",
    headers={"Authorization": f"Api-Token {os.getenv('DYNATRACE_API_TOKEN')}"}
)

span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)
