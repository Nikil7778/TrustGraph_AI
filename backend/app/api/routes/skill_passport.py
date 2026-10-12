from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.skill_passport_service import skill_passport_service
from app.schemas.skill_passport import (
    SkillPassportResponse,
    SkillProofMatrixItem,
    EvidenceTimelineItem,
    PassportSummary,
)

router = APIRouter()


@router.get("/users/{user_id}/skill-passport", response_model=SkillPassportResponse, tags=["Skill Passport"])
def get_user_skill_passport(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve comprehensive, evidence-backed Proof-of-Skill Passport for learner.
    Connects demonstrated competencies to underlying evidence artifacts.
    """
    try:
        return skill_passport_service.get_skill_passport(db, user_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load Skill Passport: {str(err)}",
        )


@router.get("/users/{user_id}/skill-passport/summary", response_model=PassportSummary, tags=["Skill Passport"])
def get_passport_summary(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve high-level credential summary of verified and developing skills.
    """
    try:
        passport = skill_passport_service.get_skill_passport(db, user_id)
        return passport.summary
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )


@router.get("/users/{user_id}/skill-passport/evidence", response_model=List[EvidenceTimelineItem], tags=["Skill Passport"])
def get_passport_evidence_timeline(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve chronological evidentiary timeline for learner.
    """
    try:
        passport = skill_passport_service.get_skill_passport(db, user_id)
        return passport.evidence_timeline
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )


@router.get("/users/{user_id}/skill-passport/{skill_id}", response_model=SkillProofMatrixItem, tags=["Skill Passport"])
def get_passport_skill_detail(user_id: int, skill_id: int, db: Session = Depends(get_db)):
    """
    Retrieve individual skill credential detail and supporting evidence items.
    """
    try:
        return skill_passport_service.get_skill_detail(db, user_id, skill_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
