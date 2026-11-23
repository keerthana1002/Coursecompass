from sqlalchemy.orm import Session
from .models import Student, Course, Enrolment

def seed_data(db: Session):
    if db.query(Course).first():
        return

    courses = [
        Course(code="CS201", title="Data Structures & Algorithms", department="CSE", credits=4,
               tags="algorithms data structures programming python", prerequisites="", capacity=60),
        Course(code="CS301", title="Machine Learning Foundations", department="CSE", credits=4,
               tags="machine learning ai data science python statistics", prerequisites="CS201", capacity=50),
        Course(code="CS410", title="Deep Learning & Neural Networks", department="CSE", credits=4,
               tags="deep learning neural networks ai computer vision", prerequisites="CS301", capacity=40),
        Course(code="CS305", title="Cloud Computing & DevOps", department="CSE", credits=3,
               tags="cloud docker kubernetes ci cd deployment", prerequisites="CS201", capacity=55),
        Course(code="CS312", title="Natural Language Processing", department="CSE", credits=3,
               tags="nlp text mining ai transformers python", prerequisites="CS301", capacity=45),
        Course(code="CS320", title="Cybersecurity & Network Defense", department="CSE", credits=3,
               tags="security cryptography network defense", prerequisites="CS201", capacity=50),
    ]
    db.add_all(courses)

    students = [
        Student(id="STU-101", name="Aarav Sharma", department="CSE", semester=5,
                interests="machine learning ai python deep learning"),
        Student(id="STU-102", name="Ananya Nair", department="CSE", semester=5,
                interests="ai nlp data science python"),
        Student(id="STU-103", name="Rohan Verma", department="CSE", semester=5,
                interests="deep learning neural networks ai"),  # Missing CS301 prerequisite!
        Student(id="STU-104", name="Meera Kulkarni", department="CSE", semester=5,
                interests="cloud docker deployment security"),
    ]
    db.add_all(students)
    db.commit()

    enrolments = [
        # STU-101 completed CS201 and CS301 -> eligible for CS410 & CS312
        Enrolment(student_id="STU-101", course_code="CS201", grade_points=9.0, status="COMPLETED"),
        Enrolment(student_id="STU-101", course_code="CS301", grade_points=9.5, status="COMPLETED"),
        # STU-102 completed CS201 and CS301 -> collaborative peer for STU-101
        Enrolment(student_id="STU-102", course_code="CS201", grade_points=8.8, status="COMPLETED"),
        Enrolment(student_id="STU-102", course_code="CS301", grade_points=9.2, status="COMPLETED"),
        Enrolment(student_id="STU-102", course_code="CS312", grade_points=9.0, status="COMPLETED"),
        # STU-103 completed ONLY CS201 -> wants Deep Learning (CS410), but MUST be blocked by CS301 prereq
        Enrolment(student_id="STU-103", course_code="CS201", grade_points=8.5, status="COMPLETED"),
        # STU-104 completed CS201 and CS305
        Enrolment(student_id="STU-104", course_code="CS201", grade_points=8.7, status="COMPLETED"),
        Enrolment(student_id="STU-104", course_code="CS305", grade_points=9.1, status="COMPLETED"),
    ]
    db.add_all(enrolments)
    db.commit()
