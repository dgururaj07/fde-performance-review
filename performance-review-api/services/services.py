"""Business logic. No SQL and no FastAPI imports here."""

from typing import Optional

from models.PerformanceReview import Review, ReviewStatus
from repositories import PerformanceReviewRepository


def list_reviews(employee_id: Optional[int] = None, period_id: Optional[int] = None) -> list[Review]:
    rows = PerformanceReviewRepository.list_reviews(employee_id=employee_id, period_id=period_id)
    # status is a display label for saved reviews, not a database column.
    return [Review(**row, status=ReviewStatus.COMPLETED) for row in rows]
