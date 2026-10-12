from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.project import Project, ProjectAttempt
from app.schemas.project import ProjectResponse, ProjectAttemptCreate, ProjectAttemptResponse

router = APIRouter()


@router.get("/projects", response_model=List[ProjectResponse], tags=["Projects"])
def list_projects(db: Session = Depends(get_db)):
    """
    Retrieve all real-world portfolio projects.
    """
    projects = db.query(Project).all()
    for p in projects:
        if p.skill:
            p.skill_name = p.skill.name
    return projects


@router.post(
    "/project-attempts",
    response_model=ProjectAttemptResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Projects"],
)
def submit_project_attempt(
    attempt_in: ProjectAttemptCreate, db: Session = Depends(get_db)
):
    """
    Submit real-world portfolio project submission result.
    """
    project = db.query(Project).filter(Project.id == attempt_in.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {attempt_in.project_id} not found.",
        )

    attempt = ProjectAttempt(
        user_id=attempt_in.user_id,
        project_id=attempt_in.project_id,
        score=attempt_in.score,
        completed_at=datetime.utcnow(),
        feedback=attempt_in.feedback,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    attempt.project_title = project.title
    return attempt
