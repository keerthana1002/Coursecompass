import time
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from .database import Base, engine, get_db, SessionLocal
from .models import Student, Course, Enrolment
from .schemas import CourseOut, StudentOut, EnrolmentCreate, EnrolmentOut, RecommendationItem
from .recommender import get_recommendations, check_prerequisites, evaluate_hit_rate
from .seed import seed_data

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CourseCompass: Course Recommendation System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_COUNT = Counter("coursecompass_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("coursecompass_request_latency_seconds", "HTTP request latency", ["endpoint"])

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(elapsed)
    return response

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "CourseCompass API", "version": "1.0.0"}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/students", response_model=list[StudentOut])
def list_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

@app.get("/api/courses", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@app.get("/api/enrolments/{student_id}", response_model=list[EnrolmentOut])
def list_student_enrolments(student_id: str, db: Session = Depends(get_db)):
    return db.query(Enrolment).filter(Enrolment.student_id == student_id).all()

@app.post("/api/enrol", response_model=EnrolmentOut)
def enrol_course(payload: EnrolmentCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    course = db.query(Course).filter(Course.code == payload.course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = (
        db.query(Enrolment)
        .filter(Enrolment.student_id == payload.student_id, Enrolment.course_code == payload.course_code)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled or completed this course")

    enrolled_count = db.query(Enrolment).filter(Enrolment.course_code == payload.course_code).count()
    if enrolled_count >= course.capacity:
        raise HTTPException(status_code=400, detail="Course capacity full")

    completed_enrols = (
        db.query(Enrolment)
        .filter(Enrolment.student_id == payload.student_id, Enrolment.status == "COMPLETED")
        .all()
    )
    completed_codes = {e.course_code for e in completed_enrols}
    eligible, missing = check_prerequisites(course, completed_codes)
    if not eligible:
        raise HTTPException(
            status_code=400,
            detail=f"Prerequisite constraint violation: missing {', '.join(missing)}"
        )

    new_enrol = Enrolment(
        student_id=payload.student_id,
        course_code=payload.course_code,
        grade_points=None,
        status="ENROLLED",
    )
    db.add(new_enrol)
    db.commit()
    db.refresh(new_enrol)
    return new_enrol

@app.get("/api/recommendations/{student_id}", response_model=list[RecommendationItem])
def recommend_electives(student_id: str, top_k: int = 5, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return get_recommendations(db, student_id, top_k=top_k)

@app.get("/api/metrics/hit-rate")
def get_hit_rate(db: Session = Depends(get_db)):
    rate = evaluate_hit_rate(db, k=3)
    return {"hit_rate_percent": rate, "target_percent": 60.0, "passed": rate >= 60.0}
