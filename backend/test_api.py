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

def run_tests():
    print("=== Testing FastAPI Endpoints ===")

    # Ensure DB tables exist and are seeded
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    
    # 1. Health
    status, data = get("/health")
    print(f"GET /api/health: {status} -> {data}")
    assert status == 200 and data["database"] == "connected"

    # 2. Roles
    status, data = get("/roles")
    print(f"GET /api/roles: {status} -> {len(data)} roles found")
    assert status == 200 and len(data) >= 3

    # 3. Skills
    status, data = get("/skills")
    print(f"GET /api/skills: {status} -> {len(data)} skills found")
    assert status == 200 and len(data) >= 8

    # 4. User #1 (Alex Mercer)
    status, data = get("/users/1")
    print(f"GET /api/users/1: {status} -> Name: {data['name']}, Target Role: {data['target_role']['name']}")
    assert status == 200 and data["name"] == "Alex Mercer"

    # 5. User #1 Skills (Skill DNA)
    status, data = get("/users/1/skills")
    print(f"GET /api/users/1/skills: {status} -> {len(data)} user skill scores found")
    assert status == 200 and len(data) >= 8

    # 6. User #1 Evidence Audit Trail
    status, data = get("/users/1/evidence")
    print(f"GET /api/users/1/evidence: {status} -> {len(data)} evidence records found")
    assert status == 200 and len(data) >= 4

    # 7. User #1 Active Roadmap
    status, data = get("/users/1/roadmap")
    print(f"GET /api/users/1/roadmap: {status} -> Version: {data['version']}, Steps: {len(data['steps'])}")
    assert status == 200 and len(data["steps"]) >= 5

    # 8. Assessments
    status, data = get("/assessments")
    print(f"GET /api/assessments: {status} -> {len(data)} diagnostic assessments found")
    assert status == 200 and len(data) >= 1

    # 9. Projects
    status, data = get("/projects")
    print(f"GET /api/projects: {status} -> {len(data)} portfolio projects found")
    assert status == 200 and len(data) >= 1

    # 10. POST /api/assessment-attempts (Submit Diagnostic Attempt)
    attempt_body = {
        "user_id": 1,
        "assessment_id": 1,
        "score": 85.0,
        "accuracy": 88.0
    }
    status, data = post("/assessment-attempts", attempt_body)
    print(f"POST /api/assessment-attempts: {status} -> Attempt ID: {data.get('id')}, Score: {data.get('score')}")
    assert status == 201 and data["score"] == 85.0

    # 11. Validation Test (Invalid body returns 422 Unprocessable Entity)
    invalid_body = {"email": "not-an-email"}
    status, data = post("/users", invalid_body)
    print(f"POST /api/users (Invalid Body): {status} -> Detail: {data.get('detail')}")
    assert status == 422

    print("\n[SUCCESS] ALL BACKEND API TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
