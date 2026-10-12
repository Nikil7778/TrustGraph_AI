"""
Phase 11 — Gemini AI Layer Test Suite
Validates the controlled AI Layer:
1. Configuration loading (model, api_key, timeout)
2. Architectural guardrails (Gemini NEVER determines Skill DNA, Skill Debt, Career Value, Next-Best-Proof, Roadmap, or Grading)
3. 'Why this?' Next-Best-Proof explanation
4. 'Why in debt?' Skill Debt explanation
5. 'Why did my roadmap change?' Roadmap change explanation
6. Progressive Hint Generation (Levels 1, 2, 3)
7. Mistake Explanation (Diagnostic/Lab failure breakdown)
8. Learning Concept Explanation (Concept, example, pitfall, role use case, check question)
9. Unscored Practice Question Generation (Explicitly flagged as unscored)
10. Role-specific Interview Questions (Conceptual, Practical, Debugging, Business Scenario)
11. Personalized Study Guidance (Derived from deterministic state)
12. Graceful Offline/Timeout Resilience (Fallback used when API is unavailable)
13. Privacy and Prompt Safety (No leaks of internal prompts or secrets)
14. Full FastAPI Client Integration
"""

import unittest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import User, Skill, UserSkill
from app.services.ai_service import ai_service
from app.seed.seed_data import reset_alex_mercer
from app.main import app


class TestPhase11GeminiAILayer(unittest.TestCase):
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

    # 1. Configuration loading
    def test_01_configuration(self):
        self.assertIsNotNone(settings.GEMINI_MODEL)
        self.assertTrue(len(settings.GEMINI_MODEL) > 0)
        self.assertGreaterEqual(settings.GEMINI_TIMEOUT_SECONDS, 5)

    # 2. Architectural Guardrail Verification
    def test_02_architectural_guardrail(self):
        # Record Alex Mercer's initial Skill DNA score for SQL JOINs (42.0)
        s_joins = self.db.query(Skill).filter(Skill.name == "SQL JOINs").first()
        us_before = self.db.query(UserSkill).filter_by(user_id=1, skill_id=s_joins.id).first()
        initial_score = us_before.skill_level

        # Request multiple AI operations
        self.client.post(
            "/api/ai/explain",
            json={
                "user_id": 1,
                "target_role": "Data Analyst",
                "skill_name": "SQL JOINs",
                "context_type": "NEXT_BEST_PROOF",
                "structured_data": {"current_skill_level": 42.0, "required_skill_level": 75.0},
            },
        )
        self.client.post(
            "/api/ai/practice-questions",
            json={"skill_name": "SQL JOINs", "difficulty": "Intermediate", "target_role": "Data Analyst", "count": 2},
        )

        # Verify that Skill DNA score did NOT change
        self.db.refresh(us_before)
        self.assertEqual(
            us_before.skill_level,
            initial_score,
            "CRITICAL: Gemini AI layer must NEVER alter deterministic Skill DNA scores!",
        )

    # 3. 'Why this?' Next-Best-Proof explanation
    def test_03_next_best_proof_why_this_explanation(self):
        payload = {
            "user_id": 1,
            "target_role": "Data Analyst",
            "skill_name": "SQL JOINs",
            "context_type": "NEXT_BEST_PROOF",
            "structured_data": {
                "current_skill_level": 42.0,
                "required_skill_level": 75.0,
                "priority": "CRITICAL",
                "skill_debt_status": "SKILL_DEBT",
                "action_type_label": "Rescue Practice",
            },
        }
        res = self.client.post("/api/ai/explain", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["skill_name"], "SQL JOINs")
        self.assertEqual(data["context_type"], "NEXT_BEST_PROOF")
        self.assertIn("SQL JOINs", data["explanation"])
        self.assertGreater(len(data["key_takeaways"]), 0)
        self.assertTrue(len(data["actionable_next_step"]) > 5)

    # 4. 'Why in debt?' Skill Debt explanation
    def test_04_skill_debt_explanation(self):
        payload = {
            "user_id": 1,
            "target_role": "Data Analyst",
            "skill_name": "SQL JOINs",
            "context_type": "SKILL_DEBT",
            "structured_data": {
                "current_skill_level": 42.0,
                "debt_status": "SKILL_DEBT",
                "debt_score": 68.0,
            },
        }
        res = self.client.post("/api/ai/explain", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("debt", data["explanation"].lower())
        self.assertTrue(any("evidence" in t.lower() or "practice" in t.lower() for t in data["key_takeaways"]))

    # 5. 'Why did my roadmap change?' Roadmap change explanation
    def test_05_roadmap_change_explanation(self):
        payload = {
            "user_id": 1,
            "target_role": "Data Analyst",
            "skill_name": "SQL JOINs",
            "context_type": "ROADMAP_CHANGE",
            "structured_data": {
                "change_type": "INSERTED_REMEDIATION",
                "reason": "Critical Skill Debt identified",
            },
        }
        res = self.client.post("/api/ai/explain", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("roadmap", data["explanation"].lower())

    # 6. Progressive Hint Generation (Levels 1, 2, 3)
    def test_06_progressive_hints(self):
        for level in [1, 2, 3]:
            res = self.client.post(
                "/api/ai/hint",
                json={
                    "task_title": "E-Commerce Customer Retention & Returns Analytics",
                    "skill_name": "SQL JOINs",
                    "context_description": "Analyze segment revenue across customers, orders, and returns.",
                    "hint_level": level,
                    "learner_query": "SELECT * FROM lab_retail_customers JOIN lab_retail_returns",
                },
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["hint_level"], level)
            self.assertTrue(len(data["hint"]) > 10)
            self.assertTrue(len(data["focus_concept"]) > 0)

    # 7. Mistake Explanation
    def test_07_mistake_explanation(self):
        payload = {
            "skill_name": "SQL JOINs",
            "task_or_question": "Calculate total revenue by segment including unreturned orders.",
            "learner_answer": "SELECT segment, SUM(amount) FROM orders JOIN returns ON orders.id = returns.order_id GROUP BY segment",
            "correct_answer_or_result": "LEFT JOIN returns ON orders.id = returns.order_id with COALESCE",
            "deterministic_evaluation": "INNER JOIN excluded non-returned orders.",
            "target_role": "Data Analyst",
        }
        res = self.client.post("/api/ai/explain-mistake", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data["what_went_wrong"]) > 0)
        self.assertTrue(len(data["why_it_happened"]) > 0)
        self.assertTrue(len(data["how_to_recognize_next_time"]) > 0)
        self.assertTrue(len(data["small_example"]) > 0)
        self.assertTrue(len(data["short_practice_question"]) > 0)

    # 8. Learning Concept Explanation
    def test_08_learning_concept_explanation(self):
        payload = {
            "skill_name": "SQL JOINs",
            "target_role": "Data Analyst",
            "specific_topic": "LEFT JOIN vs INNER JOIN",
        }
        res = self.client.post("/api/ai/learning-explanation", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["skill_name"], "SQL JOINs")
        self.assertEqual(data["target_role"], "Data Analyst")
        self.assertTrue(len(data["concept_summary"]) > 0)
        self.assertTrue(len(data["concise_example"]) > 0)
        self.assertTrue(len(data["common_pitfall"]) > 0)
        self.assertTrue(len(data["role_use_case"]) > 0)
        self.assertTrue(len(data["check_question"]) > 0)

    # 9. Unscored Practice Question Generation
    def test_09_unscored_practice_questions(self):
        payload = {
            "skill_name": "SQL JOINs",
            "difficulty": "Intermediate",
            "target_role": "Data Analyst",
            "count": 2,
        }
        res = self.client.post("/api/ai/practice-questions", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["questions"]), 2)
        for q in data["questions"]:
            self.assertTrue(q["is_unscored_practice"], "Practice question must be flagged as unscored!")
            self.assertTrue(len(q["question_text"]) > 0)
            self.assertTrue(len(q["options"]) >= 2)
            self.assertIn(q["expected_answer"], q["options"])
            self.assertTrue(len(q["explanation"]) > 0)
        self.assertIn("Does not alter Skill DNA", data["disclaimer"])

    # 10. Role-specific Interview Questions
    def test_10_role_interview_questions(self):
        payload = {
            "skill_name": "SQL JOINs",
            "target_role": "Data Analyst",
        }
        res = self.client.post("/api/ai/interview-questions", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["questions"]), 4)
        categories = [q["category"] for q in data["questions"]]
        self.assertIn("Conceptual", categories)
        self.assertTrue(any("Practical" in c for c in categories))
        self.assertIn("Debugging", categories)
        self.assertIn("Business Scenario", categories)

    # 11. Personalized Study Guidance
    def test_11_personalized_study_guidance(self):
        res = self.client.post("/api/ai/study-guidance", json={"user_id": 1})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["user_id"], 1)
        self.assertIn("Data Analyst", data["target_role"])
        self.assertGreater(data["weekly_hours"], 0)
        self.assertTrue(len(data["daily_breakdown"]) >= 3)
        self.assertTrue(len(data["coach_advice"]) > 0)

    # 12. Graceful Offline/Timeout Resilience
    def test_12_graceful_resilience_fallback(self):
        # Force service to use fallback by clearing api_key temporarily
        original_key = ai_service.api_key
        try:
            ai_service.api_key = ""
            payload = {
                "user_id": 1,
                "target_role": "Data Analyst",
                "skill_name": "SQL",
                "context_type": "NEXT_BEST_PROOF",
                "structured_data": {"current_level": 76.0, "required_level": 85.0},
            }
            res = self.client.post("/api/ai/explain", json=payload)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data["fallback_used"])
            self.assertEqual(data["model_used"], "deterministic-fallback")
            self.assertTrue(len(data["explanation"]) > 0)
        finally:
            ai_service.api_key = original_key

    # 13. Privacy and Prompt Safety
    def test_13_privacy_and_security(self):
        payload = {
            "user_id": 1,
            "target_role": "Data Analyst",
            "skill_name": "SQL JOINs",
            "context_type": "NEXT_BEST_PROOF",
            "structured_data": {"secret_token": "SHOULD_NOT_LEAK", "current_level": 42.0},
        }
        res = self.client.post("/api/ai/explain", json=payload)
        self.assertEqual(res.status_code, 200)
        resp_str = str(res.json())
        self.assertNotIn("SHOULD_NOT_LEAK", resp_str)
        self.assertNotIn("AIzaSy", resp_str)  # No Gemini API key prefix in responses


if __name__ == "__main__":
    unittest.main()
