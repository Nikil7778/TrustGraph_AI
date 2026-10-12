from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SkillDNAResponse(BaseModel):
    user_id: int
    skill_id: int
    skill_name: str
    skill_category: str
    skill_level: float
    confidence: float
    accuracy: float
    difficulty: float
    difficulty_label: str
    recency: float
    recency_label: str
    evidence_score: float
    evidence_count: int
    last_assessed_at: datetime
    status: str  # HEALTHY, STRONG, DEVELOPING, CRITICAL, UNKNOWN

    model_config = ConfigDict(from_attributes=True)
