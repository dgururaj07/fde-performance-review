"""Business logic. No SQL and no FastAPI imports here."""

from typing import Optional

from models.PerformanceReview import Review, ReviewStatus
from repositories import PerformanceReviewRepository


class NotFoundError(Exception):
    """Raised when a requested record does not exist."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def list_reviews(employee_id: Optional[int] = None, period_id: Optional[int] = None) -> list[Review]:
    rows = PerformanceReviewRepository.list_reviews(employee_id=employee_id, period_id=period_id)
    # status is a display label for saved reviews, not a database column.
    return [Review(**row, status=ReviewStatus.COMPLETED) for row in rows]


def get_review(review_id: int) -> Review:
    row = PerformanceReviewRepository.get_review(review_id)
    if row is None:
        raise NotFoundError("REVIEW_NOT_FOUND", f"No review exists with id {review_id}.")
    return Review(**row, status=ReviewStatus.COMPLETED)
