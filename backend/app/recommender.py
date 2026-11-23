import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from .models import Student, Course, Enrolment

def check_prerequisites(course: Course, completed_codes: set) -> tuple[bool, list[str]]:
    """Hard rule: Prerequisite constraints always override ML recommendation scores."""
    if not course.prerequisites or not course.prerequisites.strip():
        return True, []
    required = [p.strip() for p in course.prerequisites.split(",") if p.strip()]
    missing = [req for req in required if req not in completed_codes]
    return len(missing) == 0, missing

def get_recommendations(db: Session, student_id: str, top_k: int = 5) -> list[dict]:
    """
    Hybrid Recommender combining Content-Based Filtering (TF-IDF on interests + completed course tags)
    and Collaborative Filtering (cosine similarity on student-course grade matrix).
    Responsible AI Guardrail: Uses strictly academic/interest features; excludes gender/caste proxies
    and attaches human-readable explanations for every suggestion.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return []

    all_courses = db.query(Course).all()
    all_students = db.query(Student).all()
    all_enrolments = db.query(Enrolment).all()

    student_enrols = [e for e in all_enrolments if e.student_id == student_id]
    taken_codes = {e.course_code for e in student_enrols}
    completed_codes = {
        e.course_code for e in student_enrols
        if e.status == "COMPLETED" and (e.grade_points is None or e.grade_points >= 5.0)
    }

    candidate_courses = [c for c in all_courses if c.code not in taken_codes]
    if not candidate_courses:
        return []

    # 1. Content-Based Filtering (TF-IDF + Cosine Similarity)
    completed_tags = [
        c.tags for c in all_courses if c.code in completed_codes
    ]
    student_profile_text = f"{student.interests} {' '.join(completed_tags)}".strip()
    corpus = [student_profile_text] + [f"{c.title} {c.tags}" for c in candidate_courses]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    content_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # 2. Collaborative Filtering (User-Item Grade Matrix Cosine Similarity)
    student_ids = [s.id for s in all_students]
    course_codes = [c.code for c in all_courses]
    s_idx = {sid: i for i, sid in enumerate(student_ids)}
    c_idx = {code: j for j, code in enumerate(course_codes)}

    grade_matrix = np.zeros((len(student_ids), len(course_codes)))
    for e in all_enrolments:
        if e.student_id in s_idx and e.course_code in c_idx and e.grade_points is not None:
            grade_matrix[s_idx[e.student_id], c_idx[e.course_code]] = e.grade_points

    target_row = s_idx[student_id]
    if np.linalg.norm(grade_matrix[target_row]) > 0:
        user_sims = cosine_similarity(grade_matrix[target_row:target_row + 1], grade_matrix).flatten()
        user_sims[target_row] = 0.0
    else:
        user_sims = np.zeros(len(student_ids))

    results = []
    for idx, course in enumerate(candidate_courses):
        c_score = float(content_sims[idx])
        col_j = c_idx[course.code]
        peer_grades = grade_matrix[:, col_j]
        rated_mask = peer_grades > 0
        if np.any(rated_mask) and np.sum(np.abs(user_sims[rated_mask])) > 0:
            collab_score = float(
                np.dot(user_sims[rated_mask], peer_grades[rated_mask] / 10.0)
                / np.sum(np.abs(user_sims[rated_mask]))
            )
        else:
            collab_score = 0.5  # Neutral prior for cold-start courses

        hybrid_score = round(0.6 * c_score + 0.4 * collab_score, 4)
        eligible, missing_prereqs = check_prerequisites(course, completed_codes)

        # Prerequisite override rule: ineligible courses cannot be top-ranked for enrolment
        effective_score = hybrid_score if eligible else round(hybrid_score * 0.1, 4)

        if not eligible:
            explanation = (
                f"Blocked by Prerequisite Rule: Requires {', '.join(missing_prereqs)} before enrolment. "
                f"(Topic alignment: {int(c_score * 100)}%)"
            )
        else:
            explanation = (
                f"Matches your interests ({student.interests}) with {int(c_score * 100)}% content fit "
                f"and {int(collab_score * 100)}% peer grade affinity; all prerequisites satisfied."
            )

        results.append({
            "course_code": course.code,
            "title": course.title,
            "credits": course.credits,
            "match_score": effective_score,
            "content_score": round(c_score, 4),
            "collaborative_score": round(collab_score, 4),
            "eligible": eligible,
            "missing_prerequisites": missing_prereqs,
            "explanation": explanation,
        })

    # Sort eligible courses first by hybrid score, then blocked courses
    results.sort(key=lambda x: (x["eligible"], x["match_score"]), reverse=True)
    return results[:top_k]

def evaluate_hit_rate(db: Session, k: int = 3) -> float:
    """Evaluates held-out enrolment hit rate@k across students with >=2 completed courses."""
    students = db.query(Student).all()
    hits, total = 0, 0
    for s in students:
        completed = (
            db.query(Enrolment)
            .filter(Enrolment.student_id == s.id, Enrolment.status == "COMPLETED")
            .all()
        )
        if len(completed) < 2:
            continue
        # Hold out the last completed course
        held_out = completed[-1]
        db.delete(held_out)
        db.flush()

        recs = get_recommendations(db, s.id, top_k=k)
        rec_codes = {r["course_code"] for r in recs if r["eligible"]}
        if held_out.course_code in rec_codes:
            hits += 1
        total += 1

        # Restore held-out record
        restored = Enrolment(
            student_id=held_out.student_id,
            course_code=held_out.course_code,
            grade_points=held_out.grade_points,
            status=held_out.status,
        )
        db.add(restored)
        db.flush()

    db.rollback()
    return round((hits / total) * 100, 2) if total > 0 else 0.0
