from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
import json


class AssessmentQuestionPublicResponse(BaseModel):
    """
    Public question schema for taking an assessment.
    Sanitized to NEVER expose correct_answer or explanation before submission.
    """
    id: int
    assessment_id: int
    question_text: str
    options: List[str]
    difficulty: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("options", mode="before")
    @classmethod
    def parse_options_json(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [v]
        return v


class AssessmentQuestionDetailResponse(AssessmentQuestionPublicResponse):
    """
    Detailed question schema for post-submission review.
    Exposes correct_answer and explanation.
    """
    correct_answer: str
    explanation: Optional[str] = None


class AssessmentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    skill_id: int
    skill_name: Optional[str] = None
    difficulty: str
    question_count: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssessmentDetailResponse(AssessmentResponse):
    questions: List[AssessmentQuestionPublicResponse] = []


class SingleQuestionAnswer(BaseModel):
    question_id: int = Field(..., gt=0, description="Assessment question ID")
    answer: str = Field(..., min_length=1, max_length=1000, description="Submitted answer option or text")


class AssessmentSubmissionCreate(BaseModel):
    user_id: int = Field(..., gt=0, description="Learner user ID")
    assessment_id: int = Field(..., gt=0, description="Target assessment ID")
    answers: List[SingleQuestionAnswer] = Field(..., min_length=1, max_length=100, description="List of submitted answers")


class AssessmentAttemptCreate(BaseModel):
    user_id: int
    assessment_id: int
    score: float
    accuracy: float


class QuestionReviewResult(BaseModel):
    question_id: int
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = None


class AssessmentResultResponse(BaseModel):
    attempt_id: int
    user_id: int
    assessment_id: int
    assessment_title: str
    skill_name: str
    raw_score: int
    total_questions: int
    percentage: float
    accuracy: float
    difficulty: str
    completed_at: datetime
    interpretation: str  # Strong, Healthy, Developing, Critical Gap
    question_breakdown: List[QuestionReviewResult] = []


class AssessmentAttemptResponse(BaseModel):
    id: int
    user_id: int
    assessment_id: int
    assessment_title: Optional[str] = None
    skill_name: Optional[str] = None
    score: float
    accuracy: float
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)

