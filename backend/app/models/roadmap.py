from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(50), default="active", nullable=False)  # active, archived
    regeneration_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="roadmaps")
    target_role = relationship("Role")
    steps = relationship("RoadmapStep", back_populates="roadmap", order_by="RoadmapStep.order_index", cascade="all, delete-orphan")


class RoadmapStep(Base):
    __tablename__ = "roadmap_steps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("learning_activities.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    step_type = Column(String(50), nullable=False)  # FOUNDATION, LEARN, PRACTICE, REASSESS, PRACTICAL_TASK, PROJECT, CAPSTONE
    priority = Column(String(50), default="Medium", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(50), default="RECOMMENDED", nullable=False)  # COMPLETED, IN_PROGRESS, RECOMMENDED, BLOCKED, SKIPPED, REMEDIATION
    reason = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    estimated_minutes = Column(Integer, default=30, nullable=False)
    prerequisite_step_ids = Column(String(255), nullable=True)
    evidence_required = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    roadmap = relationship("Roadmap", back_populates="steps")
    skill = relationship("Skill")
    activity = relationship("LearningActivity", back_populates="roadmap_steps")


class RoadmapChange(Base):
    __tablename__ = "roadmap_changes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    change_type = Column(String(50), nullable=False)  # INSERTION, UNLOCKED, PROMOTED, REMOVED, COMPLETED
    skill_name = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    roadmap = relationship("Roadmap")
    user = relationship("User")

