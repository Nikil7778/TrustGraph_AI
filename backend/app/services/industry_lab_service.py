import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.industry_lab import IndustryLab, IndustryLabTask, IndustryLabAttempt
from app.models.evidence import SkillEvidence
from app.models.skill import Skill
from app.models.user import User
from app.engines.industry_lab_engine import industry_lab_engine
from app.services.skill_dna_service import SkillDNAService
from app.services.roadmap_service import roadmap_service
from app.schemas.industry_lab import (
    IndustryLabResponse,
    IndustryLabTaskResponse,
    IndustryLabQueryRunResponse,
    IndustryLabSubmitResponse,
    IndustryLabSectionScores,
    IndustryLabTablePreview,
    IndustryLabTableColumnInfo,
)


class IndustryLabService:
    def __init__(self):
        self.skill_dna_service = SkillDNAService()

    def get_labs(
        self,
        db: Session,
        role_id: Optional[int] = None,
        skill_id: Optional[int] = None,
    ) -> List[IndustryLab]:
        query = db.query(IndustryLab)
        if role_id:
            query = query.filter(IndustryLab.target_role_id == role_id)
        if skill_id:
            query = query.filter(IndustryLab.primary_skill_id == skill_id)
        return query.all()

    def get_lab(self, db: Session, identifier: str) -> IndustryLab:
        if identifier.isdigit():
            lab = db.query(IndustryLab).filter(IndustryLab.id == int(identifier)).first()
        else:
            lab = db.query(IndustryLab).filter(IndustryLab.slug == identifier).first()

        if not lab:
            raise HTTPException(status_code=404, detail=f"Industry Lab '{identifier}' not found.")
        return lab

    def get_lab_preview(self, db: Session, identifier: str) -> List[IndustryLabTablePreview]:
        lab = self.get_lab(db, identifier)
        conn = sqlite3.connect("skillpath.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        previews = []
        # Retail sandbox tables
        tables_meta = [
            {
                "table_name": "lab_retail_customers",
                "quality_notes": ["Contains 10 customer accounts across Enterprise, Mid-Market, and SMB segments."],
            },
            {
                "table_name": "lab_retail_orders",
                "quality_notes": [
                    "Contains order records.",
                    "Payment status includes 'COMPLETED', 'CANCELLED', and 'PENDING'. Filter by 'COMPLETED' for actual realized revenue.",
                ],
            },
            {
                "table_name": "lab_retail_returns",
                "quality_notes": [
                    "Contains return records with refund amounts.",
                    "Orders with zero returns have no rows here; require LEFT JOIN to preserve non-returned orders.",
                ],
            },
            {
                "table_name": "lab_retail_products",
                "quality_notes": ["Master catalog of products, categories, cost and list prices."],
            },
        ]

        for t in tables_meta:
            table_name = t["table_name"]
            try:
                # Column info
                pragma_cols = cur.execute(f"PRAGMA table_info({table_name})").fetchall()
                cols = [
                    IndustryLabTableColumnInfo(name=c[1], type=c[2])
                    for c in pragma_cols
                ]

                # Row count
                row_count = cur.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

                # Sample rows
                sample_raw = cur.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchall()
                sample_rows = [dict(r) for r in sample_raw]

                previews.append(
                    IndustryLabTablePreview(
                        table_name=table_name,
                        row_count=row_count,
                        columns=cols,
                        sample_rows=sample_rows,
                        quality_notes=t["quality_notes"],
                    )
                )
            except Exception:
                continue

        conn.close()
        return previews

    def run_query(self, db: Session, identifier: str, query: str) -> IndustryLabQueryRunResponse:
        lab = self.get_lab(db, identifier)
        res = industry_lab_engine.run_sandbox_query(query, db_path="skillpath.db")
        return IndustryLabQueryRunResponse(
            success=res["success"],
            columns=res["columns"],
            rows=res["rows"],
            row_count=res["row_count"],
            execution_time_ms=res["execution_time_ms"],
            error_message=res["error_message"],
        )

    def submit_attempt(
        self,
        db: Session,
        identifier: str,
        user_id: int,
        query: str,
        submitted_answer: Optional[str] = None,
        evidence_type: str = "PRACTICE",
    ) -> IndustryLabSubmitResponse:
        lab = self.get_lab(db, identifier)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")

        # Determine attempt number
        prev_attempts = (
            db.query(IndustryLabAttempt)
            .filter(
                IndustryLabAttempt.lab_id == lab.id,
                IndustryLabAttempt.user_id == user_id,
            )
            .count()
        )
        attempt_number = prev_attempts + 1

        # Run 4-pillar evaluation
        eval_result = industry_lab_engine.evaluate_general_query(
            lab_slug=lab.slug,
            query=query,
            submitted_answer=submitted_answer,
            db_path="skillpath.db",
        )

        section_scores = eval_result["section_scores"]

        attempt = IndustryLabAttempt(
            lab_id=lab.id,
            user_id=user_id,
            attempt_number=attempt_number,
            status=eval_result["status"],
            total_score=eval_result["total_score"],
            sql_score=section_scores["sql_correctness"],
            data_quality_score=section_scores["data_quality_handling"],
            business_score=section_scores["business_result"],
            validation_score=section_scores["validation_reasoning"],
            submitted_query=query,
            submitted_answer=submitted_answer,
            feedback=eval_result["feedback"],
            execution_time_ms=eval_result["execution_time_ms"],
            created_at=datetime.utcnow(),
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        evidence_dict = None
        # If score >= 60.0 or PASSED, create verifiable skill evidence and refresh learning state
        if eval_result["total_score"] >= 60.0:
            evidence = SkillEvidence(
                user_id=user_id,
                skill_id=lab.primary_skill_id,
                source=f"Industry Lab: {lab.title}",
                evidence_type=evidence_type,
                score=eval_result["total_score"],
                description=(
                    f"Successfully executed industry sandbox task #{attempt_number} with "
                    f"score of {eval_result['total_score']}% ({eval_result['status']}). "
                    f"Evaluated across SQL correctness, data quality handling, and business KPI derivation."
                ),
                created_at=datetime.utcnow(),
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)

            attempt.evidence_id = evidence.id
            db.commit()

            evidence_dict = {
                "id": evidence.id,
                "skill_id": evidence.skill_id,
                "evidence_type": evidence.evidence_type,
                "score": evidence.score,
                "description": evidence.description,
            }

            # Recalculate Skill DNA and refresh dynamic roadmap
            try:
                self.skill_dna_service.recalculate_skill_dna(db, user_id=user_id, skill_id=lab.primary_skill_id)
                roadmap_service.refresh_learning_state(db, user_id=user_id)
            except Exception as e:
                print(f"[Warning] Post-attempt state refresh error: {e}")

        return IndustryLabSubmitResponse(
            attempt_id=attempt.id,
            user_id=user_id,
            lab_id=lab.id,
            lab_title=lab.title,
            attempt_number=attempt.attempt_number,
            status=attempt.status,
            total_score=attempt.total_score,
            section_scores=IndustryLabSectionScores(
                sql_correctness=attempt.sql_score,
                data_quality_handling=attempt.data_quality_score,
                business_result=attempt.business_score,
                validation_reasoning=attempt.validation_score,
            ),
            feedback=attempt.feedback or "",
            diagnostic_failures=eval_result.get("diagnostic_failures", []),
            evidence_generated=evidence_dict,
            execution_time_ms=attempt.execution_time_ms,
            created_at=attempt.created_at,
        )

    def get_user_attempts(self, db: Session, identifier: str, user_id: int) -> List[IndustryLabAttempt]:
        lab = self.get_lab(db, identifier)
        return (
            db.query(IndustryLabAttempt)
            .filter(
                IndustryLabAttempt.lab_id == lab.id,
                IndustryLabAttempt.user_id == user_id,
            )
            .order_by(IndustryLabAttempt.created_at.desc())
            .all()
        )


industry_lab_service = IndustryLabService()
