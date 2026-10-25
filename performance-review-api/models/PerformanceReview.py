from pydantic import BaseModel
from sqlalchemy import VARCHAR



class performance_reviews(BaseModel):
    id: int
    employee_id: int
    period_id: int
    quality_rating: int
    delivery_rating: int
    teamwork_rating: int
    average_rating: float
    comments: str
    created_at: str
