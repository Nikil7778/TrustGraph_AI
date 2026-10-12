from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.skill_debt_service import skill_debt_service
from app.schemas.skill_debt import SkillDebtResponse

router = APIRouter()


@router.get("/users/{user_id}/skill-debt", response_model=List[SkillDebtResponse], tags=["Skill Debt"])
def get_user_skill_debt(
    user_id: int,
    role_id: Optional[int] = Query(None, description="Optional target role ID benchmark override"),
    db: Session = Depends(get_db),
):
    """
    Retrieve deterministic Skill Debt results for all competencies required by the learner's target role.
    Distinguishes between MISSING (0 evidence) and SKILL_DEBT (prior exposure, but currently weak/stale).
    """
    try:
        return skill_debt_service.calculate_skill_debt(db, user_id, role_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )


@router.get("/users/{user_id}/skill-debt/{skill_id}", response_model=SkillDebtResponse, tags=["Skill Debt"])
def get_single_skill_debt(
    user_id: int,
    skill_id: int,
    role_id: Optional[int] = Query(None, description="Optional target role ID benchmark override"),
    db: Session = Depends(get_db),
):
    """
    Retrieve detailed Skill Debt evaluation for a single competency.
    """
    try:
        return skill_debt_service.get_single_skill_debt(db, user_id, skill_id, role_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )


@router.post("/users/{user_id}/skill-debt/recalculate", response_model=List[SkillDebtResponse], tags=["Skill Debt"])
def recalculate_user_skill_debt(
    user_id: int,
    role_id: Optional[int] = Query(None, description="Optional target role ID benchmark override"),
    db: Session = Depends(get_db),
):
    """
    Recalculate Skill Debt for a learner from current source-of-truth evidence and Skill DNA.
    """
    try:
        return skill_debt_service.recalculate_skill_debt(db, user_id, role_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
