from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.models.evidence import SkillEvidence
from app.models.assessment import AssessmentAttempt, Assessment
from app.models.project import ProjectAttempt, Project
from app.services.skill_dna_service import skill_dna_service
from app.services.skill_debt_service import skill_debt_service
from app.services.career_value_service import career_value_service
from app.services.next_best_proof_service import next_best_proof_service
from app.schemas.skill_passport import (
    SkillPassportResponse,
    PassportHeader,
    PassportSummary,
    SkillProofMatrixItem,
    SkillProofEvidenceItem,
    EvidenceTimelineItem,
    StrongestProofItem,
    SkillNeedingProofItem,
    PassportProjectItem,
    PassportAssessmentItem,
    CareerRelevanceItem,
)


class SkillPassportService:
    """
    Deterministic Proof-of-Skill Passport Service.
    Produces evidence-backed credentials and audit trails for learners.
    """

    def get_skill_passport(self, db: Session, user_id: int) -> SkillPassportResponse:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        target_role_id = user.target_role_id
        if not target_role_id:
            first_role = db.query(Role).first()
            target_role_id = first_role.id if first_role else 1

        role = (
            db.query(Role)
            .options(joinedload(Role.role_skills).joinedload(RoleSkill.skill))
            .filter(Role.id == target_role_id)
            .first()
        )
        if not role:
            raise ValueError(f"Role with ID {target_role_id} not found.")

        # 1. Fetch live deterministic engine data
        dna_list = skill_dna_service.get_user_skill_dna(db, user_id)
        dna_map = {dna["skill_id"]: dna for dna in dna_list}

        debt_list = skill_debt_service.calculate_skill_debt(db, user_id, target_role_id)
        debt_map = {d["skill_id"]: d for d in debt_list}

        cv_list = career_value_service.calculate_career_value(db, user_id, target_role_id)

        nbp_data = next_best_proof_service.get_next_best_proof(db, user_id, target_role_id)

        # 2. Fetch all real SkillEvidence records
        now = datetime.utcnow()
        evidences = (
            db.query(SkillEvidence)
            .options(joinedload(SkillEvidence.skill))
            .filter(SkillEvidence.user_id == user_id)
            .order_by(SkillEvidence.created_at.desc())
            .all()
        )

        evidences_by_skill: Dict[int, List[SkillEvidence]] = {}
        for ev in evidences:
            evidences_by_skill.setdefault(ev.skill_id, []).append(ev)

        def map_evidence_strength(ev_type: str) -> str:
            clean = ev_type.upper()
            if clean in ["REAL_WORLD_TASK", "INDUSTRY_LAB"]:
                return "Practical workplace task"
            elif clean == "PROJECT":
                return "Portfolio project evidence"
            elif clean == "PRACTICE":
                return "Applied practice exercise"
            return "Conceptual diagnostic assessment"

        def get_relative_date(dt: datetime) -> str:
            diff = (now - dt).days
            if diff == 0:
                return "Today"
            elif diff == 1:
                return "Yesterday"
            elif diff < 7:
                return f"{diff} days ago"
            return dt.strftime("%b %d, %Y")

        # 3. Build Skill Proof Matrix Items
        total_weight = 0.0
        weighted_fulfillment = 0.0
        matrix_items: List[SkillProofMatrixItem] = []
        skills_verified_count = 0

        for rs in role.role_skills:
            skill = rs.skill
            if not skill:
                continue

            importance = float(rs.importance_score)
            req_level = float(rs.required_level)
            dna = dna_map.get(skill.id, {})
            curr_level = float(dna.get("skill_level", 0.0))
            confidence = float(dna.get("confidence", 50.0))
            debt_item = debt_map.get(skill.id)
            debt_status = debt_item.get("debt_status", "HEALTHY") if debt_item else "HEALTHY"

            total_weight += importance
            fulfillment_ratio = min(1.0, curr_level / max(1.0, req_level))
            weighted_fulfillment += importance * fulfillment_ratio

            # Supporting evidence items for this skill
            skill_ev_list = evidences_by_skill.get(skill.id, [])
            supporting_items: List[SkillProofEvidenceItem] = []
            for ev in skill_ev_list:
                supporting_items.append(
                    SkillProofEvidenceItem(
                        id=ev.id,
                        source=ev.source,
                        title=ev.description or ev.source,
                        evidence_type=ev.evidence_type,
                        evidence_strength=map_evidence_strength(ev.evidence_type),
                        score=round(ev.score, 1),
                        verified_date=ev.created_at.strftime("%b %d, %Y"),
                        relative_date=get_relative_date(ev.created_at),
                        description=ev.description,
                    )
                )

            # Verification logic strictly based on deterministic benchmark & evidence
            is_verified = (curr_level >= req_level and len(supporting_items) >= 1 and debt_status != "SKILL_DEBT")
            if is_verified:
                skills_verified_count += 1
                status = "VERIFIED"
            elif debt_status == "SKILL_DEBT":
                status = "SKILL DEBT"
            elif curr_level > 0:
                status = "DEVELOPING"
            else:
                status = "NOT YET PROVEN"

            last_verified_str = supporting_items[0].relative_date if supporting_items else "Awaiting baseline"

            # Evidence strength tier
            practical_count = sum(1 for s in supporting_items if s.evidence_type in ["REAL_WORLD_TASK", "PROJECT", "PRACTICE"])
            strength_tier = "Practical workplace proof" if practical_count >= 2 else "Applied practice proof" if practical_count >= 1 else "Conceptual assessment proof" if supporting_items else "No verified proof"

            matrix_items.append(
                SkillProofMatrixItem(
                    skill_id=skill.id,
                    skill_name=skill.name,
                    category=skill.category or "General",
                    skill_level=round(curr_level, 1),
                    confidence=round(confidence, 1),
                    required_level=round(req_level, 1),
                    evidence_count=len(supporting_items),
                    last_verified=last_verified_str,
                    status=status,
                    evidence_strength_label=f"{len(supporting_items)} items • {strength_tier}",
                    is_verified=is_verified,
                    supporting_evidences=supporting_items,
                )
            )

        # Sort matrix items: Verified first, then by level descending
        matrix_items.sort(key=lambda x: (not x.is_verified, -x.skill_level))

        # Career Readiness Score
        career_readiness_score = (
            round((weighted_fulfillment / max(1.0, total_weight)) * 100.0, 1)
            if total_weight > 0
            else 0.0
        )
        readiness_status = (
            "Job ready"
            if career_readiness_score >= 80.0
            else "On track"
            if career_readiness_score >= 65.0
            else "Needs improvement"
            if career_readiness_score > 0.0
            else "Awaiting baseline assessment"
        )

        last_ev_date = get_relative_date(evidences[0].created_at) if evidences else None
        passport_id = f"SP-{user.id:04d}-VERIFIED"

        header = PassportHeader(
            user_id=user.id,
            learner_name=user.name,
            target_role_id=role.id,
            target_role_name=role.name,
            career_readiness=career_readiness_score,
            career_readiness_status=readiness_status,
            skills_verified_count=skills_verified_count,
            total_role_skills_count=len(role.role_skills),
            total_evidence_count=len(evidences),
            last_verified_date=last_ev_date,
            passport_id=passport_id,
            created_at=user.created_at.strftime("%b %d, %Y"),
        )

        # Summary
        active_debt_count = sum(1 for m in matrix_items if m.status == "SKILL DEBT")
        developing_count = sum(1 for m in matrix_items if m.status == "DEVELOPING")
        strongest_skills = [m.skill_name for m in matrix_items if m.is_verified][:3]
        if not strongest_skills:
            strongest_skills = [m.skill_name for m in matrix_items if m.skill_level > 0][:3]

        skills_needing_proof_names = [m.skill_name for m in matrix_items if not m.is_verified][:3]

        summary = PassportSummary(
            headline=f"Demonstrated evidence transcript for {role.name} competencies",
            verified_skills_count=skills_verified_count,
            developing_skills_count=developing_count,
            skill_debt_count=active_debt_count,
            strongest_skills=strongest_skills,
            skills_needing_proof=skills_needing_proof_names,
        )

        # 4. Evidence Timeline (Descending Chronological)
        timeline_items: List[EvidenceTimelineItem] = []
        for ev in evidences[:15]:
            timeline_items.append(
                EvidenceTimelineItem(
                    id=ev.id,
                    skill_id=ev.skill_id,
                    skill_name=ev.skill.name if ev.skill else "Competency",
                    evidence_type=ev.evidence_type,
                    score=round(ev.score, 1),
                    source=ev.source,
                    verified_date=ev.created_at.strftime("%b %d, %Y"),
                    relative_date=get_relative_date(ev.created_at),
                    description=ev.description,
                )
            )

        # 5. Strongest Proof (Deterministic Selection)
        # Prefer REAL_WORLD_TASK / PROJECT > PRACTICE > ASSESSMENT, and higher score
        strongest_proof: Optional[StrongestProofItem] = None
        if evidences:
            sorted_by_strength = sorted(
                evidences,
                key=lambda e: (
                    3 if e.evidence_type in ["REAL_WORLD_TASK", "INDUSTRY_LAB"] else 2 if e.evidence_type == "PROJECT" else 1 if e.evidence_type == "PRACTICE" else 0,
                    e.score,
                ),
                reverse=True,
            )
            top_ev = sorted_by_strength[0]
            strongest_proof = StrongestProofItem(
                id=top_ev.id,
                title=top_ev.source,
                evidence_type=top_ev.evidence_type,
                evidence_strength=map_evidence_strength(top_ev.evidence_type),
                score=round(top_ev.score, 1),
                skills_demonstrated=[top_ev.skill.name if top_ev.skill else "Core Competency"],
                verified_date=get_relative_date(top_ev.created_at),
                description=top_ev.description or "Demonstrated hands-on performance verified by deterministic evaluator.",
            )

        # 6. Skills Needing More Proof
        skills_needing_proof: List[SkillNeedingProofItem] = []
        for cv in cv_list:
            if cv["current_skill_level"] < cv["required_skill_level"]:
                skill_id = cv["skill_id"]
                debt_item = debt_map.get(skill_id)
                sev = debt_item.get("severity", "MEDIUM") if debt_item else "MEDIUM"
                status_label = "SKILL_DEBT" if debt_item and debt_item.get("debt_status") == "SKILL_DEBT" else "DEVELOPING"

                skills_needing_proof.append(
                    SkillNeedingProofItem(
                        skill_id=skill_id,
                        skill_name=cv["skill_name"],
                        status=status_label,
                        severity=sev,
                        current_level=round(cv["current_skill_level"], 1),
                        required_level=round(cv["required_skill_level"], 1),
                        evidence_gap_reason=cv["reason"],
                        recommended_proof_title=cv["recommended_focus"],
                        action_type="PRACTICE" if status_label == "SKILL_DEBT" else "REASSESS",
                    )
                )

        # 7. Real Projects & Assessments History
        project_items: List[PassportProjectItem] = []
        # Fetch actual project attempts
        p_attempts = (
            db.query(ProjectAttempt)
            .options(joinedload(ProjectAttempt.project))
            .filter(ProjectAttempt.user_id == user_id)
            .order_by(ProjectAttempt.completed_at.desc())
            .all()
        )
        for pa in p_attempts:
            project_items.append(
                PassportProjectItem(
                    id=pa.id,
                    title=pa.project.title if pa.project else "Applied Analytics Project",
                    skills_demonstrated=["SQL", "EDA", "Data Modeling"],
                    evidence_type="PROJECT",
                    status="VERIFIED" if (pa.score is not None and pa.score >= 70.0) else "COMPLETED",
                    score=round(pa.score, 1) if pa.score is not None else None,
                    verified_date=get_relative_date(pa.completed_at),
                )
            )

        # If no project attempts yet, pull from REAL_WORLD_TASK / LAB evidences
        if not project_items:
            for ev in evidences:
                if ev.evidence_type in ["REAL_WORLD_TASK", "PROJECT", "INDUSTRY_LAB"]:
                    project_items.append(
                        PassportProjectItem(
                            id=ev.id,
                            title=ev.source,
                            skills_demonstrated=[ev.skill.name if ev.skill else "Data Analysis"],
                            evidence_type=ev.evidence_type,
                            status="VERIFIED",
                            score=round(ev.score, 1),
                            verified_date=get_relative_date(ev.created_at),
                        )
                    )

        # Assessment Attempts
        assessment_items: List[PassportAssessmentItem] = []
        assm_attempts = (
            db.query(AssessmentAttempt)
            .options(joinedload(AssessmentAttempt.assessment))
            .filter(AssessmentAttempt.user_id == user_id)
            .order_by(AssessmentAttempt.completed_at.desc())
            .all()
        )
        for aa in assm_attempts[:6]:
            assessment_items.append(
                PassportAssessmentItem(
                    id=aa.id,
                    assessment_id=aa.assessment_id,
                    assessment_title=aa.assessment.title if aa.assessment else "Diagnostic Assessment",
                    skill_name=aa.assessment.skill.name if aa.assessment and aa.assessment.skill else "Technical Skill",
                    score=round(aa.score, 1),
                    accuracy=round(aa.accuracy, 1),
                    difficulty=aa.assessment.difficulty if aa.assessment else "Medium",
                    completed_at=get_relative_date(aa.completed_at),
                )
            )

        # 8. Career Relevance
        career_relevance_items: List[CareerRelevanceItem] = []
        for cv in cv_list:
            curr = cv["current_skill_level"]
            req = cv["required_skill_level"]
            debt = cv["skill_debt_status"]

            if curr >= req and debt != "SKILL_DEBT":
                status_text = "Strong verified proof"
            elif debt == "SKILL_DEBT":
                status_text = "Needs stronger proof (Skill Debt)"
            elif curr > 0:
                status_text = "Developing proof"
            else:
                status_text = "Not yet proven"

            career_relevance_items.append(
                CareerRelevanceItem(
                    skill_name=cv["skill_name"],
                    importance=int(cv["role_importance"]),
                    evidence_status_label=status_text,
                    career_priority=cv["priority"],
                )
            )

        return SkillPassportResponse(
            header=header,
            summary=summary,
            skill_proof_matrix=matrix_items,
            evidence_timeline=timeline_items,
            strongest_proof=strongest_proof,
            skills_needing_proof=skills_needing_proof[:5],
            next_best_proof=nbp_data,
            projects=project_items[:4],
            assessment_history=assessment_items,
            career_relevance=career_relevance_items,
        )

    def get_skill_detail(self, db: Session, user_id: int, skill_id: int) -> SkillProofMatrixItem:
        passport = self.get_skill_passport(db, user_id)
        for item in passport.skill_proof_matrix:
            if item.skill_id == skill_id:
                return item
        raise ValueError(f"Skill with ID {skill_id} not found in learner's passport.")


skill_passport_service = SkillPassportService()
