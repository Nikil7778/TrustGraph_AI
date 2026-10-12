from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SkillEvidenceCreate(BaseModel):
    user_id: int
    skill_id: int
    source: str
    evidence_type: str
    score: float
    description: Optional[str] = None


class SkillEvidenceResponse(BaseModel):
    id: int
    user_id: int
    skill_id: int
    skill_name: Optional[str] = None
    source: str
    evidence_type: str
    score: float
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
