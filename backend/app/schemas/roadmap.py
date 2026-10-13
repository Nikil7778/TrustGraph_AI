from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class RoadmapStepResponse(BaseModel):
    id: int
    roadmap_id: int
    skill_id: int
    skill_name: Optional[str] = None
    activity_id: Optional[int] = None
    title: str
    step_type: str
    priority: str
    status: str
    reason: Optional[str] = None
    order_index: int
    estimated_minutes: int
    prerequisite_step_ids: Optional[str] = None
    evidence_required: Optional[str] = None
    module_slug: Optional[str] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RoadmapResponse(BaseModel):
    id: int
    user_id: int
    target_role_id: Optional[int] = None
    target_role_name: Optional[str] = None
    version: int
    status: str
    regeneration_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    steps: List[RoadmapStepResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RoadmapHistoryResponse(BaseModel):
    id: int
    user_id: int
    target_role_id: Optional[int] = None
    target_role_name: Optional[str] = None
    version: int
    status: str
    regeneration_reason: Optional[str] = None
    step_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoadmapChangeResponse(BaseModel):
    id: int
    user_id: int
    roadmap_id: int
    version: int
    change_type: str  # INSERTION, UNLOCKED, PROMOTED, REMOVED, COMPLETED
    skill_name: str
    title: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

