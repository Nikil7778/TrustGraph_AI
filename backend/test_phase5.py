import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import engine, Base, SessionLocal
from app.models.user import User, UserSkill
from app.models.skill import Skill
from app.models.evidence import SkillEvidence
from app.engines.skill_dna_engine import skill_dna_engine
from app.seed.seed_data import seed_database

client = TestClient(app)


def run_phase5_tests():
    print("=== Running Phase 5 Skill DNA Engine Tests ===")

    # Ensure DB tables exist and are seeded
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # 1. Unit Test: Recency Decay Formula
    now = datetime.datetime.utcnow()
    recency_today = skill_dna_engine.calculate_recency(now)
    assert abs(recency_today - 100.0) < 1.0, f"Expected ~100 for today, got {recency_today}"

    recency_30d = skill_dna_engine.calculate_recency(now - datetime.timedelta(days=30))
    assert 80.0 <= recency_30d <= 90.0, f"Expected ~85 for 30d, got {recency_30d}"

    recency_90d = skill_dna_engine.calculate_recency(now - datetime.timedelta(days=90))
    assert 60.0 <= recency_90d <= 75.0, f"Expected ~67 for 90d, got {recency_90d}"

    recency_365d = skill_dna_engine.calculate_recency(now - datetime.timedelta(days=365))
    assert 15.0 <= recency_365d <= 25.0, f"Expected ~20 for 365d, got {recency_365d}"

    print(f"PASS 1: Recency decay verified (Today: {recency_today}, 30d: {recency_30d}, 90d: {recency_90d}, 365d: {recency_365d}).")

    # 2. Unit Test: Difficulty Mapping
    d_easy = skill_dna_engine.map_difficulty("Easy")
    d_med = skill_dna_engine.map_difficulty("Intermediate")
    d_hard = skill_dna_engine.map_difficulty("Hard")

    assert d_easy == 35.0, f"Expected 35.0, got {d_easy}"
    assert d_med == 65.0, f"Expected 65.0, got {d_med}"
    assert d_hard == 90.0, f"Expected 90.0, got {d_hard}"

    print(f"PASS 2: Difficulty mapping verified (Easy: {d_easy}, Med: {d_med}, Hard: {d_hard}).")

    # 3. Unit Test: Evidence Scoring Hierarchy
    ev_assm = [SkillEvidence(user_id=1, skill_id=1, source="Quiz", evidence_type="ASSESSMENT", score=80.0, created_at=now)]
    ev_prac = [SkillEvidence(user_id=1, skill_id=1, source="Lab", evidence_type="PRACTICE", score=80.0, created_at=now)]
    ev_proj = [SkillEvidence(user_id=1, skill_id=1, source="Project", evidence_type="PROJECT", score=80.0, created_at=now)]
    ev_real = [SkillEvidence(user_id=1, skill_id=1, source="Task", evidence_type="REAL_WORLD_TASK", score=80.0, created_at=now)]

    score_assm = skill_dna_engine.calculate_evidence_score(ev_assm)
    score_prac = skill_dna_engine.calculate_evidence_score(ev_prac)
    score_proj = skill_dna_engine.calculate_evidence_score(ev_proj)
    score_real = skill_dna_engine.calculate_evidence_score(ev_real)

    assert score_assm < score_prac < score_proj < score_real, "Evidence hierarchy failed: ASSESSMENT < PRACTICE < PROJECT < REAL_WORLD_TASK"
    print(f"PASS 3: Evidence hierarchy verified ({score_assm} < {score_prac} < {score_proj} < {score_real}).")

    # 4. Unit Test: Confidence Calculation
    conf_0 = skill_dna_engine.calculate_confidence([])
    conf_1 = skill_dna_engine.calculate_confidence(ev_assm)
    conf_2 = skill_dna_engine.calculate_confidence(ev_assm + ev_prac)
    conf_3 = skill_dna_engine.calculate_confidence(ev_assm + ev_prac + ev_proj)

    assert conf_0 == 0.0
    assert conf_1 == 50.0
    assert conf_2 == 75.0 or conf_2 == 70.0  # 70.0 base + consistency
    assert conf_3 >= 85.0

    print(f"PASS 4: Confidence calculation verified (0 ev: {conf_0}, 1 ev: {conf_1}, 2 ev: {conf_2}, 3 ev: {conf_3}).")

    # 5. Unit Test: Skill Level Deterministic Formula
    # Formula: 0.60 * accuracy + 0.15 * difficulty + 0.15 * recency + 0.10 * evidence_score
    calc_level = skill_dna_engine.calculate_skill_level(
        accuracy=80.0, difficulty=65.0, recency=100.0, evidence_score=70.0
    )
    expected = round(0.60 * 80.0 + 0.15 * 65.0 + 0.15 * 100.0 + 0.10 * 70.0, 1)
    assert calc_level == expected, f"Expected {expected}, got {calc_level}"
    print(f"PASS 5: Skill level formula verified ({calc_level} == {expected}).")

    # 6. Integration Test: GET /api/users/1/skill-dna
    response = client.get("/api/users/1/skill-dna")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    dna_list = response.json()
    assert len(dna_list) >= 8, f"Expected at least 8 skills, got {len(dna_list)}"

    sql_joins_dna = next((d for d in dna_list if d["skill_name"] == "SQL JOINs"), None)
    assert sql_joins_dna is not None
    print(f"SQL JOINs DNA profile: level={sql_joins_dna['skill_level']}, status={sql_joins_dna['status']}, accuracy={sql_joins_dna['accuracy']}")
    assert sql_joins_dna["status"] in ["CRITICAL", "DEVELOPING"]
    assert "accuracy" in sql_joins_dna
    assert "confidence" in sql_joins_dna
    assert "recency" in sql_joins_dna
    assert "evidence_score" in sql_joins_dna
    print(f"PASS 6: GET /api/users/1/skill-dna returned {len(dna_list)} multidimensional profiles.")

    # 7. Integration Test: GET /api/users/1/skills/3/skill-dna (SQL JOINs single skill)
    response = client.get("/api/users/1/skills/3/skill-dna")
    assert response.status_code == 200
    single_dna = response.json()
    assert single_dna["skill_name"] == "SQL JOINs"
    assert single_dna["status"] in ["CRITICAL", "DEVELOPING"]
    print(f"PASS 7: GET /api/users/1/skills/3/skill-dna returned SQL JOINs profile.")

    # 8. Integration Test: POST /api/users/1/skill-dna/recalculate
    response = client.post("/api/users/1/skill-dna/recalculate")
    assert response.status_code == 200
    recalc_list = response.json()
    assert len(recalc_list) >= 8
    print(f"PASS 8: POST /api/users/1/skill-dna/recalculate succeeded.")

    # 9. Integration Loop Test: Assessment submission triggers automatic Skill DNA update
    # Submit diagnostic assessment for Python (Assessment ID 2)
    # Questions for Python assessment: fetch questions
    db = SessionLocal()
    try:
        py_assm = db.query(Skill).filter_by(name="Python").first()
    finally:
        db.close()

    submission = {
        "user_id": 1,
        "assessment_id": 2, # Python assessment
        "answers": [] # Unanswered -> score 0.0
    }
    response = client.post("/api/assessment-attempts", json=submission)
    assert response.status_code == 201

    # Verify UserSkill and Skill DNA updated for Python
    response = client.get(f"/api/users/1/skills/{py_assm.id}/skill-dna")
    assert response.status_code == 200
    updated_py_dna = response.json()
    assert updated_py_dna["accuracy"] == 0.0
    assert updated_py_dna["status"] == "CRITICAL"

    print("PASS 9: Integration loop verified: Assessment submission -> Evidence -> Skill DNA recalculate -> UserSkill updated.")

    print("\n[SUCCESS] ALL PHASE 5 SKILL DNA ENGINE TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    run_phase5_tests()
