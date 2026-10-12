from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.skill_dna_service import skill_dna_service
from app.schemas.skill_dna import SkillDNAResponse

router = APIRouter()


@router.get("/users/{user_id}/skill-dna", response_model=List[SkillDNAResponse], tags=["Skill DNA"])
def get_user_skill_dna(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve multidimensional Skill DNA profile vectors for all learner competencies.
    """
    try:
        return skill_dna_service.get_user_skill_dna(db, user_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )


@router.get("/users/{user_id}/skills/{skill_id}/skill-dna", response_model=SkillDNAResponse, tags=["Skill DNA"])
def get_single_skill_dna(user_id: int, skill_id: int, db: Session = Depends(get_db)):
    """
    Retrieve multidimensional Skill DNA profile vector for a specific learner competency.
    """
    try:
        return skill_dna_service.get_single_skill_dna(db, user_id, skill_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )


@router.post("/users/{user_id}/skill-dna/recalculate", response_model=List[SkillDNAResponse], tags=["Skill DNA"])
def recalculate_user_skill_dna(user_id: int, db: Session = Depends(get_db)):
    """
    Trigger a full deterministic recalculation of all Skill DNA vector scores for a learner.
    """
    try:
        return skill_dna_service.recalculate_all_user_skill_dna(db, user_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
