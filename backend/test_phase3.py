import time
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import engine, Base, SessionLocal
from app.seed.seed_data import seed_database

client = TestClient(app)

def get(path):
    resp = client.get(f"/api{path}")
    return resp.status_code, resp.json()

def post(path, body):
    resp = client.post(f"/api{path}", json=body)
    return resp.status_code, resp.json()

def test_phase3_onboarding():
    print("=== Testing Phase 3 Onboarding API ===")
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # 1. Fetch Roles
    status, roles = get("/roles")
    assert status == 200 and len(roles) > 0
    da_role_id = roles[0]["id"]
    print(f"Loaded {len(roles)} target roles from API. Selected Role ID: {da_role_id}")

    # 2. Onboard new learner
    test_email = f"new.learner.{int(time.time())}@example.com"
    new_user_body = {
        "name": "Jordan Lee",
        "email": test_email,
        "experience_level": "Beginner",
        "target_role_id": da_role_id,
        "weekly_learning_hours": 8,
        "learning_goal": "Get my first Data/AI job"
    }

    status, created_user = post("/users", new_user_body)
    print(f"POST /api/users: status={status}, user_id={created_user.get('id')}")
    assert status == 201
    user_id = created_user["id"]
    assert created_user["name"] == "Jordan Lee"
    assert created_user["target_role_id"] == da_role_id

    # 3. Check initialized UserSkill records (should exist for all skills with skill_level=0)
    status, user_skills = get(f"/users/{user_id}/skills")
    print(f"GET /api/users/{user_id}/skills: status={status}, count={len(user_skills)}")
    assert status == 200 and len(user_skills) >= 8
    
    for us in user_skills:
        assert us["skill_level"] == 0.0
        assert us["confidence"] == 0.0
        assert us["recency"] == "Not assessed yet"

    # 4. Test duplicate email rejection (400 Bad Request)
    status, err_resp = post("/users", new_user_body)
    print(f"POST /api/users (Duplicate Email): status={status}, detail={err_resp.get('detail')}")
    assert status == 400

    # 5. Test non-existent target role rejection (400 Bad Request)
    invalid_role_body = {
        "name": "Test User",
        "email": f"invalid.role.{int(time.time())}@example.com",
        "target_role_id": 99999
    }
    status, err_resp = post("/users", invalid_role_body)
    print(f"POST /api/users (Invalid Role ID): status={status}, detail={err_resp.get('detail')}")
    assert status == 400

    print("[SUCCESS] PHASE 3 BACKEND ONBOARDING TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_phase3_onboarding()
