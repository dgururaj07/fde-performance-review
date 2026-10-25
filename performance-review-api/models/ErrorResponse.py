"""Pydantic model for application errors (OpenAPI: ErrorResponse)."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(..., examples=["DUPLICATE_REVIEW"])
    message: str = Field(..., examples=["A review already exists for this employee and period."])
