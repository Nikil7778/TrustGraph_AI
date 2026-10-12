from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.ai_service import ai_service
from app.schemas.ai import (
    AIExplainDecisionRequest,
    AIExplainDecisionResponse,
    AIHintRequest,
    AIHintResponse,
    AIExplainMistakeRequest,
    AIExplainMistakeResponse,
    AILearningExplanationRequest,
    AILearningExplanationResponse,
    AIPracticeQuestionsRequest,
    AIPracticeQuestionsResponse,
    AIInterviewQuestionsRequest,
    AIInterviewQuestionsResponse,
    AIStudyGuidanceRequest,
    AIStudyGuidanceResponse,
)

router = APIRouter(prefix="/ai", tags=["AI Layer (Gemini)"])


@router.post("/explain", response_model=AIExplainDecisionResponse)
def explain_decision(payload: AIExplainDecisionRequest):
    """
    Generate natural language Learning Coach explanation for a deterministic engine decision:
    Next-Best-Proof, Skill Debt, Career Value, or Roadmap changes.
    """
    return ai_service.generate_explanation(payload)


@router.post("/hint", response_model=AIHintResponse)
def get_hint(payload: AIHintRequest):
    """
    Generate progressive, contextual hints (Levels 1 to 3) for a learning or sandbox task.
    """
    return ai_service.generate_hint(payload)


@router.post("/explain-mistake", response_model=AIExplainMistakeResponse)
def explain_mistake(payload: AIExplainMistakeRequest):
    """
    Explain a learner's mistake following an assessment or lab failure, highlighting
    what went wrong, why it occurred, and how to identify it next time.
    """
    return ai_service.explain_mistake(payload)


@router.post("/learning-explanation", response_model=AILearningExplanationResponse)
def explain_learning_concept(payload: AILearningExplanationRequest):
    """
    Generate a concise concept explanation, example snippet, common pitfall,
    role use case, and check question.
    """
    return ai_service.generate_learning_explanation(payload)


@router.post("/practice-questions", response_model=AIPracticeQuestionsResponse)
def generate_practice_questions(payload: AIPracticeQuestionsRequest):
    """
    Generate unscored practice questions for formative learning.
    Does NOT affect deterministic Skill DNA scores.
    """
    return ai_service.generate_practice_questions(payload)


@router.post("/interview-questions", response_model=AIInterviewQuestionsResponse)
def generate_interview_questions(payload: AIInterviewQuestionsRequest):
    """
    Generate role-specific interview preparation questions spanning Conceptual,
    Practical Query/Code, Debugging, and Business Scenario categories.
    """
    return ai_service.generate_interview_questions(payload)


@router.post("/study-guidance", response_model=AIStudyGuidanceResponse)
def get_study_guidance(payload: AIStudyGuidanceRequest, db: Session = Depends(get_db)):
    """
    Generate structured, actionable weekly study guidance derived from
    deterministic roadmap milestones, skill debts, and learner weekly availability.
    """
    return ai_service.generate_study_guidance(payload.user_id, db)
