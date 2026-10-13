from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.skill import Skill
from app.seed.seed_data import reset_alex_mercer
from app.services.skill_dna_service import skill_dna_service
from app.services.skill_debt_service import skill_debt_service
from app.services.career_value_service import career_value_service
from app.services.next_best_proof_service import next_best_proof_service
from app.services.roadmap_service import roadmap_service
from app.services.skill_passport_service import skill_passport_service

router = APIRouter(prefix="/demo", tags=["Demo & Integration"])


class DemoResetResponse(BaseModel):
    success: bool
    message: str
    user_id: int
    learner_name: str
    target_role: str
    sql_joins_level: float
    sql_joins_debt: str
    sql_joins_severity: str
    next_best_proof_title: str
    career_readiness: float


class DemoPathSnapshotItem(BaseModel):
    skill_name: str
    baseline_level: float
    current_level: float
    baseline_status: str
    current_status: str
    baseline_debt: str
    current_debt: str


class DemoStateResponse(BaseModel):
    user_id: int
    learner_name: str
    target_role: str
    has_completed_proof: bool
    career_readiness_initial: float
    career_readiness_current: float
    sql_joins_snapshot: DemoPathSnapshotItem
    roadmap_version: int
    roadmap_steps_count: int
    next_best_proof_title: str
    unlocked_next_skill: str


@router.post("/reset", response_model=DemoResetResponse)
def reset_demo_learner(
    user_id: Optional[int] = Query(None, description="Optional user ID (defaults to demo learner Alex Mercer)"),
    db: Session = Depends(get_db),
):
    """
    Development-only demo reset endpoint.
    Restores Alex Mercer to predictable initial baseline:
    - SQL JOINs: ~42-55% (Skill Debt: HIGH)
    - Next-Best-Proof: SQL JOINs Rescue Practice
    - Roadmap: Injects SQL JOIN remediation and locks downstream steps
    - Resets all non-seed evidence, lab attempts, and assessment attempts
    """
    if getattr(settings, "ENVIRONMENT", "").lower() == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development-only demo reset is disabled in production.",
        )

    alex = db.query(User).filter(User.email == "alex.mercer@example.com").first()
    if not alex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo learner Alex Mercer not found in database.",
        )

    # 1. Restore database baseline
    reset_alex_mercer(db)

    # 2. Run deterministic recalculation cascade to sync all engines
    roadmap_service.refresh_learning_state(db, alex.id)

    # 3. Pull post-reset metrics
    sql_join = db.query(Skill).filter(Skill.name == "SQL JOINs").first()
    dna = skill_dna_service.get_single_skill_dna(db, alex.id, sql_join.id if sql_join else 3)
    debt = skill_debt_service.get_single_skill_debt(db, alex.id, sql_join.id if sql_join else 3)
    nbp = next_best_proof_service.get_next_best_proof(db, alex.id)
    passport = skill_passport_service.get_skill_passport(db, alex.id)

    return DemoResetResponse(
        success=True,
        message="Demo learner Alex Mercer successfully restored to initial baseline state.",
        user_id=alex.id,
        learner_name=alex.name,
        target_role=alex.target_role.name if alex.target_role else "Data Analyst",
        sql_joins_level=round(dna["skill_level"], 1),
        sql_joins_debt=debt["debt_status"],
        sql_joins_severity=debt["severity"],
        next_best_proof_title=nbp["title"],
        career_readiness=passport.header.career_readiness,
    )


@router.get("/state", response_model=DemoStateResponse)
def get_demo_state(
    user_id: Optional[int] = Query(None, description="User ID (defaults to demo learner Alex Mercer)"),
    db: Session = Depends(get_db),
):
    """
    Returns live comparative state for the 'How your path changed' demo component.
    Tracks progression from initial baseline to current live state.
    """
    target_id = user_id or 1
    user = db.query(User).filter(User.id == target_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID {target_id} not found.",
        )

    sql_join = db.query(Skill).filter(Skill.name == "SQL JOINs").first()
    join_id = sql_join.id if sql_join else 3

    dna = skill_dna_service.get_single_skill_dna(db, user.id, join_id)
    debt = skill_debt_service.get_single_skill_debt(db, user.id, join_id)
    nbp = next_best_proof_service.get_next_best_proof(db, user.id)
    roadmap = roadmap_service.get_user_roadmap(db, user.id)
    passport = skill_passport_service.get_skill_passport(db, user.id)

    curr_level = dna["skill_level"]
    is_improved = curr_level >= 75.0 or debt["debt_status"] != "SKILL_DEBT"

    # Identify currently unlocked recommended step in dynamic roadmap
    unlocked_skill = "EDA"
    if roadmap:
        rec_step = next((s for s in roadmap.steps if s.status == "RECOMMENDED"), None)
        if rec_step and rec_step.skill:
            unlocked_skill = rec_step.skill.name

    return DemoStateResponse(
        user_id=user.id,
        learner_name=user.name,
        target_role=user.target_role.name if user.target_role else "Data Analyst",
        has_completed_proof=is_improved,
        career_readiness_initial=87.5,
        career_readiness_current=passport.header.career_readiness,
        sql_joins_snapshot=DemoPathSnapshotItem(
            skill_name="SQL JOINs",
            baseline_level=55.0,
            current_level=round(curr_level, 1),
            baseline_status="DEVELOPING",
            current_status=dna["status"],
            baseline_debt="SKILL_DEBT",
            current_debt=debt["debt_status"],
        ),
        roadmap_version=roadmap.version if roadmap else 1,
        roadmap_steps_count=len(roadmap.steps) if roadmap else 0,
        next_best_proof_title=nbp["title"],
        unlocked_next_skill=unlocked_skill,
    )
