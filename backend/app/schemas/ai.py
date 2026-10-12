from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# 1. Decision Explanation Schemas
class AIExplainDecisionRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="Learner user ID")
    target_role: Optional[str] = Field("Data Analyst", max_length=100)
    skill_name: str = Field(..., min_length=1, max_length=100)
    context_type: str = Field(
        ...,
        max_length=50,
        description="Type of context: NEXT_BEST_PROOF, SKILL_DEBT, CAREER_VALUE, ROADMAP_CHANGE",
    )
    structured_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Deterministic metrics and decision payload from the backend engine",
    )


class AIExplainDecisionResponse(BaseModel):
    skill_name: str
    context_type: str
    explanation: str
    key_takeaways: List[str] = []
    actionable_next_step: str
    model_used: str
    fallback_used: bool = False


# 2. Contextual Hint Schemas
class AIHintRequest(BaseModel):
    task_title: str = Field(..., min_length=1, max_length=200)
    skill_name: str = Field(..., min_length=1, max_length=100)
    context_description: str = Field(..., min_length=1, max_length=2000)
    hint_level: int = Field(default=1, ge=1, le=3, description="1: Orientation, 2: Edge-case, 3: Concrete direction")
    learner_query: Optional[str] = Field(None, max_length=1000)


class AIHintResponse(BaseModel):
    task_title: str
    skill_name: str
    hint_level: int
    max_hint_level: int = 3
    hint: str
    focus_concept: str
    model_used: str
    fallback_used: bool = False


# 3. Mistake Explanation Schemas
class AIExplainMistakeRequest(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=100)
    task_or_question: str = Field(..., min_length=1, max_length=2000)
    learner_answer: str = Field(..., min_length=1, max_length=3000)
    correct_answer_or_result: str = Field(..., min_length=1, max_length=3000)
    deterministic_evaluation: str = Field(..., min_length=1, max_length=3000)
    target_role: Optional[str] = Field("Data Analyst", max_length=100)


class AIExplainMistakeResponse(BaseModel):
    skill_name: str
    what_went_wrong: str
    why_it_happened: str
    how_to_recognize_next_time: str
    small_example: str
    short_practice_question: str
    model_used: str
    fallback_used: bool = False


# 4. Learning Concept Explanation Schemas
class AILearningExplanationRequest(BaseModel):
    skill_name: str
    target_role: str = "Data Analyst"
    specific_topic: Optional[str] = None


class AILearningExplanationResponse(BaseModel):
    skill_name: str
    target_role: str
    concept_summary: str
    concise_example: str
    common_pitfall: str
    role_use_case: str
    check_question: str
    model_used: str
    fallback_used: bool = False


# 5. Practice Question Generation Schemas
class AIPracticeQuestionsRequest(BaseModel):
    skill_name: str
    difficulty: str = "Intermediate"
    target_role: str = "Data Analyst"
    count: int = Field(default=2, ge=1, le=5)


class AIPracticeQuestionItem(BaseModel):
    question_text: str
    options: List[str] = []
    expected_answer: str
    explanation: str
    difficulty: str
    is_unscored_practice: bool = True


class AIPracticeQuestionsResponse(BaseModel):
    skill_name: str
    difficulty: str
    questions: List[AIPracticeQuestionItem]
    disclaimer: str = "Generated for unscored practice. Does not alter Skill DNA or verified benchmarks."
    model_used: str
    fallback_used: bool = False


# 6. Interview Question Generation Schemas
class AIInterviewQuestionsRequest(BaseModel):
    skill_name: str
    target_role: str = "Data Analyst"


class AIInterviewQuestionItem(BaseModel):
    category: str  # Conceptual, Practical Query/Code, Debugging, Business Scenario
    question: str
    evaluation_tip: str


class AIInterviewQuestionsResponse(BaseModel):
    skill_name: str
    target_role: str
    questions: List[AIInterviewQuestionItem]
    model_used: str
    fallback_used: bool = False


# 7. Personalized Study Guidance Schemas
class AIStudyGuidanceRequest(BaseModel):
    user_id: int


class AIStudyGuidanceDayItem(BaseModel):
    day_name: str
    duration_minutes: int
    activity_type: str
    task_focus: str


class AIStudyGuidanceResponse(BaseModel):
    user_id: int
    target_role: str
    weekly_hours: int
    focus_headline: str
    daily_breakdown: List[AIStudyGuidanceDayItem]
    coach_advice: str
    model_used: str
    fallback_used: bool = False
