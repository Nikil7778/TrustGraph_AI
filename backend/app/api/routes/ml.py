"""
Machine Learning API Router for SkillPath AI.
Exposes advisory mastery prediction endpoints and public model metadata.
CRITICAL RULE:
ML PREDICTS. DETERMINISTIC ENGINES DECIDE. GEMINI EXPLAINS.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.ml_service import predict_skill_mastery, get_model_info
from ml.schemas import MLPredictionRequest, MLPredictionResponse

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.post("/predict-mastery", response_model=MLPredictionResponse)
def predict_mastery_endpoint(
    request: MLPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    POST /api/ml/predict-mastery
    Predicts the likelihood of the learner successfully demonstrating the specified skill
    in their next proof attempt. Advisory only.
    Features are strictly extracted from authoritative database state (anti-leakage).
    """
    try:
        return predict_skill_mastery(
            db=db,
            user_id=request.user_id,
            skill_id=request.skill_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.get("/predict-mastery/{user_id}/{skill_id}", response_model=MLPredictionResponse)
def get_predict_mastery_endpoint(
    user_id: int,
    skill_id: int,
    db: Session = Depends(get_db)
):
    """
    GET /api/ml/predict-mastery/{user_id}/{skill_id}
    Convenience endpoint for UI queries.
    """
    try:
        return predict_skill_mastery(
            db=db,
            user_id=user_id,
            skill_id=skill_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.get("/model-info", response_model=Dict[str, Any])
def model_info_endpoint():
    """
    GET /api/ml/model-info
    Returns model metadata, performance on unseen test split, and feature signals.
    Never exposes internal filesystem paths or secrets.
    """
    try:
        return get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve model info: {str(e)}")
