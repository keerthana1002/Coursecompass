# P28 CourseCompass: Course Recommendation System

**Domain:** Education | **Stack:** Python FastAPI, PostgreSQL/SQLite, React, scikit-learn, Docker, GitHub Actions, Jenkins, SonarQube, Prometheus/Grafana

## Quick Start (VS Code)

### 1. Run Backend (FastAPI + scikit-learn Hybrid Recommender)
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
- API Docs (Swagger UI): http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health
- Prometheus Metrics: http://127.0.0.1:8000/metrics

### 2. Run Frontend (React)
Open a second terminal in VS Code:
```bash
cd frontend
npm install
npm start
```
- Web App: http://localhost:3000

### 3. Run Automated Tests & Coverage (Target >= 80%)
```bash
pytest tests/test_coursecompass.py -v --cov=backend/app --cov-report=term-missing
```

### 4. Run Full Stack via Docker Compose
```bash
docker-compose up --build
```
