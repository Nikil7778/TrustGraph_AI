from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.dashboard_service import dashboard_service
from app.schemas.dashboard import DashboardResponse

router = APIRouter()


@router.get("/dashboard/{user_id}", response_model=DashboardResponse, tags=["Dashboard"])
def get_learner_dashboard(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve unified, deterministic daily workspace payload for learner.
    Aggregates Career Readiness, Next-Best-Proof, Skill Gap Heatmap, Skill DNA,
    Dynamic Roadmap, and Recent Evidence.
    """
    try:
        return dashboard_service.get_dashboard_data(db, user_id)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate learner dashboard: {str(err)}",
        )
