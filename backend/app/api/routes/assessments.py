from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.assessment_service import assessment_service
from app.schemas.assessment import (
    AssessmentResponse,
    AssessmentDetailResponse,
    AssessmentSubmissionCreate,
    AssessmentAttemptCreate,
    AssessmentAttemptResponse,
    AssessmentResultResponse,
    GoalAssessmentSubmission,
    GoalAssessmentResultResponse,
)


router = APIRouter()


@router.get("/assessments", response_model=List[AssessmentResponse], tags=["Assessments"])
def list_assessments(db: Session = Depends(get_db)):
    """
    Retrieve all diagnostic technical assessments.
    """
    assessments = assessment_service.get_all_assessments(db)
    for a in assessments:
        if a.skill:
            a.skill_name = a.skill.name
        a.question_count = len(a.questions)
    return assessments


@router.get("/assessments/{assessment_id}", response_model=AssessmentDetailResponse, tags=["Assessments"])
def get_assessment_detail(assessment_id: int, db: Session = Depends(get_db)):
    """
    Retrieve assessment details with public question set (sanitized without correct answers or explanations).
    """
    assessment = assessment_service.get_assessment_by_id(db, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment with ID {assessment_id} not found.",
        )
    if assessment.skill:
        assessment.skill_name = assessment.skill.name
    assessment.question_count = len(assessment.questions)
    return assessment


@router.post(
    "/assessment-attempts",
    status_code=status.HTTP_201_CREATED,
    tags=["Assessments"],
)
def submit_assessment_attempt(
    payload: Union[AssessmentSubmissionCreate, AssessmentAttemptCreate],
    db: Session = Depends(get_db),
):
    """
    Submit diagnostic assessment attempt result and update demonstrated Skill DNA.
    """
    if isinstance(payload, AssessmentSubmissionCreate):
        try:
            result = assessment_service.submit_assessment(db, payload)
            return result
        except ValueError as val_err:
            msg = str(val_err)
            if "not found" in msg.lower():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    else:
        assessment = assessment_service.get_assessment_by_id(db, payload.assessment_id)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment with ID {payload.assessment_id} not found.",
            )
        attempt = assessment_service.create_assessment_attempt(db, payload)
        skill_name = assessment.skill.name if assessment.skill else "Skill"
        return {
            "id": attempt.id,
            "user_id": attempt.user_id,
            "assessment_id": attempt.assessment_id,
            "assessment_title": assessment.title,
            "skill_name": skill_name,
            "score": attempt.score,
            "accuracy": attempt.accuracy,
            "completed_at": attempt.completed_at,
        }


@router.get("/assessments/goal/{role_id}", response_model=AssessmentDetailResponse, tags=["Assessments"])
def get_goal_assessment(role_id: int, db: Session = Depends(get_db)):
    """
    Retrieve or initialize the diagnostic assessment for a career target goal.
    Returns 10-25 questions sanitized without correct answers or explanations before submission.
    """
    try:
        assessment = assessment_service.get_or_create_goal_assessment(db, role_id)
        if assessment.skill:
            assessment.skill_name = assessment.skill.name
        assessment.question_count = len(assessment.questions)
        for q in assessment.questions:
            if q.skill:
                q.skill_name = q.skill.name
        return assessment
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )


@router.post(
    "/assessments/goal/submit",
    response_model=GoalAssessmentResultResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Assessments"],
)
def submit_goal_assessment(payload: GoalAssessmentSubmission, db: Session = Depends(get_db)):
    """
    Submit initial diagnostic assessment for a target goal.
    Calculates granular skill-level scores across all competencies, generates Skill DNA evidence,
    computes skill gaps (Strong, Moderate, Weak, Missing), and provides the next recommended action.
    """
    try:
        return assessment_service.submit_goal_assessment(db, payload)
    except ValueError as val_err:
        msg = str(val_err)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process goal assessment submission: {str(err)}",
        )

