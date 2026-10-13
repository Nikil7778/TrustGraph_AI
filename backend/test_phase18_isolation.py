"""
Phase 18 — Comprehensive Data Isolation & Demo Learner Preservation Test Suite
Verifies:
1. Scenario A: Alex Mercer (user_id=1) presentation scenario is 100% intact.
2. Scenario B: Brand-new learner (e.g., NIKIL_A) has clean isolated initial state:
   - Career Readiness = 0% / Awaiting baseline assessment
   - Skills Verified = 0
   - Evidence count = 0
   - Skill DNA = all UNKNOWN / 0.0 / Not assessed
   - Skill Debt = 0 active SKILL_DEBT (statuses are MISSING)
   - Next-Best-Proof = "Complete Diagnostic Assessment"
   - ML Mastery Prediction = UNKNOWN risk & "Not enough learning evidence yet"
   - Roadmap = 3-step onboarding sequence (Diagnostic Assessment -> Build Skill DNA -> Generate Personalized Roadmap)
   - Skill Passport = 0 verified skills, 0 evidence
3. Scenario C: New learner after assessment:
   - Only new learner's DNA, CV, NBP, and roadmap update
   - Alex Mercer's state remains completely unchanged
4. Scenario D: Cross-user isolation:
   - Learner X and Learner Y data cannot leak across endpoints
"""

import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.models.user import User, UserSkill
from app.models.evidence import SkillEvidence
from app.models.assessment import AssessmentAttempt, Assessment
from app.models.roadmap import Roadmap, RoadmapStep
from app.services.skill_dna_service import skill_dna_service
from app.services.skill_debt_service import skill_debt_service
from app.services.career_value_service import career_value_service
from app.services.next_best_proof_service import next_best_proof_service
from app.services.roadmap_service import roadmap_service
from app.services.dashboard_service import dashboard_service
from app.services.ml_service import predict_skill_mastery
from app.services.coach_service import coach_service
from app.seed.seed_data import reset_alex_mercer


class TestPhase18DataIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db: Session = SessionLocal()
        cls._cleanup_test_users(cls.db)
        reset_alex_mercer(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls._cleanup_test_users(cls.db)
        reset_alex_mercer(cls.db)
        cls.db.close()

    @classmethod
    def _cleanup_test_users(cls, db: Session):
        test_emails = [
            "nikil_a_test@example.com",
            "learner_c_test@example.com",
            "learner_x_test@example.com",
            "learner_y_test@example.com",
        ]
        users = db.query(User).filter(User.email.in_(test_emails)).all()
        for u in users:
            db.query(SkillEvidence).filter(SkillEvidence.user_id == u.id).delete()
            db.query(AssessmentAttempt).filter(AssessmentAttempt.user_id == u.id).delete()
            db.query(UserSkill).filter(UserSkill.user_id == u.id).delete()
            rms = db.query(Roadmap).filter(Roadmap.user_id == u.id).all()
            for rm in rms:
                db.query(RoadmapStep).filter(RoadmapStep.roadmap_id == rm.id).delete()
                db.delete(rm)
            db.delete(u)
        db.commit()

    # =========================================================================
    # SCENARIO A: DEMO LEARNER (ALEX MERCER) PRESERVATION
    # =========================================================================
    def test_01_alex_mercer_retains_presentation_scenario(self):
        """Verify Alex Mercer (user 1) retains all presentation seed data intact."""
        alex = self.db.query(User).filter(User.id == 1).first()
        self.assertIsNotNone(alex)
        self.assertEqual(alex.name, "Alex Mercer")

        # 1. Skill DNA: SQL JOINs is weak (accuracy ~42%, skill level ~54.9%)
        dna = skill_dna_service.get_user_skill_dna(self.db, 1)
        dna_map = {d["skill_name"]: d for d in dna}
        self.assertIn("SQL JOINs", dna_map)
        self.assertAlmostEqual(dna_map["SQL JOINs"]["accuracy"], 42.0, delta=5.0)
        self.assertAlmostEqual(dna_map["SQL JOINs"]["skill_level"], 54.9, delta=5.0)
        self.assertEqual(dna_map["SQL JOINs"]["status"], "DEVELOPING")

        # 2. Skill Debt: SQL JOINs is active debt with HIGH severity
        debts = skill_debt_service.calculate_skill_debt(self.db, 1, 1)
        debt_map = {d["skill_name"]: d for d in debts}
        self.assertIn("SQL JOINs", debt_map)
        self.assertEqual(debt_map["SQL JOINs"]["debt_status"], "SKILL_DEBT")
        self.assertEqual(debt_map["SQL JOINs"]["severity"], "HIGH")

        # 3. Next-Best-Proof is SQL JOIN Rescue Practice
        nbp = next_best_proof_service.get_next_best_proof(self.db, 1, 1)
        self.assertEqual(nbp["skill_name"], "SQL JOINs")
        self.assertEqual(nbp["action_type"], "PRACTICE")
        self.assertIn("SQL JOIN", nbp["title"])

        # 4. ML Prediction is available and computed
        ml_res = predict_skill_mastery(self.db, 1, 3)  # skill_id 3 = SQL JOINs
        self.assertIn(ml_res.risk_level, ["HIGH", "MEDIUM", "LOW"])
        self.assertGreater(ml_res.mastery_probability, 0.0)
        self.assertNotEqual(ml_res.risk_level, "UNKNOWN")

        # 5. Roadmap has real steps (not 3 onboarding steps)
        rm = roadmap_service.get_user_roadmap(self.db, 1)
        self.assertIsNotNone(rm)
        self.assertGreaterEqual(len(rm.steps), 4)
        step_titles = [s.title for s in rm.steps]
        self.assertTrue(any("SQL JOIN" in t for t in step_titles))

        # 6. Dashboard endpoint returns full populated response
        dash_res = self.client.get("/api/dashboard/1")
        self.assertEqual(dash_res.status_code, 200)
        dash_data = dash_res.json()
        self.assertGreater(dash_data["metrics"]["career_readiness"]["score"], 0.0)
        self.assertGreater(dash_data["metrics"]["evidence_records_count"], 0)

    # =========================================================================
    # SCENARIO B: BRAND-NEW LEARNER INITIAL STATE
    # =========================================================================
    def test_02_new_learner_clean_isolation_before_assessment(self):
        """Verify brand-new learner has 100% clean empty state without demo values."""
        email = "nikil_a_test@example.com"
        create_res = self.client.post("/api/users", json={
            "name": "NIKIL_A",
            "email": email,
            "experience_level": "Intermediate",
            "target_role_id": 1,
            "weekly_learning_hours": 10,
            "learning_goal": "Get my first Data Analyst job",
        })
        self.assertEqual(create_res.status_code, 201)
        new_user = create_res.json()
        new_uid = new_user["id"]
        self.assertGreater(new_uid, 1)

        # 1. Evidence count must be exactly 0
        ev_count = self.db.query(SkillEvidence).filter(SkillEvidence.user_id == new_uid).count()
        self.assertEqual(ev_count, 0)

        # 2. Skill DNA: every skill must be UNKNOWN / 0.0
        dna = skill_dna_service.get_user_skill_dna(self.db, new_uid)
        for item in dna:
            self.assertEqual(item["skill_level"], 0.0, f"Skill {item['skill_name']} has non-zero level!")
            self.assertEqual(item["confidence"], 0.0, f"Skill {item['skill_name']} has non-zero confidence!")
            self.assertEqual(item["evidence_count"], 0)
            self.assertEqual(item["status"], "UNKNOWN")

        # 3. No Alex Mercer scores (SQL JOINs != 42, Power BI != 38, EDA != 65, SQL != 76)
        dna_map = {d["skill_name"]: d["skill_level"] for d in dna}
        self.assertEqual(dna_map["SQL JOINs"], 0.0)
        self.assertEqual(dna_map["Power BI"], 0.0)
        self.assertEqual(dna_map["EDA"], 0.0)
        self.assertEqual(dna_map["SQL"], 0.0)

        # 4. Skill Debt: NO active SKILL_DEBT (status is MISSING)
        debts = skill_debt_service.calculate_skill_debt(self.db, new_uid, 1)
        active_debts = [d for d in debts if d.get("debt_status") == "SKILL_DEBT"]
        self.assertEqual(len(active_debts), 0, "Brand-new learner must not inherit active SKILL_DEBT!")

        # 5. Next-Best-Proof MUST prescribe Diagnostic Assessment
        nbp = next_best_proof_service.get_next_best_proof(self.db, new_uid, 1)
        self.assertEqual(nbp["title"], "Complete Diagnostic Assessment")
        self.assertEqual(nbp["action_type"], "REASSESS")
        self.assertEqual(nbp["action_readiness"], "HIGH")
        self.assertNotIn("SQL JOIN Rescue", nbp["title"])

        # 6. ML Prediction MUST report UNKNOWN / "Not enough learning evidence yet"
        ml_res = predict_skill_mastery(self.db, new_uid, 3)
        self.assertEqual(ml_res.risk_level, "UNKNOWN")
        self.assertEqual(ml_res.mastery_probability, 0.0)
        self.assertIn("Not enough learning evidence yet", ml_res.advisory_explanation)

        # 7. Roadmap MUST return 3-step onboarding sequence
        rm = roadmap_service.get_user_roadmap(self.db, new_uid)
        self.assertIsNotNone(rm)
        self.assertEqual(len(rm.steps), 3)
        self.assertEqual(rm.steps[0].title, "Complete Diagnostic Assessment")
        self.assertEqual(rm.steps[0].status, "RECOMMENDED")
        self.assertEqual(rm.steps[1].title, "Build Skill DNA")
        self.assertEqual(rm.steps[1].status, "BLOCKED")
        self.assertEqual(rm.steps[2].title, "Generate Personalized Roadmap")
        self.assertEqual(rm.steps[2].status, "BLOCKED")

        # 8. Dashboard API verification
        dash_res = self.client.get(f"/api/dashboard/{new_uid}")
        self.assertEqual(dash_res.status_code, 200)
        dash_data = dash_res.json()
        self.assertEqual(dash_data["metrics"]["career_readiness"]["score"], 0.0)
        self.assertEqual(dash_data["metrics"]["career_readiness"]["status"], "Awaiting baseline assessment")
        self.assertEqual(dash_data["metrics"]["skills_verified"], 0)
        self.assertEqual(dash_data["metrics"]["evidence_records_count"], 0)
        self.assertIsNone(dash_data["skill_debt_alert"])

        # 9. Passport API verification
        passport_res = self.client.get(f"/api/users/{new_uid}/skill-passport")
        self.assertEqual(passport_res.status_code, 200)
        p_data = passport_res.json()
        self.assertEqual(p_data["summary"]["verified_skills_count"], 0)
        self.assertEqual(p_data["header"]["total_evidence_count"], 0)
        self.assertEqual(len(p_data["evidence_timeline"]), 0)

    # =========================================================================
    # SCENARIO C: NEW LEARNER AFTER ASSESSMENT
    # =========================================================================
    def test_03_new_learner_after_assessment(self):
        """Verify submitting an assessment for new learner updates only their data."""
        email = "learner_c_test@example.com"
        u_res = self.client.post("/api/users", json={
            "name": "LEARNER_C",
            "email": email,
            "experience_level": "Intermediate",
            "target_role_id": 1,
            "weekly_learning_hours": 8,
            "learning_goal": "Career Transition",
        })
        self.assertEqual(u_res.status_code, 201)
        uid = u_res.json()["id"]

        # Snapshot Alex Mercer state before attempt
        alex_evidence_count = self.db.query(SkillEvidence).filter(SkillEvidence.user_id == 1).count()
        alex_dna = skill_dna_service.get_user_skill_dna(self.db, 1)
        alex_sql_level = next(d["skill_level"] for d in alex_dna if d["skill_name"] == "SQL JOINs")

        # Submit diagnostic assessment attempt on SQL JOINs (assessment_id = 1, skill_id = 3)
        att_res = self.client.post("/api/assessment-attempts", json={
            "user_id": uid,
            "assessment_id": 1,
            "score": 92.0,
            "accuracy": 92.0,
        })
        self.assertEqual(att_res.status_code, 201)

        # 1. New learner evidence count is 1
        new_ev_count = self.db.query(SkillEvidence).filter(SkillEvidence.user_id == uid).count()
        self.assertEqual(new_ev_count, 1)

        # 2. New learner Skill DNA for SQL JOINs is calibrated (> 0)
        c_dna = skill_dna_service.get_user_skill_dna(self.db, uid)
        c_dna_map = {d["skill_name"]: d for d in c_dna}
        self.assertGreater(c_dna_map["SQL JOINs"]["skill_level"], 60.0)
        self.assertEqual(c_dna_map["SQL JOINs"]["evidence_count"], 1)

        # 3. Other skills for new learner remain 0.0
        self.assertEqual(c_dna_map["Power BI"]["skill_level"], 0.0)
        self.assertEqual(c_dna_map["EDA"]["skill_level"], 0.0)

        # 4. Roadmap for new learner dynamically regenerates with real evidence-based steps
        rm = roadmap_service.get_user_roadmap(self.db, uid)
        self.assertIsNotNone(rm)
        self.assertGreaterEqual(len(rm.steps), 3)

        # 5. Alex Mercer's data is 100% UNTOUCHED
        alex_ev_after = self.db.query(SkillEvidence).filter(SkillEvidence.user_id == 1).count()
        self.assertEqual(alex_evidence_count, alex_ev_after)
        alex_dna_after = skill_dna_service.get_user_skill_dna(self.db, 1)
        alex_sql_after = next(d["skill_level"] for d in alex_dna_after if d["skill_name"] == "SQL JOINs")
        self.assertAlmostEqual(alex_sql_level, alex_sql_after, delta=0.1)

    # =========================================================================
    # SCENARIO D: CROSS-USER DATA ISOLATION
    # =========================================================================
    def test_04_cross_user_isolation(self):
        """Verify Learner A and Learner B are strictly isolated across all domains."""
        # Create Learner X
        res_x = self.client.post("/api/users", json={
            "name": "LEARNER_X",
            "email": "learner_x_test@example.com",
            "experience_level": "Intermediate",
            "target_role_id": 1,
            "weekly_learning_hours": 5,
        })
        self.assertEqual(res_x.status_code, 201)
        uid_x = res_x.json()["id"]

        # Create Learner Y
        res_y = self.client.post("/api/users", json={
            "name": "LEARNER_Y",
            "email": "learner_y_test@example.com",
            "experience_level": "Beginner",
            "target_role_id": 1,
            "weekly_learning_hours": 12,
        })
        self.assertEqual(res_y.status_code, 201)
        uid_y = res_y.json()["id"]

        # Submit attempt for X on Python (assessment_id = 2)
        att_x = self.client.post("/api/assessment-attempts", json={
            "user_id": uid_x,
            "assessment_id": 2,
            "score": 95.0,
            "accuracy": 95.0,
        })
        self.assertEqual(att_x.status_code, 201)

        # Submit attempt for Y on SQL (assessment_id = 3)
        att_y = self.client.post("/api/assessment-attempts", json={
            "user_id": uid_y,
            "assessment_id": 3,
            "score": 70.0,
            "accuracy": 70.0,
        })
        self.assertEqual(att_y.status_code, 201)

        # 1. Evidence endpoints return strictly scoped results
        ev_x_res = self.client.get(f"/api/users/{uid_x}/evidence")
        ev_y_res = self.client.get(f"/api/users/{uid_y}/evidence")
        self.assertEqual(ev_x_res.status_code, 200)
        self.assertEqual(ev_y_res.status_code, 200)
        ev_x = ev_x_res.json()
        ev_y = ev_y_res.json()

        self.assertEqual(len(ev_x), 1)
        self.assertEqual(len(ev_y), 1)
        self.assertIn("Python", ev_x[0]["source"])
        self.assertIn("SQL", ev_y[0]["source"])

        # 2. X has 0 SQL evidence, Y has 0 Python evidence
        dna_x = {d["skill_name"]: d for d in skill_dna_service.get_user_skill_dna(self.db, uid_x)}
        dna_y = {d["skill_name"]: d for d in skill_dna_service.get_user_skill_dna(self.db, uid_y)}

        self.assertGreater(dna_x["Python"]["skill_level"], 0.0)
        self.assertEqual(dna_x["SQL"]["skill_level"], 0.0)

        self.assertGreater(dna_y["SQL"]["skill_level"], 0.0)
        self.assertEqual(dna_y["Python"]["skill_level"], 0.0)

        # 3. Passport isolation
        p_x = self.client.get(f"/api/users/{uid_x}/skill-passport").json()
        p_y = self.client.get(f"/api/users/{uid_y}/skill-passport").json()

        x_skills_with_ev = [m["skill_name"] for m in p_x["skill_proof_matrix"] if len(m["supporting_evidences"]) > 0]
        y_skills_with_ev = [m["skill_name"] for m in p_y["skill_proof_matrix"] if len(m["supporting_evidences"]) > 0]

        self.assertIn("Python", x_skills_with_ev)
        self.assertNotIn("SQL", x_skills_with_ev)

        self.assertIn("SQL", y_skills_with_ev)
        self.assertNotIn("Python", y_skills_with_ev)

        # 4. Career Coach tool execution isolation
        tool_res_x = coach_service.execute_tool(self.db, uid_x, "get_recent_evidence", {})
        tool_res_y = coach_service.execute_tool(self.db, uid_y, "get_recent_evidence", {})
        self.assertTrue(all("Python" in e.get("skill_name", "") for e in tool_res_x.get("recent_evidence", [])))
        self.assertTrue(all("SQL" in e.get("skill_name", "") for e in tool_res_y.get("recent_evidence", [])))

    # =========================================================================
    # SCENARIO E: OFFICIAL PRESENTATION LEARNER (nikila.2509@gmail.com)
    # =========================================================================
    def test_05_presentation_learner_nikila_state(self):
        """Verify nikila.2509@gmail.com contains halfway-completed Analytics Engineer journey."""
        from app.models.learning import UserConceptProgress
        from app.seed.seed_data import seed_presentation_learner
        seed_presentation_learner(self.db)

        nikil = self.db.query(User).filter(User.email == "nikila.2509@gmail.com").first()
        self.assertIsNotNone(nikil)
        self.assertEqual(nikil.name, "NIKIL_A")
        self.assertEqual(nikil.target_role.name, "Analytics Engineer")
        self.assertEqual(nikil.experience_level, "Intermediate")
        self.assertEqual(nikil.weekly_learning_hours, 8)
        self.assertEqual(nikil.learning_goal, "Get my first Data/AI job")

        # 1. Skill DNA: Multi-skill calibrated profile with SQL JOINs as developing/weak
        dna = skill_dna_service.get_user_skill_dna(self.db, nikil.id)
        dna_map = {d["skill_name"]: d for d in dna}
        self.assertIn("SQL JOINs", dna_map)
        self.assertAlmostEqual(dna_map["SQL JOINs"]["accuracy"], 42.0, delta=5.0)
        self.assertAlmostEqual(dna_map["SQL JOINs"]["skill_level"], 55.0, delta=6.0)
        self.assertEqual(dna_map["SQL JOINs"]["status"], "DEVELOPING")
        self.assertGreaterEqual(dna_map["Python"]["skill_level"], 80.0)
        self.assertGreaterEqual(dna_map["SQL"]["skill_level"], 70.0)

        # 2. Skill Debt: SQL JOINs is active debt with HIGH severity
        debts = skill_debt_service.calculate_skill_debt(self.db, nikil.id, nikil.target_role_id)
        debt_map = {d["skill_name"]: d for d in debts}
        self.assertIn("SQL JOINs", debt_map)
        self.assertEqual(debt_map["SQL JOINs"]["debt_status"], "SKILL_DEBT")
        self.assertEqual(debt_map["SQL JOINs"]["severity"], "HIGH")

        # 3. Next-Best-Proof: SQL JOINs Rescue Practice
        nbp = next_best_proof_service.get_next_best_proof(self.db, nikil.id, nikil.target_role_id)
        self.assertEqual(nbp["skill_name"], "SQL JOINs")
        self.assertEqual(nbp["action_type"], "PRACTICE")
        self.assertIn("SQL JOIN", nbp["title"])

        # 4. Modular Learning Progress: mastered units and remediation for SQL JOINs
        prog = self.db.query(UserConceptProgress).filter_by(user_id=nikil.id).all()
        prog_map = {p.concept_slug: p for p in prog}
        self.assertIn("sql-joins-mastery", prog_map)
        self.assertEqual(prog_map["sql-joins-mastery"].status, "REMEDIATION")
        self.assertFalse(prog_map["sql-joins-mastery"].concept_check_passed)
        self.assertEqual(prog_map["sql-fundamentals"].status, "MASTERED")
        self.assertTrue(prog_map["sql-fundamentals"].concept_check_passed)

        # 5. Applied evidence exists
        applied_ev = self.db.query(SkillEvidence).filter(
            SkillEvidence.user_id == nikil.id,
            SkillEvidence.evidence_type == "APPLIED_LAB"
        ).first()
        self.assertIsNotNone(applied_ev)

        # 6. Roadmap: Active dynamic roadmap reflecting Analytics Engineer
        rm = roadmap_service.get_user_roadmap(self.db, nikil.id)
        self.assertIsNotNone(rm)
        self.assertGreaterEqual(len(rm.steps), 4)

        # 7. Dashboard metrics reflect populated halfway state
        dash_res = self.client.get(f"/api/dashboard/{nikil.id}")
        self.assertEqual(dash_res.status_code, 200)
        dash_data = dash_res.json()
        self.assertEqual(dash_data["target_role_name"], "Analytics Engineer")
        self.assertGreater(dash_data["metrics"]["career_readiness"]["score"], 0.0)
        self.assertGreater(dash_data["metrics"]["evidence_records_count"], 0)

        # 8. Coach Tool Execution resolves NIKIL_A and Analytics Engineer
        coach_profile = coach_service.execute_tool(self.db, nikil.id, "get_learner_profile", {})
        self.assertEqual(coach_profile["name"], "NIKIL_A")
        self.assertEqual(coach_profile["target_role"], "Analytics Engineer")

    # =========================================================================
    # SCENARIO F: CROSS-ACCOUNT ISOLATION (Section 15 Specification)
    # =========================================================================
    def test_06_complete_cross_account_isolation_walkthrough(self):
        """Execute strict Section 15 cross-account isolation test."""
        nikil = self.db.query(User).filter(User.email == "nikila.2509@gmail.com").first()
        self.assertIsNotNone(nikil)
        nikil_initial_role = nikil.target_role_id
        nikil_ev_count = self.db.query(SkillEvidence).filter(SkillEvidence.user_id == nikil.id).count()

        fresh_email = "fresh_walkthrough_isolation@example.com"
        # Cleanup if exists
        old = self.db.query(User).filter(User.email == fresh_email).first()
        if old:
            self.db.query(SkillEvidence).filter(SkillEvidence.user_id == old.id).delete()
            self.db.query(AssessmentAttempt).filter(AssessmentAttempt.user_id == old.id).delete()
            self.db.query(UserSkill).filter(UserSkill.user_id == old.id).delete()
            self.db.delete(old)
            self.db.commit()

        # Step 4: Create new learner
        create_res = self.client.post("/api/users", json={
            "name": "Fresh Learner",
            "email": fresh_email,
            "experience_level": "Beginner",
            "target_role_id": 1,
            "weekly_learning_hours": 10,
        })
        self.assertEqual(create_res.status_code, 201)
        fresh_user = create_res.json()
        fresh_id = fresh_user["id"]

        # Step 5: Confirm fresh state
        dash_res = self.client.get(f"/api/dashboard/{fresh_id}")
        self.assertEqual(dash_res.status_code, 200)
        dash = dash_res.json()
        self.assertEqual(dash["metrics"]["career_readiness"]["score"], 0.0)
        self.assertEqual(dash["metrics"]["skills_verified"], 0)
        self.assertEqual(dash["metrics"]["evidence_records_count"], 0)

        # NBP is Diagnostic Assessment
        nbp = next_best_proof_service.get_next_best_proof(self.db, fresh_id, 1)
        self.assertEqual(nbp["title"], "Complete Diagnostic Assessment")

        # Step 7 & 8: Confirm presentation progress is still intact
        self.db.refresh(nikil)
        self.assertEqual(nikil.target_role_id, nikil_initial_role)
        nikil_ev_after = self.db.query(SkillEvidence).filter(SkillEvidence.user_id == nikil.id).count()
        self.assertEqual(nikil_ev_count, nikil_ev_after)

        # Step 9 & 10: Change fresh learner target role
        patch_res = self.client.patch(f"/api/users/{fresh_id}", json={"target_role_id": 2})
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.json()["target_role_id"], 2)

        # Confirm nikil target role is still intact (Analytics Engineer = 9)
        self.db.refresh(nikil)
        self.assertEqual(nikil.target_role_id, nikil_initial_role)

        # Cleanup fresh learner
        self.db.query(SkillEvidence).filter(SkillEvidence.user_id == fresh_id).delete()
        self.db.query(AssessmentAttempt).filter(AssessmentAttempt.user_id == fresh_id).delete()
        self.db.query(UserSkill).filter(UserSkill.user_id == fresh_id).delete()
        fresh_obj = self.db.query(User).filter(User.id == fresh_id).first()
        if fresh_obj:
            self.db.delete(fresh_obj)
        self.db.commit()


if __name__ == "__main__":
    unittest.main()
