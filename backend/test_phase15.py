import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.skill import Skill
from app.engines.industry_lab_engine import IndustryLabEngine
from app.services.ai_service import ai_service


class TestPhase15HardeningAndEdgeCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db: Session = SessionLocal()
        cls.lab_engine = IndustryLabEngine()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_sql_sandbox_security_rejections(self):
        """Part C & H: Verify SQL sandbox rejects all dangerous, mutating, or multi-statement queries."""
        dangerous_queries = [
            ("DROP TABLE lab_retail_customers", "DROP"),
            ("DELETE FROM lab_retail_orders WHERE id = 1", "DELETE"),
            ("INSERT INTO lab_retail_products (id, name) VALUES (999, 'Malicious')", "INSERT"),
            ("UPDATE lab_retail_orders SET total_amount = 0", "UPDATE"),
            ("ALTER TABLE lab_retail_orders ADD COLUMN hack text", "ALTER"),
            ("TRUNCATE TABLE lab_retail_returns", "TRUNCATE"),
            ("CREATE TABLE hacked (id int)", "CREATE"),
            ("SELECT * FROM lab_retail_orders; DROP TABLE lab_retail_returns", "Multiple SQL statements"),
            ("", "Query cannot be empty"),
            ("   -- just a comment\n  ", "Query cannot be empty"),
            ("EXEC xp_cmdshell('dir')", "Unauthorized query type"),
        ]

        for query, expected_fragment in dangerous_queries:
            # 1. Direct engine validation
            is_safe, err_msg = self.lab_engine.validate_sql_security(query)
            self.assertFalse(is_safe, f"Query '{query}' should have been rejected!")
            self.assertIsNotNone(err_msg)

            # 2. API Sandbox Run endpoint validation
            resp = self.client.post(
                "/api/industry-labs/retail-returns-analytics/run",
                json={"query": query},
            )
            # Either 422 for empty query validation or 200 with success=False
            if resp.status_code == 200:
                data = resp.json()
                self.assertFalse(data["success"])
                self.assertIsNotNone(data["error_message"])
            else:
                self.assertEqual(resp.status_code, 422)

    def test_02_sql_sandbox_read_only_allowed_queries(self):
        """Part C: Verify legitimate read-only queries with JOIN and CTE execute cleanly."""
        safe_query = """
        WITH HighOrders AS (
            SELECT customer_id, total_amount
            FROM lab_retail_orders
            WHERE payment_status = 'COMPLETED'
        )
        SELECT c.segment, COUNT(o.customer_id) as num_orders
        FROM lab_retail_customers c
        LEFT JOIN HighOrders o ON c.id = o.customer_id
        GROUP BY c.segment
        """
        is_safe, err_msg = self.lab_engine.validate_sql_security(safe_query)
        self.assertTrue(is_safe, f"Safe query failed validation: {err_msg}")

        resp = self.client.post(
            "/api/industry-labs/retail-returns-analytics/run",
            json={"query": safe_query},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertGreater(data["row_count"], 0)
        self.assertIn("segment", [c.lower() for c in data["columns"]])

    def test_03_pydantic_input_bounds_and_validations(self):
        """Part C & G: Verify strict Pydantic rejection of invalid types, IDs, and payload sizes."""
        # Negative user_id
        resp = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={"user_id": -5, "query": "SELECT * FROM lab_retail_customers"},
        )
        self.assertEqual(resp.status_code, 422)

        # Empty query
        resp = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={"user_id": 1, "query": ""},
        )
        self.assertEqual(resp.status_code, 422)

        # Proof completion with invalid negative score or invalid ID
        resp = self.client.post(
            "/api/users/1/next-best-proof/complete",
            json={
                "skill_id": -1,
                "action_type": "PRACTICE",
                "score": 150.0,  # Invalid: score > 100
                "description": "Exceeded bound test",
            },
        )
        self.assertEqual(resp.status_code, 422)

        # Assessment submission with empty answers
        resp = self.client.post(
            "/api/assessment-attempts",
            json={"user_id": 1, "assessment_id": 1, "answers": []},
        )
        self.assertEqual(resp.status_code, 422)

    def test_04_gemini_fallback_offline_graceful_degradation(self):
        """Part D & E: Verify system degrades gracefully when Gemini API key is missing or offline."""
        # 1. Decision explanation fallback
        resp = self.client.post(
            "/api/ai/explain",
            json={
                "user_id": 1,
                "target_role": "Data Analyst",
                "skill_name": "SQL JOINs",
                "context_type": "NEXT_BEST_PROOF",
                "structured_data": {"priority": "CRITICAL", "skill_debt_status": "SKILL_DEBT"},
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("SQL JOINs", data["explanation"])
        self.assertGreater(len(data["key_takeaways"]), 0)

        # 2. Hint generation fallback
        resp_hint = self.client.post(
            "/api/ai/hint",
            json={
                "task_title": "Retail Returns Analytics",
                "skill_name": "SQL JOINs",
                "context_description": "Orders without returns should not disappear",
                "hint_level": 1,
            },
        )
        self.assertEqual(resp_hint.status_code, 200)
        hint_data = resp_hint.json()
        self.assertEqual(hint_data["hint_level"], 1)
        self.assertGreater(len(hint_data["hint"]), 10)

        # 3. Mistake explanation fallback
        resp_mistake = self.client.post(
            "/api/ai/explain-mistake",
            json={
                "skill_name": "SQL JOINs",
                "task_or_question": "Calculate customer refund rate",
                "learner_answer": "Used INNER JOIN on orders and returns",
                "correct_answer_or_result": "Use LEFT JOIN to retain orders without returns",
                "deterministic_evaluation": "Dropped non-returned orders resulting in 100% refund rate",
            },
        )
        self.assertEqual(resp_mistake.status_code, 200)
        mistake_data = resp_mistake.json()
        self.assertTrue(mistake_data["fallback_used"])
        self.assertGreater(len(mistake_data["what_went_wrong"]), 10)
        self.assertGreater(len(mistake_data["why_it_happened"]), 10)

    def test_05_new_learner_edge_case_no_evidence_no_crashes(self):
        """Part H: Test brand new learner with 0 evidence across all 8 modules."""
        # Create brand new user
        test_email = "new.learner.hardening@example.com"
        existing = self.db.query(User).filter_by(email=test_email).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()

        create_resp = self.client.post(
            "/api/users",
            json={
                "name": "Jordan Casey",
                "email": test_email,
                "experience_level": "Beginner",
                "target_role_id": 1,  # Data Analyst
                "weekly_learning_hours": 8,
            },
        )
        self.assertEqual(create_resp.status_code, 201)
        new_user = create_resp.json()
        new_uid = new_user["id"]

        try:
            # 1. Skill DNA (Should return all 0s/empty without division errors)
            dna_resp = self.client.get(f"/api/users/{new_uid}/skill-dna")
            self.assertEqual(dna_resp.status_code, 200)

            # 2. Skill Debt
            debt_resp = self.client.get(f"/api/users/{new_uid}/skill-debt")
            self.assertEqual(debt_resp.status_code, 200)

            # 3. Career Value
            cv_resp = self.client.get(f"/api/users/{new_uid}/career-value")
            self.assertEqual(cv_resp.status_code, 200)

            # 4. Next-Best-Proof
            nbp_resp = self.client.get(f"/api/users/{new_uid}/next-best-proof")
            self.assertEqual(nbp_resp.status_code, 200)
            nbp_data = nbp_resp.json()
            self.assertIsNotNone(nbp_data["title"])

            # 5. Roadmap
            roadmap_resp = self.client.get(f"/api/users/{new_uid}/roadmap")
            self.assertEqual(roadmap_resp.status_code, 200)

            # 6. Passport
            passport_resp = self.client.get(f"/api/users/{new_uid}/skill-passport")
            self.assertEqual(passport_resp.status_code, 200)
            passport_data = passport_resp.json()
            self.assertEqual(passport_data["header"]["total_evidence_count"], 0)

            # 7. Dashboard
            dash_resp = self.client.get(f"/api/dashboard/{new_uid}")
            self.assertEqual(dash_resp.status_code, 200)
            dash_data = dash_resp.json()
            self.assertEqual(dash_data["learner_name"], "Jordan Casey")
            self.assertEqual(dash_data["metrics"]["evidence_records_count"], 0)

        finally:
            # Cleanup created test user
            u = self.db.query(User).filter_by(id=new_uid).first()
            if u:
                self.db.delete(u)
                self.db.commit()

    def test_06_data_consistency_across_endpoints(self):
        """Part B: Verify single source of truth consistency between Dashboard, DNA, and Passport."""
        # 1. Reset demo learner
        reset_resp = self.client.post("/api/demo/reset")
        self.assertEqual(reset_resp.status_code, 200)
        reset_data = reset_resp.json()
        alex_id = reset_data["user_id"]

        # 2. Fetch Dashboard
        dash = self.client.get(f"/api/dashboard/{alex_id}").json()
        # 3. Fetch Skill DNA
        dna_list = self.client.get(f"/api/users/{alex_id}/skill-dna").json()
        # 4. Fetch Next-Best-Proof
        nbp = self.client.get(f"/api/users/{alex_id}/next-best-proof").json()

        # Find SQL JOINs in Skill DNA
        sql_dna = next((d for d in dna_list if d["skill_name"] == "SQL JOINs"), None)
        self.assertIsNotNone(sql_dna)

        # Dashboard top skill gap must match DNA status
        self.assertEqual(dash["highest_career_gap"]["skill_name"], "SQL JOINs")
        self.assertEqual(dash["next_best_proof"]["skill_name"], "SQL JOINs")
        self.assertEqual(nbp["skill_name"], "SQL JOINs")

        # Verify no contradictory values:
        # Dashboard level for SQL JOINs in heatmap should match DNA level within integer rounding
        heatmap_sql = next((g for g in dash["skill_gap_heatmap"] if g["skill_name"] == "SQL JOINs"), None)
        self.assertIsNotNone(heatmap_sql)
        self.assertAlmostEqual(
            heatmap_sql["current_level"],
            sql_dna["skill_level"],
            delta=1.0,
        )


if __name__ == "__main__":
    unittest.main()
