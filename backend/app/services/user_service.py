from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models.user import User, UserSkill
from app.models.role import Role
from app.models.skill import Skill
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return (
            db.query(User)
            .options(joinedload(User.target_role))
            .filter(User.id == user_id)
            .first()
        )

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_all_users(self, db: Session) -> List[User]:
        return (
            db.query(User)
            .options(joinedload(User.target_role))
            .order_by(User.id.asc())
            .all()
        )

    def create_user(self, db: Session, user_in: UserCreate) -> User:
        # Validate target role exists
        if user_in.target_role_id:
            role = db.query(Role).filter(Role.id == user_in.target_role_id).first()
            if not role:
                raise ValueError(f"Target role with ID {user_in.target_role_id} does not exist.")

        user = User(
            name=user_in.name,
            email=user_in.email,
            experience_level=user_in.experience_level or "Intermediate",
            target_role_id=user_in.target_role_id,
            weekly_learning_hours=user_in.weekly_learning_hours or 10,
            learning_goal=user_in.learning_goal,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Initialize UserSkill records for all existing skills in database
        skills = db.query(Skill).all()
        for s in skills:
            us = UserSkill(
                user_id=user.id,
                skill_id=s.id,
                skill_level=0.0,
                confidence=0.0,
                accuracy=0.0,
                difficulty=user_in.experience_level or "Intermediate",
                recency="Not assessed yet",
                evidence_score=0.0,
                last_assessed_at=datetime.utcnow(),
            )
            db.add(us)
        db.commit()

        # Re-fetch user with target role relationship populated
        return self.get_user_by_id(db, user.id) or user

    def update_user(self, db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
        user = self.get_user_by_id(db, user_id)
        if not user:
            return None
        
        if user_in.target_role_id is not None:
            role = db.query(Role).filter(Role.id == user_in.target_role_id).first()
            if not role:
                raise ValueError(f"Target role with ID {user_in.target_role_id} does not exist.")

        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    def get_user_skills(self, db: Session, user_id: int) -> List[UserSkill]:
        return (
            db.query(UserSkill)
            .options(joinedload(UserSkill.skill))
            .filter(UserSkill.user_id == user_id)
            .all()
        )


user_service = UserService()
