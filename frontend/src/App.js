import React, { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState("STU-101");
  const [courses, setCourses] = useState([]);
  const [enrolments, setEnrolments] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/api/students`).then(r => r.json()).then(setStudents);
    fetch(`${API_BASE}/api/courses`).then(r => r.json()).then(setCourses);
  }, []);

  const loadStudentData = (sid) => {
    fetch(`${API_BASE}/api/enrolments/${sid}`).then(r => r.json()).then(setEnrolments);
    fetch(`${API_BASE}/api/recommendations/${sid}`).then(r => r.json()).then(setRecommendations);
  };

  useEffect(() => {
    if (selectedStudent) loadStudentData(selectedStudent);
  }, [selectedStudent]);

  const handleEnrol = async (courseCode) => {
    setMessage("");
    const res = await fetch(`${API_BASE}/api/enrol`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: selectedStudent, course_code: courseCode }),
    });
    const data = await res.json();
    if (!res.ok) {
      setMessage(`Error: ${data.detail}`);
    } else {
      setMessage(`Successfully enrolled in ${courseCode}!`);
      loadStudentData(selectedStudent);
    }
  };

  const currentStudent = students.find(s => s.id === selectedStudent);

  return (
    <div style={{ fontFamily: "Segoe UI, sans-serif", maxWidth: 1050, margin: "0 auto", padding: 24 }}>
      <header style={{ borderBottom: "2px solid #1e3a8a", paddingBottom: 12, marginBottom: 20 }}>
        <h1 style={{ color: "#1e3a8a", margin: 0 }}>CourseCompass: Elective Recommendation System</h1>
        <p style={{ color: "#475569", margin: "4px 0 0" }}>
          Hybrid Content + Collaborative Filtering | Prerequisite Guardrails | Responsible AI Explainability
        </p>
      </header>

      <div style={{ background: "#f8fafc", padding: 16, borderRadius: 8, marginBottom: 20 }}>
        <label htmlFor="student-select" style={{ fontWeight: "bold", marginRight: 12 }}>
          Select Student Profile:
        </label>
        <select
          id="student-select"
          value={selectedStudent}
          onChange={(e) => setSelectedStudent(e.target.value)}
          style={{ padding: 8, fontSize: 15 }}
        >
          {students.map(s => (
            <option key={s.id} value={s.id}>
              {s.id} - {s.name} ({s.department}, Sem {s.semester})
            </option>
          ))}
        </select>
        {currentStudent && (
          <p style={{ marginTop: 8, color: "#334155" }}>
            <strong>Academic Interests:</strong> {currentStudent.interests} |{" "}
            <strong>Fairness Note:</strong> Recommendations use zero gender/caste proxies.
          </p>
        )}
      </div>

      {message && (
        <div style={{
          padding: 12,
          marginBottom: 16,
          borderRadius: 6,
          background: message.startsWith("Error") ? "#fee2e2" : "#dcfce7",
          color: message.startsWith("Error") ? "#991b1b" : "#166534"
        }}>
          {message}
        </div>
      )}

      <h2>Personalised Elective Recommendations</h2>
      <div style={{ display: "grid", gap: 12, marginBottom: 28 }}>
        {recommendations.map(rec => (
          <div key={rec.course_code} style={{
            border: rec.eligible ? "1px solid #cbd5e1" : "1px solid #fca5a5",
            background: rec.eligible ? "#ffffff" : "#fef2f2",
            padding: 16,
            borderRadius: 8
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ margin: 0 }}>{rec.course_code}: {rec.title} ({rec.credits} Credits)</h3>
              <span style={{
                padding: "4px 10px",
                borderRadius: 12,
                fontSize: 13,
                fontWeight: "bold",
                background: rec.eligible ? "#dbeafe" : "#fee2e2",
                color: rec.eligible ? "#1e40af" : "#991b1b"
              }}>
                {rec.eligible ? `Match Score: ${(rec.match_score * 100).toFixed(1)}%` : "PREREQUISITE LOCKED"}
              </span>
            </div>
            <p style={{ margin: "8px 0", color: "#334155" }}><strong>Reason:</strong> {rec.explanation}</p>
            <button
              onClick={() => handleEnrol(rec.course_code)}
              disabled={!rec.eligible}
              style={{
                padding: "8px 16px",
                background: rec.eligible ? "#1d4ed8" : "#94a3b8",
                color: "#fff",
                border: "none",
                borderRadius: 6,
                cursor: rec.eligible ? "pointer" : "not-allowed"
              }}
            >
              {rec.eligible ? "Enrol Now" : `Requires: ${rec.missing_prerequisites.join(", ")}`}
            </button>
          </div>
        ))}
      </div>

      <h2>Current & Completed Enrolments</h2>
      <table border="1" cellPadding="8" style={{ width: "100%", borderCollapse: "collapse", marginBottom: 28 }}>
        <thead style={{ background: "#1e3a8a", color: "#fff" }}>
          <tr><th>Course Code</th><th>Status</th><th>Grade Points</th></tr>
        </thead>
        <tbody>
          {enrolments.map(e => (
            <tr key={e.id}>
              <td>{e.course_code}</td>
              <td>{e.status}</td>
              <td>{e.grade_points ?? "In Progress"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Full Course Catalogue</h2>
      <table border="1" cellPadding="8" style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead style={{ background: "#334155", color: "#fff" }}>
          <tr><th>Code</th><th>Title</th><th>Credits</th><th>Prerequisites</th><th>Tags</th></tr>
        </thead>
        <tbody>
          {courses.map(c => (
            <tr key={c.code}>
              <td>{c.code}</td>
              <td>{c.title}</td>
              <td>{c.credits}</td>
              <td>{c.prerequisites || "None"}</td>
              <td>{c.tags}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
