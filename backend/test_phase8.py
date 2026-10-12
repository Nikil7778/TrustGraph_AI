import sys
from fastapi.testclient import TestClient
from app.main import app
from app.engines.next_best_proof_engine import next_best_proof_engine

client = TestClient(app)


def test_next_best_proof():
    print("=== Running Phase 8 Next-Best-Proof Engine Tests ===")

    # 1. Unit Tests on Engine Decision Rules

    # Test 1: Learned but weak skill with Skill Debt -> PRACTICE
    action_debt = next_best_proof_engine.select_action_type(
        skill_name="SQL JOINs",
        current_level=55.0,
        required_level=80.0,
        accuracy=42.0,
        confidence=50.0,
        evidence_count=2,
        practical_evidence_count=0,
        debt_status="SKILL_DEBT",
        prereq_info={"healthy": True, "blocking": []},
        recent_evidence_types=["ASSESSMENT"],
    )
    assert action_debt["action_type"] == "PRACTICE", f"Expected PRACTICE, got {action_debt['action_type']}"
    assert "Rescue Practice" in action_debt["title"]
    print(f"PASS 1: Learned skill with Skill Debt selects PRACTICE ({action_debt['title']}).")

    # Test 2: Prerequisite blocked -> REVIEW_PREREQUISITE
    action_prereq = next_best_proof_engine.select_action_type(
        skill_name="SQL JOINs",
        current_level=30.0,
        required_level=80.0,
        accuracy=30.0,
        confidence=20.0,
        evidence_count=1,
        practical_evidence_count=0,
        debt_status="SKILL_DEBT",
        prereq_info={"healthy": False, "blocking": ["SQL"]},
        recent_evidence_types=[],
    )
    assert action_prereq["action_type"] == "REVIEW_PREREQUISITE", f"Expected REVIEW_PREREQUISITE, got {action_prereq['action_type']}"
    print(f"PASS 2: Unhealthy prerequisite blocks skill and selects REVIEW_PREREQUISITE ({action_prereq['title']}).")

    # Test 3: Zero evidence / missing skill -> LEARN
    action_missing = next_best_proof_engine.select_action_type(
        skill_name="Deep Learning",
        current_level=0.0,
        required_level=70.0,
        accuracy=0.0,
        confidence=0.0,
        evidence_count=0,
        practical_evidence_count=0,
        debt_status="MISSING",
        prereq_info={"healthy": True, "blocking": []},
        recent_evidence_types=[],
    )
    assert action_missing["action_type"] == "LEARN", f"Expected LEARN, got {action_missing['action_type']}"
    print(f"PASS 3: Zero evidence skill selects LEARN ({action_missing['title']}).")

    # Test 4: Strong conceptual skill + weak practical evidence -> PRACTICAL_TASK
    action_practical = next_best_proof_engine.select_action_type(
        skill_name="SQL",
        current_level=77.0,
        required_level=85.0,
        accuracy=75.0,
        confidence=70.0,
        evidence_count=3,
        practical_evidence_count=0,
        debt_status="SKILL_DEBT",
        prereq_info={"healthy": True, "blocking": []},
        recent_evidence_types=["ASSESSMENT"],
    )
    assert action_practical["action_type"] == "PRACTICAL_TASK", f"Expected PRACTICAL_TASK, got {action_practical['action_type']}"
    print(f"PASS 4: Strong conceptual baseline with missing practical proof selects PRACTICAL_TASK ({action_practical['title']}).")

    # Test 5: Recent practice completed + uncertain confidence -> REASSESS
    action_reassess = next_best_proof_engine.select_action_type(
        skill_name="SQL JOINs",
        current_level=68.0,
        required_level=80.0,
        accuracy=72.0,
        confidence=60.0,
        evidence_count=4,
        practical_evidence_count=1,
        debt_status="SKILL_DEBT",
        prereq_info={"healthy": True, "blocking": []},
        recent_evidence_types=["PRACTICE"],
    )
    assert action_reassess["action_type"] == "REASSESS", f"Expected REASSESS, got {action_reassess['action_type']}"
    print(f"PASS 5: Submitted practice awaiting verification selects REASSESS ({action_reassess['title']}).")

    # Test 6: High benchmark mastery -> PROJECT
    action_project = next_best_proof_engine.select_action_type(
        skill_name="Python",
        current_level=85.0,
        required_level=80.0,
        accuracy=88.0,
        confidence=90.0,
        evidence_count=5,
        practical_evidence_count=2,
        debt_status="HEALTHY",
        prereq_info={"healthy": True, "blocking": []},
        recent_evidence_types=["PRACTICAL_TASK"],
    )
    assert action_project["action_type"] == "PROJECT", f"Expected PROJECT, got {action_project['action_type']}"
    print(f"PASS 6: High benchmark mastery selects PROJECT ({action_project['title']}).")

    # Test 7: Score formula stays 0-100
    score_clamped = next_best_proof_engine.calculate_score(
        career_value_score=100.0,
        skill_debt_score=100.0,
        evidence_gap=100.0,
        confidence_gap=100.0,
        practical_evidence_gap=100.0,
        action_readiness=100.0,
    )
    assert score_clamped == 100.0, f"Expected 100.0, got {score_clamped}"
    score_low = next_best_proof_engine.calculate_score(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    assert score_low == 0.0, f"Expected 0.0, got {score_low}"
    print("PASS 7: Score calculation strictly clamped to [0.0, 100.0].")

    # Test 8: Prerequisites checking
    dna_map = {
        "SQL": {"skill_level": 77.0, "evidence_count": 2},
        "Python": {"skill_level": 83.0, "evidence_count": 3},
        "Statistics": {"skill_level": 50.0, "evidence_count": 1},  # Weak!
    }
    sql_check = next_best_proof_engine.check_prerequisites("SQL JOINs", dna_map)
    assert sql_check["healthy"] is True, "Expected SQL JOINs prerequisites to be healthy"
    eda_check = next_best_proof_engine.check_prerequisites("EDA", dna_map)
    assert eda_check["healthy"] is False, "Expected EDA prerequisites to be blocked by Statistics"
    assert "Statistics" in eda_check["blocking"]
    print("PASS 8: Prerequisites evaluated accurately against demonstrated Skill DNA.")

    # 2. Integration & Demo Tests (Alex Mercer, User 1)
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        from app.seed.seed_data import reset_alex_mercer
        reset_alex_mercer(db)
    finally:
        db.close()

    # Test 9: Fetch single Next-Best-Proof
    res = client.get("/api/users/1/next-best-proof")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    nbp = res.json()

    # Test 10: SQL JOINs demo verification
    assert nbp["skill_name"] == "SQL JOINs", f"Expected SQL JOINs, got {nbp['skill_name']}"
    assert nbp["action_type"] == "PRACTICE", f"Expected PRACTICE action, got {nbp['action_type']}"
    assert "Rescue Practice" in nbp["title"]
    assert nbp["priority"] in ("CRITICAL", "HIGH")
    assert nbp["estimated_minutes"] == 25
    assert "8/10" in nbp["expected_proof"]
    assert len(nbp["reason"]) > 10
    assert len(nbp["why_now"]) > 10
    assert len(nbp["why_this_action"]) > 10
    print(f"PASS 9 & 10: Alex Mercer Next-Best-Proof correctly selected SQL JOINs ({nbp['title']}).")
    print(f"       Expected proof: '{nbp['expected_proof']}'")
    print(f"       Score: {nbp['next_best_proof_score']}, Priority: {nbp['priority']}")

    # Test 11: Candidates endpoint
    cand_res = client.get("/api/users/1/next-best-proof/candidates")
    assert cand_res.status_code == 200
    candidates = cand_res.json()
    assert len(candidates) >= 8
    assert candidates[0]["skill_name"] == "SQL JOINs"
    # Ensure ranked sequentially
    ranks = [c["rank"] for c in candidates]
    assert ranks == list(range(1, len(candidates) + 1))
    print(f"PASS 11: Candidate actions ranked deterministically (Top: #{candidates[0]['rank']} {candidates[0]['skill_name']} - {candidates[0]['action_type']}).")

    # Test 12: Recalculate endpoint
    recalc_res = client.post("/api/users/1/next-best-proof/recalculate")
    assert recalc_res.status_code == 200
    assert recalc_res.json()["skill_name"] == "SQL JOINs"
    print("PASS 12: Recalculate endpoint returns freshly computed Next-Best-Proof.")

    # Test 13: Proof Completion Flow (Section 18)
    # Simulate Alex Mercer completing the SQL JOIN practice with 90% score!
    comp_payload = {
        "skill_id": 3,
        "action_type": "PRACTICE",
        "score": 90.0,
        "description": "Completed SQL JOIN Rescue Practice with 9/10 problems solved correctly.",
        "source": "Interactive Practice Lab",
    }
    complete_res = client.post("/api/users/1/next-best-proof/complete", json=comp_payload)
    assert complete_res.status_code == 200
    updated_nbp = complete_res.json()
    print(f"PASS 13: Proof completion flow executed successfully. New Next-Best-Proof: {updated_nbp['skill_name']} ({updated_nbp['title']} - {updated_nbp['action_type']}).")

    # Clean up test practice evidence so Alex Mercer remains in baseline demo state
    from app.core.database import SessionLocal
    from app.models.evidence import SkillEvidence
    db = SessionLocal()
    try:
        db.query(SkillEvidence).filter(
            SkillEvidence.user_id == 1,
            SkillEvidence.source == "Interactive Practice Lab",
        ).delete()
        db.commit()
    finally:
        db.close()
    client.post("/api/users/1/next-best-proof/recalculate")

    print("\n[SUCCESS] ALL PHASE 8 NEXT-BEST-PROOF ENGINE TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    test_next_best_proof()
