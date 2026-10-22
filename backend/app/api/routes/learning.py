from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.learning_service import learning_service
from app.schemas.learning import (
    LearningModuleSummary,
    LearningModuleDetail,
    LearningPracticeSubmitRequest,
    LearningPracticeSubmitResponse,
    ConceptCheckSubmitRequest,
    ConceptCheckSubmitResponse,
    AppliedTaskSubmitRequest,
    AppliedTaskSubmitResponse,
)

router = APIRouter(prefix="/learning", tags=["Adaptive Learning Curriculum"])


@router.get("/modules", response_model=List[LearningModuleSummary])
def list_learning_modules(
    user_id: int = Query(..., description="Active learner ID"),
    role_id: Optional[int] = Query(None, description="Optional target role ID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve personalized learning curriculum modules for the active learner.
    Determines real-time unlocking status, prerequisites, and mastery based on Skill DNA.
    """
    return learning_service.get_modules_for_user(db, user_id=user_id, role_id=role_id)


@router.get("/modules/{identifier}", response_model=LearningModuleDetail)
def get_learning_module_detail(
    identifier: str,
    user_id: int = Query(..., description="Active learner ID"),
    level: Optional[str] = Query(None, description="Optional learner level adaptation (Beginner, Intermediate, Advanced)"),
    db: Session = Depends(get_db),
):
    """
    Retrieve full learning module with explanation, worked example, practice, check questions, and applied task.
    STRICT BACKEND ENFORCEMENT: Rejects with HTTP 403 Forbidden if prerequisite concepts are not satisfied.
    Adapts content to target role and specified or calculated learner level.
    """
    return learning_service.get_module_detail(db, user_id=user_id, identifier=identifier, level=level)


@router.post("/modules/{identifier}/practice", response_model=LearningPracticeSubmitResponse)
def submit_practice_exercise(
    identifier: str,
    payload: LearningPracticeSubmitRequest,
    user_id: Optional[int] = Query(None, description="Active learner ID"),
    db: Session = Depends(get_db),
):
    """
    Submit guided or independent practice exercise for adaptive evaluation and instant feedback.
    Generates PRACTICE SkillEvidence upon successful completion (>= 60%).
    """
    eff_user_id = user_id or payload.user_id
    if not eff_user_id:
        raise HTTPException(status_code=400, detail="user_id is required via query param or payload.")
    return learning_service.submit_practice(db, user_id=eff_user_id, identifier=identifier, payload=payload)


@router.post("/modules/{identifier}/check", response_model=ConceptCheckSubmitResponse)
@router.post("/modules/{identifier}/concept-check", response_model=ConceptCheckSubmitResponse)
def submit_concept_check(
    identifier: str,
    payload: ConceptCheckSubmitRequest,
    user_id: Optional[int] = Query(None, description="Active learner ID"),
    db: Session = Depends(get_db),
):
    """
    Submit formative concept check answers.
    Passing (>= 75%) moves concept to MASTERED, generates ASSESSMENT SkillEvidence,
    recalculates Skill DNA, and unblocks downstream prerequisite concepts.
    """
    eff_user_id = user_id or payload.user_id
    if not eff_user_id:
        raise HTTPException(status_code=400, detail="user_id is required via query param or payload.")
    return learning_service.submit_concept_check(db, user_id=eff_user_id, identifier=identifier, payload=payload)


@router.post("/modules/{identifier}/applied", response_model=AppliedTaskSubmitResponse)
@router.post("/modules/{identifier}/applied-task", response_model=AppliedTaskSubmitResponse)
def submit_applied_task(
    identifier: str,
    payload: AppliedTaskSubmitRequest,
    user_id: Optional[int] = Query(None, description="Active learner ID"),
    db: Session = Depends(get_db),
):
    """
    Submit role-specific applied task for verification.
    Generates PRACTICAL_TASK SkillEvidence, updates Skill DNA, and advances roadmap.
    """
    eff_user_id = user_id or getattr(payload, "user_id", None)
    if not eff_user_id:
        raise HTTPException(status_code=400, detail="user_id is required via query param or payload.")
    return learning_service.submit_applied_task(db, user_id=eff_user_id, identifier=identifier, payload=payload)
