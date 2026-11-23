# CourseCompass (P28) — Phase 1 to 5 Evidence, Logs & Checklists

## Phase 1: Requirements, Process Model & SRS (Days 3-6)
- **Chosen Process Model:** Incremental + Agile Scrum (2 one-week sprints) selected over Waterfall because elective recommendation algorithms require iterative feedback from students and advisors.
- **Stakeholder Interview Notes:**
  - *Students:* Want elective suggestions aligned with career interests and past strengths, with transparent reasons why a course is suggested.
  - *Advisors:* Require strict enforcement of course prerequisites and seat capacity limits so students cannot enrol in advanced electives prematurely.
- **Manual SRS Corrections (v1 -> v2):**
  - Removed vague requirement *"System should suggest good courses quickly"* -> replaced with *"System shall achieve >=60% hit rate@3 on held-out enrolments and respond within <300ms."*
  - Added explicit rule: *"Prerequisite constraints must override ML recommendation scores."*

## Phase 2: Agile User Stories, Sprint Plan & Lean Wastes (Days 7-10)
- **Sprint 1 (Catalogue & Enrolment):** US-01 to US-10 (View catalogue, check prerequisites, enrol in course, prevent duplicate enrolment, enforce capacity).
- **Sprint 2 (Hybrid AI Recommender):** US-11 to US-20 (TF-IDF content matching, collaborative grade matrix filtering, explainable reasons, prerequisite lock badges, advisor audit view).
- **Lean Wastes Eliminated:** Eliminated over-processing (removed unused demographic fields), waiting (automated test fixtures), and defects (test-first prerequisite validation).

## Phase 3: AI-Assisted Development Prompt Log (Days 11-15)
1. **Prompt 1:** *"Generate a FastAPI SQLAlchemy schema for Student, Course, and Enrolment without storing gender or caste fields."* -> Verified and accepted.
2. **Prompt 2:** *"Write a hybrid recommender combining TF-IDF cosine similarity and user-item collaborative filtering in scikit-learn."* -> Modified to add cold-start prior (0.5) and explicit prerequisite override multiplier.
3. **Merge Conflict Resolution:** Resolved conflict in `backend/app/main.py` between `feature/enrolment-rules` and `feature/hybrid-recommender` on `/api/enrol` validation order.

## Phase 4: Testing & Defect Prediction (Days 16-19)
- **15 Manual vs Automated Test Cases:** Automated via `pytest` (`tests/test_coursecompass.py`) and Selenium Page-Object suite (`tests/selenium_e2e.py`).
- **Special Case Verified:** `STU-103` (Rohan Verma) has high interest in Deep Learning (`CS410`) but lacks `CS301`; system locks `CS410` and blocks enrolment with HTTP 400.

## Phase 5: SQA Plan & Responsible AI Checklist (Days 20-23)
- **SQA Scores (out of 5):** Correctness: 4.8 | Reliability: 4.7 | Maintainability: 4.6 | Usability: 4.8 | Efficiency: 4.7.
- **Responsible AI & Ethics Checkpoint:**
  - [x] **No Gender or Caste Proxies:** Schema and feature vector strictly exclude gender, caste, surname embeddings, and socioeconomic proxies.
  - [x] **Explainability:** Every recommendation displays an itemized reason (`content_score`, `collaborative_score`, and prerequisite status).
  - [x] **Privacy:** Student IDs are pseudonymized (`STU-101`) in prompts and logs.
