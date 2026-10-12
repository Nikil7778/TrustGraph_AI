from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class SkillEvidence(Base):
    """
    Evidence layer driving verified Skill DNA profile scores.
    """
    __tablename__ = "skill_evidences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(100), nullable=False)  # e.g., Diagnostic Assessment #1, Practice Lab
    evidence_type = Column(String(50), nullable=False)  # ASSESSMENT, PRACTICE, PROJECT, REAL_WORLD_TASK
    score = Column(Float, nullable=False)  # 0.0 to 100.0
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="evidences")
    skill = relationship("Skill", back_populates="evidences")
