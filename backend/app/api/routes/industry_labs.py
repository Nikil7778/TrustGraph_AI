from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.industry_lab_service import industry_lab_service
from app.schemas.industry_lab import (
    IndustryLabResponse,
    IndustryLabQueryRunRequest,
    IndustryLabQueryRunResponse,
    IndustryLabSubmitRequest,
    IndustryLabSubmitResponse,
    IndustryLabAttemptResponse,
    IndustryLabTablePreview,
)

router = APIRouter(prefix="/industry-labs", tags=["Industry Labs"])


@router.get("", response_model=List[IndustryLabResponse])
@router.get("/", response_model=List[IndustryLabResponse])
def get_industry_labs(
    role_id: Optional[int] = Query(None, description="Filter by target role ID"),
    skill_id: Optional[int] = Query(None, description="Filter by primary skill ID"),
    db: Session = Depends(get_db),
):
    """
    List all available industry practical labs with optional role and skill filtering.
    """
    labs = industry_lab_service.get_labs(db, role_id=role_id, skill_id=skill_id)
    result = []
    for lab in labs:
        res = IndustryLabResponse(
            id=lab.id,
            slug=lab.slug,
            title=lab.title,
            description=lab.description,
            target_role_id=lab.target_role_id,
            target_role_name=lab.target_role.name if lab.target_role else None,
            primary_skill_id=lab.primary_skill_id,
            primary_skill_name=lab.primary_skill.name if lab.primary_skill else None,
            difficulty=lab.difficulty,
            estimated_minutes=lab.estimated_minutes,
            business_context=lab.business_context,
            datasets_info=lab.datasets_info,
            created_at=lab.created_at,
            tasks=[t for t in lab.tasks],
        )
        result.append(res)
    return result


@router.get("/{id_or_slug}", response_model=IndustryLabResponse)
def get_industry_lab(
    id_or_slug: str,
    db: Session = Depends(get_db),
):
    """
    Fetch comprehensive details, business context, and tasks for a specific industry lab.
    """
    lab = industry_lab_service.get_lab(db, id_or_slug)
    return IndustryLabResponse(
        id=lab.id,
        slug=lab.slug,
        title=lab.title,
        description=lab.description,
        target_role_id=lab.target_role_id,
        target_role_name=lab.target_role.name if lab.target_role else None,
        primary_skill_id=lab.primary_skill_id,
        primary_skill_name=lab.primary_skill.name if lab.primary_skill else None,
        difficulty=lab.difficulty,
        estimated_minutes=lab.estimated_minutes,
        business_context=lab.business_context,
        datasets_info=lab.datasets_info,
        created_at=lab.created_at,
        tasks=[t for t in lab.tasks],
    )


@router.get("/{id_or_slug}/preview", response_model=List[IndustryLabTablePreview])
def get_industry_lab_preview(
    id_or_slug: str,
    db: Session = Depends(get_db),
):
    """
    Fetch schema definitions, sample records, and data quality alerts for lab datasets.
    """
    return industry_lab_service.get_lab_preview(db, id_or_slug)


@router.post("/{id_or_slug}/run", response_model=IndustryLabQueryRunResponse)
def run_industry_lab_query(
    id_or_slug: str,
    payload: IndustryLabQueryRunRequest,
    db: Session = Depends(get_db),
):
    """
    Safely execute a learner's SQL query in the sandbox SQLite database.
    """
    return industry_lab_service.run_query(db, id_or_slug, payload.query)


@router.post("/{id_or_slug}/submit", response_model=IndustryLabSubmitResponse)
def submit_industry_lab_attempt(
    id_or_slug: str,
    payload: IndustryLabSubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a lab query for 4-pillar automated evaluation, record attempt, and update Skill DNA.
    """
    return industry_lab_service.submit_attempt(
        db,
        identifier=id_or_slug,
        user_id=payload.user_id,
        query=payload.query,
        submitted_answer=payload.submitted_answer,
        evidence_type=payload.evidence_type or "PRACTICE",
    )


@router.get("/{id_or_slug}/attempts", response_model=List[IndustryLabAttemptResponse])
def get_industry_lab_attempts(
    id_or_slug: str,
    user_id: int = Query(..., description="ID of the learner"),
    db: Session = Depends(get_db),
):
    """
    Retrieve learner submission history and scores for a specific industry lab.
    """
    attempts = industry_lab_service.get_user_attempts(db, id_or_slug, user_id=user_id)
    return [
        IndustryLabAttemptResponse(
            id=a.id,
            lab_id=a.lab_id,
            user_id=a.user_id,
            attempt_number=a.attempt_number,
            status=a.status,
            total_score=a.total_score,
            sql_score=a.sql_score,
            data_quality_score=a.data_quality_score,
            business_score=a.business_score,
            validation_score=a.validation_score,
            submitted_query=a.submitted_query,
            feedback=a.feedback,
            execution_time_ms=a.execution_time_ms,
            created_at=a.created_at,
        )
        for a in attempts
    ]
