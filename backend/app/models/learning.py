from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearningModule(Base):
    """
    Structured Learning Module / Concept Model (Phase 19).
    Represents an authoritative learning unit containing:
    1. Conceptual Explanation
    2. Worked Example
    3. Guided & Independent Practice Exercises
    4. Formative Concept Check (with passing threshold)
    5. Role-Specific Applied Task
    """
    __tablename__ = "learning_modules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    concept_name = Column(String(200), nullable=False)
    difficulty = Column(String(50), default="Intermediate", nullable=False)  # Beginner, Intermediate, Advanced
    estimated_minutes = Column(Integer, default=25, nullable=False)
    order_index = Column(Integer, default=1, nullable=False)
    prerequisite_concept_slugs = Column(String(255), nullable=True)  # Comma-separated slugs
    target_role_name = Column(String(100), default="All", nullable=False)  # Data Analyst, Data Scientist, ML Engineer, All

    # 1. Explanation
    learning_objectives = Column(Text, nullable=False)  # JSON array of bullet strings
    explanation = Column(Text, nullable=False)  # Rich Markdown teaching text
    key_rules = Column(Text, nullable=True)  # Markdown or JSON rules
    common_mistakes = Column(Text, nullable=True)  # Markdown or JSON common pitfalls

    # 2. Worked Example
    worked_example = Column(Text, nullable=False)  # JSON object {scenario, code, explanation, output}

    # 3. Practice
    guided_practice = Column(Text, nullable=False)  # JSON object {prompt, starter_code, solution, hints: [lvl1, lvl2, lvl3]}
    independent_practice = Column(Text, nullable=False)  # JSON object {prompt, starter_code, solution, test_criteria}

    # 4. Formative Concept Check
    concept_check = Column(Text, nullable=False)  # JSON array of check questions [{question, options, correct, exp}]
    passing_threshold = Column(Float, default=75.0, nullable=False)  # Percentage score required to pass

    # 5. Applied Task
    applied_task = Column(Text, nullable=False)  # JSON object {role_scenario, task_description, starter_code, rubrics}

    # 6. Comprehensive Structural Extensions (Phase 21)
    subtopics = Column(Text, nullable=True)  # JSON array of [{"id": "...", "title": "..."}]
    why_it_matters_by_role = Column(Text, nullable=True)  # JSON dict {"Data Analyst": "...", "Data Scientist": "...", "Python Developer": "..."}
    code_examples = Column(Text, nullable=True)  # JSON array of [{"title": "...", "language": "...", "code": "...", "explanation": "..."}]
    quick_reference = Column(Text, nullable=True)  # JSON dict {"key_terms": [...], "formulas_rules": [...], "takeaways": [...]}
    level_variations = Column(Text, nullable=True)  # JSON dict {"Beginner": {...}, "Advanced": {...}}

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    skill = relationship("Skill")
    user_progress = relationship("UserConceptProgress", back_populates="module", cascade="all, delete-orphan")


class UserConceptProgress(Base):
    """
    Tracks a specific learner's progression and demonstrated mastery
    on a given learning module.
    States:
    LOCKED -> AVAILABLE -> LEARNING -> PRACTICING -> CHECK_PENDING -> DEVELOPING / MASTERED / REMEDIATION
    """
    __tablename__ = "user_concept_progress"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_slug = Column(String(100), index=True, nullable=True)
    status = Column(String(50), default="LOCKED", nullable=False)  # LOCKED, AVAILABLE, LEARNING, PRACTICING, CHECK_PENDING, DEVELOPING, MASTERED, REMEDIATION

    lesson_completed = Column(Boolean, default=False, nullable=False)
    guided_practice_completed = Column(Boolean, default=False, nullable=False)
    independent_practice_completed = Column(Boolean, default=False, nullable=False)
    practice_score = Column(Float, default=0.0, nullable=False)

    concept_check_attempts = Column(Integer, default=0, nullable=False)
    concept_check_score = Column(Float, default=0.0, nullable=False)
    concept_check_passed = Column(Boolean, default=False, nullable=False)

    applied_task_completed = Column(Boolean, default=False, nullable=False)
    applied_task_score = Column(Float, default=0.0, nullable=False)

    last_attempt_at = Column(DateTime, nullable=True)
    mastered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", name="uq_user_module_progress"),
    )

    # Relationships
    user = relationship("User")
    module = relationship("LearningModule", back_populates="user_progress")


class LearningResource(Base):
    """
    Authoritative Verified External Learning Resource Registry (Phase 20).
    Provides structured links to verified external documentation and educational materials
    mapped to specific roles, skills, and concepts.
    Enforces zero-hallucination URL verification.
    """
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)  # e.g., 'Python Official Docs', 'PostgreSQL Docs'
    url = Column(String(500), nullable=False)  # Real, verified URL
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    concept_slug = Column(String(100), nullable=False, index=True)  # e.g., 'python-oop-architecture'
    role_name = Column(String(100), default="All", nullable=False, index=True)  # Data Scientist, Python Developer, Data Analyst, All
    difficulty = Column(String(50), default="Intermediate", nullable=False)  # Beginner, Intermediate, Advanced
    resource_type = Column(String(50), default="Official Documentation", nullable=False)  # Official Documentation, Interactive Tutorial, Reference Guide
    estimated_minutes = Column(Integer, default=20, nullable=False)
    quality_rank = Column(Integer, default=1, nullable=False)  # 1 = Tier 1 (Official), 2 = Tier 2 (Platform)
    description = Column(String(500), nullable=True)
    verified = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    skill = relationship("Skill")

