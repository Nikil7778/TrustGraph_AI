from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MLFeatureVector(BaseModel):
    """
    Validated feature vector representing learner state strictly BEFORE the next attempt.
    All features pass the anti-leakage test: known immediately prior to prediction timestamp.
    """
    # Behavioral Features
    previous_attempts: int = Field(ge=0, description="Total prior attempts on this skill")
    total_attempts: int = Field(ge=0, description="Total prior attempts across all skills")
    previous_accuracy: float = Field(ge=0.0, le=100.0, description="Accuracy on immediately preceding attempt on this skill")
    recent_accuracy: float = Field(ge=0.0, le=100.0, description="Rolling average accuracy of up to 3 recent attempts")
    rolling_accuracy: float = Field(ge=0.0, le=100.0, description="Cumulative accuracy on this skill up to this point")
    correct_streak: int = Field(ge=0, description="Consecutive successful attempts on this skill prior to this attempt")
    incorrect_streak: int = Field(ge=0, description="Consecutive unsuccessful attempts on this skill prior to this attempt")
    average_response_time: float = Field(ge=0.0, description="Average response time in minutes across prior attempts")
    recent_response_time: float = Field(ge=0.0, description="Response time in minutes on most recent prior attempt")
    days_since_previous_attempt: float = Field(ge=0.0, description="Calendar days since prior attempt on this skill")

    # Difficulty Features
    average_difficulty_exposure: float = Field(ge=0.0, le=100.0, description="Mean difficulty score of prior attempts (35-90)")
    recent_difficulty: float = Field(ge=0.0, le=100.0, description="Difficulty of most recent prior attempt")
    hard_question_exposure: int = Field(ge=0, description="Count of hard difficulty tasks attempted")
    medium_question_exposure: int = Field(ge=0, description="Count of medium difficulty tasks attempted")
    easy_question_exposure: int = Field(ge=0, description="Count of easy difficulty tasks attempted")

    # Evidence Features
    assessment_evidence_count: int = Field(ge=0, description="Number of prior assessment evidence artifacts")
    practice_evidence_count: int = Field(ge=0, description="Number of prior practice evidence artifacts")
    project_evidence_count: int = Field(ge=0, description="Number of prior project evidence artifacts")
    practical_evidence_count: int = Field(ge=0, description="Total practical/applied evidence artifacts")
    days_since_last_evidence: float = Field(ge=0.0, description="Calendar days since last evidence was logged")
    evidence_recency: float = Field(ge=0.0, le=100.0, description="Exponential recency decay score (0-100)")

    # Skill Features
    current_skill_level: float = Field(ge=0.0, le=100.0, description="Prior demonstrated skill level (0-100)")
    current_confidence: float = Field(ge=0.0, le=100.0, description="Prior deterministic confidence score (0-100)")
    current_accuracy: float = Field(ge=0.0, le=100.0, description="Prior accuracy score (0-100)")
    current_evidence_score: float = Field(ge=0.0, le=100.0, description="Prior evidence score (0-100)")
    current_practical_evidence: int = Field(ge=0, le=1, description="Binary flag indicating prior practical proof exists (0 or 1)")

    # Career Context
    role_skill_importance: float = Field(ge=0.0, le=100.0, description="Skill importance score for target role (0-100)")
    role_requirement_level: float = Field(ge=0.0, le=100.0, description="Target role required skill proficiency (0-100)")


class MLPredictionRequest(BaseModel):
    user_id: int = Field(..., ge=1, description="Learner ID")
    skill_id: int = Field(..., ge=1, description="Skill ID")


class MLTopSignal(BaseModel):
    feature: str
    importance: float
    description: str
    learner_value: Optional[float] = None


class MLPredictionResponse(BaseModel):
    skill_id: int
    skill_name: str
    mastery_probability: float = Field(ge=0.0, le=1.0, description="Predicted likelihood of success on next proof attempt")
    risk_level: str = Field(..., description="Advisory risk classification: LOW (>=0.70), MEDIUM (0.40-0.69), HIGH (<0.40)")
    model_version: str
    prediction_timestamp: datetime
    feature_schema_version: str
    top_signals: List[MLTopSignal] = []
    advisory_explanation: str
    is_advisory: bool = True
