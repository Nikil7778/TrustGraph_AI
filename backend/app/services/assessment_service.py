import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from app.models.assessment import Assessment, AssessmentAttempt, AssessmentQuestion
from app.models.user import User, UserSkill
from app.models.evidence import SkillEvidence
from app.schemas.assessment import AssessmentSubmissionCreate, AssessmentAttemptCreate


class AssessmentService:
    def get_all_assessments(self, db: Session) -> List[Assessment]:
        return (
            db.query(Assessment)
            .options(joinedload(Assessment.skill), joinedload(Assessment.questions))
            .all()
        )

    def get_assessment_by_id(self, db: Session, assessment_id: int) -> Optional[Assessment]:
        return (
            db.query(Assessment)
            .options(joinedload(Assessment.skill), joinedload(Assessment.questions))
            .filter(Assessment.id == assessment_id)
            .first()
        )

    def submit_assessment(
        self, db: Session, submission: AssessmentSubmissionCreate
    ) -> Dict[str, Any]:
        # 1. Validate user exists
        user = db.query(User).filter(User.id == submission.user_id).first()
        if not user:
            raise ValueError(f"User with ID {submission.user_id} not found.")

        # 2. Validate assessment exists
        assessment = (
            db.query(Assessment)
            .options(joinedload(Assessment.skill), joinedload(Assessment.questions))
            .filter(Assessment.id == submission.assessment_id)
            .first()
        )
        if not assessment:
            raise ValueError(f"Assessment with ID {submission.assessment_id} not found.")

        # 3. Validate question IDs belong to assessment & check for duplicates
        valid_q_map = {q.id: q for q in assessment.questions}
        submitted_q_ids = set()
        user_answers_map = {}

        for ans in submission.answers:
            if ans.question_id not in valid_q_map:
                raise ValueError(
                    f"Question ID {ans.question_id} does not belong to assessment '{assessment.title}' (ID {assessment.id})."
                )
            if ans.question_id in submitted_q_ids:
                raise ValueError(f"Duplicate answer submitted for question ID {ans.question_id}.")
            submitted_q_ids.add(ans.question_id)
            user_answers_map[ans.question_id] = ans.answer

        # 4. Deterministic score calculation
        total_questions = len(assessment.questions)
        raw_score = 0
        question_breakdown = []

        for q in assessment.questions:
            user_ans_raw = user_answers_map.get(q.id, "").strip()
            is_correct = False

            # Parse options list
            options_list = []
            if isinstance(q.options, str):
                try:
                    options_list = json.loads(q.options)
                except Exception:
                    options_list = [q.options]
            elif isinstance(q.options, list):
                options_list = q.options

            correct_str = (q.correct_answer or "").strip()

            if user_ans_raw:
                # Direct string match (case-insensitive)
                if user_ans_raw.lower() == correct_str.lower():
                    is_correct = True
                else:
                    # Check letter index (A=0, B=1, C=2, D=3)
                    letter_idx = None
                    if len(user_ans_raw) == 1 and user_ans_raw.upper() in ["A", "B", "C", "D"]:
                        letter_idx = ord(user_ans_raw.upper()) - 65
                    elif user_ans_raw.isdigit():
                        letter_idx = int(user_ans_raw)

                    if letter_idx is not None and 0 <= letter_idx < len(options_list):
                        selected_opt_text = options_list[letter_idx].strip()
                        if selected_opt_text.lower() == correct_str.lower():
                            is_correct = True

                    # Reverse check if correct_answer was letter (A/B/C/D)
                    if not is_correct and len(correct_str) == 1 and correct_str.upper() in ["A", "B", "C", "D"]:
                        correct_letter_idx = ord(correct_str.upper()) - 65
                        if 0 <= correct_letter_idx < len(options_list):
                            if options_list[correct_letter_idx].strip().lower() == user_ans_raw.lower():
                                is_correct = True

            if is_correct:
                raw_score += 1

            question_breakdown.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "user_answer": user_ans_raw if user_ans_raw else "Unanswered",
                "correct_answer": correct_str,
                "is_correct": is_correct,
                "explanation": q.explanation,
            })

        percentage = round((raw_score / total_questions * 100.0), 1) if total_questions > 0 else 0.0
        percentage = max(0.0, min(100.0, percentage))
        accuracy = percentage

        # Deterministic interpretation
        if percentage >= 90.0:
            interpretation = "Strong"
        elif percentage >= 75.0:
            interpretation = "Healthy"
        elif percentage >= 50.0:
            interpretation = "Developing"
        else:
            interpretation = "Critical Gap"

        now = datetime.utcnow()

        # 5. Save AssessmentAttempt
        attempt = AssessmentAttempt(
            user_id=submission.user_id,
            assessment_id=submission.assessment_id,
            score=percentage,
            accuracy=accuracy,
            completed_at=now,
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        # 6. Save SkillEvidence
        skill_name = assessment.skill.name if assessment.skill else "Skill"
        evidence = SkillEvidence(
            user_id=submission.user_id,
            skill_id=assessment.skill_id,
            source=f"Diagnostic Assessment: {assessment.title}",
            evidence_type="ASSESSMENT",
            score=percentage,
            description=f"Diagnostic {assessment.title} result: {raw_score}/{total_questions} correct ({percentage:.0f}%)",
            created_at=now,
        )
        db.add(evidence)
        db.commit()

        # 7. Recalculate Skill DNA & Update UserSkill & Roadmap
        from app.services.skill_dna_service import skill_dna_service
        skill_dna_service.recalculate_skill_dna(db, submission.user_id, assessment.skill_id)
        from app.services.roadmap_service import roadmap_service
        roadmap_service.refresh_learning_state(db, submission.user_id)

        return {
            "attempt_id": attempt.id,
            "user_id": submission.user_id,
            "assessment_id": submission.assessment_id,
            "assessment_title": assessment.title,
            "skill_name": skill_name,
            "raw_score": raw_score,
            "total_questions": total_questions,
            "percentage": percentage,
            "accuracy": accuracy,
            "difficulty": assessment.difficulty,
            "completed_at": now,
            "interpretation": interpretation,
            "question_breakdown": question_breakdown,
        }

    def create_assessment_attempt(
        self, db: Session, attempt_in: AssessmentAttemptCreate
    ) -> AssessmentAttempt:
        attempt = AssessmentAttempt(
            user_id=attempt_in.user_id,
            assessment_id=attempt_in.assessment_id,
            score=attempt_in.score,
            accuracy=attempt_in.accuracy,
            completed_at=datetime.utcnow(),
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        assessment = db.query(Assessment).filter(Assessment.id == attempt_in.assessment_id).first()
        if assessment:
            user_skill = (
                db.query(UserSkill)
                .filter(
                    UserSkill.user_id == attempt_in.user_id,
                    UserSkill.skill_id == assessment.skill_id,
                )
                .first()
            )
            if user_skill:
                user_skill.accuracy = round(attempt_in.accuracy, 1)
                user_skill.skill_level = round(attempt_in.score, 1)
                user_skill.last_assessed_at = datetime.utcnow()
                db.commit()

        return attempt

    def get_user_assessment_attempts(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        attempts = (
            db.query(AssessmentAttempt)
            .options(joinedload(AssessmentAttempt.assessment).joinedload(Assessment.skill))
            .filter(AssessmentAttempt.user_id == user_id)
            .order_by(AssessmentAttempt.completed_at.desc())
            .all()
        )

        results = []
        for att in attempts:
            title = att.assessment.title if att.assessment else "Assessment"
            skill_name = att.assessment.skill.name if (att.assessment and att.assessment.skill) else "Skill"
            results.append({
                "id": att.id,
                "user_id": att.user_id,
                "assessment_id": att.assessment_id,
                "assessment_title": title,
                "skill_name": skill_name,
                "score": att.score,
                "accuracy": att.accuracy,
                "completed_at": att.completed_at,
            })
        return results


assessment_service = AssessmentService()
