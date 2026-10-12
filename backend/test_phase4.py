import sys
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User, UserSkill
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentAttempt
from app.models.evidence import SkillEvidence
from app.seed.seed_data import seed_database

client = TestClient(app)


def run_phase4_tests():
    print("=== Running Phase 4 Diagnostic Assessment Engine Tests ===")

    # Ensure DB tables are created and database is seeded
    from app.core.database import engine, Base
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # 1. Test GET /api/assessments - verify list of assessments
    response = client.get("/api/assessments")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assessments = response.json()
    assert len(assessments) >= 7, f"Expected at least 7 assessments, got {len(assessments)}"
    print(f"PASS 1: Listed {len(assessments)} diagnostic assessments.")

    # 2. Test GET /api/assessments/{id} - verify correct_answer & explanation are NOT exposed
    sql_joins_assm = next(a for a in assessments if a["title"].startswith("SQL Join"))
    assm_id = sql_joins_assm["id"]

    response = client.get(f"/api/assessments/{assm_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    detail = response.json()
    assert "questions" in detail
    assert len(detail["questions"]) == 10

    for q in detail["questions"]:
        assert "correct_answer" not in q, f"SECURITY VIOLATION: correct_answer exposed in question {q['id']}"
        assert "explanation" not in q, f"SECURITY VIOLATION: explanation exposed in question {q['id']}"
        assert "options" in q
        assert "question_text" in q
        assert "difficulty" in q

    print("PASS 2: GET /api/assessments/{id} correctly sanitized (correct_answer & explanation hidden).")

    # 3. Fetch actual correct answers from DB to construct test submissions
    db = SessionLocal()
    try:
        db_questions = (
            db.query(AssessmentQuestion)
            .filter(AssessmentQuestion.assessment_id == assm_id)
            .all()
        )
        correct_answers_map = {q.id: q.correct_answer for q in db_questions}

        python_assm = db.query(Assessment).filter(Assessment.id != assm_id).first()
        python_q = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == python_assm.id).first()
    finally:
        db.close()

    # 4. Test submission: All correct answers produce 100% score
    all_correct_answers = [
        {"question_id": q_id, "answer": ans} for q_id, ans in correct_answers_map.items()
    ]
    submission_payload = {
        "user_id": 1,
        "assessment_id": assm_id,
        "answers": all_correct_answers,
        "fake_client_score": 10.0  # Should be IGNORED
    }

    response = client.post("/api/assessment-attempts", json=submission_payload)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    result = response.json()

    assert result["percentage"] == 100.0
    assert result["raw_score"] == 10
    assert result["total_questions"] == 10
    assert result["interpretation"] == "Strong"
    assert len(result["question_breakdown"]) == 10
    print("PASS 3: All correct answers produced 100.0% score and 'Strong' interpretation.")

    # 5. Test submission: Incorrect answers produce 0% score
    all_wrong_answers = [
        {"question_id": q_id, "answer": "DEFINITELY_WRONG_ANSWER_TEXT_12345"}
        for q_id in correct_answers_map.keys()
    ]
    submission_wrong = {
        "user_id": 1,
        "assessment_id": assm_id,
        "answers": all_wrong_answers,
    }
    response = client.post("/api/assessment-attempts", json=submission_wrong)
    assert response.status_code == 201
    result_wrong = response.json()
    assert result_wrong["percentage"] == 0.0
    assert result_wrong["raw_score"] == 0
    assert result_wrong["interpretation"] == "Critical Gap"
    print("PASS 4: All wrong answers produced 0.0% score and 'Critical Gap' interpretation.")

    # 6. Test submission: Partial/Unanswered questions (e.g. Target Demo Scenario ~40-42%)
    # Submit 4 correct answers out of 10
    q_ids = list(correct_answers_map.keys())
    partial_answers = [
        {"question_id": q_ids[0], "answer": correct_answers_map[q_ids[0]]},
        {"question_id": q_ids[1], "answer": correct_answers_map[q_ids[1]]},
        {"question_id": q_ids[2], "answer": correct_answers_map[q_ids[2]]},
        {"question_id": q_ids[3], "answer": correct_answers_map[q_ids[3]]},
        {"question_id": q_ids[4], "answer": "WRONG_ANSWER"},
    ]
    submission_partial = {
        "user_id": 1,
        "assessment_id": assm_id,
        "answers": partial_answers,
    }
    response = client.post("/api/assessment-attempts", json=submission_partial)
    assert response.status_code == 201
    result_partial = response.json()
    assert result_partial["raw_score"] == 4
    assert result_partial["total_questions"] == 10
    assert result_partial["percentage"] == 40.0
    assert result_partial["interpretation"] == "Critical Gap"
    print("PASS 5: Target demo scenario (4/10 correct = 40.0%) verified server-side.")

    # 7. Test Security: Invalid question ID rejection
    bad_q_payload = {
        "user_id": 1,
        "assessment_id": assm_id,
        "answers": [{"question_id": 999999, "answer": "B"}],
    }
    response = client.post("/api/assessment-attempts", json=bad_q_payload)
    assert response.status_code == 400, f"Expected 400 for invalid question ID, got {response.status_code}"
    print("PASS 6: Invalid question ID rejected with 400 Bad Request.")

    # 8. Test Security: Question from another assessment rejection
    cross_q_payload = {
        "user_id": 1,
        "assessment_id": assm_id,
        "answers": [{"question_id": python_q.id, "answer": "pd.read_csv()"}],
    }
    response = client.post("/api/assessment-attempts", json=cross_q_payload)
    assert response.status_code == 400, f"Expected 400 for cross-assessment question ID, got {response.status_code}"
    print("PASS 7: Cross-assessment question ID rejected with 400 Bad Request.")

    # 9. Test DB Integrity: Verify AssessmentAttempt, SkillEvidence, and UserSkill update
    db = SessionLocal()
    try:
        attempts_count = db.query(AssessmentAttempt).filter_by(user_id=1, assessment_id=assm_id).count()
        assert attempts_count >= 3, f"Expected at least 3 attempts saved in history, got {attempts_count}"

        latest_ev = (
            db.query(SkillEvidence)
            .filter_by(user_id=1)
            .order_by(SkillEvidence.id.desc())
            .first()
        )
        assert latest_ev is not None
        assert latest_ev.evidence_type == "ASSESSMENT"
        assert latest_ev.score == 40.0

        user_skill = (
            db.query(UserSkill)
            .filter_by(user_id=1, skill_id=sql_joins_assm["skill_id"])
            .first()
        )
        assert user_skill is not None
        assert user_skill.accuracy == 40.0
        assert user_skill.skill_level > 0.0  # Computed via Phase 5 Skill DNA formula
    finally:
        db.close()
    print("PASS 8: AssessmentAttempt, SkillEvidence, and UserSkill persisted & updated in PostgreSQL/SQLite.")

    # 10. Test GET /api/users/{user_id}/assessment-attempts - verify history retrieval
    response = client.get("/api/users/1/assessment-attempts")
    assert response.status_code == 200
    user_attempts = response.json()
    assert len(user_attempts) >= 3
    assert "assessment_title" in user_attempts[0]
    assert "skill_name" in user_attempts[0]
    print(f"PASS 9: GET /api/users/1/assessment-attempts returned {len(user_attempts)} historical attempts.")

    print("\n[SUCCESS] ALL PHASE 4 DIAGNOSTIC ASSESSMENT ENGINE TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    run_phase4_tests()
