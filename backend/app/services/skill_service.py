from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.role import Role, RoleSkill
from app.models.skill import Skill


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


skill_service = SkillService()
