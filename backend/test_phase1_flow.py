"""
Phase 1 Validation Test Suite
Tests:
1. Target Goals (5 Predefined + Custom Goal Creation)
2. Goal -> Skill Map (Categorized domains, benchmark weights)
3. Initial Goal Diagnostic Assessment (Questions with skill tagging)
4. Granular Skill-Level Scoring & Skill Gap Analysis (Strong, Moderate, Weak, Missing)
5. Central Action Recommendation ("What should I do next?") with explicit gap rationale
"""

import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User, UserSkill
from app.models.role import Role
from app.models.assessment import Assessment


class TestPhase1GoalAssessmentFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db: Session = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_predefined_goals_and_skill_maps(self):
        """Verify all 5 predefined goals exist and return structured categorized skill maps."""
        response = self.client.get("/api/roles")
        self.assertEqual(response.status_code, 200)
        roles = response.json()
        role_names = [r["name"] for r in roles]

        required_goals = [
            "Java Backend Developer",
            "Python Developer",
            "Data Analyst",
            "Full Stack Developer",
            "AI/ML Engineer",
        ]
        for goal in required_goals:
            self.assertIn(goal, role_names, f"Goal {goal} must be available in DB")

        # Test Skill Map endpoint for Java Backend Developer
        java_role = next(r for r in roles if r["name"] == "Java Backend Developer")
        sm_resp = self.client.get(f"/api/roles/{java_role['id']}/skill-map")
        self.assertEqual(sm_resp.status_code, 200)
        sm_data = sm_resp.json()
        self.assertEqual(sm_data["role_name"], "Java Backend Developer")
        self.assertGreaterEqual(sm_data["total_skills"], 10)
        self.assertTrue(len(sm_data["categories"]) >= 3)
        cat_names = [c["category_name"] for c in sm_data["categories"]]
        self.assertTrue(any("Java" in c for c in cat_names))
        self.assertTrue(any("Database" in c or "Backend" in c for c in cat_names))

    def test_02_custom_goal_creation(self):
        """Verify users can create a custom goal with extensible skill competencies."""
        payload = {
            "name": "Cloud DevOps Engineer (Custom)",
            "description": "Custom career goal for Kubernetes, Terraform, and CI/CD automation.",
            "skills": ["Docker", "Kubernetes", "Git", "Linux Basics", "CI/CD Pipelines"],
        }
        resp = self.client.post("/api/roles/custom", json=payload)
        self.assertEqual(resp.status_code, 201)
        created = resp.json()
        self.assertEqual(created["name"], "Cloud DevOps Engineer (Custom)")
        self.assertGreaterEqual(len(created["role_skills"]), 5)

        # Check skill map for the custom role
        sm_resp = self.client.get(f"/api/roles/{created['id']}/skill-map")
        self.assertEqual(sm_resp.status_code, 200)
        self.assertEqual(sm_resp.json()["role_id"], created["id"])

    def test_03_initial_goal_assessment_retrieval(self):
        """Verify initial diagnostic assessment retrieval has questions with skill tagging."""
        roles = self.client.get("/api/roles").json()
        java_role = next(r for r in roles if r["name"] == "Java Backend Developer")

        resp = self.client.get(f"/api/assessments/goal/{java_role['id']}")
        self.assertEqual(resp.status_code, 200)
        assm = resp.json()
        self.assertIn("Java Backend Developer", assm["title"])
        self.assertGreaterEqual(len(assm["questions"]), 10)

        # Check question structure (sanitized, options present, skill_name populated)
        q1 = assm["questions"][0]
        self.assertIn("question_text", q1)
        self.assertIn("options", q1)
        self.assertNotIn("correct_answer", q1)  # Sanitized!
        self.assertNotIn("explanation", q1)     # Sanitized!
        self.assertTrue(len(q1["options"]) >= 2)

    def test_04_submit_goal_assessment_and_skill_level_analysis(self):
        """
        Verify submitting the initial assessment calculates a score for EVERY skill,
        updates UserSkill and Skill DNA, computes Skill Gaps (Strong, Moderate, Weak, Missing),
        and delivers the central 'What should I do next?' recommendation.
        """
        # Create a test learner
        test_email = "phase1_learner@example.com"
        existing = self.db.query(User).filter_by(email=test_email).first()
        if existing:
            self.db.delete(existing)
            self.db.commit()

        user_resp = self.client.post(
            "/api/users",
            json={
                "name": "Phase 1 Learner",
                "email": test_email,
                "experience_level": "Beginner",
                "learning_goal": "Become Java Backend Developer",
            },
        )
        self.assertEqual(user_resp.status_code, 201)
        user_id = user_resp.json()["id"]

        roles = self.client.get("/api/roles").json()
        java_role = next(r for r in roles if r["name"] == "Java Backend Developer")

        # Fetch diagnostic questions
        assm_resp = self.client.get(f"/api/assessments/goal/{java_role['id']}")
        questions = assm_resp.json()["questions"]

        # Submit answers: answer first half correctly, second half with dummy string
        answers = []
        for i, q in enumerate(questions):
            # Select first option
            chosen_option = q["options"][0] if q["options"] else "Option A"
            answers.append({"question_id": q["id"], "answer": chosen_option})

        submit_resp = self.client.post(
            "/api/assessments/goal/submit",
            json={
                "user_id": user_id,
                "role_id": java_role["id"],
                "answers": answers,
            },
        )
        self.assertEqual(submit_resp.status_code, 201)
        result = submit_resp.json()

        # 1. Overall stats
        self.assertEqual(result["user_id"], user_id)
        self.assertEqual(result["role_id"], java_role["id"])
        self.assertIn("overall_score", result)
        self.assertGreaterEqual(result["total_questions"], 10)

        # 2. Skill-level score analysis (CRITICAL REQUIREMENT)
        skill_scores = result["skill_scores"]
        self.assertGreater(len(skill_scores), 0)
        for s in skill_scores:
            self.assertIn("skill_name", s)
            self.assertIn("score", s)
            self.assertIn("gap", s)
            self.assertIn(s["status"], ["Strong", "Moderate", "Weak", "Missing"])

        # 3. Gap classification lists
        self.assertIn("strong_skills", result)
        self.assertIn("moderate_skills", result)
        self.assertIn("weak_skills", result)
        self.assertIn("missing_skills", result)

        # 4. Central Recommendation ("What should I do next?")
        next_action = result["next_recommended_action"]
        self.assertIsNotNone(next_action)
        self.assertIn("title", next_action)
        self.assertIn("skill_name", next_action)
        self.assertIn("reason", next_action)
        self.assertIn("gap", next_action["reason"].lower() or next_action["reason"])

        # 5. Standalone gap analysis endpoint
        gap_resp = self.client.get(f"/api/skills/gap-analysis/{user_id}")
        self.assertEqual(gap_resp.status_code, 200)
        gap_data = gap_resp.json()
        self.assertEqual(gap_data["user_id"], user_id)
        self.assertEqual(gap_data["role_id"], java_role["id"])
        self.assertGreater(len(gap_data["all_gaps"]), 0)


if __name__ == "__main__":
    unittest.main()
