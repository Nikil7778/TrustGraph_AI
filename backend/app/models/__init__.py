from app.core.database import Base
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.models.user import User, UserSkill
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentAttempt
from app.models.activity import LearningActivity
from app.models.evidence import SkillEvidence
from app.models.roadmap import Roadmap, RoadmapStep, RoadmapChange
from app.models.project import Project, ProjectAttempt
from app.models.industry_lab import IndustryLab, IndustryLabTask, IndustryLabAttempt

__all__ = [
    "Base",
    "Role",
    "RoleSkill",
    "Skill",
    "User",
    "UserSkill",
    "Assessment",
    "AssessmentQuestion",
    "AssessmentAttempt",
    "LearningActivity",
    "SkillEvidence",
    "Roadmap",
    "RoadmapStep",
    "RoadmapChange",
    "Project",
    "ProjectAttempt",
    "IndustryLab",
    "IndustryLabTask",
    "IndustryLabAttempt",
]

