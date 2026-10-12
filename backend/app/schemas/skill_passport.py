from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class PassportHeader(BaseModel):
    user_id: int
    learner_name: str
    target_role_id: int
    target_role_name: str
    career_readiness: float
    career_readiness_status: str
    skills_verified_count: int
    total_role_skills_count: int
    total_evidence_count: int
    last_verified_date: Optional[str] = None
    passport_id: str
    created_at: str


class PassportSummary(BaseModel):
    headline: str
    verified_skills_count: int
    developing_skills_count: int
    skill_debt_count: int
    strongest_skills: List[str]
    skills_needing_proof: List[str]


class SkillProofEvidenceItem(BaseModel):
    id: int
    source: str
    title: str
    evidence_type: str  # ASSESSMENT, PRACTICE, REAL_WORLD_TASK, PROJECT, LAB
    evidence_strength: str  # Conceptual assessment, Applied practice, Practical workplace task, Portfolio project
    score: float
    verified_date: str
    relative_date: str
    description: Optional[str] = None


class SkillProofMatrixItem(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    skill_level: float
    confidence: float
    required_level: float
    evidence_count: int
    last_verified: str
    status: str  # VERIFIED | DEVELOPING | CRITICAL | SKILL DEBT | NOT YET PROVEN
    evidence_strength_label: str
    is_verified: bool
    supporting_evidences: List[SkillProofEvidenceItem]


class EvidenceTimelineItem(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    evidence_type: str
    score: float
    source: str
    verified_date: str
    relative_date: str
    description: Optional[str] = None


class StrongestProofItem(BaseModel):
    id: int
    title: str
    evidence_type: str
    evidence_strength: str
    score: float
    skills_demonstrated: List[str]
    verified_date: str
    description: str


class SkillNeedingProofItem(BaseModel):
    skill_id: int
    skill_name: str
    status: str
    severity: str
    current_level: float
    required_level: float
    evidence_gap_reason: str
    recommended_proof_title: str
    action_type: str


class PassportProjectItem(BaseModel):
    id: int
    title: str
    skills_demonstrated: List[str]
    evidence_type: str
    status: str
    score: Optional[float] = None
    verified_date: str


class PassportAssessmentItem(BaseModel):
    id: int
    assessment_id: int
    assessment_title: str
    skill_name: str
    score: float
    accuracy: float
    difficulty: str
    completed_at: str


class CareerRelevanceItem(BaseModel):
    skill_name: str
    importance: int
    evidence_status_label: str
    career_priority: str


class SkillPassportResponse(BaseModel):
    header: PassportHeader
    summary: PassportSummary
    skill_proof_matrix: List[SkillProofMatrixItem]
    evidence_timeline: List[EvidenceTimelineItem]
    strongest_proof: Optional[StrongestProofItem] = None
    skills_needing_proof: List[SkillNeedingProofItem]
    next_best_proof: Optional[Dict[str, Any]] = None
    projects: List[PassportProjectItem]
    assessment_history: List[PassportAssessmentItem]
    career_relevance: List[CareerRelevanceItem]
