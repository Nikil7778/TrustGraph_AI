from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    difficulty = Column(String(50), default="Intermediate", nullable=False)
    estimated_minutes = Column(Integer, default=120, nullable=False)
    project_type = Column(String(50), default="Portfolio", nullable=False)

    # Relationships
    skill = relationship("Skill", back_populates="projects")
    attempts = relationship("ProjectAttempt", back_populates="project", cascade="all, delete-orphan")


class ProjectAttempt(Base):
    __tablename__ = "project_attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)  # 0.0 to 100.0
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    feedback = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="project_attempts")
    project = relationship("Project", back_populates="attempts")
