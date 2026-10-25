"""FastAPI app for the Employee Performance Review API."""

from typing import Optional

import psycopg
from fastapi import APIRouter, FastAPI, Query, Request
from fastapi.responses import JSONResponse

from models.ErrorResponse import ErrorResponse
from models.PerformanceReview import Review
from services import services

app = FastAPI(title="Employee Performance Review Management System API", version="1.0.0")
router = APIRouter(prefix="/api")


@app.exception_handler(psycopg.OperationalError)
async def database_unavailable(_: Request, __: psycopg.OperationalError) -> JSONResponse:
    body = ErrorResponse(code="DATABASE_UNAVAILABLE", message="Database is unavailable. Try again later.")
    return JSONResponse(status_code=503, content=body.model_dump())


@router.get(
    "/reviews",
    response_model=list[Review],
    summary="List submitted performance reviews",
    tags=["Mandatory - Reviews"],
    operation_id="listReviews",
)
def list_reviews(
    employee_id: Optional[int] = Query(None, ge=1, description="employees.id (numeric DB key), not the EMP101-style code"),
    period_id: Optional[int] = Query(None, ge=1, description="review_periods.id (numeric DB key)"),
) -> list[Review]:
    return services.list_reviews(employee_id=employee_id, period_id=period_id)


app.include_router(router)
