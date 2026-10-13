"""
Phase 9 — Dynamic Roadmap Engine Test Suite
Tests all 14 deterministic validation criteria required by Section 21:
1. Baseline roadmap generation.
2. High Skill Debt inserts remediation.
3. Next-Best-Proof becomes recommended step.
4. Prerequisite blocking works.
5. Completed skill is marked completed / skipped.
6. Weak prerequisite blocks downstream skill.
7. Roadmap rebuild occurs after evidence update.
8. SQL JOIN demo inserts remediation.
9. Improved SQL JOIN evidence removes unnecessary remediation.
10. Roadmap ordering is deterministic.
11. Change explanation is generated.
12. Roadmap history/revision works.
13. API responses are valid.
14. No duplicate roadmap steps are created on repeated rebuilds.
"""

import unittest
from datetime import datetime
from fastapi.testclient import TestClient
from app.core.database import SessionLocal
from app.models import User, Role, Skill, UserSkill, SkillEvidence, Roadmap, RoadmapStep, RoadmapChange
from app.services.roadmap_service import roadmap_service
from app.seed.seed_data import reset_alex_mercer
from app.main import app


class TestPhase9DynamicRoadmapEngine(unittest.TestCase):
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

    # 1. Baseline roadmap generation
    def test_01_baseline_roadmap_generation(self):
        roadmap = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        self.assertIsNotNone(roadmap)
        step_titles = [s.title for s in roadmap.steps]
        step_skills = [s.skill.name for s in roadmap.steps if s.skill]

        # Machine Learning (importance 40) must NOT be in Data Analyst baseline
        self.assertNotIn("Machine Learning", step_skills)
        # Primary competencies must exist
        self.assertIn("Python", step_skills)
        self.assertIn("SQL", step_skills)
        self.assertIn("EDA", step_skills)
        self.assertTrue(any("Capstone" in t for t in step_titles))

    # 2. High Skill Debt inserts remediation
    def test_02_high_skill_debt_inserts_remediation(self):
        roadmap = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        remediation_steps = [s for s in roadmap.steps if "Rescue" in s.title or "Reassessment" in s.title or "Real-World" in s.title]
        self.assertTrue(len(remediation_steps) >= 3, "Expected 3-part remediation sequence for high debt")
        step_types = [s.step_type for s in remediation_steps]
        self.assertIn("PRACTICE", step_types)
        self.assertIn("REASSESS", step_types)
        self.assertIn("PRACTICAL_TASK", step_types)

    # 3. Next-Best-Proof becomes recommended step
    def test_03_next_best_proof_becomes_recommended_step(self):
        roadmap = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        recommended_steps = [s for s in roadmap.steps if s.status == "RECOMMENDED"]
        self.assertEqual(len(recommended_steps), 1, "Exactly one step should be active RECOMMENDED")
        # For Alex Mercer, Next-Best-Proof is SQL JOIN Rescue Practice
        self.assertIn("SQL JOIN", recommended_steps[0].title)
        self.assertEqual(recommended_steps[0].step_type, "PRACTICE")

    # 4. Prerequisite blocking works
    def test_04_prerequisite_blocking_works(self):
        roadmap = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        reassess = next(s for s in roadmap.steps if s.step_type == "REASSESS")
        task = next(s for s in roadmap.steps if s.step_type == "PRACTICAL_TASK")
        # Diagnostic Reassessment and Practical task are blocked until prior proof
        self.assertEqual(reassess.status, "BLOCKED")
        self.assertEqual(task.status, "BLOCKED")
        self.assertIsNotNone(reassess.prerequisite_step_ids)
        self.assertIsNotNone(task.prerequisite_step_ids)

    # 5. Completed skill is marked completed / skipped
    def test_05_completed_skill_is_completed(self):
        roadmap = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        python_step = next(s for s in roadmap.steps if s.skill and s.skill.name == "Python")
        self.assertEqual(python_step.status, "COMPLETED")
        self.assertIn("proficiency exceeding role requirement", python_step.reason)

    # 6. Weak prerequisite blocks downstream skill
    def test_06_weak_prerequisite_blocks_downstream_skill(self):
        roadmap = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        eda_step = next(s for s in roadmap.steps if s.skill and s.skill.name == "EDA")
        data_viz_step = next(s for s in roadmap.steps if s.skill and s.skill.name == "Data Visualization")
        self.assertEqual(eda_step.status, "BLOCKED")
        self.assertEqual(data_viz_step.status, "BLOCKED")
        self.assertIn("Blocked", eda_step.reason)

    # 7. Roadmap rebuild occurs after evidence update
    def test_07_roadmap_rebuild_occurs_after_evidence_update(self):
        r1 = roadmap_service.get_user_roadmap(self.db, user_id=1)
        v1 = r1.version

        # Add new practice evidence for EDA
        eda_skill = self.db.query(Skill).filter(Skill.name == "EDA").first()
        ev = SkillEvidence(
            user_id=1,
            skill_id=eda_skill.id,
            source="Test Practice Lab",
            evidence_type="PRACTICE",
            score=78.0,
            description="Completed exploratory analysis lab",
            created_at=datetime.utcnow(),
        )
        self.db.add(ev)
        self.db.commit()

        # Trigger refresh_learning_state
        r2 = roadmap_service.refresh_learning_state(self.db, user_id=1)
        self.assertGreater(r2.version, v1)
        self.assertEqual(r2.status, "active")

        # Cleanup
        self.db.delete(ev)
        self.db.commit()

    # 8. SQL JOIN demo inserts remediation
    def test_08_sql_join_demo_inserts_remediation(self):
        roadmap = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        sql_join_steps = [s for s in roadmap.steps if s.skill and s.skill.name == "SQL JOINs"]
        self.assertEqual(len(sql_join_steps), 3)
        self.assertTrue(any("Rescue Practice" in s.title for s in sql_join_steps))
        self.assertTrue(any("Reassessment" in s.title for s in sql_join_steps))
        self.assertTrue(any("Real-World" in s.title for s in sql_join_steps))

    # 9. Improved SQL JOIN evidence removes unnecessary remediation
    def test_09_improved_sql_join_evidence_removes_remediation(self):
        # Baseline before improvement
        r_before = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        self.assertTrue(any("Rescue Practice" in s.title for s in r_before.steps))

        # Simulate learner improving SQL JOINs to 82%
        s_join = self.db.query(Skill).filter(Skill.name == "SQL JOINs").first()
        us = self.db.query(UserSkill).filter(UserSkill.user_id == 1, UserSkill.skill_id == s_join.id).first()
        us.skill_level = 82.0
        ev = SkillEvidence(
            user_id=1,
            skill_id=s_join.id,
            source="SQL JOIN Diagnostic Assessment",
            evidence_type="ASSESSMENT",
            score=82.0,
            description="Achieved 82% on diagnostic exam",
            created_at=datetime.utcnow(),
        )
        self.db.add(ev)
        self.db.commit()

        # Rebuild roadmap after demonstrated proficiency
        r_after = roadmap_service.refresh_learning_state(self.db, user_id=1)
        # Remediation sequence should be removed
        rescue_steps = [s for s in r_after.steps if "Rescue Practice" in s.title]
        self.assertEqual(len(rescue_steps), 0, "Remediation sequence should be removed after improvement")

        # SQL JOINs is now verified and COMPLETED
        join_step = next(s for s in r_after.steps if s.skill and s.skill.name == "SQL JOINs")
        self.assertEqual(join_step.status, "COMPLETED")

        # EDA is now unlocked and RECOMMENDED
        eda_step = next(s for s in r_after.steps if s.skill and s.skill.name == "EDA")
        self.assertEqual(eda_step.status, "RECOMMENDED")

    # 10. Roadmap ordering is deterministic
    def test_10_roadmap_ordering_is_deterministic(self):
        r1 = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        r2 = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        self.assertEqual(len(r1.steps), len(r2.steps))
        for s1, s2 in zip(r1.steps, r2.steps):
            self.assertEqual(s1.order_index, s2.order_index)
            self.assertEqual(s1.title, s2.title)
            self.assertEqual(s1.status, s2.status)
            self.assertEqual(s1.step_type, s2.step_type)

    # 11. Change explanation is generated
    def test_11_change_explanation_is_generated(self):
        # 1. Initial generation
        roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        # 2. Improve SQL JOINs
        s_join = self.db.query(Skill).filter(Skill.name == "SQL JOINs").first()
        us = self.db.query(UserSkill).filter(UserSkill.user_id == 1, UserSkill.skill_id == s_join.id).first()
        us.skill_level = 82.0
        ev = SkillEvidence(
            user_id=1,
            skill_id=s_join.id,
            source="Assessment Pass",
            evidence_type="ASSESSMENT",
            score=82.0,
            description="Verified mastery",
            created_at=datetime.utcnow(),
        )
        self.db.add(ev)
        self.db.commit()

        roadmap_service.refresh_learning_state(self.db, user_id=1)

        changes = roadmap_service.get_roadmap_changes(self.db, user_id=1)
        self.assertTrue(len(changes) > 0)
        types = [c.change_type for c in changes]
        self.assertIn("REMOVED", types)
        self.assertIn("COMPLETED", types)
        self.assertIn("UNLOCKED", types)

        removed_change = next(c for c in changes if c.change_type == "REMOVED")
        self.assertIn("SQL JOIN", removed_change.description)

    # 12. Roadmap history/revision works
    def test_12_roadmap_history_works(self):
        r1 = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        r2 = roadmap_service.generate_dynamic_roadmap(self.db, user_id=1, role_id=1)
        history = roadmap_service.get_roadmap_history(self.db, user_id=1)
        self.assertTrue(len(history) >= 2)
        versions = [h["version"] for h in history]
        self.assertIn(r1.version, versions)
        self.assertIn(r2.version, versions)

    # 13. API responses are valid
    def test_13_api_responses_are_valid(self):
        res1 = self.client.get("/api/users/1/roadmap")
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertIn("steps", data1)
        self.assertIn("version", data1)
        self.assertTrue(len(data1["steps"]) > 0)

        res2 = self.client.post("/api/users/1/roadmap/rebuild")
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertGreater(data2["version"], data1["version"])

        res3 = self.client.get("/api/users/1/roadmap/history")
        self.assertEqual(res3.status_code, 200)
        self.assertIsInstance(res3.json(), list)

        res4 = self.client.get("/api/users/1/roadmap/changes")
        self.assertEqual(res4.status_code, 200)
        self.assertIsInstance(res4.json(), list)

    # 14. No duplicate roadmap steps on repeated rebuilds
    def test_14_no_duplicate_roadmap_steps_on_repeated_rebuilds(self):
        r1 = roadmap_service.rebuild_user_roadmap(self.db, user_id=1)
        count1 = len(r1.steps)
        step_ids1 = [s.id for s in r1.steps]
        self.assertEqual(len(step_ids1), len(set(step_ids1)), "All step IDs in active roadmap must be unique")

        r2 = roadmap_service.rebuild_user_roadmap(self.db, user_id=1)
        count2 = len(r2.steps)
        step_ids2 = [s.id for s in r2.steps]
        self.assertEqual(len(step_ids2), len(set(step_ids2)), "All step IDs in new active roadmap must be unique")
        self.assertEqual(count1, count2, "Repeated rebuild with identical state must have identical step count")


if __name__ == "__main__":
    unittest.main()
