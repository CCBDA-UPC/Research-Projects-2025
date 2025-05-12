from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from dynatrace.backend.dynatrace_logger import send_log_to_dynatrace
from dynatrace.backend.otel_metrics import setup_metrics
import time, random
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
FastAPIInstrumentor().instrument_app(app)

# Setup OpenTelemetry meter
meter = setup_metrics()
# Replace histogram with counter
overload_duration = meter.create_up_down_counter(
    "overload_duration_seconds",
    unit="s",
    description="Duration of overload simulations (as up/down counter)"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or set to ["http://localhost:5500"] for stricter control
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Thing(BaseModel):
    item: str

@app.post("/add-thing")
def add_thing(data: Thing):
    send_log_to_dynatrace(
        f"Adding thing: {data.item}",
        level="INFO",
        route="/add-thing",
        item=data.item
    )
    return {"message": f"Thing '{data.item}' added successfully."}

@app.post("/overload")
def overload_app():
    send_log_to_dynatrace("Overload triggered", level="WARNING", route="/overload")

    start = time.time()
    for _ in range(5_000_000):
        _ = random.random() * random.random()
    duration = time.time() - start

    overload_duration.add(duration, {"route": "/overload"})

    send_log_to_dynatrace(f"Overload completed in {duration:.2f}s", level="INFO", duration=f"{duration:.2f}")
    return {"status": "Overload simulated"}


from fastapi.responses import JSONResponse
@app.get("/random-error")
def always_fail():
    send_log_to_dynatrace(
        "Intentional error triggered",
        level="ERROR",
        route="/random-error",
        error="ForcedError"
    )
    return JSONResponse(
        status_code=500,
        content={"error": "This error was intentionally triggered."}
    )