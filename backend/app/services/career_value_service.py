from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.services.skill_dna_service import skill_dna_service
from app.services.skill_debt_service import skill_debt_service
from app.engines.career_value_engine import career_value_engine


class CareerValueService:
    """
    Service coordinating the Career Value Engine with Skill DNA,
    Skill Debt, and Role requirements.
    """

    def calculate_career_value(
        self, db: Session, user_id: int, role_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculates deterministic, ranked career values for all skills
        benchmarked in the learner's target role.
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

        # 1. Fetch Skill DNA vector for user
        dna_list = skill_dna_service.get_user_skill_dna(db, user_id)
        dna_map = {dna["skill_id"]: dna for dna in dna_list}

        # 2. Fetch Skill Debt evaluations for user
        debt_list = skill_debt_service.calculate_skill_debt(db, user_id, target_role_id)
        debt_map = {d["skill_id"]: d for d in debt_list}

        results: List[Dict[str, Any]] = []

        for rs in role.role_skills:
            skill = rs.skill
            if not skill:
                continue

            dna = dna_map.get(skill.id, {})
            debt_item = debt_map.get(skill.id)

            curr_level = dna.get("skill_level", 0.0)
            confidence = dna.get("confidence", 0.0)
            recency = dna.get("recency", 0.0)
            evidence_score = dna.get("evidence_score", 0.0)

            evaluated = career_value_engine.evaluate_career_value(
                skill_id=skill.id,
                skill_name=skill.name,
                skill_category=skill.category,
                role_id=role.id,
                role_name=role.name,
                current_skill_level=curr_level,
                required_skill_level=float(rs.required_level),
                role_importance=float(rs.importance_score),
                industry_relevance_raw=rs.industry_relevance,
                confidence=confidence,
                recency=recency,
                evidence_score=evidence_score,
                skill_debt_item=debt_item,
            )
            results.append(evaluated)

        # Sort deterministically:
        # 1. career_value_score descending
        # 2. role_importance descending
        # 3. gap_score descending
        ranked = sorted(
            results,
            key=lambda x: (x["career_value_score"], x["role_importance"], x["gap_score"]),
            reverse=True,
        )

        for idx, item in enumerate(ranked):
            item["rank"] = idx + 1

        return ranked

    def get_single_career_value(
        self, db: Session, user_id: int, skill_id: int, role_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieves evaluated career value for a single skill.
        """
        all_values = self.calculate_career_value(db, user_id, role_id)
        item = next((v for v in all_values if v["skill_id"] == skill_id), None)
        if not item:
            # Fallback if skill is not part of target role
            user = db.query(User).filter(User.id == user_id).first()
            skill = db.query(Skill).filter(Skill.id == skill_id).first()
            if not user or not skill:
                raise ValueError(f"User {user_id} or Skill {skill_id} not found.")

            target_role_id = role_id or user.target_role_id or 1
            role = db.query(Role).filter(Role.id == target_role_id).first()
            role_name = role.name if role else "Target Role"

            dna = skill_dna_service.get_single_skill_dna(db, user_id, skill_id)
            debt_item = skill_debt_service.get_single_skill_debt(db, user_id, skill_id, target_role_id)

            evaluated = career_value_engine.evaluate_career_value(
                skill_id=skill.id,
                skill_name=skill.name,
                skill_category=skill.category,
                role_id=target_role_id,
                role_name=role_name,
                current_skill_level=dna.get("skill_level", 0.0),
                required_skill_level=80.0,
                role_importance=70.0,
                industry_relevance_raw="High",
                confidence=dna.get("confidence", 0.0),
                recency=dna.get("recency", 0.0),
                evidence_score=dna.get("evidence_score", 0.0),
                skill_debt_item=debt_item,
            )
            evaluated["rank"] = 1
            return evaluated

        return item

    def recalculate_career_value(
        self, db: Session, user_id: int, role_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Recalculates current Skill DNA and Skill Debt from source-of-truth evidence,
        then returns freshly calculated Career Value priorities.
        """
        skill_dna_service.recalculate_all_user_skill_dna(db, user_id)
        skill_debt_service.recalculate_skill_debt(db, user_id, role_id)
        return self.calculate_career_value(db, user_id, role_id)


career_value_service = CareerValueService()
