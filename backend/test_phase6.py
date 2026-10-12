import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.skill import Skill
from app.models.evidence import SkillEvidence
from app.engines.skill_debt_engine import skill_debt_engine
from app.seed.seed_data import seed_database

client = TestClient(app)


def run_phase6_tests():
    print("=== Running Phase 6 Skill Debt Engine Tests ===")

    # Ensure DB tables exist and are seeded
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # 1. Unit Test: Classification Logic (MISSING vs SKILL_DEBT vs HEALTHY vs UNKNOWN)
    # 0 evidence -> MISSING
    debt_missing = skill_debt_engine.evaluate_skill_debt(
        skill_id=99,
        skill_name="Docker MLOps",
        skill_category="DevOps",
        role_id=1,
        role_name="Data Analyst",
        role_requirement=80.0,
        importance_score=75.0,
        skill_dna={"skill_level": 0.0, "confidence": 0.0, "evidence_count": 0},
        evidences=[],
    )
    assert debt_missing["debt_status"] == "MISSING"
    assert debt_missing["severity"] == "HIGH"
    assert "no verified learning evidence" in debt_missing["reason"].lower()
    print("PASS 1: 0 evidence correctly classified as MISSING.")

    # Evidence exists + weak skill -> SKILL_DEBT
    now = datetime.datetime.utcnow()
    ev_weak = [SkillEvidence(user_id=1, skill_id=3, source="Quiz", evidence_type="ASSESSMENT", score=42.0, created_at=now)]
    debt_weak = skill_debt_engine.evaluate_skill_debt(
        skill_id=3,
        skill_name="SQL JOINs",
        skill_category="Database Querying",
        role_id=1,
        role_name="Data Analyst",
        role_requirement=80.0,
        importance_score=90.0,
        skill_dna={
            "skill_level": 42.0,
            "confidence": 50.0,
            "accuracy": 42.0,
            "recency": 100.0,
            "recency_label": "Today",
            "evidence_score": 50.0,
            "evidence_count": 1,
            "last_assessed_at": now,
        },
        evidences=ev_weak,
    )
    assert debt_weak["debt_status"] == "SKILL_DEBT"
    assert debt_weak["severity"] == "HIGH"
    assert "previously demonstrated exposure" in debt_weak["reason"].lower()
    assert debt_weak["debt_score"] > 0.0
    print(f"PASS 2: Weak skill with prior evidence correctly classified as SKILL_DEBT (Score: {debt_weak['debt_score']}, Severity: {debt_weak['severity']}).")

    # Evidence exists + strong current skill -> HEALTHY
    ev_strong = [SkillEvidence(user_id=1, skill_id=1, source="Quiz", evidence_type="ASSESSMENT", score=85.0, created_at=now)]
    debt_healthy = skill_debt_engine.evaluate_skill_debt(
        skill_id=1,
        skill_name="Python",
        skill_category="Programming",
        role_id=1,
        role_name="Data Analyst",
        role_requirement=80.0,
        importance_score=80.0,
        skill_dna={
            "skill_level": 85.0,
            "confidence": 90.0,
            "accuracy": 85.0,
            "recency": 100.0,
            "recency_label": "Today",
            "evidence_score": 85.0,
            "evidence_count": 5,
            "last_assessed_at": now,
        },
        evidences=ev_strong,
    )
    assert debt_healthy["debt_status"] == "HEALTHY"
    assert debt_healthy["debt_score"] == 0.0
    assert debt_healthy["severity"] == "NONE"
    print("PASS 3: Strong skill correctly classified as HEALTHY with 0 debt score.")

    # 2. Test Stale/Old Evidence Increases Debt Score
    debt_fresh = skill_debt_engine.calculate_debt_score(
        role_requirement=80.0, skill_level=70.0, confidence=70.0, recency=100.0, evidence_score=70.0, has_practical_evidence=True, debt_status="SKILL_DEBT"
    )
    debt_stale = skill_debt_engine.calculate_debt_score(
        role_requirement=80.0, skill_level=70.0, confidence=70.0, recency=20.0, evidence_score=70.0, has_practical_evidence=True, debt_status="SKILL_DEBT"
    )
    assert debt_stale > debt_fresh, f"Expected stale evidence debt ({debt_stale}) > fresh debt ({debt_fresh})"
    print(f"PASS 4: Old/stale evidence correctly increases debt score ({debt_stale:.1f} > {debt_fresh:.1f}).")

    # 3. Test Integration: GET /api/users/1/skill-debt (Alex Mercer Demo Target Role)
    response = client.get("/api/users/1/skill-debt")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    debts = response.json()
    assert len(debts) >= 5, f"Expected at least 5 role skill debt items, got {len(debts)}"

    sql_joins_item = next((d for d in debts if d["skill_name"] == "SQL JOINs"), None)
    assert sql_joins_item is not None, "SQL JOINs item missing from skill debt API response"
    assert sql_joins_item["debt_status"] == "SKILL_DEBT"
    assert sql_joins_item["severity"] == "HIGH"
    assert sql_joins_item["role_requirement"] >= 80.0
    assert "previously demonstrated exposure" in sql_joins_item["reason"].lower()
    assert "reassess" in sql_joins_item["recommended_intervention"].lower()

    print(f"PASS 5: Alex Mercer SQL JOINs target demo scenario verified:")
    print(f"       Status: {sql_joins_item['debt_status']}, Severity: {sql_joins_item['severity']}, Score: {sql_joins_item['debt_score']}")
    print(f"       Reason: {sql_joins_item['reason']}")
    print(f"       Intervention: {sql_joins_item['recommended_intervention']}")

    # 4. Test Single Skill Debt API: GET /api/users/1/skill-debt/3
    response = client.get("/api/users/1/skill-debt/3")
    assert response.status_code == 200
    single_item = response.json()
    assert single_item["skill_name"] == "SQL JOINs"
    assert single_item["debt_status"] == "SKILL_DEBT"
    print("PASS 6: GET /api/users/1/skill-debt/3 single skill debt endpoint verified.")

    # 5. Test Recalculate Skill Debt API: POST /api/users/1/skill-debt/recalculate
    response = client.post("/api/users/1/skill-debt/recalculate")
    assert response.status_code == 200
    recalc_debts = response.json()
    assert len(recalc_debts) >= 5
    print("PASS 7: POST /api/users/1/skill-debt/recalculate endpoint verified.")

    print("\n[SUCCESS] ALL PHASE 6 SKILL DEBT ENGINE TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    run_phase6_tests()
