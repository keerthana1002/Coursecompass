# P28 CourseCompass — 12-Slide Presentation Script (6 Minutes)

1. **Slide 1 — Title (20s):** P28 CourseCompass: Course Recommendation System | Team NEXGRID | Dayananda Sagar University.
2. **Slide 2 — Problem & Users (30s):** Students pick electives blindly without knowing academic fit or prerequisites. Users: Students and Faculty Advisors.
3. **Slide 3 — Architecture (30s):** React frontend -> FastAPI backend -> PostgreSQL/SQLite DB + scikit-learn Hybrid Recommender, containerized with Docker, CI/CD via GitHub Actions & Jenkins, monitored by Prometheus & Grafana.
4. **Slide 4 — Phase 1: AI in SE (30s):** Interviewed students/advisors, refined ChatGPT SRS manually to remove ambiguity, selected Incremental/Agile model, built ER/Use-Case models.
5. **Slide 5 — Phase 2: Agile & Planning (30s):** 20 user stories across two 1-week sprints in Jira, Planning Poker vs AI estimates, Kanban WIP limits, XP test-first development.
6. **Slide 6 — Phase 3: Development & CI/CD (30s):** Hybrid TF-IDF + Collaborative Filtering recommender, feature branches + resolved merge conflict, Docker Compose, GitHub Actions + Jenkinsfile.
7. **Slide 7 — Phase 4: Testing & Monitoring (30s):** Pytest unit/integration suite (>=80% coverage), explicit test proving prerequisite rules override ML scores, Selenium Page-Object E2E, Prometheus `/metrics`.
8. **Slide 8 — Phase 5: SQA & Ethics (30s):** SonarQube zero-blocker quality gate, AI vs human code review, 5-attribute SQA plan.
9. **Slide 9 — Live Demo (60s):** Select `STU-103` to show Prerequisite Override locking `CS410 Deep Learning`; switch to `STU-101` to show explainable hybrid match scores and one-click enrolment.
10. **Slide 10 — Results vs Targets (30s):** Hit Rate >= 60% achieved | Test Coverage >= 80% | 0 Blocker Issues | CI/CD Pipeline Green.
11. **Slide 11 — Responsible AI (20s):** Zero steering by gender or caste proxies; every recommendation includes a clear explanation.
12. **Slide 12 — Conclusion & Q&A (20s):** End-to-end AI-assisted SDLC deliverable ready for questions.
