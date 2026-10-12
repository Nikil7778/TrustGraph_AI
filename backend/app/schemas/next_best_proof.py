from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum


class ActionTypeEnum(str, Enum):
    LEARN = "LEARN"
    PRACTICE = "PRACTICE"
    REASSESS = "REASSESS"
    PRACTICAL_TASK = "PRACTICAL_TASK"
    PROJECT = "PROJECT"
    REVIEW_PREREQUISITE = "REVIEW_PREREQUISITE"


class ActionPriorityEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class NextBestProofResponse(BaseModel):
    user_id: int
    role_id: int
    role_name: str
    skill_id: int
    skill_name: str
    skill_category: str
    action_type: ActionTypeEnum
    action_type_label: str
    title: str
    priority: ActionPriorityEnum
    next_best_proof_score: float
    current_skill_level: float
    required_skill_level: float
    career_value_score: float
    skill_debt_score: float
    skill_debt_status: str
    confidence: float
    evidence_score: float
    practical_evidence_score: float
    estimated_minutes: int
    expected_proof: str
    reason: str
    why_now: str
    why_this_action: str
    prerequisites: List[str] = []
    action_readiness: str
    rank: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
