from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.user import User, UserSkill
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.models.evidence import SkillEvidence
from app.services.skill_dna_service import skill_dna_service
from app.engines.skill_debt_engine import skill_debt_engine


class SkillDebtService:
    def calculate_skill_debt(
        self, db: Session, user_id: int, role_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculates deterministic Skill Debt for all relevant competencies of the learner's target role.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        target_role_id = role_id or user.target_role_id
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

        # Fetch Skill DNA vectors for all skills of user
        dna_list = skill_dna_service.get_user_skill_dna(db, user_id)
        dna_map = {dna["skill_id"]: dna for dna in dna_list}

        # Fetch all evidence for user
        all_evidences = (
            db.query(SkillEvidence)
            .filter(SkillEvidence.user_id == user_id)
            .order_by(SkillEvidence.created_at.desc())
            .all()
        )
        evidence_map: Dict[int, List[SkillEvidence]] = {}
        for ev in all_evidences:
            evidence_map.setdefault(ev.skill_id, []).append(ev)

        results = []
        for rs in role.role_skills:
            skill = rs.skill
            if not skill:
                continue

            dna = dna_map.get(skill.id, {})
            evs = evidence_map.get(skill.id, [])

            debt_item = skill_debt_engine.evaluate_skill_debt(
                skill_id=skill.id,
                skill_name=skill.name,
                skill_category=skill.category,
                role_id=role.id,
                role_name=role.name,
                role_requirement=float(rs.required_level),
                importance_score=float(rs.importance_score),
                skill_dna=dna,
                evidences=evs,
            )
            results.append(debt_item)

        # Sort by debt_score descending (highest priority debt first)
        return sorted(results, key=lambda x: x["debt_score"], reverse=True)

    def get_single_skill_debt(
        self, db: Session, user_id: int, skill_id: int, role_id: Optional[int] = None
    ) -> Dict[str, Any]:
        all_debt = self.calculate_skill_debt(db, user_id, role_id)
        item = next((d for d in all_debt if d["skill_id"] == skill_id), None)
        if not item:
            # Fallback if skill is not part of role skills directly
            user = db.query(User).filter(User.id == user_id).first()
            skill = db.query(Skill).filter(Skill.id == skill_id).first()
            if not user or not skill:
                raise ValueError(f"User {user_id} or Skill {skill_id} not found.")

            target_role_id = role_id or user.target_role_id or 1
            role = db.query(Role).filter(Role.id == target_role_id).first()
            role_name = role.name if role else "Target Role"

            dna = skill_dna_service.get_single_skill_dna(db, user_id, skill_id)
            evs = (
                db.query(SkillEvidence)
                .filter(SkillEvidence.user_id == user_id, SkillEvidence.skill_id == skill_id)
                .all()
            )
            return skill_debt_engine.evaluate_skill_debt(
                skill_id=skill.id,
                skill_name=skill.name,
                skill_category=skill.category,
                role_id=target_role_id,
                role_name=role_name,
                role_requirement=80.0,
                importance_score=75.0,
                skill_dna=dna,
                evidences=evs,
            )
        return item

    def recalculate_skill_debt(
        self, db: Session, user_id: int, role_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        # Recalculates Skill DNA first to ensure evidence trends are fresh
        skill_dna_service.recalculate_all_user_skill_dna(db, user_id)
        return self.calculate_skill_debt(db, user_id, role_id)


skill_debt_service = SkillDebtService()
