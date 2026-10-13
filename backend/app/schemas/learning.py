from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LearningModuleSummary(BaseModel):
    id: int
    slug: str
    skill_id: int
    skill_name: str
    title: str
    concept_name: str
    difficulty: str
    estimated_minutes: int
    order_index: int
    status: str  # LOCKED, AVAILABLE, LEARNING, PRACTICING, CHECK_PENDING, DEVELOPING, MASTERED, REMEDIATION
    prerequisite_concept_slugs: Optional[str] = None
    target_role_name: str
    practice_score: float = 0.0
    concept_check_score: float = 0.0
    concept_check_passed: bool = False
    applied_task_completed: bool = False
    is_locked: bool = False
    unlock_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


class LearningResourceResponse(BaseModel):
    id: int
    title: str
    provider: str
    url: str
    skill_id: Optional[int] = None
    skill_name: Optional[str] = None
    concept_slug: str
    role_name: str
    difficulty: str
    resource_type: str
    estimated_minutes: int
    quality_rank: int
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


class LearningModuleDetail(BaseModel):
    id: int
    slug: str
    skill_id: int
    skill_name: str
    title: str
    concept_name: str
    difficulty: str
    estimated_minutes: int
    order_index: int
    status: str
    prerequisite_concept_slugs: Optional[str] = None
    target_role_name: str

    learning_objectives: List[str]
    explanation: str
    key_rules: Optional[str] = None
    common_mistakes: Optional[str] = None

    worked_example: Dict[str, Any]
    guided_practice: Dict[str, Any]
    independent_practice: Dict[str, Any]
    concept_check_questions: List[Dict[str, Any]]
    passing_threshold: float
    applied_task: Dict[str, Any]

    # External Learning Resources (Section 12-16)
    external_resources: List[LearningResourceResponse] = []

    # User progress metadata
    user_status: str
    practice_score: float = 0.0
    concept_check_score: float = 0.0
    concept_check_passed: bool = False
    concept_check_attempts: int = 0
    applied_task_completed: bool = False
    applied_task_score: float = 0.0
    is_locked: bool = False
    lock_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


class LearningPracticeSubmitRequest(BaseModel):
    user_id: Optional[int] = None
    mode: Optional[str] = "guided"  # guided or independent
    practice_type: Optional[str] = None
    code_or_answer: Optional[str] = None
    code: Optional[str] = None
    hints_used: int = 0


class LearningPracticeSubmitResponse(BaseModel):
    module_slug: str
    mode: str
    success: bool
    is_correct: bool = True
    score: float
    feedback: str
    adapted_guidance: str
    recommended_difficulty: str
    evidence_created: bool
    new_status: str

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


class ConceptCheckAnswerItem(BaseModel):
    question_index: int
    selected_option: str


class ConceptCheckSubmitRequest(BaseModel):
    user_id: Optional[int] = None
    answers: Union[List[ConceptCheckAnswerItem], Dict[str, Any]]


class ConceptCheckSubmitResponse(BaseModel):
    module_slug: str
    passed: bool
    score: float
    passing_threshold: float
    status: str = "MASTERED"
    correct_count: int = 0
    total_questions: int = 0
    results: List[Dict[str, Any]] = []
    new_status: str = "MASTERED"
    evidence_created: bool = False
    unlocked_concepts: List[str] = []
    message: str = ""

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


class AppliedTaskSubmitRequest(BaseModel):
    code_or_query: str
    business_rationale: Optional[str] = None


class AppliedTaskSubmitResponse(BaseModel):
    module_slug: str
    success: bool
    score: float
    feedback: str
    rubric_scores: Dict[str, float]
    evidence_created: bool
    new_status: str
