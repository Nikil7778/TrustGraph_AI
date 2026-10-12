from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SkillDebtResponse(BaseModel):
    skill_id: int
    skill_name: str
    skill_category: str
    role_id: int
    role_name: str
    role_requirement: float
    current_skill_level: float
    confidence: float
    accuracy: float
    recency: float
    recency_label: str
    evidence_count: int
    practical_evidence_count: int
    latest_evidence_at: Optional[datetime] = None
    debt_status: str  # SKILL_DEBT, MISSING, HEALTHY, UNKNOWN
    debt_score: float  # 0 to 100
    severity: str  # HIGH, MEDIUM, LOW, NONE
    reason: str
    recommended_intervention: str

    model_config = ConfigDict(from_attributes=True)
