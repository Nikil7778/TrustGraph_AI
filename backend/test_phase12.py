import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role

client = TestClient(app)


class Phase12DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        cls.alex = cls.db.query(User).filter(User.id == 1).first()
        if not cls.alex:
            cls.alex = cls.db.query(User).first()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_dashboard_structure(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/dashboard/{user_id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["user_id"], user_id)
        self.assertIn("learner_name", data)
        self.assertIn("target_role_name", data)
        self.assertIn("all_roles", data)
        self.assertIn("metrics", data)
        self.assertIn("next_best_proof", data)
        self.assertIn("highest_career_gap", data)
        self.assertIn("skill_gap_heatmap", data)
        self.assertIn("skill_dna_snapshot", data)
        self.assertIn("top_career_priorities", data)
        self.assertIn("recent_evidence", data)
        self.assertIn("roadmap_preview", data)
        self.assertIn("progress_history", data)

    def test_02_career_readiness_calculation(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/dashboard/{user_id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        readiness = data["metrics"]["career_readiness"]
        self.assertIsInstance(readiness["score"], float)
        self.assertGreater(readiness["score"], 0.0)
        self.assertLessEqual(readiness["score"], 100.0)
        self.assertIn(readiness["status"], ["Job ready", "On track", "Needs improvement", "Awaiting baseline assessment"])
        self.assertTrue(len(readiness["formula_explanation"]) > 10)

    def test_03_supporting_metrics(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/dashboard/{user_id}")
        self.assertEqual(res.status_code, 200)
        metrics = res.json()["metrics"]

        self.assertGreaterEqual(metrics["skills_verified"], 0)
        self.assertGreaterEqual(metrics["total_role_skills"], 1)
        self.assertGreaterEqual(metrics["active_skill_debt_count"], 0)
        self.assertGreaterEqual(metrics["evidence_records_count"], 1)

    def test_04_next_best_proof_primary_action(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/dashboard/{user_id}")
        self.assertEqual(res.status_code, 200)
        nbp = res.json()["next_best_proof"]
        self.assertIsNotNone(nbp)
        self.assertIn("SQL JOIN", nbp["skill_name"])
        self.assertIn(nbp["priority"], ["CRITICAL", "HIGH"])
        self.assertIn("action_type", nbp)
        self.assertIn("expected_proof", nbp)

    def test_05_skill_debt_alert(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/dashboard/{user_id}")
        self.assertEqual(res.status_code, 200)
        alert = res.json()["skill_debt_alert"]
        self.assertIsNotNone(alert)
        self.assertEqual(alert["severity"], "HIGH")
        self.assertIn("SQL JOIN", alert["skill_name"])
        self.assertTrue(len(alert["message"]) > 10)

    def test_06_skill_gap_heatmap(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/dashboard/{user_id}")
        self.assertEqual(res.status_code, 200)
        heatmap = res.json()["skill_gap_heatmap"]
        self.assertGreater(len(heatmap), 0)

        first_item = heatmap[0]
        self.assertIn("skill_name", first_item)
        self.assertIn("current_level", first_item)
        self.assertIn("required_level", first_item)
        self.assertIn("gap", first_item)
        self.assertIn("status", first_item)
        self.assertIn(first_item["status"], ["healthy", "developing", "critical", "unknown"])

    def test_07_recent_evidence(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/dashboard/{user_id}")
        self.assertEqual(res.status_code, 200)
        evidence = res.json()["recent_evidence"]
        self.assertGreater(len(evidence), 0)

        ev0 = evidence[0]
        self.assertIn("skill_name", ev0)
        self.assertIn("evidence_type", ev0)
        self.assertIn("score", ev0)
        self.assertIn("verified_date", ev0)

    def test_08_dynamic_roadmap_preview(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/dashboard/{user_id}")
        self.assertEqual(res.status_code, 200)
        roadmap_preview = res.json()["roadmap_preview"]
        self.assertGreater(len(roadmap_preview), 0)

        step0 = roadmap_preview[0]
        self.assertIn("title", step0)
        self.assertIn("status", step0)
        self.assertIn("step_type", step0)

    def test_09_progress_history(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/dashboard/{user_id}")
        self.assertEqual(res.status_code, 200)
        progress = res.json()["progress_history"]
        self.assertGreater(len(progress), 0)

        prog0 = progress[0]
        self.assertIn("skill_name", prog0)
        self.assertIn("history", prog0)
        self.assertGreater(len(prog0["history"]), 0)

    def test_10_nonexistent_user(self):
        res = client.get("/api/dashboard/999999")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
