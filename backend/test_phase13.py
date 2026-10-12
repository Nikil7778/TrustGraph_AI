import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User

client = TestClient(app)


class Phase13SkillPassportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        cls.alex = cls.db.query(User).filter(User.id == 1).first()
        if not cls.alex:
            cls.alex = cls.db.query(User).first()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_skill_passport_structure(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/users/{user_id}/skill-passport")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("header", data)
        self.assertIn("summary", data)
        self.assertIn("skill_proof_matrix", data)
        self.assertIn("evidence_timeline", data)
        self.assertIn("strongest_proof", data)
        self.assertIn("skills_needing_proof", data)
        self.assertIn("career_relevance", data)

        header = data["header"]
        self.assertEqual(header["user_id"], user_id)
        self.assertIn("Alex", header["learner_name"])
        self.assertEqual(header["target_role_name"], "Data Analyst")
        self.assertGreaterEqual(header["skills_verified_count"], 1)
        self.assertGreaterEqual(header["total_evidence_count"], 1)
        self.assertTrue(header["passport_id"].startswith("SP-"))

    def test_02_skill_proof_matrix_and_evidence_connection(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/users/{user_id}/skill-passport")
        self.assertEqual(res.status_code, 200)
        matrix = res.json()["skill_proof_matrix"]
        self.assertGreater(len(matrix), 0)

        # Check Python or SQL item
        python_item = next((m for m in matrix if m["skill_name"] == "Python"), None)
        self.assertIsNotNone(python_item)
        self.assertTrue(python_item["is_verified"])
        self.assertEqual(python_item["status"], "VERIFIED")
        self.assertGreater(len(python_item["supporting_evidences"]), 0)

        ev0 = python_item["supporting_evidences"][0]
        self.assertIn("source", ev0)
        self.assertIn("evidence_type", ev0)
        self.assertIn("evidence_strength", ev0)
        self.assertGreater(ev0["score"], 0)

    def test_03_skill_debt_in_passport(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/users/{user_id}/skill-passport")
        self.assertEqual(res.status_code, 200)
        matrix = res.json()["skill_proof_matrix"]

        # SQL JOINs has seeded skill debt
        joins_item = next((m for m in matrix if m["skill_name"] == "SQL JOINs"), None)
        self.assertIsNotNone(joins_item)
        self.assertFalse(joins_item["is_verified"])
        self.assertEqual(joins_item["status"], "SKILL DEBT")
        self.assertGreater(len(joins_item["supporting_evidences"]), 0)

    def test_04_evidence_timeline(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/users/{user_id}/skill-passport")
        self.assertEqual(res.status_code, 200)
        timeline = res.json()["evidence_timeline"]
        self.assertGreater(len(timeline), 0)

        item = timeline[0]
        self.assertIn("skill_name", item)
        self.assertIn("score", item)
        self.assertIn("verified_date", item)

    def test_05_strongest_proof(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/users/{user_id}/skill-passport")
        self.assertEqual(res.status_code, 200)
        strongest = res.json()["strongest_proof"]
        self.assertIsNotNone(strongest)
        self.assertIn("title", strongest)
        self.assertGreater(strongest["score"], 0)
        self.assertIn("evidence_strength", strongest)

    def test_06_skills_needing_more_proof(self):
        user_id = self.alex.id if self.alex else 1
        res = client.get(f"/api/users/{user_id}/skill-passport")
        self.assertEqual(res.status_code, 200)
        needing = res.json()["skills_needing_proof"]
        self.assertGreater(len(needing), 0)

        joins_need = next((n for n in needing if n["skill_name"] == "SQL JOINs"), None)
        self.assertIsNotNone(joins_need)
        self.assertEqual(joins_need["status"], "SKILL_DEBT")

    def test_07_individual_skill_detail_endpoint(self):
        user_id = self.alex.id if self.alex else 1
        res_full = client.get(f"/api/users/{user_id}/skill-passport")
        first_skill_id = res_full.json()["skill_proof_matrix"][0]["skill_id"]

        res = client.get(f"/api/users/{user_id}/skill-passport/{first_skill_id}")
        self.assertEqual(res.status_code, 200)
        detail = res.json()
        self.assertEqual(detail["skill_id"], first_skill_id)
        self.assertIn("supporting_evidences", detail)

    def test_08_sub_endpoints(self):
        user_id = self.alex.id if self.alex else 1
        res_summary = client.get(f"/api/users/{user_id}/skill-passport/summary")
        self.assertEqual(res_summary.status_code, 200)
        self.assertIn("verified_skills_count", res_summary.json())

        res_ev = client.get(f"/api/users/{user_id}/skill-passport/evidence")
        self.assertEqual(res_ev.status_code, 200)
        self.assertIsInstance(res_ev.json(), list)

    def test_09_nonexistent_user(self):
        res = client.get("/api/users/999999/skill-passport")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
