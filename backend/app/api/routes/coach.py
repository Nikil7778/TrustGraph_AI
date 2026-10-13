from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user_optional
from app.services.coach_service import coach_service
from app.schemas.coach import (
    CoachChatRequest,
    CoachChatResponse,
)

router = APIRouter(prefix="/coach", tags=["AI Career Coach"])


@router.post("/chat", response_model=CoachChatResponse)
def coach_chat(
    payload: CoachChatRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Interact with the System-Aware SkillPath AI Career Coach.
    Answers natural language inquiries regarding the learner's actual current state
    (DNA, Debt, Career Value, Next-Best-Proof, Roadmap, Evidence, Passport)
    via Gemini function calling or high-yield deterministic fallback.
    Automatically resolves the authenticated learner.
    """
    current_user = get_current_user_optional(request, db)
    if current_user:
        payload.user_id = current_user.id
    try:
        return coach_service.chat(db, payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Career Coach conversation failed: {str(e)}",
        )


@router.get("/suggested-prompts", response_model=List[str])
def get_suggested_prompts():
    """
    Returns standard quick starter prompts for the career coach.
    """
    return [
        "What should I do next?",
        "What is my predicted readiness for SQL JOINs?",
        "Why is SQL JOINs my priority?",
        "What are my weakest skills?",
        "How close am I to being ready for Data Analyst?",
        "Why did my roadmap change?",
        "Give me a SQL JOIN practice question.",
        "What evidence do I have for SQL?",
    ]
