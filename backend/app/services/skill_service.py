from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.models.user import User


class SkillService:

    def get_all_roles(self, db: Session) -> List[Role]:
        return (
            db.query(Role)
            .options(joinedload(Role.role_skills).joinedload(RoleSkill.skill))
            .all()
        )

    def get_role_by_id(self, db: Session, role_id: int) -> Optional[Role]:
        return (
            db.query(Role)
            .options(joinedload(Role.role_skills).joinedload(RoleSkill.skill))
            .filter(Role.id == role_id)
            .first()
        )

    def get_all_skills(self, db: Session) -> List[Skill]:
        return db.query(Skill).all()

    def get_skill_by_id(self, db: Session, skill_id: int) -> Optional[Skill]:
        return db.query(Skill).filter(Skill.id == skill_id).first()

    def get_role_skill_map(self, db: Session, role_id: int) -> Dict[str, Any]:
        role = self.get_role_by_id(db, role_id)
        if not role:
            raise ValueError(f"Role with ID {role_id} not found.")

        # Group skills by category
        categories_dict: Dict[str, List[Dict[str, Any]]] = {}
        all_skills: List[Dict[str, Any]] = []

        for rs in role.role_skills:
            if not rs.skill:
                continue
            skill_info = {
                "id": rs.skill.id,
                "skill_id": rs.skill.id,
                "name": rs.skill.name,
                "category": rs.skill.category,
                "description": rs.skill.description,
                "required_level": rs.required_level,
                "importance_score": rs.importance_score,
                "industry_relevance": rs.industry_relevance,
            }

            cat = rs.skill.category or "General Competencies"
            if cat not in categories_dict:
                categories_dict[cat] = []
            categories_dict[cat].append(skill_info)
            all_skills.append(skill_info)

        categories = [
            {"category_name": cat, "skills": s_list}
            for cat, s_list in categories_dict.items()
        ]

        return {
            "role_id": role.id,
            "role_name": role.name,
            "description": role.description,
            "total_skills": len(all_skills),
            "categories": categories,
            "skills": all_skills,
        }

    def create_custom_role(
        self, db: Session, name: str, description: Optional[str] = None, skill_names: Optional[List[str]] = None
    ) -> Role:
        clean_name = name.strip()
        existing = db.query(Role).filter(Role.name.ilike(clean_name)).first()
        if existing:
            return existing

        role = Role(
            name=clean_name,
            description=description or f"Custom personalized target career goal: {clean_name}",
        )
        db.add(role)
        db.commit()
        db.refresh(role)

        skills_to_link = skill_names or [
            "Python",
            "SQL Basics",
            "Git",
            "HTTP & REST APIs",
            "Unit Testing",
        ]
        for s_name in skills_to_link:
            s_clean = s_name.strip()
            s_obj = db.query(Skill).filter(Skill.name.ilike(s_clean)).first()
            if not s_obj:
                s_obj = Skill(name=s_clean, category="Custom Goal Competency", description=f"Skill required for {clean_name}")
                db.add(s_obj)
                db.commit()
                db.refresh(s_obj)

            rs = RoleSkill(
                role_id=role.id,
                skill_id=s_obj.id,
                importance_score=85,
                industry_relevance="High",
                required_level=80,
            )
            db.add(rs)
        db.commit()
        db.refresh(role)
        return role

    def get_skill_gap_analysis(
        self, db: Session, user_id: int, role_id: Optional[int] = None
    ) -> Dict[str, Any]:
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

        user_skills = {us.skill_id: us for us in user.user_skills}

        all_gaps = []
        strong_skills = []
        moderate_skills = []
        weak_skills = []
        missing_skills = []
        progress_sum = 0.0

        for rs in role.role_skills:
            if not rs.skill:
                continue
            skill = rs.skill
            us = user_skills.get(skill.id)
            current_level = round(us.skill_level, 1) if us else 0.0
            required_level = rs.required_level
            gap = max(0.0, round(required_level - current_level, 1))

            if current_level >= required_level or current_level >= 75.0:
                status = "Strong"
                strong_skills.append(skill.name)
            elif current_level >= 50.0:
                status = "Moderate"
                moderate_skills.append(skill.name)
            elif current_level > 0.0:
                status = "Weak"
                weak_skills.append(skill.name)
            else:
                status = "Missing"
                missing_skills.append(skill.name)

            pct_met = min(100.0, (current_level / required_level * 100.0)) if required_level > 0 else 0.0
            progress_sum += pct_met

            all_gaps.append({
                "skill_id": skill.id,
                "skill_name": skill.name,
                "category": skill.category or "General Competencies",
                "current_level": current_level,
                "required_level": required_level,
                "gap": gap,
                "importance_score": rs.importance_score,
                "industry_relevance": rs.industry_relevance,
                "status": status,
            })

        all_gaps.sort(key=lambda x: (x["gap"], x["importance_score"]), reverse=True)
        overall_progress = round(progress_sum / len(role.role_skills), 1) if role.role_skills else 0.0

        next_action = None
        if all_gaps:
            top_gap = all_gaps[0]
            next_action = {
                "title": f"Master {top_gap['skill_name']} – Core Competency",
                "skill_id": top_gap["skill_id"],
                "skill_name": top_gap["skill_name"],
                "current_level": top_gap["current_level"],
                "required_level": top_gap["required_level"],
                "gap": top_gap["gap"],
                "status": top_gap["status"],
                "reason": (
                    f"Your {top_gap['skill_name']} skill is currently {top_gap['current_level']}%, "
                    f"and it is one of the largest remaining gaps ({top_gap['gap']}% gap) for your target goal of {role.name}."
                ),
            }

        return {
            "user_id": user.id,
            "role_id": role.id,
            "role_name": role.name,
            "overall_progress": overall_progress,
            "total_skills": len(role.role_skills),
            "strong_count": len(strong_skills),
            "moderate_count": len(moderate_skills),
            "weak_count": len(weak_skills),
            "missing_count": len(missing_skills),
            "strong_skills": strong_skills,
            "moderate_skills": moderate_skills,
            "weak_skills": weak_skills,
            "missing_skills": missing_skills,
            "all_gaps": all_gaps,
            "next_recommended_action": next_action,
        }


skill_service = SkillService()

