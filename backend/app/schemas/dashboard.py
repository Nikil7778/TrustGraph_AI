from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.schemas.next_best_proof import NextBestProofResponse


class CareerReadinessMetric(BaseModel):
    score: float
    status: str  # "Job ready" | "On track" | "Needs improvement" | "Awaiting baseline assessment"
    trend_label: Optional[str] = None
    formula_explanation: str


class DashboardMetrics(BaseModel):
    career_readiness: CareerReadinessMetric
    skills_verified: int
    total_role_skills: int
    active_skill_debt_count: int
    high_debt_count: int
    evidence_records_count: int
    next_best_proof_title: Optional[str] = None


class DashboardSkillGapItem(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    current_level: float
    required_level: float
    gap: float  # current_level - required_level (negative = deficit)
    role_importance: float
    industry_relevance: str
    status: str  # "healthy" | "developing" | "critical" | "unknown"
    priority: str  # "Critical" | "High" | "Medium" | "Low"
    skill_debt_status: str
    skill_debt_severity: Optional[str] = None


class DashboardSkillDnaItem(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    skill_level: float
    confidence: float
    accuracy: float
    status: str
    evidence_count: int
    recency_label: str


class DashboardCareerPriorityItem(BaseModel):
    rank: int
    skill_id: int
    skill_name: str
    priority: str
    career_value_score: float
    gap_score: float
    role_importance: float
    reason: str
    recommended_focus: str


class DashboardSkillDebtAlert(BaseModel):
    skill_id: int
    skill_name: str
    severity: str
    debt_score: float
    current_level: float
    required_level: float
    message: str
    cta_text: str
    action_type: str


class DashboardEvidenceItem(BaseModel):
    id: int
    skill_name: str
    evidence_type: str
    score: float
    source: str
    description: Optional[str] = None
    verified_date: str


class DashboardRoadmapStepItem(BaseModel):
    id: int
    order_index: int
    title: str
    step_type: str
    status: str  # COMPLETED | IN_PROGRESS | RECOMMENDED | REMEDIATION | BLOCKED | UPCOMING
    skill_name: str
    estimated_minutes: int
    priority: str


class DashboardProgressPoint(BaseModel):
    week: str
    score: float


class DashboardSkillProgressItem(BaseModel):
    skill_name: str
    history: List[DashboardProgressPoint]


class RoleOption(BaseModel):
    id: int
    name: str


class DashboardResponse(BaseModel):
    user_id: int
    learner_name: str
    target_role_id: int
    target_role_name: str
    all_roles: List[RoleOption]
    metrics: DashboardMetrics
    next_best_proof: Optional[NextBestProofResponse] = None
    highest_career_gap: Optional[DashboardCareerPriorityItem] = None
    skill_gap_heatmap: List[DashboardSkillGapItem]
    skill_dna_snapshot: List[DashboardSkillDnaItem]
    top_career_priorities: List[DashboardCareerPriorityItem]
    skill_debt_alert: Optional[DashboardSkillDebtAlert] = None
    recent_evidence: List[DashboardEvidenceItem]
    roadmap_preview: List[DashboardRoadmapStepItem]
    progress_history: List[DashboardSkillProgressItem]
