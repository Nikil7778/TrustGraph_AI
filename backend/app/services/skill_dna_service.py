from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User, UserSkill
from app.models.skill import Skill
from app.models.evidence import SkillEvidence
from app.engines.skill_dna_engine import skill_dna_engine


class SkillDNAService:
    def recalculate_skill_dna(
        self, db: Session, user_id: int, skill_id: int
    ) -> Dict[str, Any]:
        """
        Recalculates multi-dimensional Skill DNA for a specific user and skill from evidence history.
        Persists updated scores to UserSkill and returns the Skill DNA profile.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise ValueError(f"Skill with ID {skill_id} not found.")

        evidences = (
            db.query(SkillEvidence)
            .filter(
                SkillEvidence.user_id == user_id,
                SkillEvidence.skill_id == skill_id,
            )
            .order_by(SkillEvidence.created_at.desc())
            .all()
        )

        user_skill = (
            db.query(UserSkill)
            .filter(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == skill_id,
            )
            .first()
        )

        user_diff_label = user_skill.difficulty if user_skill else "Intermediate"

        dna = skill_dna_engine.compute_skill_dna(
            user_id=user_id,
            skill_id=skill_id,
            skill_name=skill.name,
            skill_category=skill.category,
            evidences=evidences,
            user_skill_difficulty=user_diff_label,
        )

        # Update or create UserSkill DB record
        if not user_skill:
            if len(evidences) > 0:
                user_skill = UserSkill(
                    user_id=user_id,
                    skill_id=skill_id,
                    skill_level=dna["skill_level"],
                    confidence=dna["confidence"],
                    accuracy=dna["accuracy"],
                    difficulty=dna["difficulty_label"],
                    recency=dna["recency_label"],
                    evidence_score=dna["evidence_score"],
                    last_assessed_at=dna["last_assessed_at"],
                )
                db.add(user_skill)
        else:
            user_skill.accuracy = dna["accuracy"]
            user_skill.confidence = dna["confidence"]
            user_skill.skill_level = dna["skill_level"]
            user_skill.evidence_score = dna["evidence_score"]
            user_skill.difficulty = dna["difficulty_label"]
            user_skill.recency = dna["recency_label"]
            user_skill.last_assessed_at = dna["last_assessed_at"]

        db.commit()
        return dna

    def recalculate_all_user_skill_dna(
        self, db: Session, user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Recalculates Skill DNA for all skills for a user.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        skills = db.query(Skill).all()
        results = []
        for s in skills:
            dna = self.recalculate_skill_dna(db, user_id, s.id)
            results.append(dna)
        return results

    def get_user_skill_dna(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves current Skill DNA profiles for all skills for a user.
        Recalculates dynamically to ensure recency and evidence values are fresh.
        """
        return self.recalculate_all_user_skill_dna(db, user_id)

    def get_single_skill_dna(
        self, db: Session, user_id: int, skill_id: int
    ) -> Dict[str, Any]:
        """
        Retrieves current Skill DNA profile for a specific skill.
        """
        return self.recalculate_skill_dna(db, user_id, skill_id)


skill_dna_service = SkillDNAService()
