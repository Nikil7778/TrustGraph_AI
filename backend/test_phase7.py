import sys
from fastapi.testclient import TestClient
from app.main import app
from app.engines.career_value_engine import career_value_engine
from app.core.database import SessionLocal
from app.models.user import User

client = TestClient(app)


def test_career_value():
    print("=== Running Phase 7 Career Value Engine Tests ===")

    # 1. Formula Unit Tests
    # Baseline comparison: gap=30, role_imp=80, ind_rel=80, conf_gap=40, rec_gap=20, ev_gap=40, debt_boost=0
    base_score = career_value_engine.calculate_career_value_score(
        gap_score=30.0,
        role_importance=80.0,
        industry_relevance=80.0,
        confidence_gap=40.0,
        recency_gap=20.0,
        evidence_gap=40.0,
        debt_boost=0.0,
    )

    # Test 1: Larger role importance increases score
    higher_role_imp_score = career_value_engine.calculate_career_value_score(
        gap_score=30.0,
        role_importance=95.0,  # +15 importance
        industry_relevance=80.0,
        confidence_gap=40.0,
        recency_gap=20.0,
        evidence_gap=40.0,
        debt_boost=0.0,
    )
    assert higher_role_imp_score > base_score, f"Expected {higher_role_imp_score} > {base_score}"
    print(f"PASS 1: Larger role importance increases score ({higher_role_imp_score} > {base_score}).")

    # Test 2: Larger skill gap increases score
    higher_gap_score = career_value_engine.calculate_career_value_score(
        gap_score=50.0,  # +20 gap
        role_importance=80.0,
        industry_relevance=80.0,
        confidence_gap=40.0,
        recency_gap=20.0,
        evidence_gap=40.0,
        debt_boost=0.0,
    )
    assert higher_gap_score > base_score, f"Expected {higher_gap_score} > {base_score}"
    print(f"PASS 2: Larger skill gap increases score ({higher_gap_score} > {base_score}).")

    # Test 3: Higher industry relevance increases score
    higher_ind_score = career_value_engine.calculate_career_value_score(
        gap_score=30.0,
        role_importance=80.0,
        industry_relevance=100.0,  # +20 industry relevance
        confidence_gap=40.0,
        recency_gap=20.0,
        evidence_gap=40.0,
        debt_boost=0.0,
    )
    assert higher_ind_score > base_score, f"Expected {higher_ind_score} > {base_score}"
    print(f"PASS 3: Higher industry relevance increases score ({higher_ind_score} > {base_score}).")

    # Test 4: Lower confidence increases priority (larger confidence gap)
    lower_conf_score = career_value_engine.calculate_career_value_score(
        gap_score=30.0,
        role_importance=80.0,
        industry_relevance=80.0,
        confidence_gap=70.0,  # was 40
        recency_gap=20.0,
        evidence_gap=40.0,
        debt_boost=0.0,
    )
    assert lower_conf_score > base_score, f"Expected {lower_conf_score} > {base_score}"
    print(f"PASS 4: Lower confidence increases priority ({lower_conf_score} > {base_score}).")

    # Test 5 & 6: Older & weaker evidence increases priority
    weaker_ev_score = career_value_engine.calculate_career_value_score(
        gap_score=30.0,
        role_importance=80.0,
        industry_relevance=80.0,
        confidence_gap=40.0,
        recency_gap=80.0,  # older evidence
        evidence_gap=80.0,  # weaker evidence
        debt_boost=0.0,
    )
    assert weaker_ev_score > base_score, f"Expected {weaker_ev_score} > {base_score}"
    print(f"PASS 5 & 6: Older & weaker evidence increases priority ({weaker_ev_score} > {base_score}).")

    # Test 7: HIGH Skill Debt receives correct boost (+10)
    debt_boost_val = career_value_engine.determine_debt_boost("SKILL_DEBT", "HIGH")
    assert debt_boost_val == 10.0, f"Expected 10.0, got {debt_boost_val}"
    boosted_score = career_value_engine.calculate_career_value_score(
        gap_score=30.0,
        role_importance=80.0,
        industry_relevance=80.0,
        confidence_gap=40.0,
        recency_gap=20.0,
        evidence_gap=40.0,
        debt_boost=debt_boost_val,
    )
    assert round(boosted_score - base_score, 1) == 10.0, f"Expected +10 boost, got {boosted_score - base_score}"
    print(f"PASS 7: HIGH Skill Debt receives +10 boost ({base_score} -> {boosted_score}).")

    # Test 8: Career score remains clamped 0–100
    clamped_high = career_value_engine.calculate_career_value_score(
        gap_score=100.0, role_importance=100.0, industry_relevance=100.0,
        confidence_gap=100.0, recency_gap=100.0, evidence_gap=100.0, debt_boost=50.0
    )
    assert clamped_high == 100.0, f"Expected 100.0, got {clamped_high}"
    clamped_low = career_value_engine.calculate_career_value_score(
        gap_score=0.0, role_importance=0.0, industry_relevance=0.0,
        confidence_gap=0.0, recency_gap=0.0, evidence_gap=0.0, debt_boost=0.0
    )
    assert clamped_low == 0.0, f"Expected 0.0, got {clamped_low}"
    print("PASS 8: Career value score clamped strictly to [0.0, 100.0].")

    # Test 9: Priority classification is deterministic
    # Test 9: Priority classification matches expected tiers
    assert career_value_engine.classify_priority(80.0) == "CRITICAL"
    assert career_value_engine.classify_priority(65.0) == "HIGH"
    assert career_value_engine.classify_priority(48.0) == "MEDIUM"
    assert career_value_engine.classify_priority(30.0) == "LOW"
    print("PASS 9: Priority classification matches expected tiers.")

    # 2. Integration & Demo Scenario Tests (Alex Mercer, User 1)
    db = SessionLocal()
    try:
        from app.seed.seed_data import reset_alex_mercer
        reset_alex_mercer(db)
    finally:
        db.close()

    recalc_init = client.post("/api/users/1/career-value/recalculate")
    assert recalc_init.status_code == 200, f"Failed recalculating: {recalc_init.text}"

    res = client.get("/api/users/1/career-value")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    ranked = res.json()
    assert len(ranked) >= 8, f"Expected at least 8 skills, got {len(ranked)}"

    # Test 10: Check sorting order
    scores = [item["career_value_score"] for item in ranked]
    assert scores == sorted(scores, reverse=True), "Expected items sorted descending by career_value_score"
    ranks = [item["rank"] for item in ranked]
    assert ranks == list(range(1, len(ranked) + 1)), "Expected sequential ranks starting from 1"
    print(f"PASS 10: Skills returned in correct ranking order (Ranks 1 to {len(ranked)}).")

    # Test 11: SQL JOINs produces meaningful high career value
    sql_joins_item = next((item for item in ranked if item["skill_name"] == "SQL JOINs"), None)
    assert sql_joins_item is not None, "SQL JOINs missing from ranked results"
    assert sql_joins_item["rank"] == 1, f"Expected SQL JOINs to be Rank #1, got Rank #{sql_joins_item['rank']}"
    assert sql_joins_item["career_value_score"] >= 55.0, f"Expected SQL JOINs score >= 55.0, got {sql_joins_item['career_value_score']}"
    assert sql_joins_item["priority"] == "HIGH", f"Expected HIGH priority, got {sql_joins_item['priority']}"
    assert sql_joins_item["debt_boost"] == 10.0, "Expected +10 debt boost for SQL JOINs"
    print(f"PASS 11: SQL JOINs achieved high career priority (Score: {sql_joins_item['career_value_score']}, Priority: {sql_joins_item['priority']}, Rank: #{sql_joins_item['rank']}).")

    # Test 12: Machine Learning does NOT automatically win merely because its proficiency is low (35%)
    ml_item = next((item for item in ranked if item["skill_name"] == "Machine Learning"), None)
    assert ml_item is not None, "Machine Learning missing from ranked results"
    # Machine Learning has low role importance (40%) and low industry relevance (40%)
    assert ml_item["priority"] == "LOW", f"Expected Machine Learning to be LOW priority, got {ml_item['priority']}"
    assert ml_item["career_value_score"] < sql_joins_item["career_value_score"], (
        f"SQL JOINs ({sql_joins_item['career_value_score']}) should outrank Machine Learning ({ml_item['career_value_score']})"
    )
    print(f"PASS 12: Machine Learning correctly deprioritized due to role relevance (Score: {ml_item['career_value_score']}, Rank: #{ml_item['rank']} vs SQL JOINs Rank: #{sql_joins_item['rank']}).")

    # Test 13: Explanation contains meaningful structured reasons
    assert "SQL JOINs" in sql_joins_item["reason"]
    assert "Data Analyst" in sql_joins_item["reason"]
    assert "lower priority" in ml_item["reason"].lower() or "lower importance" in ml_item["reason"].lower()
    print("PASS 13: Structured explanations explain both high-priority focus and low-priority postponement.")

    # Test 14: Single skill endpoint
    single_res = client.get(f"/api/users/1/career-value/{sql_joins_item['skill_id']}")
    assert single_res.status_code == 200
    assert single_res.json()["skill_name"] == "SQL JOINs"
    print("PASS 14: Single skill and recalculation API endpoints verified.")

    print("\n[SUCCESS] ALL PHASE 7 CAREER VALUE ENGINE TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    test_career_value()
