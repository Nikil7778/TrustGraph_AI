from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class IndustryLabTaskResponse(BaseModel):
    id: int
    lab_id: int
    task_order: int
    task_type: str
    title: str
    prompt: str
    requirements: str
    expected_output_desc: str
    weight: float

    model_config = ConfigDict(from_attributes=True)


class IndustryLabResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    target_role_id: Optional[int] = None
    target_role_name: Optional[str] = None
    primary_skill_id: int
    primary_skill_name: Optional[str] = None
    difficulty: str
    estimated_minutes: int
    business_context: str
    datasets_info: Optional[str] = None
    created_at: datetime
    tasks: List[IndustryLabTaskResponse] = []

    model_config = ConfigDict(from_attributes=True)


class IndustryLabQueryRunRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000, description="SQL query string to execute in read-only sandbox")


class IndustryLabQueryRunResponse(BaseModel):
    success: bool
    columns: List[str] = []
    rows: List[Dict[str, Any]] = []
    row_count: int = 0
    execution_time_ms: int = 0
    error_message: Optional[str] = None


class IndustryLabSubmitRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="Learner user ID")
    query: str = Field(..., min_length=1, max_length=10000, description="SQL query string for 4-pillar evaluation")
    submitted_answer: Optional[str] = Field(None, max_length=5000, description="Qualitative business reasoning/rationale")
    evidence_type: Optional[str] = Field("PRACTICE", max_length=50, description="Evidence type ledger stamp")


class IndustryLabSectionScores(BaseModel):
    sql_correctness: float  # out of 40
    data_quality_handling: float  # out of 20
    business_result: float  # out of 25
    validation_reasoning: float  # out of 15


class IndustryLabSubmitResponse(BaseModel):
    attempt_id: int
    user_id: int
    lab_id: int
    lab_title: str
    attempt_number: int
    status: str  # PASSED, PARTIAL, FAILED
    total_score: float  # 0 to 100
    section_scores: IndustryLabSectionScores
    feedback: str
    diagnostic_failures: List[str] = []
    evidence_generated: Optional[Dict[str, Any]] = None
    execution_time_ms: int = 0
    created_at: datetime


class IndustryLabAttemptResponse(BaseModel):
    id: int
    lab_id: int
    user_id: int
    attempt_number: int
    status: str
    total_score: float
    sql_score: float
    data_quality_score: float
    business_score: float
    validation_score: float
    submitted_query: Optional[str] = None
    feedback: Optional[str] = None
    execution_time_ms: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IndustryLabTableColumnInfo(BaseModel):
    name: str
    type: str
    description: Optional[str] = None


class IndustryLabTablePreview(BaseModel):
    table_name: str
    row_count: int
    columns: List[IndustryLabTableColumnInfo]
    sample_rows: List[Dict[str, Any]]
    quality_notes: List[str] = []
