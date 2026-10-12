from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.role import RoleResponse


class UserSkillResponse(BaseModel):
    id: int
    user_id: int
    skill_id: int
    skill_name: Optional[str] = None
    skill_category: Optional[str] = None
    skill_level: float
    confidence: float
    accuracy: float
    difficulty: str
    recency: str
    evidence_score: float
    last_assessed_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    experience_level: Optional[str] = "Intermediate"
    target_role_id: Optional[int] = None
    weekly_learning_hours: Optional[int] = 10
    learning_goal: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    experience_level: Optional[str] = None
    target_role_id: Optional[int] = None
    weekly_learning_hours: Optional[int] = None
    learning_goal: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    experience_level: str
    target_role_id: Optional[int] = None
    target_role: Optional[RoleResponse] = None
    weekly_learning_hours: int
    learning_goal: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
