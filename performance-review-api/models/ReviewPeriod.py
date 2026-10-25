"""Pydantic models for the review_periods table (OpenAPI: ReviewPeriod)."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class ReviewPeriodStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"


class ReviewPeriod(BaseModel):
    """A review cycle; annual and half-yearly cycles are period records."""

    id: int = Field(..., ge=1, examples=[1])
    name: str = Field(..., max_length=50, examples=["H2 2026 (Jul–Dec)"])
    start_date: date = Field(..., examples=["2026-07-01"])
    end_date: date = Field(..., examples=["2026-12-31"])
    status: ReviewPeriodStatus = Field(ReviewPeriodStatus.OPEN, examples=["Open"])
