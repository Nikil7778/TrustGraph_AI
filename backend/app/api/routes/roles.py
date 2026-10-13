from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.skill_service import skill_service
from app.schemas.role import RoleResponse, RoleSkillMapResponse, CustomRoleCreate

router = APIRouter()


@router.get("/roles", response_model=List[RoleResponse], tags=["Roles"])
def list_roles(db: Session = Depends(get_db)):
    """
    Retrieve all registered career target goals with benchmark skills.
    """
    roles = skill_service.get_all_roles(db)
    # Populate skill_name in role_skills for response payload
    for r in roles:
        for rs in r.role_skills:
            if rs.skill:
                rs.skill_name = rs.skill.name
    return roles


@router.get("/roles/{role_id}/skill-map", response_model=RoleSkillMapResponse, tags=["Roles"])
def get_role_skill_map(role_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the categorized, structured skill map for a target goal.
    """
    skill_map = skill_service.get_role_skill_map(db, role_id)
    if not skill_map:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target goal with ID {role_id} not found.",
        )
    return skill_map


@router.post("/roles/custom", response_model=RoleResponse, status_code=status.HTTP_201_CREATED, tags=["Roles"])
def create_custom_role(payload: CustomRoleCreate, db: Session = Depends(get_db)):
    """
    Allow users to create a custom goal with required skill competencies stored in the database.
    """
    if not payload.name or not payload.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Custom goal name cannot be empty.",
        )
    role = skill_service.create_custom_role(
        db,
        name=payload.name.strip(),
        description=payload.description,
        skill_names=payload.skills,
    )
    for rs in role.role_skills:
        if rs.skill:
            rs.skill_name = rs.skill.name
    return role

