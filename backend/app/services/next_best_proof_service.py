from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.models.evidence import SkillEvidence
from app.services.skill_dna_service import skill_dna_service
from app.services.career_value_service import career_value_service
from app.engines.next_best_proof_engine import next_best_proof_engine


class NextBestProofService:
    """
    Coordinates Candidate Generation, Evaluation, and Selection for
    the Next-Best-Proof Decision Engine.
    """

    def get_candidates(
        self, db: Session, user_id: int, role_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates and ranks all candidate proof actions across competencies
        of the learner's target role.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        target_role_id = role_id or user.target_role_id
        if not target_role_id:
            first_role = db.query(Role).first()
            target_role_id = first_role.id if first_role else 1

        role = db.query(Role).filter(Role.id == target_role_id).first()
        role_name = role.name if role else "Target Role"

        # 1. Pipeline: Career Value (which incorporates Skill DNA and Skill Debt)
        cv_list = career_value_service.calculate_career_value(db, user_id, target_role_id)

        # 2. Skill DNA vector map
        dna_list = skill_dna_service.get_user_skill_dna(db, user_id)
        dna_map_by_id = {d["skill_id"]: d for d in dna_list}
        dna_map_by_name = {d["skill_name"]: d for d in dna_list}

        # 3. Evidence history
        evidences = (
            db.query(SkillEvidence)
            .filter(SkillEvidence.user_id == user_id)
            .order_by(SkillEvidence.created_at.desc())
            .all()
        )
        evidence_map: Dict[int, List[SkillEvidence]] = {}
        for ev in evidences:
            evidence_map.setdefault(ev.skill_id, []).append(ev)

        candidates = []
        for cv_item in cv_list:
            s_id = cv_item["skill_id"]
            s_dna = dna_map_by_id.get(s_id, {})
            s_evs = evidence_map.get(s_id, [])

            candidate = next_best_proof_engine.evaluate_candidate(
                user_id=user_id,
                role_id=target_role_id,
                role_name=role_name,
                career_value_item=cv_item,
                skill_dna=s_dna,
                all_skills_dna_map=dna_map_by_name,
                evidences=s_evs,
            )
            candidates.append(candidate)

        # Sort deterministically:
        # 1. next_best_proof_score descending
        # 2. career_value_score descending
        # 3. skill_debt_score descending
        ranked = sorted(
            candidates,
            key=lambda x: (
                x["next_best_proof_score"],
                x["career_value_score"],
                x["skill_debt_score"],
            ),
            reverse=True,
        )

        for idx, item in enumerate(ranked):
            item["rank"] = idx + 1

        return ranked

    def get_next_best_proof(
        self, db: Session, user_id: int, role_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Selects the single highest-impact Next-Best-Proof action for the learner.
        For a brand-new learner with no verified evidence, prescribes baseline diagnostic assessment.
        """
        user = db.query(User).filter(User.id == user_id).first()
        target_role_id = role_id or (user.target_role_id if user else None) or 1
        role = db.query(Role).filter(Role.id == target_role_id).first()
        role_name = role.name if role else "Target Role"

        total_ev_count = db.query(SkillEvidence).filter(SkillEvidence.user_id == user_id).count()
        if total_ev_count == 0:
            first_skill = role.role_skills[0].skill if (role and role.role_skills) else None
            return {
                "user_id": user_id,
                "role_id": target_role_id,
                "role_name": role_name,
                "skill_id": first_skill.id if first_skill else 1,
                "skill_name": first_skill.name if first_skill else "Diagnostic",
                "skill_category": "Diagnostic Assessment",
                "action_type": "REASSESS",
                "action_type_label": "Diagnostic Assessment",
                "title": "Complete Diagnostic Assessment",
                "priority": "HIGH",
                "next_best_proof_score": 100.0,
                "current_skill_level": 0.0,
                "required_skill_level": 80.0,
                "career_value_score": 90.0,
                "skill_debt_score": 0.0,
                "skill_debt_status": "MISSING",
                "confidence": 0.0,
                "evidence_score": 0.0,
                "practical_evidence_score": 0.0,
                "estimated_minutes": 20,
                "expected_proof": "Complete your baseline diagnostic assessment to calibrate your Skill DNA.",
                "reason": "Complete your diagnostic assessment to identify your highest-impact skill gaps and build your personalized career roadmap.",
                "why_now": "Baseline diagnostic evaluation is required before personalized proof recommendations can be derived.",
                "why_this_action": "We'll use your assessment results to build your Skill DNA and create a personalized career roadmap.",
                "prerequisites": [],
                "action_readiness": "HIGH",
                "rank": 1,
                "created_at": datetime.utcnow(),
            }

        candidates = self.get_candidates(db, user_id, role_id)
        if not candidates:
            raise ValueError(f"No candidates generated for user {user_id}.")
        return candidates[0]

    def recalculate_next_best_proof(
        self, db: Session, user_id: int, role_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Recalculates underlying evidence, Skill DNA, Skill Debt, Career Value,
        and returns the freshly selected Next-Best-Proof action.
        """
        career_value_service.recalculate_career_value(db, user_id, role_id)
        return self.get_next_best_proof(db, user_id, role_id)

    def complete_proof_action(
        self,
        db: Session,
        user_id: int,
        skill_id: int,
        action_type: str,
        score: float,
        description: str,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes proof completion workflow:
        1. Persists SkillEvidence audit record
        2. Recalculates Skill DNA, Skill Debt, Career Value, and Next-Best-Proof
        3. Returns updated Next-Best-Proof recommendation
        """
        source_label = source or f"Completed {action_type.replace('_', ' ').title()}"
        ev = SkillEvidence(
            user_id=user_id,
            skill_id=skill_id,
            source=source_label,
            evidence_type=action_type,
            score=score,
            description=description,
            created_at=datetime.utcnow(),
        )
        db.add(ev)
        db.commit()

        # Cascade recalculations across all engines and refresh roadmap
        res = self.recalculate_next_best_proof(db, user_id)
        from app.services.roadmap_service import roadmap_service
        roadmap_service.refresh_learning_state(db, user_id)
        return res


next_best_proof_service = NextBestProofService()
