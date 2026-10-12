from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearningActivity(Base):
    __tablename__ = "learning_activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    activity_type = Column(String(50), nullable=False)  # LEARN, PRACTICE, REVIEW, REASSESS, PROJECT
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    difficulty = Column(String(50), default="Intermediate", nullable=False)
    estimated_minutes = Column(Integer, default=30, nullable=False)

    # Relationships
    skill = relationship("Skill", back_populates="activities")
    roadmap_steps = relationship("RoadmapStep", back_populates="activity")
