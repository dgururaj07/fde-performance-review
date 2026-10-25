"""Pydantic models for the performance_reviews table (OpenAPI: ReviewCreate, Review)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class ReviewStatus(str, Enum):
    COMPLETED = "Completed"


class ReviewCreate(BaseModel):
    """Submitted values. average_rating and id are created by the backend."""

    model_config = ConfigDict(extra="forbid")

    employee_id: int = Field(..., ge=1, description="Foreign key to employees.id, NOT the employee code", examples=[1])
    period_id: int = Field(..., ge=1, description="Foreign key to review_periods.id", examples=[1])
    quality_rating: int = Field(..., ge=1, le=5, examples=[4])
    delivery_rating: int = Field(..., ge=1, le=5, examples=[5])
    teamwork_rating: int = Field(..., ge=1, le=5, examples=[4])
    comments: str = Field(
        ...,
        min_length=1,
        pattern=r"\S",
        description="Required, non-whitespace manager feedback",
        examples=["Strong ownership and collaboration throughout the review period."],
    )


class Review(BaseModel):
    """Stored performance review enriched with employee/period labels for the register UI."""

    id: int = Field(..., ge=1, examples=[101])
    employee_id: int = Field(..., ge=1, examples=[1])
    employee_code: str = Field(..., examples=["EMP101"])
    employee_name: str = Field(..., examples=["John Smith"])
    period_id: int = Field(..., ge=1, examples=[1])
    period_name: str = Field(..., examples=["H2 2026 (Jul–Dec)"])
    quality_rating: int = Field(..., ge=1, le=5, examples=[4])
    delivery_rating: int = Field(..., ge=1, le=5, examples=[5])
    teamwork_rating: int = Field(..., ge=1, le=5, examples=[4])
    average_rating: float = Field(
        ...,
        ge=1,
        le=5,
        description="Server-calculated arithmetic average rounded to 2 decimal places",
        examples=[4.33],
    )
    comments: str = Field(..., min_length=1, examples=["Strong ownership and collaboration throughout the review period."])
    status: Literal[ReviewStatus.COMPLETED] = Field(
        ReviewStatus.COMPLETED,
        description="Display-only label for submitted review; derived, not a DB column",
    )
    created_at: datetime = Field(..., examples=["2026-10-25T09:30:00Z"])

    @field_validator("average_rating")
    @classmethod
    def _round_average(cls, value: float) -> float:
        return round(value, 2)

    @field_serializer("created_at")
    def _serialize_created_at(self, value: datetime) -> str:
        # The DB column is TIMESTAMP without time zone; treat naive values as UTC.
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
