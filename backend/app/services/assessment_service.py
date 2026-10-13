import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from app.models.assessment import Assessment, AssessmentAttempt, AssessmentQuestion
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.models.user import User, UserSkill
from app.models.evidence import SkillEvidence
from app.schemas.assessment import (
    AssessmentSubmissionCreate,
    AssessmentAttemptCreate,
    GoalAssessmentSubmission,
)



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
            now = datetime.utcnow()
            ev = SkillEvidence(
                user_id=attempt_in.user_id,
                skill_id=assessment.skill_id,
                source=f"Diagnostic Assessment: {assessment.title}",
                evidence_type="ASSESSMENT",
                score=attempt_in.score,
                description=f"Diagnostic assessment {assessment.title} completed with score {attempt_in.score:.1f}%",
                created_at=now,
            )
            db.add(ev)
            db.commit()

            from app.services.skill_dna_service import skill_dna_service
            skill_dna_service.recalculate_skill_dna(db, attempt_in.user_id, assessment.skill_id)
            from app.services.roadmap_service import roadmap_service
            roadmap_service.refresh_learning_state(db, attempt_in.user_id)

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

    def get_or_create_goal_assessment(self, db: Session, role_id: int) -> Assessment:
        role = (
            db.query(Role)
            .options(joinedload(Role.role_skills).joinedload(RoleSkill.skill))
            .filter(Role.id == role_id)
            .first()
        )
        if not role:
            raise ValueError(f"Target goal with ID {role_id} not found.")

        assessment = (
            db.query(Assessment)
            .options(
                joinedload(Assessment.skill),
                joinedload(Assessment.questions).joinedload(AssessmentQuestion.skill),
            )
            .filter(Assessment.role_id == role_id)
            .first()
        )

        if not assessment:
            primary_skill_id = role.role_skills[0].skill_id if role.role_skills else None
            assessment = Assessment(
                title=f"{role.name} Initial Diagnostic Assessment",
                description=f"Personalized skill gap assessment for {role.name}. Evaluates core competencies across all domains.",
                skill_id=primary_skill_id,
                role_id=role.id,
                difficulty="Adaptive Diagnostic",
            )
            db.add(assessment)
            db.commit()
            db.refresh(assessment)

            # Seed diagnostic questions for each skill in role if none exist
            for rs in role.role_skills:
                skill = rs.skill
                if not skill:
                    continue
                q1 = AssessmentQuestion(
                    assessment_id=assessment.id,
                    skill_id=skill.id,
                    question_text=f"Which of the following best describes the core architectural purpose or primary use case of {skill.name}?",
                    options=json.dumps([
                        f"Enables modular, scalable, and standardized implementation for {skill.name}.",
                        "Acts solely as an optional configuration layer with no runtime effect.",
                        "Replaces all underlying network and storage protocols entirely.",
                        "Used exclusively for legacy compatibility in deprecated environments.",
                    ]),
                    correct_answer=f"Enables modular, scalable, and standardized implementation for {skill.name}.",
                    explanation=f"{skill.name} provides fundamental modularity, structural predictability, and industry standard patterns for modern software systems.",
                    difficulty="Medium",
                )
                db.add(q1)
            db.commit()
            db.refresh(assessment)

        # Ensure skill_name is populated on all questions
        for q in assessment.questions:
            q.skill_name = q.skill.name if q.skill else role.name

        return assessment

    def submit_goal_assessment(
        self, db: Session, submission: GoalAssessmentSubmission
    ) -> Dict[str, Any]:
        user = db.query(User).filter(User.id == submission.user_id).first()
        if not user:
            raise ValueError(f"User with ID {submission.user_id} not found.")

        role = (
            db.query(Role)
            .options(joinedload(Role.role_skills).joinedload(RoleSkill.skill))
            .filter(Role.id == submission.role_id)
            .first()
        )
        if not role:
            raise ValueError(f"Target goal with ID {submission.role_id} not found.")

        # Sync user's target role
        if user.target_role_id != role.id:
            user.target_role_id = role.id
            db.commit()

        assessment = self.get_or_create_goal_assessment(db, role.id)
        valid_q_map = {q.id: q for q in assessment.questions}
        submitted_q_ids = set()
        user_answers_map = {}

        for ans in submission.answers:
            if ans.question_id not in valid_q_map:
                continue
            if ans.question_id not in submitted_q_ids:
                submitted_q_ids.add(ans.question_id)
                user_answers_map[ans.question_id] = ans.answer

        question_breakdown = []
        skill_stats: Dict[int, Dict[str, Any]] = {}

        for q in assessment.questions:
            user_ans_raw = user_answers_map.get(q.id, "").strip()
            is_correct = False

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
                if user_ans_raw.lower() == correct_str.lower():
                    is_correct = True
                else:
                    letter_idx = None
                    if len(user_ans_raw) == 1 and user_ans_raw.upper() in ["A", "B", "C", "D"]:
                        letter_idx = ord(user_ans_raw.upper()) - 65
                    elif user_ans_raw.isdigit():
                        letter_idx = int(user_ans_raw)

                    if letter_idx is not None and 0 <= letter_idx < len(options_list):
                        selected_opt_text = options_list[letter_idx].strip()
                        if selected_opt_text.lower() == correct_str.lower():
                            is_correct = True

                    if not is_correct and len(correct_str) == 1 and correct_str.upper() in ["A", "B", "C", "D"]:
                        correct_letter_idx = ord(correct_str.upper()) - 65
                        if 0 <= correct_letter_idx < len(options_list):
                            if options_list[correct_letter_idx].strip().lower() == user_ans_raw.lower():
                                is_correct = True

            q_skill_id = q.skill_id or assessment.skill_id or (role.role_skills[0].skill_id if role.role_skills else 1)
            skill_obj = q.skill or db.query(Skill).filter(Skill.id == q_skill_id).first()
            s_name = skill_obj.name if skill_obj else "General"
            s_cat = skill_obj.category if skill_obj else "General"

            if q_skill_id not in skill_stats:
                skill_stats[q_skill_id] = {"total": 0, "correct": 0, "name": s_name, "category": s_cat}
            skill_stats[q_skill_id]["total"] += 1
            if is_correct:
                skill_stats[q_skill_id]["correct"] += 1

            question_breakdown.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "user_answer": user_ans_raw if user_ans_raw else "Unanswered",
                "correct_answer": correct_str,
                "is_correct": is_correct,
                "explanation": q.explanation,
            })

        now = datetime.utcnow()

        # Update UserSkill & create SkillEvidence for tested competencies
        for rs in role.role_skills:
            if not rs.skill:
                continue
            s_id = rs.skill_id
            if s_id in skill_stats:
                s_tot = skill_stats[s_id]["total"]
                s_cor = skill_stats[s_id]["correct"]
                s_score = round((s_cor / s_tot * 100.0), 1) if s_tot > 0 else 0.0
            else:
                s_tot = 0
                s_cor = 0
                s_score = 0.0

            u_skill = db.query(UserSkill).filter(UserSkill.user_id == user.id, UserSkill.skill_id == s_id).first()
            if not u_skill:
                u_skill = UserSkill(
                    user_id=user.id,
                    skill_id=s_id,
                    skill_level=s_score,
                    confidence=75.0 if s_tot > 0 else 10.0,
                    accuracy=s_score if s_tot > 0 else 0.0,
                    evidence_score=s_score,
                    last_assessed_at=now,
                )
                db.add(u_skill)
            else:
                u_skill.skill_level = s_score
                if s_tot > 0:
                    u_skill.confidence = 75.0
                    u_skill.accuracy = s_score
                u_skill.evidence_score = s_score
                u_skill.last_assessed_at = now
            db.commit()

            if s_tot > 0:
                ev = SkillEvidence(
                    user_id=user.id,
                    skill_id=s_id,
                    source=f"Goal Diagnostic: {role.name}",
                    evidence_type="ASSESSMENT",
                    score=s_score,
                    description=f"{role.name} Initial Diagnostic: {s_cor}/{s_tot} correct ({s_score:.0f}%)",
                    created_at=now,
                )
                db.add(ev)
                db.commit()

                from app.services.skill_dna_service import skill_dna_service
                skill_dna_service.recalculate_skill_dna(db, user.id, s_id)

        # Record overall attempt
        total_questions = len(assessment.questions)
        raw_correct = sum(1 for qb in question_breakdown if qb["is_correct"])
        overall_score = round((raw_correct / total_questions * 100.0), 1) if total_questions > 0 else 0.0

        attempt = AssessmentAttempt(
            user_id=user.id,
            assessment_id=assessment.id,
            score=overall_score,
            accuracy=overall_score,
            completed_at=now,
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        # Refresh learning state and roadmap
        from app.services.roadmap_service import roadmap_service
        roadmap_service.refresh_learning_state(db, user.id)

        # Calculate comprehensive skill gap analysis
        from app.services.skill_service import skill_service
        gap_data = skill_service.get_skill_gap_analysis(db, user.id, role.id)

        skill_scores_list = []
        for item in gap_data["all_gaps"]:
            stat = skill_stats.get(item["skill_id"], {"total": 0, "correct": 0})
            skill_scores_list.append({
                "skill_id": item["skill_id"],
                "skill_name": item["skill_name"],
                "category": item["category"],
                "score": item["current_level"],
                "questions_tested": stat["total"],
                "questions_correct": stat["correct"],
                "required_level": item["required_level"],
                "gap": item["gap"],
                "status": item["status"],
            })

        return {
            "attempt_id": attempt.id,
            "user_id": user.id,
            "role_id": role.id,
            "role_name": role.name,
            "overall_score": overall_score,
            "accuracy": overall_score,
            "total_questions": total_questions,
            "correct_questions": raw_correct,
            "completed_at": now,
            "skill_scores": skill_scores_list,
            "strong_skills": gap_data["strong_skills"],
            "moderate_skills": gap_data["moderate_skills"],
            "weak_skills": gap_data["weak_skills"],
            "missing_skills": gap_data["missing_skills"],
            "next_recommended_action": gap_data["next_recommended_action"],
            "question_breakdown": question_breakdown,
        }


assessment_service = AssessmentService()

