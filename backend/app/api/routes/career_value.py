from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.career_value import CareerValueResponse
from app.services.career_value_service import career_value_service

router = APIRouter(prefix="/users/{user_id}/career-value", tags=["Career Value"])


@router.get("", response_model=List[CareerValueResponse])
def get_user_career_value(
    user_id: int,
    role_id: Optional[int] = Query(None, description="Optional target role ID benchmark"),
    db: Session = Depends(get_db),
):
    """
    Returns deterministic, ranked Career Value results for the learner's target role.
    Ranked by career value priority, role importance, and skill gap.
    """
    try:
        return career_value_service.calculate_career_value(db, user_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate career value: {str(e)}",
        )


@router.get("/{skill_id}", response_model=CareerValueResponse)
def get_user_single_skill_career_value(
    user_id: int,
    skill_id: int,
    role_id: Optional[int] = Query(None, description="Optional target role ID benchmark"),
    db: Session = Depends(get_db),
):
    """
    Returns detailed Career Value analysis for a single skill.
    """
    try:
        return career_value_service.get_single_career_value(db, user_id, skill_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch career value for skill {skill_id}: {str(e)}",
        )


@router.post("/recalculate", response_model=List[CareerValueResponse])
def recalculate_user_career_value(
    user_id: int,
    role_id: Optional[int] = Query(None, description="Optional target role ID benchmark"),
    db: Session = Depends(get_db),
):
    """
    Recalculates Career Value priorities by refreshing Skill DNA and Skill Debt from raw evidence.
    """
    try:
        return career_value_service.recalculate_career_value(db, user_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recalculate career value: {str(e)}",
        )
