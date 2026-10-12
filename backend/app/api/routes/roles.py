from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.skill_service import skill_service
from app.schemas.role import RoleResponse

router = APIRouter()


@router.get("/roles", response_model=List[RoleResponse], tags=["Roles"])
def list_roles(db: Session = Depends(get_db)):
    """
    Retrieve target career roles (Data Analyst, Data Scientist, ML Engineer) with skill benchmark weights.
    """
    roles = skill_service.get_all_roles(db)
    # Populate skill_name in role_skills for response payload
    for r in roles:
        for rs in r.role_skills:
            if rs.skill:
                rs.skill_name = rs.skill.name
    return roles
