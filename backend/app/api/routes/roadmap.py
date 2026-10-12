from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.roadmap_service import roadmap_service
from app.services.user_service import user_service
from app.schemas.roadmap import (
    RoadmapResponse,
    RoadmapHistoryResponse,
    RoadmapChangeResponse,
)

router = APIRouter()


@router.get("/users/{user_id}/roadmap", response_model=RoadmapResponse, tags=["Roadmap"])
def get_user_roadmap(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve learner's active evidence-driven learning roadmap.
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    roadmap = roadmap_service.get_user_roadmap(db, user_id)
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active roadmap for user ID {user_id} not found.",
        )

    if roadmap.target_role:
        roadmap.target_role_name = roadmap.target_role.name
    for step in roadmap.steps:
        if step.skill:
            step.skill_name = step.skill.name

    return roadmap


@router.post("/users/{user_id}/roadmap/rebuild", response_model=RoadmapResponse, tags=["Roadmap"])
def rebuild_user_roadmap(user_id: int, db: Session = Depends(get_db)):
    """
    Dynamically rebuild and re-sequence the learner's roadmap matching their latest demonstrated proof.
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    roadmap = roadmap_service.rebuild_user_roadmap(db, user_id)
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not rebuild roadmap for user ID {user_id}.",
        )

    if roadmap.target_role:
        roadmap.target_role_name = roadmap.target_role.name
    for step in roadmap.steps:
        if step.skill:
            step.skill_name = step.skill.name

    return roadmap


@router.get(
    "/users/{user_id}/roadmap/history",
    response_model=List[RoadmapHistoryResponse],
    tags=["Roadmap"],
)
def get_roadmap_history(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve previous roadmap revisions and regeneration reasons.
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    return roadmap_service.get_roadmap_history(db, user_id)


@router.get(
    "/users/{user_id}/roadmap/changes",
    response_model=List[RoadmapChangeResponse],
    tags=["Roadmap"],
)
def get_roadmap_changes(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve recent deterministic roadmap changes and explanations.
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    return roadmap_service.get_roadmap_changes(db, user_id)
