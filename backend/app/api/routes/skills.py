from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.skill_service import skill_service
from app.schemas.skill import SkillResponse

router = APIRouter()


@router.get("/skills", response_model=List[SkillResponse], tags=["Skills"])
def list_skills(db: Session = Depends(get_db)):
    """
    Retrieve all registered technical competencies across Data Science domains.
    """
    return skill_service.get_all_skills(db)
