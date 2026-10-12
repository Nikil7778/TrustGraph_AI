from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import user_service
from app.services.evidence_service import evidence_service
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UserSkillResponse
from app.schemas.evidence import SkillEvidenceResponse
from app.schemas.assessment import AssessmentAttemptResponse

router = APIRouter()


@router.get("/users", response_model=List[UserResponse], tags=["Users"])
def list_users(db: Session = Depends(get_db)):
    """
    List all registered learners.
    """
    return user_service.get_all_users(db)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new learner profile and initialize baseline Skill DNA records.
    """
    existing = user_service.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )
    try:
        return user_service.create_user(db, user_in)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve learner profile by ID.
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return user


@router.patch("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    """
    Update learner profile attributes (e.g., target role, learning hours, experience level).
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    try:
        updated = user_service.update_user(db, user_id, user_in)
        return updated
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )


@router.get("/users/{user_id}/skills", response_model=List[UserSkillResponse], tags=["Users"])
def get_user_skills(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve learner's demonstrated Skill DNA vector scores.
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    user_skills = user_service.get_user_skills(db, user_id)
    for us in user_skills:
        if us.skill:
            us.skill_name = us.skill.name
            us.skill_category = us.skill.category
    return user_skills


@router.get("/users/{user_id}/evidence", response_model=List[SkillEvidenceResponse], tags=["Users"])
def get_user_evidence(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve audit trail of verified skill evidence artifacts for learner.
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    evidences = evidence_service.get_user_evidences(db, user_id)
    for ev in evidences:
        if ev.skill:
            ev.skill_name = ev.skill.name
    return evidences


@router.get("/users/{user_id}/assessment-attempts", response_model=List[AssessmentAttemptResponse], tags=["Users"])
def get_user_assessment_attempts(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve learner's previous assessment attempts.
    """
    from app.services.assessment_service import assessment_service
    try:
        return assessment_service.get_user_assessment_attempts(db, user_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )

