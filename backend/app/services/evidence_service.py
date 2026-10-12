from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models.evidence import SkillEvidence
from app.schemas.evidence import SkillEvidenceCreate


class EvidenceService:
    def get_user_evidences(self, db: Session, user_id: int) -> List[SkillEvidence]:
        return (
            db.query(SkillEvidence)
            .options(joinedload(SkillEvidence.skill))
            .filter(SkillEvidence.user_id == user_id)
            .order_by(SkillEvidence.created_at.desc())
            .all()
        )

    def create_evidence(self, db: Session, evidence_in: SkillEvidenceCreate) -> SkillEvidence:
        evidence = SkillEvidence(
            user_id=evidence_in.user_id,
            skill_id=evidence_in.skill_id,
            source=evidence_in.source,
            evidence_type=evidence_in.evidence_type,
            score=evidence_in.score,
            description=evidence_in.description,
            created_at=datetime.utcnow(),
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        # Recalculate Skill DNA and refresh dynamic roadmap
        from app.services.skill_dna_service import skill_dna_service
        skill_dna_service.recalculate_skill_dna(db, evidence_in.user_id, evidence_in.skill_id)
        from app.services.roadmap_service import roadmap_service
        roadmap_service.refresh_learning_state(db, evidence_in.user_id)

        return evidence


evidence_service = EvidenceService()
