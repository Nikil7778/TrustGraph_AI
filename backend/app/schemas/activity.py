from typing import Optional
from pydantic import BaseModel, ConfigDict


class LearningActivityResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    activity_type: str
    skill_id: int
    skill_name: Optional[str] = None
    difficulty: str
    estimated_minutes: int

    model_config = ConfigDict(from_attributes=True)
