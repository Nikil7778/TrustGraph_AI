from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message author: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, max_length=5000, description="Message text content")


class ChatAction(BaseModel):
    label: str = Field(..., description="Display label for the action button")
    action_type: str = Field(..., description="Action type: NAVIGATE, START_PRACTICE, TAKE_ASSESSMENT, VIEW_EVIDENCE")
    target_route: str = Field(..., description="Frontend route to navigate or launch")
    skill_id: Optional[int] = None
    skill_name: Optional[str] = None


class CoachChatRequest(BaseModel):
    user_id: int = Field(default=1, gt=0, description="Active learner ID")
    message: str = Field(..., min_length=1, max_length=2000, description="Learner user prompt")
    history: List[ChatMessage] = Field(default_factory=list, description="Prior conversation message turns")
    context_hint: Optional[str] = Field(None, max_length=200, description="Optional page context (e.g. 'roadmap', 'skill_dna')")


class CoachChatResponse(BaseModel):
    reply: str
    actions: List[ChatAction] = []
    tools_used: List[str] = []
    suggested_prompts: List[str] = []
    fallback_used: bool = False
    model_used: str = "gemini-2.5-flash"
