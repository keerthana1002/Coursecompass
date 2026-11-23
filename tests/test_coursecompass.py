import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, close_all_sessions

from app.database import Base, get_db
from app.main import app
from app.seed import seed_data

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_coursecompass.db"))
SQLALCHEMY_TEST_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


def teardown_module(module):
    close_all_sessions()
    engine.dispose()
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            pass


def test_health_and_metrics():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        m_res = client.get("/metrics")
        assert m_res.status_code == 200
        assert "coursecompass_requests_total" in m_res.text


def test_catalogue_and_students():
    with TestClient(app) as client:
        courses = client.get("/api/courses").json()
        assert len(courses) >= 6
        students = client.get("/api/students").json()
        assert len(students) >= 4


def test_prerequisite_override_blocks_ineligible_recommendation():
    """Phase 4 Special Case: Prerequisite rules must override ML affinity."""
    with TestClient(app) as client:
        # STU-103 likes deep learning (CS410) but has NOT completed CS301
        recs = client.get("/api/recommendations/STU-103").json()
        cs410 = next(r for r in recs if r["course_code"] == "CS410")
        assert cs410["eligible"] is False
        assert "CS301" in cs410["missing_prerequisites"]
        assert "Blocked by Prerequisite Rule" in cs410["explanation"]

        # Direct enrolment attempt must also fail with HTTP 400
        enrol_res = client.post("/api/enrol", json={"student_id": "STU-103", "course_code": "CS410"})
        assert enrol_res.status_code == 400
        assert "Prerequisite constraint violation" in enrol_res.json()["detail"]


def test_eligible_recommendation_and_enrolment_flow():
    with TestClient(app) as client:
        # STU-101 completed CS201 and CS301 -> eligible for CS410
        recs = client.get("/api/recommendations/STU-101").json()
        assert len(recs) > 0
        top_rec = recs[0]
        assert top_rec["eligible"] is True
        assert len(top_rec["explanation"]) > 10

        enrol_res = client.post("/api/enrol", json={"student_id": "STU-101", "course_code": "CS410"})
        assert enrol_res.status_code == 200
        assert enrol_res.json()["status"] == "ENROLLED"

        # Duplicate enrolment must fail
        dup_res = client.post("/api/enrol", json={"student_id": "STU-101", "course_code": "CS410"})
        assert dup_res.status_code == 400


def test_hit_rate_success_metric():
    with TestClient(app) as client:
        res = client.get("/api/metrics/hit-rate").json()
        assert res["hit_rate_percent"] >= 60.0
        assert res["passed"] is True