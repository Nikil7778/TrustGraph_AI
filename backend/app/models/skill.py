from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    role_skills = relationship("RoleSkill", back_populates="skill", cascade="all, delete-orphan")
    user_skills = relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="skill")
    activities = relationship("LearningActivity", back_populates="skill")
    evidences = relationship("SkillEvidence", back_populates="skill")
    projects = relationship("Project", back_populates="skill")
