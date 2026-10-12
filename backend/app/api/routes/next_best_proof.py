from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.next_best_proof import NextBestProofResponse
from app.services.next_best_proof_service import next_best_proof_service

router = APIRouter(prefix="/users/{user_id}/next-best-proof", tags=["Next-Best-Proof"])


class ProofCompletionPayload(BaseModel):
    skill_id: int = Field(..., gt=0, description="Target skill ID")
    action_type: str = Field(..., min_length=1, max_length=50, description="Proof action type (e.g. PRACTICE, REAL_WORLD_TASK)")
    score: float = Field(..., ge=0.0, le=100.0, description="Achieved score percentage 0-100")
    description: str = Field(..., min_length=1, max_length=1000, description="Verifiable proof description")
    source: Optional[str] = Field(None, max_length=255, description="Evidence source identifier")


@router.get("", response_model=NextBestProofResponse)
def get_user_next_best_proof(
    user_id: int,
    role_id: Optional[int] = Query(None, description="Optional target role ID benchmark"),
    db: Session = Depends(get_db),
):
    """
    Returns the single most valuable next proof action for the learner.
    Determined deterministically from Skill DNA, Skill Debt, Career Value, and Evidence.
    """
    try:
        return next_best_proof_service.get_next_best_proof(db, user_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate next-best-proof: {str(e)}",
        )


@router.get("/candidates", response_model=List[NextBestProofResponse])
def get_user_next_best_proof_candidates(
    user_id: int,
    role_id: Optional[int] = Query(None, description="Optional target role ID benchmark"),
    db: Session = Depends(get_db),
):
    """
    Returns ranked candidate proof actions for all relevant skills of the target role.
    """
    try:
        return next_best_proof_service.get_candidates(db, user_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch next-best-proof candidates: {str(e)}",
        )


@router.post("/recalculate", response_model=NextBestProofResponse)
def recalculate_user_next_best_proof(
    user_id: int,
    role_id: Optional[int] = Query(None, description="Optional target role ID benchmark"),
    db: Session = Depends(get_db),
):
    """
    Recalculates underlying Skill DNA, Skill Debt, and Career Value,
    then returns the freshly selected Next-Best-Proof action.
    """
    try:
        return next_best_proof_service.recalculate_next_best_proof(db, user_id, role_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recalculate next-best-proof: {str(e)}",
        )


@router.post("/complete", response_model=NextBestProofResponse)
def complete_proof_action(
    user_id: int,
    payload: ProofCompletionPayload,
    db: Session = Depends(get_db),
):
    """
    Records completed proof evidence and triggers full recalculation loop
    (Evidence -> DNA -> Debt -> Career Value -> Next-Best-Proof).
    """
    try:
        return next_best_proof_service.complete_proof_action(
            db=db,
            user_id=user_id,
            skill_id=payload.skill_id,
            action_type=payload.action_type,
            score=payload.score,
            description=payload.description,
            source=payload.source,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete proof action: {str(e)}",
        )
