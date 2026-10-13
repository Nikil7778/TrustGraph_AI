from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    experience_level = Column(String(50), default="Intermediate", nullable=False)
    target_role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    weekly_learning_hours = Column(Integer, default=10, nullable=False)
    learning_goal = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    google_id = Column(String(255), nullable=True, index=True)
    avatar_url = Column(String(1024), nullable=True)
    password_hash = Column(String(255), nullable=True)

    # Relationships
    target_role = relationship("Role", back_populates="users")
    user_skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="user", cascade="all, delete-orphan")
    evidences = relationship("SkillEvidence", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    project_attempts = relationship("ProjectAttempt", back_populates="user", cascade="all, delete-orphan")


class UserSkill(Base):
    """
    Database foundation for Skill DNA vector modeling per learner.
    """
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_level = Column(Float, default=0.0, nullable=False) # e.g. 85.0 for 85%
    confidence = Column(Float, default=50.0, nullable=False)
    accuracy = Column(Float, default=50.0, nullable=False)
    difficulty = Column(String(50), default="Intermediate", nullable=False)
    recency = Column(String(50), default="Recently assessed", nullable=False)
    evidence_score = Column(Float, default=0.0, nullable=False)
    last_assessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),
    )

    # Relationships
    user = relationship("User", back_populates="user_skills")
    skill = relationship("Skill", back_populates="user_skills")
