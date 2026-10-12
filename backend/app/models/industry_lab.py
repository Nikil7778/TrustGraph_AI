from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class IndustryLab(Base):
    __tablename__ = "industry_labs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    target_role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    primary_skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    difficulty = Column(String(50), default="Intermediate", nullable=False)
    estimated_minutes = Column(Integer, default=45, nullable=False)
    business_context = Column(Text, nullable=False)
    datasets_info = Column(Text, nullable=True)  # JSON metadata describing datasets
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    target_role = relationship("Role")
    primary_skill = relationship("Skill")
    tasks = relationship("IndustryLabTask", back_populates="lab", order_by="IndustryLabTask.task_order", cascade="all, delete-orphan")
    attempts = relationship("IndustryLabAttempt", back_populates="lab", order_by="IndustryLabAttempt.created_at.desc()", cascade="all, delete-orphan")


class IndustryLabTask(Base):
    __tablename__ = "industry_lab_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lab_id = Column(Integer, ForeignKey("industry_labs.id", ondelete="CASCADE"), nullable=False, index=True)
    task_order = Column(Integer, default=1, nullable=False)
    task_type = Column(String(50), default="SQL_QUERY", nullable=False)  # DATA_PROFILING, SQL_QUERY, DATA_CLEANING, DATA_VALIDATION, BUSINESS_ANALYSIS
    title = Column(String(200), nullable=False)
    prompt = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    expected_output_desc = Column(Text, nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    evaluation_rules = Column(Text, nullable=True)  # JSON evaluation configuration

    # Relationships
    lab = relationship("IndustryLab", back_populates="tasks")


class IndustryLabAttempt(Base):
    __tablename__ = "industry_lab_attempts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lab_id = Column(Integer, ForeignKey("industry_labs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_number = Column(Integer, default=1, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)  # PASSED, PARTIAL, FAILED
    total_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 100.0
    sql_score = Column(Float, default=0.0, nullable=False)  # 40% weight
    data_quality_score = Column(Float, default=0.0, nullable=False)  # 20% weight
    business_score = Column(Float, default=0.0, nullable=False)  # 25% weight
    validation_score = Column(Float, default=0.0, nullable=False)  # 15% weight
    submitted_query = Column(Text, nullable=True)
    submitted_answer = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, default=0, nullable=False)
    evidence_id = Column(Integer, ForeignKey("skill_evidences.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    lab = relationship("IndustryLab", back_populates="attempts")
    user = relationship("User")
    evidence = relationship("SkillEvidence")
