from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models.roadmap import Roadmap, RoadmapStep, RoadmapChange
from app.models.user import User
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.services.skill_dna_service import skill_dna_service
from app.services.skill_debt_service import skill_debt_service
from app.services.career_value_service import career_value_service
from app.services.next_best_proof_service import next_best_proof_service
from app.engines.roadmap_engine import roadmap_engine


class RoadmapService:
    def get_user_roadmap(self, db: Session, user_id: int) -> Optional[Roadmap]:
        """
        Fetch the active dynamic roadmap for the user.
        Generates or rebuilds if none exists or if learner's target role has changed.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        roadmap = (
            db.query(Roadmap)
            .options(
                joinedload(Roadmap.target_role),
                joinedload(Roadmap.steps).joinedload(RoadmapStep.skill),
            )
            .filter(Roadmap.user_id == user_id, Roadmap.status == "active")
            .first()
        )
        if not roadmap or (user.target_role_id and roadmap.target_role_id != user.target_role_id):
            return self.generate_dynamic_roadmap(db, user_id, user.target_role_id)
        return roadmap

    def rebuild_user_roadmap(
        self, db: Session, user_id: int, role_id: Optional[int] = None
    ) -> Optional[Roadmap]:
        """
        Explicitly triggers dynamic rebuild of learner's roadmap.
        """
        return self.generate_dynamic_roadmap(db, user_id, role_id)

    def generate_dynamic_roadmap(
        self, db: Session, user_id: int, role_id: Optional[int] = None
    ) -> Optional[Roadmap]:
        """
        Generates an evidence-driven dynamic roadmap for learner.
        1. Load learner target role.
        2. Load RoleSkill requirements.
        3. Load Skill DNA.
        4. Load Skill Debt.
        5. Load Career Value.
        6. Load Next-Best-Proof.
        7. Run RoadmapEngine to resolve DAG dependencies & adaptive remediation.
        8. Version and persist roadmap with deterministic change logging.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        target_role_id = role_id or user.target_role_id or 1
        role = db.query(Role).filter(Role.id == target_role_id).first()
        role_name = role.name if role else "Target Role"

        # Fetch RoleSkills
        role_skills_entities = (
            db.query(RoleSkill)
            .options(joinedload(RoleSkill.skill))
            .filter(RoleSkill.role_id == target_role_id)
            .all()
        )
        role_skills_data = [
            {
                "skill_id": rs.skill_id,
                "skill_name": rs.skill.name if rs.skill else f"Skill {rs.skill_id}",
                "required_level": rs.required_level,
                "importance_score": rs.importance_score,
                "industry_relevance": rs.industry_relevance,
            }
            for rs in role_skills_entities
        ]

        # Fetch current Skill DNA
        dna_list = skill_dna_service.get_user_skill_dna(db, user_id)
        dna_map = {d["skill_id"]: d for d in dna_list}

        # Fetch current Skill Debt
        debt_items = skill_debt_service.calculate_skill_debt(db, user_id, target_role_id)
        debt_map = {d["skill_id"]: d for d in debt_items}

        # Fetch Career Value
        cval_list = career_value_service.calculate_career_value(db, user_id, target_role_id)
        career_values = {s["skill_id"]: s for s in cval_list}

        # Fetch Next-Best-Proof
        candidates = next_best_proof_service.get_candidates(db, user_id, target_role_id)
        nbp = candidates[0] if candidates else None

        # Check existing active roadmap to track version and changes
        existing_active = (
            db.query(Roadmap)
            .options(joinedload(Roadmap.steps).joinedload(RoadmapStep.skill))
            .filter(Roadmap.user_id == user_id, Roadmap.status == "active")
            .first()
        )

        previous_steps = None
        current_version = 1
        if existing_active:
            current_version = existing_active.version + 1
            previous_steps = [
                {
                    "title": s.title,
                    "skill_name": s.skill.name if s.skill else "",
                    "step_type": s.step_type,
                    "status": s.status,
                }
                for s in existing_active.steps
            ]
            # Archive previous roadmap to preserve history
            existing_active.status = "archived"
            db.flush()

        # Run deterministic engine
        engine_steps, reason, changes = roadmap_engine.generate_roadmap(
            user_id=user_id,
            target_role_name=role_name,
            role_skills=role_skills_data,
            dna_map=dna_map,
            debt_map=debt_map,
            career_values=career_values,
            nbp=nbp,
            previous_steps=previous_steps,
        )

        # Create new active roadmap
        new_roadmap = Roadmap(
            user_id=user_id,
            target_role_id=target_role_id,
            version=current_version,
            status="active",
            regeneration_reason=reason,
        )
        db.add(new_roadmap)
        db.flush()

        # Insert new steps
        for st in engine_steps:
            new_step = RoadmapStep(
                roadmap_id=new_roadmap.id,
                skill_id=st["skill_id"],
                title=st["title"],
                step_type=st["step_type"],
                priority=st["priority"],
                status=st["status"],
                reason=st["reason"],
                order_index=st["order_index"],
                estimated_minutes=st["estimated_minutes"],
                prerequisite_step_ids=st.get("prerequisite_step_ids"),
                evidence_required=st.get("evidence_required"),
                module_slug=st.get("module_slug"),
                completed_at=datetime.fromisoformat(st["completed_at"]) if st.get("completed_at") else None,
            )
            db.add(new_step)

        # Insert change records
        for ch in changes:
            change_rec = RoadmapChange(
                user_id=user_id,
                roadmap_id=new_roadmap.id,
                version=current_version,
                change_type=ch["change_type"],
                skill_name=ch["skill_name"],
                title=ch["title"],
                description=ch["description"],
            )
            db.add(change_rec)

        db.commit()

        # Return refreshed roadmap
        return (
            db.query(Roadmap)
            .options(
                joinedload(Roadmap.target_role),
                joinedload(Roadmap.steps).joinedload(RoadmapStep.skill),
            )
            .filter(Roadmap.id == new_roadmap.id)
            .first()
        )

    def refresh_learning_state(self, db: Session, user_id: int) -> Optional[Roadmap]:
        """
        Orchestration flow when new evidence is added:
        Skill DNA -> Skill Debt -> Career Value -> Next-Best-Proof -> Roadmap.
        Ensures consistent sequential recalculation without circular dependencies.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        target_role_id = user.target_role_id or 1

        # 1. Skill DNA (reads latest evidences)
        skill_dna_service.get_user_skill_dna(db, user_id)

        # 2. Skill Debt
        skill_debt_service.calculate_skill_debt(db, user_id, target_role_id)

        # 3. Career Value
        career_value_service.calculate_career_value(db, user_id, target_role_id)

        # 4. Next-Best-Proof
        next_best_proof_service.get_candidates(db, user_id, target_role_id)

        # 5. Roadmap
        return self.generate_dynamic_roadmap(db, user_id, target_role_id)

    def get_roadmap_history(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Returns previous and current roadmap versions.
        """
        roadmaps = (
            db.query(Roadmap)
            .options(
                joinedload(Roadmap.target_role),
                joinedload(Roadmap.steps),
            )
            .filter(Roadmap.user_id == user_id)
            .order_by(Roadmap.version.desc())
            .all()
        )

        history = []
        for r in roadmaps:
            history.append({
                "id": r.id,
                "user_id": r.user_id,
                "target_role_id": r.target_role_id,
                "target_role_name": r.target_role.name if r.target_role else "Target Role",
                "version": r.version,
                "status": r.status,
                "regeneration_reason": r.regeneration_reason,
                "step_count": len(r.steps),
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            })
        return history

    def get_roadmap_changes(self, db: Session, user_id: int) -> List[RoadmapChange]:
        """
        Returns recent roadmap changes and deterministic reasons.
        """
        return (
            db.query(RoadmapChange)
            .filter(RoadmapChange.user_id == user_id)
            .order_by(RoadmapChange.created_at.desc(), RoadmapChange.id.desc())
            .all()
        )


roadmap_service = RoadmapService()
