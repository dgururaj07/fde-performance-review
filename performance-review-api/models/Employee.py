from pydantic import BaseModel

class employees(BaseModel):
    id: int
    employee_id: str
    name: str
    department: str
    email: str
    status: str