import unittest
import sys
import os

# Ensure backend root is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.user import User, UserSkill
from app.models.role import Role
from app.models.roadmap import Roadmap, RoadmapStep
from app.models.learning import LearningModule, LearningResource
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import user_service
from app.services.roadmap_service import roadmap_service
from app.services.learning_service import learning_service


class TestDynamicRoleRoadmapAndLearning(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        # Clean up any test user from previous run
        test_user = self.db.query(User).filter(User.email == "test_dynamic_role@skillpath.ai").first()
        if test_user:
            self.db.query(RoadmapStep).filter(RoadmapStep.roadmap_id.in_(
                self.db.query(Roadmap.id).filter(Roadmap.user_id == test_user.id)
            )).delete(synchronize_session=False)
            self.db.query(Roadmap).filter(Roadmap.user_id == test_user.id).delete(synchronize_session=False)
            self.db.query(UserSkill).filter(UserSkill.user_id == test_user.id).delete(synchronize_session=False)
            self.db.delete(test_user)
            self.db.commit()

        # Create fresh test user with Data Analyst role (id: 1)
        user_create = UserCreate(
            name="Dynamic Role Tester",
            email="test_dynamic_role@skillpath.ai",
            experience_level="Intermediate",
            target_role_id=1,
            weekly_learning_hours=10
        )
        self.user = user_service.create_user(self.db, user_create)

    def tearDown(self):
        if hasattr(self, 'user') and self.user.id:
            test_user = self.db.query(User).filter(User.id == self.user.id).first()
            if test_user:
                self.db.query(RoadmapStep).filter(RoadmapStep.roadmap_id.in_(
                    self.db.query(Roadmap.id).filter(Roadmap.user_id == test_user.id)
                )).delete(synchronize_session=False)
                self.db.query(Roadmap).filter(Roadmap.user_id == test_user.id).delete(synchronize_session=False)
                self.db.query(UserSkill).filter(UserSkill.user_id == test_user.id).delete(synchronize_session=False)
                self.db.delete(test_user)
                self.db.commit()
        self.db.close()

    def test_section_22_and_23_full_role_switching_and_adaptive_lifecycle(self):
        """
        Tests:
        TEST E: Fresh Learner Verification (diagnostic step, no fabricated DNA)
        TEST A: Data Analyst -> DA roadmap, DA modules, DA resources
        TEST B: Switch to Data Scientist -> DS roadmap, DS modules, DS resources
        TEST C: Switch to Python Developer -> PyDev roadmap, PyDev modules, PyDev resources
        TEST D: Switch back to Data Analyst -> DA roadmap and DA modules return
        TEST F: Evidence preservation across role switches (Python skill transfers)
        """
        # =====================================================================
        # TEST E: Fresh Learner Verification (Section 23)
        # =====================================================================
        # Brand new user has all skill scores at 0.0 with "Not assessed yet"
        user_skills = self.db.query(UserSkill).filter(UserSkill.user_id == self.user.id).all()
        for us in user_skills:
            self.assertEqual(us.skill_level, 0.0, "Fresh learner must have NO fabricated Skill DNA scores")
            self.assertEqual(us.recency, "Not assessed yet", "Fresh learner must have recency as 'Not assessed yet'")

        # Initial roadmap for unassessed learner must direct to diagnostic
        initial_rm = roadmap_service.get_user_roadmap(self.db, self.user.id)
        self.assertIsNotNone(initial_rm, "Roadmap must be generated")
        self.assertGreater(len(initial_rm.steps), 0, "Roadmap should have steps")
        first_step = initial_rm.steps[0]
        self.assertEqual(first_step.step_type.upper(), "ASSESSMENT", f"First step for fresh user must be ASSESSMENT, got: {first_step.step_type}")
        self.assertIn("diagnostic", first_step.title.lower(), f"First step title must mention diagnostic, got: {first_step.title}")

        # =====================================================================
        # TEST A: Data Analyst Assessment & Progression (Section 22 TEST A)
        # =====================================================================
        # Simulate assessed scores: Python (id:1) strong at 80.0, SQL (id:2) weak at 25.0
        py_us = self.db.query(UserSkill).filter_by(user_id=self.user.id, skill_id=1).first()
        if py_us:
            py_us.skill_level = 80.0
            py_us.confidence = 85.0
            py_us.accuracy = 80.0
            py_us.recency = "Recently assessed"

        sql_us = self.db.query(UserSkill).filter_by(user_id=self.user.id, skill_id=2).first()
        if sql_us:
            sql_us.skill_level = 25.0
            sql_us.confidence = 40.0
            sql_us.accuracy = 25.0
            sql_us.recency = "Recently assessed"
        self.db.commit()

        # Re-generate roadmap for Data Analyst after diagnostic assessment
        da_rm = roadmap_service.generate_dynamic_roadmap(self.db, self.user.id, role_id=1)
        self.assertEqual(da_rm.target_role_id, 1, "Roadmap target role must be Data Analyst (1)")
        da_step_titles = [s.title for s in da_rm.steps]

        # DA should emphasize SQL / BI / Rescue for weak SQL
        self.assertTrue(any("sql" in t.lower() for t in da_step_titles), f"DA roadmap must contain SQL-focused steps: {da_step_titles}")
        
        # Check DA Learning Modules
        da_modules = learning_service.get_modules_for_user(self.db, self.user.id)
        da_slugs = [m.slug for m in da_modules]
        self.assertIn("sql-joins-mastery", da_slugs, "DA learning list must contain SQL Joins Mastery")
        self.assertIn("power-bi-dax-modeling", da_slugs, "DA learning list must contain Power BI DAX Modeling")
        self.assertNotIn("fastapi-rest-endpoints", da_slugs, "DA learning list must NOT contain FastAPI")
        self.assertNotIn("pytest-automated-testing", da_slugs, "DA learning list must NOT contain PyTest")

        # Check External Resources for DA module (sql-fundamentals is active & unlocked for SQL rescue)
        da_sql_detail = learning_service.get_module_detail(self.db, self.user.id, "sql-fundamentals")
        self.assertIsNotNone(da_sql_detail)
        self.assertGreater(len(da_sql_detail.external_resources), 0, "Must have verified external resources")
        for res in da_sql_detail.external_resources:
            self.assertTrue(res.url.startswith("http"), f"Resource URL {res.url} must be a valid http link")
            self.assertIn("postgresql.org", res.url, "DA SQL resource must point to postgresql.org")

        # =====================================================================
        # TEST B: Switch Target Role -> Data Scientist (Section 22 TEST B)
        # =====================================================================
        updated_user = user_service.update_user(self.db, self.user.id, UserUpdate(target_role_id=2))
        self.assertEqual(updated_user.target_role_id, 2)

        # Roadmap must automatically update to Data Scientist
        ds_rm = roadmap_service.get_user_roadmap(self.db, self.user.id)
        self.assertEqual(ds_rm.target_role_id, 2, "Roadmap target role must now be Data Scientist (2)")
        ds_step_titles = [s.title for s in ds_rm.steps]

        # DS should emphasize Machine Learning / Feature Engineering / Statistics / EDA
        self.assertTrue(
            any("machine learning" in t.lower() or "statistics" in t.lower() or "eda" in t.lower() for t in ds_step_titles),
            f"DS roadmap steps should include ML/Stats/EDA: {ds_step_titles}"
        )

        # Check DS Learning Modules
        ds_modules = learning_service.get_modules_for_user(self.db, self.user.id)
        ds_slugs = [m.slug for m in ds_modules]
        self.assertIn("feature-engineering-pipelines", ds_slugs, "DS learning list must contain Feature Engineering")
        self.assertIn("model-evaluation-metrics", ds_slugs, "DS learning list must contain Model Evaluation")
        self.assertIn("machine-learning-foundations", ds_slugs, "DS learning list must contain ML Foundations")
        self.assertNotIn("fastapi-rest-endpoints", ds_slugs, "DS learning list must NOT contain FastAPI")
        self.assertNotIn("power-bi-dax-modeling", ds_slugs, "DS learning list must NOT contain Power BI")

        # Check External Resources for DS module (python-pandas-pipelines is foundational & unlocked)
        ds_detail = learning_service.get_module_detail(self.db, self.user.id, "python-pandas-pipelines")
        self.assertIsNotNone(ds_detail)
        self.assertGreater(len(ds_detail.external_resources), 0, "Must have verified resources for DS")
        self.assertTrue(any("pandas.pydata.org" in r.url for r in ds_detail.external_resources),
                        "DS resources must point to official pandas documentation")

        # =====================================================================
        # TEST C: Switch Target Role -> Python Developer (Section 22 TEST C)
        # =====================================================================
        updated_user = user_service.update_user(self.db, self.user.id, UserUpdate(target_role_id=5))
        self.assertEqual(updated_user.target_role_id, 5)

        # Roadmap must automatically update to Python Developer
        py_rm = roadmap_service.get_user_roadmap(self.db, self.user.id)
        self.assertEqual(py_rm.target_role_id, 5, "Roadmap target role must now be Python Developer (5)")
        py_step_titles = [s.title for s in py_rm.steps]

        # PyDev must emphasize OOP / APIs / Testing / Deployment
        self.assertTrue(
            any("oop" in t.lower() or "api" in t.lower() or "test" in t.lower() or "python" in t.lower() for t in py_step_titles),
            f"PyDev roadmap must contain OOP/API/Testing/Deployment: {py_step_titles}"
        )

        # Check PyDev Learning Modules
        py_modules = learning_service.get_modules_for_user(self.db, self.user.id)
        py_slugs = [m.slug for m in py_modules]
        self.assertIn("python-oop-architecture", py_slugs, "PyDev learning list must contain Python OOP Architecture")
        self.assertIn("fastapi-rest-endpoints", py_slugs, "PyDev learning list must contain FastAPI REST Endpoints")
        self.assertIn("pytest-automated-testing", py_slugs, "PyDev learning list must contain PyTest Automated Testing")
        self.assertIn("docker-container-deployment", py_slugs, "PyDev learning list must contain Docker Container Deployment")
        self.assertNotIn("power-bi-dax-modeling", py_slugs, "PyDev learning list must NOT contain Power BI")
        self.assertNotIn("model-evaluation-metrics", py_slugs, "PyDev learning list must NOT contain Model Evaluation")

        # Check PyDev External Resources (python-core-fundamentals is foundational & unlocked)
        py_detail = learning_service.get_module_detail(self.db, self.user.id, "python-core-fundamentals")
        self.assertIsNotNone(py_detail)
        self.assertGreater(len(py_detail.external_resources), 0, "Must have verified external resources for Python Core")
        self.assertTrue(any("docs.python.org" in r.url for r in py_detail.external_resources),
                        "Python core resource must point to official documentation")

        # =====================================================================
        # TEST D: Switch back to Data Analyst (Section 22 TEST D)
        # =====================================================================
        updated_user = user_service.update_user(self.db, self.user.id, UserUpdate(target_role_id=1))
        self.assertEqual(updated_user.target_role_id, 1)

        da_rm_again = roadmap_service.get_user_roadmap(self.db, self.user.id)
        self.assertEqual(da_rm_again.target_role_id, 1, "Roadmap must switch back to Data Analyst (1)")

        da_modules_again = learning_service.get_modules_for_user(self.db, self.user.id)
        da_slugs_again = [m.slug for m in da_modules_again]
        self.assertIn("sql-joins-mastery", da_slugs_again)
        self.assertIn("power-bi-dax-modeling", da_slugs_again)
        self.assertNotIn("fastapi-rest-endpoints", da_slugs_again)

        # =====================================================================
        # TEST F: Evidence Preservation (Section 7)
        # =====================================================================
        # Check that user's skill scores were preserved throughout all role switches
        final_py = self.db.query(UserSkill).filter_by(user_id=self.user.id, skill_id=1).first()
        final_sql = self.db.query(UserSkill).filter_by(user_id=self.user.id, skill_id=2).first()
        self.assertIsNotNone(final_py)
        self.assertIsNotNone(final_sql)
        self.assertEqual(final_py.skill_level, 80.0, "Python score (80.0) must be preserved across role switches")
        self.assertEqual(final_sql.skill_level, 25.0, "SQL score (25.0) must be preserved across role switches")


if __name__ == "__main__":
    unittest.main()
