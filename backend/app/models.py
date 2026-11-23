from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    interests = Column(String, nullable=False)  # Comma-separated tags
    # Responsible AI: No gender or caste attributes used in recommendation scoring
    enrolments = relationship("Enrolment", back_populates="student")

class Course(Base):
    __tablename__ = "courses"
    code = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    department = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    tags = Column(String, nullable=False)  # Content keywords
    prerequisites = Column(String, default="")  # Comma-separated course codes
    capacity = Column(Integer, default=60)
    enrolments = relationship("Enrolment", back_populates="course")

class Enrolment(Base):
    __tablename__ = "enrolments"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    course_code = Column(String, ForeignKey("courses.code"), nullable=False)
    grade_points = Column(Float, nullable=True)  # Out of 10.0; None if currently enrolled
    status = Column(String, default="ENROLLED")  # COMPLETED or ENROLLED

    student = relationship("Student", back_populates="enrolments")
    course = relationship("Course", back_populates="enrolments")

    __table_args__ = (UniqueConstraint("student_id", "course_code", name="uq_student_course"),)
