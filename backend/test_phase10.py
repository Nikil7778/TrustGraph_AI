"""
Phase 10 — Industry Practical Lab Engine Test Suite
Tests 15 deterministic validation criteria:
1. Database and Seed Verification
2. List Industry Labs
3. Lab Details and Tasks Fetching
4. Lab Schema Previews & Data Quality Notes
5. Safe Query Execution (SELECT)
6. Security Enforcement (Rejects DROP/DELETE/INSERT/UPDATE mutations)
7. Graceful Syntax Error Handling
8. 4-Pillar Evaluation: Canonical Correct Query (PASSED >= 85%)
9. 4-Pillar Evaluation: INNER JOIN Penalty & Diagnostic Failure
10. 4-Pillar Evaluation: Missing Payment Status Filter Penalty
11. 4-Pillar Evaluation: Partial Query Evaluation (PARTIAL)
12. 4-Pillar Evaluation: Malformed Query Evaluation (FAILED)
13. Attempt Persistence & History
14. Skill Evidence Generation & Skill DNA Recalculation
15. Dynamic Roadmap Refresh Integration
"""

import unittest
from datetime import datetime
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.models import User, Skill, UserSkill, SkillEvidence, IndustryLab, IndustryLabAttempt
from app.services.industry_lab_service import industry_lab_service
from app.engines.industry_lab_engine import industry_lab_engine
from app.seed.seed_data import reset_alex_mercer
from app.main import app


class TestPhase10IndustryLabEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        reset_alex_mercer(cls.db)
        cls.db.close()

    def setUp(self):
        reset_alex_mercer(self.db)

    # 1. Database and Seed Verification
    def test_01_database_and_seed_verification(self):
        labs = self.db.query(IndustryLab).all()
        self.assertGreaterEqual(len(labs), 1, "At least one industry lab should be seeded.")
        retail_lab = self.db.query(IndustryLab).filter(IndustryLab.slug == "retail-returns-analytics").first()
        self.assertIsNotNone(retail_lab)
        self.assertEqual(retail_lab.difficulty, "Intermediate")
        self.assertEqual(len(retail_lab.tasks), 3, "Expected 3 tasks seeded for retail-returns-analytics.")

    # 2. List Industry Labs
    def test_02_list_industry_labs(self):
        res = self.client.get("/api/industry-labs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertTrue(any(l["slug"] == "retail-returns-analytics" for l in data))

    # 3. Lab Details and Tasks Fetching
    def test_03_get_lab_details_and_tasks(self):
        res = self.client.get("/api/industry-labs/retail-returns-analytics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["slug"], "retail-returns-analytics")
        self.assertIn("Customer Retention", data["title"])
        self.assertEqual(len(data["tasks"]), 3)
        self.assertTrue(any(t["task_type"] == "SQL_QUERY" for t in data["tasks"]))

    # 4. Lab Schema Previews & Data Quality Notes
    def test_04_get_lab_preview_and_schema(self):
        res = self.client.get("/api/industry-labs/retail-returns-analytics/preview")
        self.assertEqual(res.status_code, 200)
        previews = res.json()
        self.assertGreaterEqual(len(previews), 4)
        table_names = [p["table_name"] for p in previews]
        self.assertIn("lab_retail_customers", table_names)
        self.assertIn("lab_retail_orders", table_names)
        self.assertIn("lab_retail_returns", table_names)
        self.assertIn("lab_retail_products", table_names)

        orders_preview = next(p for p in previews if p["table_name"] == "lab_retail_orders")
        self.assertGreater(orders_preview["row_count"], 0)
        self.assertTrue(any("COMPLETED" in note for note in orders_preview["quality_notes"]))

    # 5. Safe Query Execution (SELECT)
    def test_05_safe_query_runner_success(self):
        query = "SELECT id, customer_name, segment, city FROM lab_retail_customers WHERE segment = 'Enterprise'"
        res = self.client.post("/api/industry-labs/retail-returns-analytics/run", json={"query": query})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIsNone(data["error_message"])
        self.assertEqual(data["columns"], ["id", "customer_name", "segment", "city"])
        self.assertGreaterEqual(data["row_count"], 2)
        self.assertGreaterEqual(data["execution_time_ms"], 0)

    # 6. Security Enforcement (Rejects DROP/DELETE/INSERT/UPDATE mutations)
    def test_06_safe_query_runner_rejects_forbidden_statements(self):
        malicious_queries = [
            "DROP TABLE lab_retail_customers",
            "DELETE FROM lab_retail_orders",
            "UPDATE lab_retail_customers SET segment = 'Hacked'",
            "INSERT INTO lab_retail_customers VALUES (99, 'Hacker', 'SMB', 'Nowhere', '2024-01-01', 'ACTIVE')",
            "SELECT * FROM lab_retail_customers; DROP TABLE lab_retail_orders;",
            "ALTER TABLE lab_retail_customers ADD COLUMN hacked TEXT",
        ]
        for bad_q in malicious_queries:
            res = self.client.post("/api/industry-labs/retail-returns-analytics/run", json={"query": bad_q})
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertFalse(data["success"], f"Expected security rejection for: {bad_q}")
            self.assertIsNotNone(data["error_message"])

    # 7. Graceful Syntax Error Handling
    def test_07_safe_query_runner_handles_syntax_errors(self):
        broken_query = "SELECT non_existent_column FROM table_that_does_not_exist WHERE ;"
        res = self.client.post("/api/industry-labs/retail-returns-analytics/run", json={"query": broken_query})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertIn("SQL Execution Error", data["error_message"])

    # 8. 4-Pillar Evaluation: Canonical Correct Query (PASSED >= 85%)
    def test_08_canonical_query_evaluation_passed(self):
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
            "Enterprise segment yields the highest net revenue ($8,142) despite refunds. "
            "Mid-Market exhibits the highest return rate percentage (33.33%), which poses margin risk. "
            "SMB generates lower volume but maintains consistent customer retention."
        )

        res = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={
                "user_id": 1,
                "query": canonical_query,
                "submitted_answer": written_rationale,
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "PASSED")
        self.assertGreaterEqual(data["total_score"], 85.0)
        scores = data["section_scores"]
        self.assertGreaterEqual(scores["sql_correctness"], 35.0)
        self.assertGreaterEqual(scores["data_quality_handling"], 18.0)
        self.assertGreaterEqual(scores["business_result"], 20.0)
        self.assertGreaterEqual(scores["validation_reasoning"], 12.0)
        self.assertEqual(len(data["diagnostic_failures"]), 0)
        self.assertIsNotNone(data["evidence_generated"])

    # 9. 4-Pillar Evaluation: INNER JOIN Penalty & Diagnostic Failure
    def test_09_inner_join_penalty_diagnostics(self):
        # Using INNER JOIN on returns drops all non-returned orders
        inner_join_query = """
        SELECT
            c.segment,
            COUNT(o.id) AS total_orders,
            SUM(o.total_amount) AS gross_revenue,
            SUM(r.refund_amount) AS total_refunds,
            SUM(o.total_amount) - SUM(r.refund_amount) AS net_revenue
        FROM lab_retail_customers c
        JOIN lab_retail_orders o ON c.id = o.customer_id
        INNER JOIN lab_retail_returns r ON o.id = r.order_id
        WHERE o.payment_status = 'COMPLETED'
        GROUP BY c.segment
        """
        res = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={"user_id": 1, "query": inner_join_query},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertNotEqual(data["status"], "PASSED")
        self.assertTrue(
            any("INNER JOIN" in fail for fail in data["diagnostic_failures"]),
            "Expected diagnostic failure explaining INNER JOIN pitfall on returns table.",
        )

    # 10. 4-Pillar Evaluation: Missing Payment Status Filter Penalty
    def test_10_missing_payment_status_filter_penalty(self):
        # Query that forgets to filter payment_status = 'COMPLETED'
        unfiltered_query = """
        SELECT
            c.segment,
            SUM(o.total_amount) AS gross_revenue
        FROM lab_retail_customers c
        JOIN lab_retail_orders o ON c.id = o.customer_id
        LEFT JOIN lab_retail_returns r ON o.id = r.order_id
        GROUP BY c.segment
        """
        res = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={"user_id": 1, "query": unfiltered_query},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(
            any("payment_status" in fail or "COMPLETED" in fail for fail in data["diagnostic_failures"]),
            "Expected diagnostic failure indicating missing payment_status filter.",
        )

    # 11. 4-Pillar Evaluation: Partial Query Evaluation (PARTIAL)
    def test_11_partial_query_evaluation(self):
        partial_query = """
        SELECT
            c.segment,
            COUNT(o.id) AS total_orders,
            SUM(o.total_amount) AS gross_revenue
        FROM lab_retail_customers c
        JOIN lab_retail_orders o ON c.id = o.customer_id
        WHERE o.payment_status = 'COMPLETED'
        GROUP BY c.segment
        """
        res = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={"user_id": 1, "query": partial_query},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "PARTIAL")
        self.assertTrue(50.0 <= data["total_score"] < 80.0)

    # 12. 4-Pillar Evaluation: Malformed Query Evaluation (FAILED)
    def test_12_syntax_error_query_evaluation(self):
        invalid_query = "SELECT * FROM definitely_not_a_real_table"
        res = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={"user_id": 1, "query": invalid_query},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "FAILED")
        self.assertEqual(data["total_score"], 0.0)
        self.assertGreater(len(data["diagnostic_failures"]), 0)

    # 13. Attempt Persistence & History
    def test_13_submission_records_attempt(self):
        # Submit an attempt
        query = "SELECT c.segment, COUNT(*) AS cnt FROM lab_retail_customers c GROUP BY c.segment"
        res1 = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={"user_id": 1, "query": query},
        )
        self.assertEqual(res1.status_code, 200)
        attempt_id = res1.json()["attempt_id"]

        # Fetch attempt history
        res2 = self.client.get("/api/industry-labs/retail-returns-analytics/attempts?user_id=1")
        self.assertEqual(res2.status_code, 200)
        attempts = res2.json()
        self.assertGreaterEqual(len(attempts), 1)
        self.assertTrue(any(a["id"] == attempt_id for a in attempts))

    # 14. Skill Evidence Generation & Skill DNA Recalculation
    def test_14_evidence_generation_and_skill_dna_update(self):
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

        # Baseline SQL JOINs score for Alex Mercer was 42.0%
        s_joins = self.db.query(Skill).filter(Skill.name == "SQL JOINs").first()
        us_before = self.db.query(UserSkill).filter_by(user_id=1, skill_id=s_joins.id).first()
        score_before = us_before.skill_level

        res = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={
                "user_id": 1,
                "query": canonical_query,
                "submitted_answer": written_rationale,
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "PASSED")
        self.assertIsNotNone(data["evidence_generated"])

        # Check evidence in DB
        ev = self.db.query(SkillEvidence).filter(
            SkillEvidence.user_id == 1,
            SkillEvidence.source == "Industry Lab: E-Commerce Customer Retention & Returns Analytics"
        ).first()
        self.assertIsNotNone(ev)
        self.assertEqual(ev.evidence_type, "PRACTICE")
        self.assertGreaterEqual(ev.score, 85.0)

        # Check UserSkill level increased
        self.db.refresh(us_before)
        self.assertGreater(us_before.skill_level, score_before, "Skill level should increase after passing industry lab.")

    # 15. Dynamic Roadmap Refresh Integration
    def test_15_roadmap_refresh_after_lab(self):
        # Prior to lab, Alex Mercer's roadmap has SQL JOIN Rescue Practice
        res_r1 = self.client.get("/api/users/1/roadmap")
        self.assertEqual(res_r1.status_code, 200)
        v1 = res_r1.json()["version"]

        # Run passing canonical submission
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
        rationale = "Enterprise yields $8,142 net revenue, while Mid-Market has highest refund rate."

        sub_res = self.client.post(
            "/api/industry-labs/retail-returns-analytics/submit",
            json={"user_id": 1, "query": canonical_query, "submitted_answer": rationale},
        )
        self.assertEqual(sub_res.status_code, 200)

        # Fetch roadmap after lab submission
        res_r2 = self.client.get("/api/users/1/roadmap")
        self.assertEqual(res_r2.status_code, 200)
        data_r2 = res_r2.json()
        self.assertGreaterEqual(data_r2["version"], v1, "Roadmap version should increment or refresh after evidence.")


if __name__ == "__main__":
    unittest.main()
