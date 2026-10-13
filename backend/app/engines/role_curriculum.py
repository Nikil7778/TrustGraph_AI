from typing import Dict, Any, List, Optional, Tuple


class RoleCurriculumEngine:
    """
    Role Curriculum & Skill Dependency Engine (Phase 19).
    Defines role-correct skill requirements, proficiency thresholds,
    importance weights, and prerequisite DAGs for each supported career role.

    Principle:
    'The destination is determined by the learner's target role.
     The route is determined by the learner's demonstrated ability.'
    """

    ROLE_PROFILES: Dict[str, Dict[str, Any]] = {
        "Data Analyst": {
            "role_id": 1,
            "role_name": "Data Analyst",
            "description": "Business intelligence, relational querying, exploratory data analysis, and executive dashboard communication.",
            "target_proficiency": {
                "SQL": 85,
                "SQL JOINs": 85,
                "Python": 80,
                "Statistics": 75,
                "EDA": 85,
                "Data Visualization": 85,
                "Power BI": 80,
                "Machine Learning": 40,
            },
            "importance_scores": {
                "SQL": 90,
                "SQL JOINs": 95,
                "Python": 80,
                "Statistics": 75,
                "EDA": 85,
                "Data Visualization": 90,
                "Power BI": 85,
                "Machine Learning": 30,
            },
            "industry_relevance": {
                "SQL": "Critical",
                "SQL JOINs": "Critical",
                "Python": "High",
                "Statistics": "Medium",
                "EDA": "High",
                "Data Visualization": "Critical",
                "Power BI": "Critical",
                "Machine Learning": "Low",
            },
            # Role-specific prerequisite DAG
            "prerequisite_graph": {
                "SQL JOINs": ["SQL"],
                "EDA": ["Python", "Statistics"],
                "Data Visualization": ["EDA"],
                "Applied Analytics": ["EDA", "Data Visualization"],
                "Power BI": ["Data Visualization"],
                "Machine Learning": ["Python", "Statistics", "EDA"],
            },
            # Natural conceptual learning sequence for this role
            "baseline_pathway": [
                "SQL",
                "SQL JOINs",
                "Python",
                "Statistics",
                "EDA",
                "Data Visualization",
                "Power BI",
            ],
            "capstone_title": "End-to-End E-Commerce Executive Intelligence Portfolio Project",
            "capstone_description": "Multi-table relational schema analysis with automated SQL extraction, EDA, KPI dashboard, and executive presentation.",
        },
        "Data Scientist": {
            "role_id": 2,
            "role_name": "Data Scientist",
            "description": "Statistical modeling, predictive analytics, feature engineering, and production machine learning pipelines.",
            "target_proficiency": {
                "Python": 85,
                "Statistics": 85,
                "Machine Learning": 85,
                "EDA": 80,
                "SQL": 80,
                "Data Visualization": 75,
                "Deep Learning": 75,
                "Power BI": 40,
            },
            "importance_scores": {
                "Python": 95,
                "Statistics": 95,
                "Machine Learning": 95,
                "EDA": 85,
                "SQL": 80,
                "Data Visualization": 70,
                "Deep Learning": 80,
                "Power BI": 30,
            },
            "industry_relevance": {
                "Python": "Critical",
                "Statistics": "Critical",
                "Machine Learning": "Critical",
                "EDA": "High",
                "SQL": "High",
                "Data Visualization": "Medium",
                "Deep Learning": "High",
                "Power BI": "Low",
            },
            "prerequisite_graph": {
                "EDA": ["Python"],
                "Machine Learning": ["Python", "Statistics", "EDA"],
                "Deep Learning": ["Machine Learning"],
                "Data Visualization": ["EDA"],
            },
            "baseline_pathway": [
                "Python",
                "SQL",
                "Statistics",
                "EDA",
                "Machine Learning",
                "Data Visualization",
                "Deep Learning",
            ],
            "capstone_title": "Predictive Modeling & Statistical Inference Portfolio Project",
            "capstone_description": "End-to-end dataset modeling with statistical hypothesis testing, feature pipelines, regression/classification, and model explainability.",
        },
        "Python Developer": {
            "role_id": 5,
            "role_name": "Python Developer",
            "description": "Backend API development, object-oriented software engineering, automated testing, and containerized deployment.",
            "target_proficiency": {
                "Python Basics": 85,
                "Python": 85,
                "OOP": 85,
                "Data Structures": 80,
                "Exception Handling": 80,
                "SQL Basics": 75,
                "SQL": 75,
                "HTTP & REST APIs": 85,
                "FastAPI": 85,
                "Testing & PyTest": 80,
                "Git": 80,
                "Deployment & Docker": 75,
            },
            "importance_scores": {
                "Python Basics": 95,
                "Python": 95,
                "OOP": 95,
                "Data Structures": 85,
                "Exception Handling": 85,
                "SQL Basics": 75,
                "SQL": 75,
                "HTTP & REST APIs": 90,
                "FastAPI": 95,
                "Testing & PyTest": 85,
                "Git": 80,
                "Deployment & Docker": 75,
            },
            "industry_relevance": {
                "Python Basics": "Critical",
                "Python": "Critical",
                "OOP": "Critical",
                "Data Structures": "High",
                "Exception Handling": "High",
                "SQL Basics": "High",
                "SQL": "High",
                "HTTP & REST APIs": "Critical",
                "FastAPI": "Critical",
                "Testing & PyTest": "High",
                "Git": "High",
                "Deployment & Docker": "Medium",
            },
            "prerequisite_graph": {
                "OOP": ["Python Basics"],
                "Data Structures": ["Python Basics"],
                "Exception Handling": ["Python Basics"],
                "HTTP & REST APIs": ["Python Basics", "OOP"],
                "FastAPI": ["HTTP & REST APIs", "Exception Handling"],
                "Testing & PyTest": ["FastAPI"],
                "Deployment & Docker": ["FastAPI", "Testing & PyTest"],
            },
            "baseline_pathway": [
                "Python Basics",
                "OOP",
                "Data Structures",
                "Exception Handling",
                "SQL Basics",
                "HTTP & REST APIs",
                "FastAPI",
                "Testing & PyTest",
                "Deployment & Docker",
            ],
            "capstone_title": "Production FastAPI Microservices & Containerized API Architecture Project",
            "capstone_description": "Scalable REST API with database transactions, automated PyTest suite, JWT security, and Docker container deployment.",
        },
        "Machine Learning Engineer": {
            "role_id": 3,
            "role_name": "Machine Learning Engineer",
            "description": "Scalable ML architectures, deep neural networks, model deployment pipelines, and MLOps reliability.",
            "target_proficiency": {
                "Python": 90,
                "Machine Learning": 90,
                "MLOps": 85,
                "Deep Learning": 80,
                "SQL": 75,
                "Statistics": 75,
                "EDA": 70,
                "Data Visualization": 50,
                "Power BI": 30,
            },
            "importance_scores": {
                "Python": 95,
                "Machine Learning": 95,
                "MLOps": 95,
                "Deep Learning": 85,
                "SQL": 75,
                "Statistics": 75,
                "EDA": 65,
                "Data Visualization": 40,
                "Power BI": 20,
            },
            "industry_relevance": {
                "Python": "Critical",
                "Machine Learning": "Critical",
                "MLOps": "Critical",
                "Deep Learning": "High",
                "SQL": "Medium",
                "Statistics": "High",
                "EDA": "Medium",
                "Data Visualization": "Low",
                "Power BI": "Low",
            },
            "prerequisite_graph": {
                "Machine Learning": ["Python", "Statistics"],
                "Deep Learning": ["Machine Learning"],
                "MLOps": ["Python", "Machine Learning", "Deep Learning"],
                "EDA": ["Python"],
            },
            "baseline_pathway": [
                "Python",
                "SQL",
                "Statistics",
                "Machine Learning",
                "Deep Learning",
                "MLOps",
            ],
            "capstone_title": "Production ML Pipeline & Containerized Model Serving Project",
            "capstone_description": "Complete scalable ML architecture with automated CI/CD pipeline, FastAPI inference endpoint, and model drift monitoring.",
        },
        "Analytics Engineer": {
            "role_id": 9,
            "role_name": "Analytics Engineer",
            "description": "Modern data stack, SQL transformation, dbt modeling, data pipelines, and BI enablement.",
            "target_proficiency": {
                "SQL": 90,
                "SQL JOINs": 90,
                "Python": 80,
                "EDA": 80,
                "Data Visualization": 85,
                "Power BI": 80,
                "Statistics": 75,
                "Machine Learning": 30,
            },
            "importance_scores": {
                "SQL": 95,
                "SQL JOINs": 95,
                "Python": 80,
                "EDA": 80,
                "Data Visualization": 85,
                "Power BI": 80,
                "Statistics": 70,
                "Machine Learning": 30,
            },
            "industry_relevance": {
                "SQL": "Critical",
                "SQL JOINs": "Critical",
                "Python": "High",
                "EDA": "High",
                "Data Visualization": "High",
                "Power BI": "High",
                "Statistics": "Medium",
                "Machine Learning": "Low",
            },
            "prerequisite_graph": {
                "SQL JOINs": ["SQL"],
                "EDA": ["SQL", "Python"],
                "Data Visualization": ["EDA"],
                "Power BI": ["Data Visualization"],
            },
            "baseline_pathway": [
                "SQL",
                "SQL JOINs",
                "Python",
                "EDA",
                "Statistics",
                "Data Visualization",
                "Power BI",
            ],
            "capstone_title": "Analytics Engineering & Multi-Source Dimensional Modeling Portfolio Project",
            "capstone_description": "End-to-end data transformation pipeline with dbt, modular SQL layers, automated testing, and Power BI semantic layer.",
        },
    }

    def __init__(self):
        # Automatically mirror target_proficiency to skills attribute for each profile
        for prof in self.ROLE_PROFILES.values():
            prof["skills"] = prof["target_proficiency"]

    def get_role_profile(self, role_name_or_id: Any) -> Dict[str, Any]:
        """
        Retrieves normalized role profile by name or ID.
        Defaults to Data Analyst if unspecified.
        """
        if isinstance(role_name_or_id, int):
            try:
                from app.core.database import SessionLocal
                from app.models.role import Role
                _db = SessionLocal()
                _role = _db.query(Role).filter(Role.id == role_name_or_id).first()
                _db.close()
                if _role:
                    for name, prof in self.ROLE_PROFILES.items():
                        if name.lower() == _role.name.lower() or prof["role_name"].lower() == _role.name.lower():
                            return prof
            except Exception:
                pass

            for prof in self.ROLE_PROFILES.values():
                if prof.get("role_id") == role_name_or_id:
                    return prof
        elif isinstance(role_name_or_id, str):
            clean = role_name_or_id.lower().strip()
            if clean in ["python developer", "python dev", "python backend developer", "python engineer"]:
                return self.ROLE_PROFILES["Python Developer"]
            if clean in ["data scientist", "ds"]:
                return self.ROLE_PROFILES["Data Scientist"]
            if clean in ["data analyst", "da"]:
                return self.ROLE_PROFILES["Data Analyst"]
            if clean in ["ml engineer", "machine learning engineer", "mle"]:
                for prof in self.ROLE_PROFILES.values():
                    if prof.get("role_id") == 3:
                        return prof
            for name, prof in self.ROLE_PROFILES.items():
                if name.lower() == clean or prof["role_name"].lower() == clean:
                    return prof

        return self.ROLE_PROFILES["Data Analyst"]

    def get_prerequisite_graph_for_role(self, role_name: str) -> Dict[str, List[str]]:
        prof = self.get_role_profile(role_name)
        return prof.get("prerequisite_graph", {})

    def get_baseline_pathway_for_role(self, role_name: str) -> List[str]:
        prof = self.get_role_profile(role_name)
        return prof.get("baseline_pathway", [])

    def get_required_level(self, role_name: str, skill_name: str) -> int:
        prof = self.get_role_profile(role_name)
        return prof.get("target_proficiency", {}).get(skill_name, 75)

    def get_importance_score(self, role_name: str, skill_name: str) -> int:
        prof = self.get_role_profile(role_name)
        return prof.get("importance_scores", {}).get(skill_name, 50)


role_curriculum_engine = RoleCurriculumEngine()
