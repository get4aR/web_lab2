from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List

Base = declarative_base()

class StudentOut(BaseModel):
    last_name: str
    first_name: str
    patronymic: str
    study_year: int
    group_name: str
    faculty_name: str

    class Config:
        from_attributes=True
        # orm_mode = True

class PaginatedResponse(BaseModel):
    students: List[StudentOut]
    totalPages: int
