import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.services.coach_service import coach_service


class TestPhase16MLMastery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db: Session = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_get_model_info(self):
        """Verify GET /api/ml/model-info returns metadata and validation metrics."""
        resp = self.client.get("/api/ml/model-info")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "active")
        self.assertTrue(data["is_advisory"])
        self.assertIn("validation_metrics", data)
        self.assertIn("top_feature_signals", data)
        self.assertGreater(data["feature_count"], 10)

    def test_02_predict_mastery_post(self):
        """Verify POST /api/ml/predict-mastery returns advisory prediction with top signals."""
        resp = self.client.post(
            "/api/ml/predict-mastery",
            json={"user_id": 1, "skill_id": 3}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["skill_id"], 3)
        self.assertIn("mastery_probability", data)
        self.assertTrue(0.0 <= data["mastery_probability"] <= 1.0)
        self.assertIn(data["risk_level"], ["LOW", "MEDIUM", "HIGH"])
        self.assertTrue(data["is_advisory"])
        self.assertGreaterEqual(len(data["top_signals"]), 1)
        self.assertIn("advisory_explanation", data)

    def test_03_predict_mastery_get_convenience(self):
        """Verify GET /api/ml/predict-mastery/{user_id}/{skill_id} convenience endpoint."""
        resp = self.client.get("/api/ml/predict-mastery/1/3")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["skill_id"], 3)
        self.assertIn("mastery_probability", data)

    def test_04_coach_mastery_prediction_tool(self):
        """Verify Coach tool get_skill_mastery_prediction executes and returns advisory facts."""
        result = coach_service.execute_tool(
            self.db,
            user_id=1,
            tool_name="get_skill_mastery_prediction",
            args={"skill_name": "SQL"}
        )
        self.assertNotIn("error", result)
        self.assertIn("mastery_probability", result)
        self.assertIn("risk_level", result)
        self.assertTrue(result["is_advisory"])
        self.assertIn("top_signals", result)


if __name__ == "__main__":
    unittest.main()
