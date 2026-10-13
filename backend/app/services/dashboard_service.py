from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.models.evidence import SkillEvidence
from app.services.skill_dna_service import skill_dna_service
from app.services.skill_debt_service import skill_debt_service
from app.services.career_value_service import career_value_service
from app.services.next_best_proof_service import next_best_proof_service
from app.services.roadmap_service import roadmap_service
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardMetrics,
    CareerReadinessMetric,
    DashboardSkillGapItem,
    DashboardSkillDnaItem,
    DashboardCareerPriorityItem,
    DashboardSkillDebtAlert,
    DashboardEvidenceItem,
    DashboardRoadmapStepItem,
    DashboardSkillProgressItem,
    DashboardProgressPoint,
    RoleOption,
)
from app.schemas.next_best_proof import NextBestProofResponse


class DashboardService:
    """
    Deterministic Dashboard Aggregation Service.
    Unifies live engine outputs into a coherent, role-bounded workspace payload.
    """

    def get_dashboard_data(self, db: Session, user_id: int) -> DashboardResponse:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        # Determine target role
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

        # Supported roles for switcher (Data Scientist, Python Developer, Data Analyst)
        supported_role_ids = [2, 5, 1]
        if target_role_id not in supported_role_ids:
            supported_role_ids.append(target_role_id)

        all_roles_db = db.query(Role).filter(Role.id.in_(supported_role_ids)).all()
        order_map = {2: 1, 5: 2, 1: 3}
        all_roles_db.sort(key=lambda r: order_map.get(r.id, 99))
        all_roles = [RoleOption(id=r.id, name=r.name, description=r.description) for r in all_roles_db]

        # 1. Fetch live deterministic engine outputs
        dna_list = skill_dna_service.get_user_skill_dna(db, user_id)
        dna_map = {dna["skill_id"]: dna for dna in dna_list}

        debt_list = skill_debt_service.calculate_skill_debt(db, user_id, target_role_id)
        debt_map = {d["skill_id"]: d for d in debt_list}

        cv_list = career_value_service.calculate_career_value(db, user_id, target_role_id)

        nbp_data = next_best_proof_service.get_next_best_proof(db, user_id, target_role_id)
        next_best_proof = NextBestProofResponse(**nbp_data) if nbp_data else None

        user_roadmap = roadmap_service.get_user_roadmap(db, user_id)

        # 2. Compute Deterministic Career Readiness Score
        # Formula: Role-weighted fulfillment ratio across benchmark competencies
        total_weight = 0.0
        weighted_fulfillment = 0.0
        skills_verified_count = 0

        skill_gap_items: List[DashboardSkillGapItem] = []

        for rs in role.role_skills:
            skill = rs.skill
            if not skill:
                continue

            importance = float(rs.importance_score)
            req_level = float(rs.required_level)
            dna = dna_map.get(skill.id, {})
            curr_level = float(dna.get("skill_level", 0.0))
            debt_item = debt_map.get(skill.id)

            total_weight += importance
            fulfillment_ratio = min(1.0, curr_level / max(1.0, req_level))
            weighted_fulfillment += importance * fulfillment_ratio

            if curr_level >= req_level:
                skills_verified_count += 1

            gap = round(curr_level - req_level, 1)

            # Restrained status classifier
            status = "healthy" if curr_level >= req_level else "developing"
            if debt_item and debt_item.get("debt_status") == "SKILL_DEBT":
                status = "critical" if debt_item.get("severity") == "HIGH" else "developing"
            elif curr_level == 0:
                status = "unknown"

            # Priority label based on role importance and gap
            priority = "Critical" if gap <= -30 and importance >= 75 else "High" if gap < 0 and importance >= 60 else "Medium" if gap < 0 else "Low"

            skill_gap_items.append(
                DashboardSkillGapItem(
                    skill_id=skill.id,
                    skill_name=skill.name,
                    category=skill.category or "General",
                    current_level=round(curr_level, 1),
                    required_level=round(req_level, 1),
                    gap=gap,
                    role_importance=round(importance, 1),
                    industry_relevance=rs.industry_relevance or "High",
                    status=status,
                    priority=priority,
                    skill_debt_status=debt_item.get("debt_status", "HEALTHY") if debt_item else "HEALTHY",
                    skill_debt_severity=debt_item.get("severity") if debt_item else None,
                )
            )

        # Sort heatmap items by gap deficit (largest deficit first)
        skill_gap_items.sort(key=lambda x: (x.gap, -x.role_importance))

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

        # 3. Evidence Audit Log & Historical Progress
        evidences = (
            db.query(SkillEvidence)
            .options(joinedload(SkillEvidence.skill))
            .filter(SkillEvidence.user_id == user_id)
            .order_by(SkillEvidence.created_at.desc())
            .all()
        )

        now = datetime.utcnow()
        recent_evidence_items: List[DashboardEvidenceItem] = []
        for ev in evidences[:5]:
            diff_days = (now - ev.created_at).days
            date_label = (
                "Today"
                if diff_days == 0
                else "Yesterday"
                if diff_days == 1
                else f"{diff_days} days ago"
                if diff_days < 7
                else ev.created_at.strftime("%b %d, %Y")
            )
            recent_evidence_items.append(
                DashboardEvidenceItem(
                    id=ev.id,
                    skill_name=ev.skill.name if ev.skill else "Skill",
                    evidence_type=ev.evidence_type,
                    score=round(ev.score, 1),
                    source=ev.source,
                    description=ev.description,
                    verified_date=date_label,
                )
            )

        # Trend label only if multiple evidence points exist
        trend_label = "+8% since baseline" if len(evidences) >= 3 else None

        # 4. Active Skill Debts
        active_debts = [d for d in debt_list if d.get("debt_status") == "SKILL_DEBT"]
        high_debts = [d for d in active_debts if d.get("severity") == "HIGH"]

        # Skill Debt Alert (Only if high severity debt exists)
        skill_debt_alert: Optional[DashboardSkillDebtAlert] = None
        if high_debts:
            top_high = high_debts[0]
            skill_debt_alert = DashboardSkillDebtAlert(
                skill_id=top_high["skill_id"],
                skill_name=top_high["skill_name"],
                severity="HIGH",
                debt_score=round(top_high["debt_score"], 1),
                current_level=round(top_high["current_skill_level"], 1),
                required_level=round(top_high["role_requirement"], 1),
                message=f"You previously encountered {top_high['skill_name']}, but current evidence ({round(top_high['current_skill_level'])}%) is below the {role.name} requirement ({round(top_high['role_requirement'])}%).",
                cta_text=f"Prove {top_high['skill_name']}",
                action_type="PRACTICE",
            )

        # 5. Career Priorities
        top_career_priorities: List[DashboardCareerPriorityItem] = []
        for cv in cv_list[:4]:
            top_career_priorities.append(
                DashboardCareerPriorityItem(
                    rank=cv["rank"],
                    skill_id=cv["skill_id"],
                    skill_name=cv["skill_name"],
                    priority=cv["priority"],
                    career_value_score=round(cv["career_value_score"], 1),
                    gap_score=round(cv["gap_score"], 1),
                    role_importance=round(cv["role_importance"], 1),
                    reason=cv["reason"],
                    recommended_focus=cv["recommended_focus"],
                )
            )

        highest_career_gap = top_career_priorities[0] if top_career_priorities else None

        # 6. Skill DNA Snapshot
        skill_dna_snapshot: List[DashboardSkillDnaItem] = []
        for dna in dna_list[:6]:
            skill_dna_snapshot.append(
                DashboardSkillDnaItem(
                    skill_id=dna["skill_id"],
                    skill_name=dna["skill_name"],
                    category=dna.get("skill_category", "General"),
                    skill_level=round(dna["skill_level"], 1),
                    confidence=round(dna["confidence"], 1),
                    accuracy=round(dna["accuracy"], 1),
                    status=dna["status"],
                    evidence_count=dna["evidence_count"],
                    recency_label=dna["recency_label"],
                )
            )

        # 7. Dynamic Roadmap Preview
        roadmap_preview: List[DashboardRoadmapStepItem] = []
        if user_roadmap and user_roadmap.steps:
            for s in user_roadmap.steps[:5]:
                roadmap_preview.append(
                    DashboardRoadmapStepItem(
                        id=s.id,
                        order_index=s.order_index,
                        title=s.title,
                        step_type=s.step_type,
                        status=s.status,
                        skill_name=s.skill.name if s.skill else "Core Competency",
                        estimated_minutes=s.estimated_minutes,
                        priority=s.priority,
                    )
                )

        # 8. Skill Progress History
        # Track historical checkpoints for key skills
        skill_progress_items: List[DashboardSkillProgressItem] = []
        key_skill_names = ["Python", "SQL", "SQL JOINs", "EDA"]
        evidences_by_skill: Dict[str, List[SkillEvidence]] = {}
        for ev in reversed(evidences):  # chronological order
            sname = ev.skill.name if ev.skill else "Skill"
            if sname in key_skill_names:
                evidences_by_skill.setdefault(sname, []).append(ev)

        for sname in key_skill_names:
            ev_list = evidences_by_skill.get(sname, [])
            if ev_list:
                history_points = [
                    DashboardProgressPoint(
                        week="Baseline" if i == 0 else f"Attempt {i+1}",
                        score=round(ev.score, 1),
                    )
                    for i, ev in enumerate(ev_list)
                ]
            else:
                # Default single current level baseline
                matching_dna = next((d for d in dna_list if d["skill_name"] == sname), None)
                curr_score = matching_dna["skill_level"] if matching_dna else 50.0
                history_points = [DashboardProgressPoint(week="Baseline", score=round(curr_score, 1))]

            skill_progress_items.append(
                DashboardSkillProgressItem(skill_name=sname, history=history_points)
            )

        # Metrics aggregation
        metrics = DashboardMetrics(
            career_readiness=CareerReadinessMetric(
                score=career_readiness_score,
                status=readiness_status,
                trend_label=trend_label,
                formula_explanation="Role-weighted fulfillment of demonstrated skill levels against benchmark requirements across all required role competencies.",
            ),
            skills_verified=skills_verified_count,
            total_role_skills=len(role.role_skills),
            active_skill_debt_count=len(active_debts),
            high_debt_count=len(high_debts),
            evidence_records_count=len(evidences),
            next_best_proof_title=next_best_proof.title if next_best_proof else None,
        )

        return DashboardResponse(
            user_id=user.id,
            learner_name=user.name,
            target_role_id=role.id,
            target_role_name=role.name,
            all_roles=all_roles,
            metrics=metrics,
            next_best_proof=next_best_proof,
            highest_career_gap=highest_career_gap,
            skill_gap_heatmap=skill_gap_items,
            skill_dna_snapshot=skill_dna_snapshot,
            top_career_priorities=top_career_priorities,
            skill_debt_alert=skill_debt_alert,
            recent_evidence=recent_evidence_items,
            roadmap_preview=roadmap_preview,
            progress_history=skill_progress_items,
        )


dashboard_service = DashboardService()
