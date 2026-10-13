from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.skill_service import skill_service
from app.schemas.skill import SkillResponse

router = APIRouter()


@router.get("/skills", response_model=List[SkillResponse], tags=["Skills"])
def list_skills(db: Session = Depends(get_db)):
    """
    Retrieve all registered technical competencies across all learning domains.
    """
    return skill_service.get_all_skills(db)


@router.get("/skills/gap-analysis/{user_id}", tags=["Skills"])
def get_user_skill_gap_analysis(
    user_id: int,
    role_id: Optional[int] = Query(None, description="Optional target role ID to evaluate gaps against"),
    db: Session = Depends(get_db),
):
    """
    Analyze skill gaps between learner's current verified Skill DNA and target career goal requirements.
    Identifies Strong, Moderate, Weak, and Missing skills with explicit next recommended actions.
    """
    try:
        return skill_service.get_skill_gap_analysis(db, user_id, role_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate skill gap analysis: {str(err)}",
        )

