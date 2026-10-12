from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    skill_id: int
    skill_name: Optional[str] = None
    difficulty: str
    estimated_minutes: int
    project_type: str

    model_config = ConfigDict(from_attributes=True)


class ProjectAttemptCreate(BaseModel):
    user_id: int
    project_id: int
    score: float
    feedback: Optional[str] = None


class ProjectAttemptResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    project_title: Optional[str] = None
    score: float
    completed_at: datetime
    feedback: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
