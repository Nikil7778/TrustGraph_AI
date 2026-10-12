from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SkillResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
