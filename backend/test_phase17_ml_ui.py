import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.services.skill_dna_service import skill_dna_service
from app.services.skill_debt_service import skill_debt_service
from app.services.career_value_service import career_value_service
from app.services.next_best_proof_service import next_best_proof_service
from app.services.roadmap_service import roadmap_service
from app.services.coach_service import coach_service
from app.schemas.coach import CoachChatRequest


class TestPhase17MLUIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db: Session = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_ml_prediction_does_not_modify_deterministic_engines(self):
        """CRITICAL: ML must NOT silently modify Career Value, Skill Debt, Next-Best-Proof, or Roadmap."""
        # 1. Snapshot deterministic states BEFORE ML call
        dna_before = skill_dna_service.get_user_skill_dna(self.db, 1)
        debt_before = skill_debt_service.calculate_skill_debt(self.db, 1, 1)
        cv_before = career_value_service.calculate_career_value(self.db, 1, 1)
        nbp_before = next_best_proof_service.get_next_best_proof(self.db, 1, 1)
        rm_before = roadmap_service.get_user_roadmap(self.db, 1)
        rm_steps_before = [(s.id, s.order_index, s.status, s.reason) for s in rm_before.steps] if rm_before else []

        # 2. Invoke ML predictions multiple times
        resp1 = self.client.post("/api/ml/predict-mastery", json={"user_id": 1, "skill_id": 3})
        self.assertEqual(resp1.status_code, 200)
        resp2 = self.client.get("/api/ml/predict-mastery/1/1")
        self.assertEqual(resp2.status_code, 200)

        # 3. Snapshot deterministic states AFTER ML call
        dna_after = skill_dna_service.get_user_skill_dna(self.db, 1)
        debt_after = skill_debt_service.calculate_skill_debt(self.db, 1, 1)
        cv_after = career_value_service.calculate_career_value(self.db, 1, 1)
        nbp_after = next_best_proof_service.get_next_best_proof(self.db, 1, 1)
        rm_after = roadmap_service.get_user_roadmap(self.db, 1)
        rm_steps_after = [(s.id, s.order_index, s.status, s.reason) for s in rm_after.steps] if rm_after else []

        # 4. Strict assertions: 100% identical outputs
        self.assertEqual(
            [(d["skill_name"], d["skill_level"], d["confidence"]) for d in dna_before],
            [(d["skill_name"], d["skill_level"], d["confidence"]) for d in dna_after],
            "Skill DNA vector mutated by ML prediction!"
        )
        self.assertEqual(
            [(d["skill_name"], d["debt_score"], d["debt_status"]) for d in debt_before],
            [(d["skill_name"], d["debt_score"], d["debt_status"]) for d in debt_after],
            "Skill Debt scores mutated by ML prediction!"
        )
        self.assertEqual(
            [(c["skill_name"], c["career_value_score"], c["priority"]) for c in cv_before],
            [(c["skill_name"], c["career_value_score"], c["priority"]) for c in cv_after],
            "Career Value rankings mutated by ML prediction!"
        )
        self.assertEqual(nbp_before["skill_name"], nbp_after["skill_name"], "Next-Best-Proof skill changed!")
        self.assertEqual(nbp_before["action_type"], nbp_after["action_type"], "Next-Best-Proof action changed!")
        self.assertEqual(nbp_before["priority"], nbp_after["priority"], "Next-Best-Proof priority changed!")
        self.assertEqual(rm_steps_before, rm_steps_after, "Roadmap ordering or status changed!")

    def test_02_career_coach_retrieves_actual_ml_prediction(self):
        """Career Coach answers 'What is my predicted readiness for SQL JOINs?' using live model data."""
        req = CoachChatRequest(user_id=1, message="What is my predicted readiness for SQL JOINs?")
        res = coach_service.chat(self.db, req)

        self.assertIn("get_skill_mastery_prediction", res.tools_used)
        self.assertIn("Predicted Likelihood of Success on Next Proof", res.reply)
        self.assertIn("Risk", res.reply)
        self.assertIn("Advisory", res.reply)

    def test_03_no_hardcoded_predictions_distinct_competencies(self):
        """Verify that ML predictions differ across skills based on real learner evidence history."""
        resp_sql = self.client.get("/api/ml/predict-mastery/1/3").json()
        resp_python = self.client.get("/api/ml/predict-mastery/1/1").json()

        # Both valid probabilities
        self.assertTrue(0.0 <= resp_sql["mastery_probability"] <= 1.0)
        self.assertTrue(0.0 <= resp_python["mastery_probability"] <= 1.0)

        # Distinct scores and risk classifications
        self.assertNotEqual(resp_sql["mastery_probability"], resp_python["mastery_probability"])
        self.assertIn(resp_sql["risk_level"], ["HIGH", "MEDIUM"])
        self.assertEqual(resp_python["risk_level"], "LOW")

    def test_04_risk_level_threshold_conformance(self):
        """Verify risk level mapping: LOW (>=0.70), MEDIUM (0.40-0.69), HIGH (<0.40)."""
        from ml.inference.mastery_predictor import get_mastery_predictor
        predictor = get_mastery_predictor()
        self.assertEqual(predictor.determine_risk_level(0.85), "LOW")
        self.assertEqual(predictor.determine_risk_level(0.70), "LOW")
        self.assertEqual(predictor.determine_risk_level(0.69), "MEDIUM")
        self.assertEqual(predictor.determine_risk_level(0.40), "MEDIUM")
        self.assertEqual(predictor.determine_risk_level(0.39), "HIGH")
        self.assertEqual(predictor.determine_risk_level(0.10), "HIGH")

    def test_05_unknown_skill_graceful_handling(self):
        """Verify system handles nonexistent skill safely without fabrication or 500 error."""
        resp = self.client.get("/api/ml/predict-mastery/1/99999")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("not found", resp.json()["detail"].lower())

        coach_req = CoachChatRequest(user_id=1, message="What is my predicted mastery for Quantum Computing?")
        coach_res = coach_service.chat(self.db, coach_req)
        self.assertIn("not found", coach_res.reply.lower())


if __name__ == "__main__":
    unittest.main()
