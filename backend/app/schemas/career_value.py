from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum


class CareerPriorityEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CareerValueResponse(BaseModel):
    skill_id: int
    skill_name: str
    skill_category: str
    role_id: int
    role_name: str
    current_skill_level: float
    required_skill_level: float
    gap_score: float
    role_importance: float
    industry_relevance: float
    industry_relevance_label: str
    confidence: float
    confidence_gap: float
    recency: float
    recency_gap: float
    evidence_score: float
    evidence_gap: float
    skill_debt_status: str
    skill_debt_score: float
    debt_boost: float
    career_value_score: float
    priority: CareerPriorityEnum
    reason: str
    recommended_focus: str
    rank: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
