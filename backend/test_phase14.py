import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.seed.seed_data import reset_alex_mercer
from app.models.user import User
from app.models.skill import Skill
from app.models.evidence import SkillEvidence
from app.models.roadmap import Roadmap


class Phase14EndToEndDemoIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        # Restore clean demo state upon suite completion
        reset_alex_mercer(cls.db)
        cls.db.close()

    def setUp(self):
        reset_alex_mercer(self.db)

    def test_01_demo_reset_endpoint(self):
        """
        Verify POST /api/demo/reset restores Alex Mercer to the initial baseline state.
        """
        res = self.client.post("/api/demo/reset")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["learner_name"], "Alex Mercer")
        self.assertEqual(data["target_role"], "Data Analyst")
        self.assertEqual(data["sql_joins_debt"], "SKILL_DEBT")
        self.assertIn("Rescue", data["next_best_proof_title"])

    def test_02_demo_initial_state_verification(self):
        """
        Verify initial state:
        - SQL JOINs weak & marked with HIGH Skill Debt
        - Next-Best-Proof recommends SQL JOIN Rescue Practice
        - Roadmap contains SQL JOIN Rescue Practice
        """
        # Check Next-Best-Proof
        res_nbp = self.client.get("/api/users/1/next-best-proof")
        self.assertEqual(res_nbp.status_code, 200)
        nbp_data = res_nbp.json()
        self.assertEqual(nbp_data["skill_name"], "SQL JOINs")
        self.assertEqual(nbp_data["skill_debt_status"], "SKILL_DEBT")
        self.assertEqual(nbp_data["priority"], "CRITICAL")
        self.assertIn("Rescue", nbp_data["title"])

        # Check Skill Debt
        res_debt = self.client.get("/api/users/1/skill-debt/3")
        self.assertEqual(res_debt.status_code, 200)
        debt_data = res_debt.json()
        self.assertEqual(debt_data["debt_status"], "SKILL_DEBT")
        self.assertEqual(debt_data["severity"], "HIGH")

        # Check Roadmap
        res_roadmap = self.client.get("/api/users/1/roadmap")
        self.assertEqual(res_roadmap.status_code, 200)
        roadmap_data = res_roadmap.json()
        step_titles = [s["title"] for s in roadmap_data["steps"]]
        self.assertTrue(any("SQL JOIN" in t and "Rescue" in t for t in step_titles))

    def test_03_submit_practice_evidence(self):
        """
        Submit practice proof for SQL JOINs and assert Skill DNA & Debt progression.
        """
        res_practice = self.client.post(
            "/api/users/1/next-best-proof/complete",
            json={
                "skill_id": 3,
                "action_type": "PRACTICE",
                "score": 78.0,
                "description": "Completed multi-table join rescue practice scenarios.",
                "source": "SQL JOINs Rescue Practice",
            },
        )
        self.assertEqual(res_practice.status_code, 200)

        # Check evidence was persisted
        ev = (
            self.db.query(SkillEvidence)
            .filter_by(user_id=1, skill_id=3, source="SQL JOINs Rescue Practice")
            .first()
        )
        self.assertIsNotNone(ev)
        self.assertEqual(ev.score, 78.0)

    def test_04_submit_real_world_task_in_industry_lab(self):
        """
        Submit realistic SQL JOIN business query to Industry Failure Lab.
        Verify deterministic 4-pillar evaluation and REAL_WORLD_TASK evidence creation.
        """
        canonical_query = """
        SELECT
            c.segment,
            COUNT(DISTINCT o.id) AS total_orders,
            ROUND(SUM(o.total_amount), 2) AS gross_revenue,
            ROUND(COALESCE(SUM(r.refund_amount), 0), 2) AS total_refunds,
            ROUND(SUM(o.total_amount) - COALESCE(SUM(r.refund_amount), 0), 2) AS net_revenue,
            ROUND((COUNT(DISTINCT r.id) * 100.0) / COUNT(DISTINCT o.id), 2) AS return_rate_pct
        FROM lab_retail_customers c
        JOIN lab_retail_orders o ON c.id = o.customer_id
        LEFT JOIN lab_retail_returns r ON o.id = r.order_id
        WHERE o.payment_status = 'COMPLETED'
        GROUP BY c.segment
        ORDER BY net_revenue DESC
        """
        written_rationale = (
            "Enterprise segment delivers $8,142 net revenue with high retention. "
            "Mid-Market suffers higher refund percentages affecting margins."
        )

        res_lab = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={
                "user_id": 1,
                "query": canonical_query,
                "submitted_answer": written_rationale,
                "evidence_type": "REAL_WORLD_TASK",
            },
        )
        self.assertEqual(res_lab.status_code, 200)
        lab_data = res_lab.json()
        self.assertEqual(lab_data["status"], "PASSED")
        self.assertGreaterEqual(lab_data["total_score"], 80.0)

        # Check REAL_WORLD_TASK evidence in DB
        ev = (
            self.db.query(SkillEvidence)
            .filter(
                SkillEvidence.user_id == 1,
                SkillEvidence.skill_id == 3,
                SkillEvidence.evidence_type == "REAL_WORLD_TASK",
            )
            .first()
        )
        self.assertIsNotNone(ev)
        self.assertGreaterEqual(ev.score, 80.0)

    def test_05_complete_orchestration_loop_and_recalculation(self):
        """
        Validate the complete recalculation cascade:
        1. Baseline state
        2. Practice + Real-world evidence submitted
        3. Skill DNA level improves
        4. Skill Debt resolved (HEALTHY / NONE)
        5. Next-Best-Proof recalculates away from SQL JOINs
        6. Dynamic Roadmap transforms: remediation step disappears, downstream step unlocked
        7. Proof-of-Skill Passport shows SQL JOINs as VERIFIED
        """
        # 1. Complete Practice
        self.client.post(
            "/api/users/1/next-best-proof/complete",
            json={
                "skill_id": 3,
                "action_type": "PRACTICE",
                "score": 78.0,
                "description": "SQL JOINs targeted practice completion.",
                "source": "SQL JOINs Rescue Practice",
            },
        )

        # 2. Complete Real-World Workplace Task
        self.client.post(
            "/api/users/1/next-best-proof/complete",
            json={
                "skill_id": 3,
                "action_type": "REAL_WORLD_TASK",
                "score": 88.0,
                "description": "Retail E-Commerce Returns Analytics & multi-table SQL joins.",
                "source": "Retail Customer Analytics Lab",
            },
        )

        # 3. Check Skill DNA update
        res_dna = self.client.get("/api/users/1/skills/3/skill-dna")
        self.assertEqual(res_dna.status_code, 200)
        dna_data = res_dna.json()
        self.assertGreaterEqual(dna_data["skill_level"], 75.0)
        self.assertIn(dna_data["status"], ["STRONG", "HEALTHY"])
        self.assertGreaterEqual(dna_data["evidence_count"], 3)

        # 4. Check Skill Debt update
        res_debt = self.client.get("/api/users/1/skill-debt/3")
        self.assertEqual(res_debt.status_code, 200)
        debt_data = res_debt.json()
        self.assertEqual(debt_data["debt_status"], "HEALTHY")
        self.assertEqual(debt_data["severity"], "NONE")

        # 5. Check Next-Best-Proof recalculation
        res_nbp = self.client.get("/api/users/1/next-best-proof")
        self.assertEqual(res_nbp.status_code, 200)
        nbp_data = res_nbp.json()
        # NBP should NO LONGER be SQL JOINs since SQL JOINs is now healthy!
        self.assertNotEqual(nbp_data["skill_name"], "SQL JOINs")

        # 6. Check Roadmap Transformation
        res_roadmap = self.client.get("/api/users/1/roadmap")
        self.assertEqual(res_roadmap.status_code, 200)
        roadmap_data = res_roadmap.json()
        steps = roadmap_data["steps"]

        # SQL JOINs Verification is now COMPLETED
        join_step = next((s for s in steps if s["skill_name"] == "SQL JOINs"), None)
        self.assertIsNotNone(join_step)
        self.assertEqual(join_step["status"], "COMPLETED")

        # Downstream step (e.g. EDA) has unlocked and is RECOMMENDED
        recommended_step = next((s for s in steps if s["status"] == "RECOMMENDED"), None)
        self.assertIsNotNone(recommended_step)
        self.assertNotEqual(recommended_step["skill_name"], "SQL JOINs")

        # 7. Check Skill Passport
        res_passport = self.client.get("/api/users/1/skill-passport")
        self.assertEqual(res_passport.status_code, 200)
        passport_data = res_passport.json()
        matrix = passport_data["skill_proof_matrix"]
        join_matrix_item = next((s for s in matrix if s["skill_name"] == "SQL JOINs"), None)
        self.assertIsNotNone(join_matrix_item)
        self.assertTrue(join_matrix_item["is_verified"])
        self.assertEqual(join_matrix_item["status"], "VERIFIED")
        self.assertGreaterEqual(len(join_matrix_item["supporting_evidences"]), 3)

    def test_06_demo_state_route(self):
        """
        Verify GET /api/demo/state returns accurate comparative metrics.
        """
        res = self.client.get("/api/demo/state?user_id=1")
        self.assertEqual(res.status_code, 200)
        state_data = res.json()
        self.assertEqual(state_data["learner_name"], "Alex Mercer")
        self.assertEqual(state_data["target_role"], "Data Analyst")
        self.assertIn("sql_joins_snapshot", state_data)


if __name__ == "__main__":
    unittest.main()
