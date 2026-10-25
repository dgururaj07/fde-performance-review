
from pydantic import BaseModel


class review_periods(BaseModel):
    id: int
    name: str
    start_date: str
    end_date: str
    status: str