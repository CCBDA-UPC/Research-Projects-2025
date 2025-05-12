import os
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import set_meter_provider, get_meter_provider
from dotenv import load_dotenv

load_dotenv()



def setup_metrics():
    exporter = OTLPMetricExporter(
        endpoint=f"{os.getenv('DYNATRACE_OTLP_ENDPOINT')}/v1/metrics",
        headers={"Authorization": f"Api-Token {os.getenv('DYNATRACE_API_TOKEN')}"}
    )
    reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(metric_readers=[reader])
    set_meter_provider(provider)
    return get_meter_provider().get_meter("overload_app")
