import unittest
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.core.auth import generate_session_token
from app.models.user import User, UserSkill
from app.models.roadmap import Roadmap, RoadmapStep
from app.models.resource_preference import UserResourcePreference, SUPPORTED_PLATFORMS
from app.models.learning import LearningModule, LearningResource
from app.schemas.user import UserCreate
from app.services.user_service import user_service
from app.services.learning_service import learning_service
from app.services.resource_recommendation_service import resource_recommendation_service


class TestPhase21ResourcePreferencesComprehensive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        # Clean any old test users
        for email in ["learner_a_p21@skillpath.ai", "learner_b_p21@skillpath.ai"]:
            existing = cls.db.query(User).filter(User.email == email).first()
            if existing:
                cls.db.query(UserResourcePreference).filter(UserResourcePreference.user_id == existing.id).delete()
                cls.db.query(RoadmapStep).filter(RoadmapStep.roadmap_id.in_(
                    cls.db.query(Roadmap.id).filter(Roadmap.user_id == existing.id)
                )).delete(synchronize_session=False)
                cls.db.query(Roadmap).filter(Roadmap.user_id == existing.id).delete(synchronize_session=False)
                cls.db.query(UserSkill).filter(UserSkill.user_id == existing.id).delete(synchronize_session=False)
                cls.db.delete(existing)
                cls.db.commit()

        # Create User A (Beginner)
        cls.user_a = user_service.create_user(cls.db, UserCreate(
            name="Learner A",
            email="learner_a_p21@skillpath.ai",
            experience_level="Beginner",
            target_role_id=1,
            weekly_learning_hours=10,
            learning_goal="Master SQL Joins",
        ))
        cls.token_a = generate_session_token(cls.user_a.id)

        # Create User B (Intermediate)
        cls.user_b = user_service.create_user(cls.db, UserCreate(
            name="Learner B",
            email="learner_b_p21@skillpath.ai",
            experience_level="Intermediate",
            target_role_id=1,
            weekly_learning_hours=15,
            learning_goal="Advanced Python & Data",
        ))
        cls.token_b = generate_session_token(cls.user_b.id)

    @classmethod
    def tearDownClass(cls):
        for user in [cls.user_a, cls.user_b]:
            if user:
                cls.db.query(UserResourcePreference).filter(UserResourcePreference.user_id == user.id).delete()
                cls.db.query(RoadmapStep).filter(RoadmapStep.roadmap_id.in_(
                    cls.db.query(Roadmap.id).filter(Roadmap.user_id == user.id)
                )).delete(synchronize_session=False)
                cls.db.query(Roadmap).filter(Roadmap.user_id == user.id).delete(synchronize_session=False)
                cls.db.query(UserSkill).filter(UserSkill.user_id == user.id).delete(synchronize_session=False)
                record = cls.db.query(User).filter(User.id == user.id).first()
                if record:
                    cls.db.delete(record)
                cls.db.commit()
        cls.db.close()

    # 14. Unauthenticated access rejection
    def test_01_unauthenticated_access_rejection(self):
        """Endpoints /api/preferences/resources require valid authentication."""
        resp_get = self.client.get("/api/preferences/resources")
        self.assertEqual(resp_get.status_code, 401)

        resp_put = self.client.put(
            "/api/preferences/resources",
            json={"primary_platform": "geeksforgeeks", "secondary_platforms": []}
        )
        self.assertEqual(resp_put.status_code, 401)

    # 1. Save resource preference & 4. Primary platform selection & 5. Multiple platform selection
    def test_02_save_and_retrieve_resource_preference(self):
        """Learner can save primary and multiple secondary platforms via authenticated session."""
        headers_a = {"Authorization": f"Bearer {self.token_a}"}
        payload = {
            "primary_platform": "geeksforgeeks",
            "secondary_platforms": ["datacamp", "w3schools"],
        }
        res_put = self.client.put("/api/preferences/resources", json=payload, headers=headers_a)
        self.assertEqual(res_put.status_code, 200)
        data_put = res_put.json()
        self.assertEqual(data_put["user_id"], self.user_a.id)
        self.assertEqual(data_put["primary_platform"], "geeksforgeeks")
        self.assertEqual(sorted(data_put["secondary_platforms"]), ["datacamp", "w3schools"])

        # 2. Retrieve resource preference & 15. Preference persistence
        res_get = self.client.get("/api/preferences/resources", headers=headers_a)
        self.assertEqual(res_get.status_code, 200)
        data_get = res_get.json()
        self.assertEqual(data_get["primary_platform"], "geeksforgeeks")
        self.assertEqual(sorted(data_get["secondary_platforms"]), ["datacamp", "w3schools"])

    # 3. Update resource preference
    def test_03_update_resource_preference(self):
        """Updating preference replaces existing configuration cleanly."""
        headers_a = {"Authorization": f"Bearer {self.token_a}"}
        update_payload = {
            "primary_platform": "w3schools",
            "secondary_platforms": ["coursera"],
        }
        res = self.client.put("/api/preferences/resources", json=update_payload, headers=headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["primary_platform"], "w3schools")
        self.assertEqual(data["secondary_platforms"], ["coursera"])

    # 6. No-preference selection
    def test_04_no_preference_selection(self):
        """Selecting 'Let SkillPath choose' (no_preference) saves valid state."""
        headers_a = {"Authorization": f"Bearer {self.token_a}"}
        payload = {
            "primary_platform": "no_preference",
            "secondary_platforms": [],
        }
        res = self.client.put("/api/preferences/resources", json=payload, headers=headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["primary_platform"], "no_preference")
        self.assertEqual(data["secondary_platforms"], [])

    # 13. User isolation
    def test_05_user_isolation(self):
        """User A and User B maintain completely isolated preferences; cross-user tampering is rejected."""
        headers_a = {"Authorization": f"Bearer {self.token_a}"}
        headers_b = {"Authorization": f"Bearer {self.token_b}"}

        # Set User A -> geeksforgeeks
        self.client.put(
            "/api/preferences/resources",
            json={"primary_platform": "geeksforgeeks", "secondary_platforms": ["datacamp"]},
            headers=headers_a,
        )

        # Set User B -> w3schools
        self.client.put(
            "/api/preferences/resources",
            json={"primary_platform": "w3schools", "secondary_platforms": ["khanacademy"]},
            headers=headers_b,
        )

        # Verify A gets A
        res_a = self.client.get("/api/preferences/resources", headers=headers_a).json()
        self.assertEqual(res_a["primary_platform"], "geeksforgeeks")
        self.assertEqual(res_a["secondary_platforms"], ["datacamp"])

        # Verify B gets B
        res_b = self.client.get("/api/preferences/resources", headers=headers_b).json()
        self.assertEqual(res_b["primary_platform"], "w3schools")
        self.assertEqual(res_b["secondary_platforms"], ["khanacademy"])

        # Forbidden cross-user tampering: User A tries to edit User B's endpoint
        tamper_res = self.client.put(
            f"/api/users/{self.user_b.id}/resource-preferences",
            json={"primary_platform": "coursera", "secondary_platforms": []},
            headers=headers_a,
        )
        self.assertEqual(tamper_res.status_code, 403)

    # 7. Primary resource match
    def test_06_primary_resource_match(self):
        """Primary platform recommendation engine returns matched verified platform resource."""
        headers_a = {"Authorization": f"Bearer {self.token_a}"}
        self.client.put(
            "/api/preferences/resources",
            json={"primary_platform": "geeksforgeeks", "secondary_platforms": ["w3schools"]},
            headers=headers_a,
        )

        res = self.client.get("/api/resources/recommended/sql-joins-mastery", headers=headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["provider"].lower(), "geeksforgeeks")
        self.assertEqual(data["platform_match_type"], "primary")
        self.assertTrue("preferred platform" in data["selection_reason"].lower() or "matches" in data["selection_reason"].lower())
        self.assertTrue(data["url"].startswith("http"))

    # 8. Secondary fallback
    def test_07_secondary_fallback(self):
        """If primary platform has no resource for the concept, fall back to secondary platform."""
        headers_a = {"Authorization": f"Bearer {self.token_a}"}
        # Coursera has no python-pandas-pipelines resource, but W3Schools does
        self.client.put(
            "/api/preferences/resources",
            json={"primary_platform": "coursera", "secondary_platforms": ["w3schools"]},
            headers=headers_a,
        )

        res = self.client.get("/api/resources/recommended/python-pandas-pipelines", headers=headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["provider"].lower(), "w3schools")
        self.assertEqual(data["platform_match_type"], "secondary")
        self.assertTrue("secondary" in data["selection_reason"].lower() or "fallback" in data["selection_reason"].lower())

    # 9. SkillPath fallback
    def test_08_skillpath_fallback(self):
        """If neither primary nor secondary match, fallback to verified SkillPath resource."""
        headers_a = {"Authorization": f"Bearer {self.token_a}"}
        # Neither Coursera nor Khan Academy has python-pandas-pipelines
        self.client.put(
            "/api/preferences/resources",
            json={"primary_platform": "coursera", "secondary_platforms": ["khanacademy"]},
            headers=headers_a,
        )

        res = self.client.get("/api/resources/recommended/python-pandas-pipelines", headers=headers_a)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn(data["platform_match_type"], ["skillpath_fallback", "automatic"])
        self.assertTrue("skillpath" in data["selection_reason"].lower() or "verified" in data["selection_reason"].lower())

    # 10. Level matching
    def test_09_level_matching(self):
        """Learner level (e.g. Beginner vs Advanced) influences ranking."""
        db = SessionLocal()
        try:
            pref = db.query(UserResourcePreference).filter(UserResourcePreference.user_id == self.user_a.id).first()
            if not pref:
                pref = UserResourcePreference(user_id=self.user_a.id)
                db.add(pref)
            pref.primary_platform = "geeksforgeeks"
            pref.secondary_platforms = ""
            pref.preferred_platforms = ""
            db.commit()

            rec_beg = resource_recommendation_service.get_recommended_resource(
                db=db,
                user=self.user_a,
                concept_slug="sql-joins-mastery",
                level_override="Beginner",
            )
            self.assertIsNotNone(rec_beg)
            self.assertIn(rec_beg["difficulty"].lower(), ["beginner", "intermediate", "all_levels"])
        finally:
            db.close()

    # 11. Invalid resource exclusion & 12. Inactive resource exclusion
    def test_10_inactive_and_invalid_resource_exclusion(self):
        """Inactive or unverified resources are never recommended."""
        db = SessionLocal()
        inactive = None
        try:
            # Create a dummy inactive resource
            inactive = LearningResource(
                skill_id=1,
                title="Fake Inactive Guide",
                provider="geeksforgeeks",
                url="https://example.com/fake",
                resource_type="article",
                difficulty="Beginner",
                is_active=False,
                verified=True,
                concept_slug="sql-joins-mastery",
            )
            db.add(inactive)
            db.commit()

            rec = resource_recommendation_service.get_recommended_resource(
                db=db,
                user=self.user_a,
                concept_slug="sql-joins-mastery",
            )
            self.assertIsNotNone(rec)
            self.assertNotEqual(rec["id"], inactive.id)
        finally:
            if inactive and inactive.id:
                db.delete(inactive)
                db.commit()
            db.close()

    # 16. Existing learning page still works
    def test_11_existing_learning_page_module_detail(self):
        """Existing /api/learning/modules/{slug} endpoint continues to function seamlessly with preference ranking."""
        module = self.db.query(LearningModule).first()
        self.assertIsNotNone(module)
        headers_a = {"Authorization": f"Bearer {self.token_a}"}

        resp = self.client.get(
            f"/api/learning/modules/{module.slug}?user_id={self.user_a.id}",
            headers=headers_a,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["slug"], module.slug)
        self.assertIn("external_resources", data)

    # 17. Avoid YouTube videos
    def test_12_avoid_youtube_videos(self):
        """Recommendation service strictly excludes YouTube video resources."""
        headers_a = {"Authorization": f"Bearer {self.token_a}"}
        for concept in ["sql-joins-mastery", "sql-fundamentals", "python-core-fundamentals", "python-pandas-pipelines"]:
            res = self.client.get(f"/api/resources/recommended/{concept}", headers=headers_a)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertNotEqual(data["provider"].lower(), "youtube")
            self.assertNotIn("youtube.com", data["url"].lower())
            self.assertNotIn("youtu.be", data["url"].lower())


if __name__ == "__main__":
    unittest.main()
