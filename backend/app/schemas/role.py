from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class RoleSkillResponse(BaseModel):
    id: int
    role_id: int
    skill_id: int
    skill_name: Optional[str] = None
    importance_score: int
    industry_relevance: str
    required_level: int

    model_config = ConfigDict(from_attributes=True)


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    role_skills: List[RoleSkillResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CustomRoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    skills: Optional[List[str]] = None


class SkillMapItem(BaseModel):
    id: Optional[int] = None
    skill_id: Optional[int] = None
    name: str
    category: Optional[str] = "General Competencies"
    description: Optional[str] = None
    importance_score: int
    required_level: int
    industry_relevance: str



class SkillMapCategory(BaseModel):
    category_name: str
    skills: List[SkillMapItem]


class RoleSkillMapResponse(BaseModel):
    role_id: int
    role_name: str
    description: Optional[str] = None
    total_skills: int
    categories: List[SkillMapCategory]
    skills: List[SkillMapItem]

