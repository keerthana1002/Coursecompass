from pydantic import BaseModel
from typing import List, Optional

class CourseOut(BaseModel):
    code: str
    title: str
    department: str
    credits: int
    tags: str
    prerequisites: str
    capacity: int

    class Config:
        from_attributes = True

class StudentOut(BaseModel):
    id: str
    name: str
    department: str
    semester: int
    interests: str

    class Config:
        from_attributes = True

class EnrolmentCreate(BaseModel):
    student_id: str
    course_code: str

class EnrolmentOut(BaseModel):
    id: int
    student_id: str
    course_code: str
    grade_points: Optional[float]
    status: str

    class Config:
        from_attributes = True

class RecommendationItem(BaseModel):
    course_code: str
    title: str
    credits: int
    match_score: float
    content_score: float
    collaborative_score: float
    eligible: bool
    missing_prerequisites: List[str]
    explanation: str
