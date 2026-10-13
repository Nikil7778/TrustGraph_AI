import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User, UserSkill
from app.models.evidence import SkillEvidence
from app.models.roadmap import Roadmap, RoadmapStep
from app.core.auth import hash_password, verify_password, generate_session_token, verify_session_token
from app.services.skill_dna_service import skill_dna_service
from app.services.skill_debt_service import skill_debt_service
from app.services.next_best_proof_service import next_best_proof_service
from app.services.roadmap_service import roadmap_service


class TestAuthAndGoogleSignIn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db: Session = SessionLocal()
        cls._cleanup(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls._cleanup(cls.db)
        cls.db.close()

    @classmethod
    def _cleanup(cls, db: Session):
        emails = [
            "google_existing_test@example.com",
            "google_new_test@example.com",
            "password_test_user@example.com",
        ]
        users = db.query(User).filter(User.email.in_(emails)).all()
        for u in users:
            db.query(SkillEvidence).filter(SkillEvidence.user_id == u.id).delete()
            db.query(UserSkill).filter(UserSkill.user_id == u.id).delete()
            rms = db.query(Roadmap).filter(Roadmap.user_id == u.id).all()
            for rm in rms:
                db.query(RoadmapStep).filter(RoadmapStep.roadmap_id == rm.id).delete()
                db.delete(rm)
            db.delete(u)
        db.commit()

    def test_password_hashing_and_verification(self):
        pw = "SuperSecret123!"
        hashed = hash_password(pw)
        self.assertTrue(hashed.startswith("pbkdf2_sha256$"))
        self.assertTrue(verify_password(pw, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))
        self.assertFalse(verify_password("", hashed))
        self.assertFalse(verify_password(pw, None))

    def test_email_password_login_and_hash_persisted(self):
        # 1. Register a user with password
        email = "password_test_user@example.com"
        reg_res = self.client.post("/api/auth/register", json={
            "name": "Password User",
            "email": email,
            "password": "MyStrongPassword456",
            "target_role_id": 1,
        })
        self.assertEqual(reg_res.status_code, 201)
        data = reg_res.json()
        self.assertEqual(data["user"]["email"], email)

        # 2. Try login with wrong password -> 401
        bad_res = self.client.post("/api/auth/login", json={
            "email": email,
            "password": "wrongpassword",
        })
        self.assertEqual(bad_res.status_code, 401)
        self.assertIn("Incorrect password", bad_res.json()["detail"])

        # 3. Try login with correct password -> 200
        good_res = self.client.post("/api/auth/login", json={
            "email": email,
            "password": "MyStrongPassword456",
        })
        self.assertEqual(good_res.status_code, 200)
        self.assertIn("token", good_res.json())

    @patch("app.api.routes.auth.verify_google_credential")
    def test_google_existing_user_match_no_duplicate(self, mock_verify):
        # Create user first via regular email
        email = "google_existing_test@example.com"
        user = User(
            name="Existing Google Learner",
            email=email,
            target_role_id=1,
            experience_level="Intermediate",
            weekly_learning_hours=10,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        original_id = user.id

        # Mock Google Token Verification response
        mock_verify.return_value = {
            "sub": "google-sub-12345",
            "email": email,
            "name": "Existing Google Learner",
            "picture": "https://lh3.googleusercontent.com/avatar.jpg",
            "email_verified": True,
        }

        # Call /api/auth/google
        res = self.client.post("/api/auth/google", json={"credential": "mock_id_token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["user"]["id"], original_id)
        self.assertEqual(data["user"]["email"], email)
        self.assertFalse(data["is_new_user"])
        self.assertFalse(data["needs_onboarding"])

        # Confirm user in DB now has google_id and avatar_url linked
        self.db.expire_all()
        db_user = self.db.query(User).filter(User.id == original_id).first()
        self.assertEqual(db_user.google_id, "google-sub-12345")
        self.assertEqual(db_user.avatar_url, "https://lh3.googleusercontent.com/avatar.jpg")

    @patch("app.api.routes.auth.verify_google_credential")
    def test_google_new_user_clean_state_no_demo_leak(self, mock_verify):
        email = "google_new_test@example.com"
        mock_verify.return_value = {
            "sub": "google-sub-99999",
            "email": email,
            "name": "Fresh Google Learner",
            "picture": "https://lh3.googleusercontent.com/fresh.jpg",
            "email_verified": True,
        }

        res = self.client.post("/api/auth/google", json={"credential": "mock_fresh_token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        new_uid = data["user"]["id"]
        self.assertTrue(data["is_new_user"])
        self.assertTrue(data["needs_onboarding"])

        # Check evidence count = 0
        ev_count = self.db.query(SkillEvidence).filter(SkillEvidence.user_id == new_uid).count()
        self.assertEqual(ev_count, 0)

        # Check Skill DNA = UNKNOWN / 0.0
        dna = skill_dna_service.get_user_skill_dna(self.db, new_uid)
        for item in dna:
            self.assertEqual(item["skill_level"], 0.0)
            self.assertEqual(item["status"], "UNKNOWN")

        # Check Skill Debt = 0 active SKILL_DEBT
        debts = skill_debt_service.calculate_skill_debt(self.db, new_uid, 1)
        active_debts = [d for d in debts if d.get("debt_status") == "SKILL_DEBT"]
        self.assertEqual(len(active_debts), 0)

        # Check Next-Best-Proof = Complete Diagnostic Assessment
        nbp = next_best_proof_service.get_next_best_proof(self.db, new_uid, 1)
        self.assertEqual(nbp["title"], "Complete Diagnostic Assessment")
        self.assertNotIn("SQL JOIN", nbp["title"])

        # Check Roadmap has 3-step onboarding sequence
        rm = roadmap_service.get_user_roadmap(self.db, new_uid)
        self.assertEqual(len(rm.steps), 3)
        self.assertEqual(rm.steps[0].title, "Complete Diagnostic Assessment")


if __name__ == "__main__":
    unittest.main()
