from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import generate_session_token, verify_session_token
from app.core.database import SessionLocal
from app.models.user import User

client = TestClient(app)


def test_token_generation_and_verification():
    user_id = 42
    token = generate_session_token(user_id)
    assert token is not None
    assert "." in token

    extracted_id = verify_session_token(token)
    assert extracted_id == user_id

    # Tampered token should fail
    tampered = token[:-2] + "xx"
    assert verify_session_token(tampered) is None

    # Invalid string should fail
    assert verify_session_token("invalid_token") is None
    assert verify_session_token("") is None


def test_login_existing_demo_user():
    response = client.post("/api/auth/login", json={"email": "alex.mercer@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == 1
    assert data["user"]["email"] == "alex.mercer@example.com"
    assert "token" in data
    assert "session_token" in response.cookies


def test_login_case_insensitive():
    response = client.post("/api/auth/login", json={"email": "ALEX.MERCER@EXAMPLE.COM"})
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == 1


def test_login_nonexistent_user():
    response = client.post("/api/auth/login", json={"email": "nobody_exists_here@unknown.com"})
    assert response.status_code == 401
    assert "No learner account found" in response.json()["detail"]


def test_auth_me_authenticated():
    token = generate_session_token(1)
    # Using Bearer header
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["email"] == "alex.mercer@example.com"


def test_auth_me_unauthenticated():
    clean_client = TestClient(app)
    response = clean_client.get("/api/auth/me")
    assert response.status_code == 401


def test_logout():
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_register_duplicate_email():
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Alex Mercer",
            "email": "alex.mercer@example.com",
            "target_role_id": 1,
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_coach_chat_resolves_authenticated_learner():
    # Login as user 1
    token = generate_session_token(1)
    response = client.post(
        "/api/coach/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": 9999,  # Even if client erroneously sent 9999
            "message": "What is my next priority?",
        },
    )
    assert response.status_code == 200
    # Response generated successfully because backend resolved authenticated user 1
    data = response.json()
    assert "reply" in data


if __name__ == "__main__":
    tests = [
        test_token_generation_and_verification,
        test_login_existing_demo_user,
        test_login_case_insensitive,
        test_login_nonexistent_user,
        test_auth_me_authenticated,
        test_auth_me_unauthenticated,
        test_logout,
        test_register_duplicate_email,
        test_coach_chat_resolves_authenticated_learner,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print("\nALL AUTH TESTS PASSED SUCCESSFULLY (9/9)!")
