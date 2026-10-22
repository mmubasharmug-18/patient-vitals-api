from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.handlers import validation_error_handler
from app.routes import health, vitals

app = FastAPI(
    title="Patient Vitals API",
    version="1.0.0",
    description="Receives, validates, stores and summarizes patient vitals. Data is kept in memory.",
)

app.add_exception_handler(RequestValidationError, validation_error_handler)

app.include_router(health.router)
app.include_router(vitals.router)
