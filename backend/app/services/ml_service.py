"""
ML Service for SkillPath AI.
Integrates the MasteryPredictor with the database, dynamically extracting
learner features with strict anti-leakage guarantees.
CRITICAL RULE:
ML PREDICTS. DETERMINISTIC ENGINES DECIDE. GEMINI EXPLAINS.
The ML service is purely advisory and does NOT mutate deterministic models.
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User, UserSkill
from app.models.skill import Skill
from app.models.role import RoleSkill
from app.models.evidence import SkillEvidence
from app.models.assessment import Assessment, AssessmentAttempt
from app.models.industry_lab import IndustryLabAttempt
from app.models.ml_prediction import MLPrediction
from ml.inference.mastery_predictor import get_mastery_predictor
from ml.schemas import MLPredictionResponse

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "ml"
METADATA_PATH = BASE_DIR / "model_metadata.json"


def extract_learner_features(db: Session, user_id: int, skill_id: int) -> Dict[str, Any]:
    """
    Extracts validated feature vector strictly representing learner state
    immediately BEFORE the next attempt.
    Frontend values are NEVER trusted; features are derived authoritatively from database.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Learner with ID {user_id} not found")

    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill with ID {skill_id} not found")

    now = datetime.utcnow()

    # User skill record (authoritative deterministic Skill DNA baseline)
    user_skill = db.query(UserSkill).filter(
        UserSkill.user_id == user_id,
        UserSkill.skill_id == skill_id
    ).first()

    # Evidences for this skill
    evidences = db.query(SkillEvidence).filter(
        SkillEvidence.user_id == user_id,
        SkillEvidence.skill_id == skill_id
    ).order_by(SkillEvidence.created_at.asc()).all()

    # All evidences across all skills for this user
    all_evidences = db.query(SkillEvidence).filter(
        SkillEvidence.user_id == user_id
    ).all()

    # Assessment attempts
    assessment_attempts = db.query(AssessmentAttempt).join(
        Assessment, AssessmentAttempt.assessment_id == Assessment.id
    ).filter(
        AssessmentAttempt.user_id == user_id,
        Assessment.skill_id == skill_id
    ).order_by(AssessmentAttempt.completed_at.asc()).all()

    # Role context
    role_skill = None
    if user.target_role_id:
        role_skill = db.query(RoleSkill).filter(
            RoleSkill.role_id == user.target_role_id,
            RoleSkill.skill_id == skill_id
        ).first()

    # --- 1. Behavioral Features ---
    prev_attempts_count = len(evidences) + len(assessment_attempts)
    total_learner_attempts = len(all_evidences)

    recent_scores = [ev.score for ev in evidences[-3:]] if evidences else []
    if assessment_attempts:
        recent_scores.extend([att.score for att in assessment_attempts[-3:]])
    recent_scores = recent_scores[-3:]

    all_scores = [ev.score for ev in evidences] + [att.score for att in assessment_attempts]

    if all_scores:
        previous_acc = float(all_scores[-1])
        recent_acc = float(sum(recent_scores) / len(recent_scores)) if recent_scores else previous_acc
        rolling_acc = float(sum(all_scores) / len(all_scores))
    elif user_skill:
        previous_acc = float(user_skill.accuracy)
        recent_acc = float(user_skill.accuracy)
        rolling_acc = float(user_skill.accuracy)
    else:
        previous_acc = 40.0
        recent_acc = 40.0
        rolling_acc = 40.0

    # Streaks
    correct_streak = 0
    incorrect_streak = 0
    for s in reversed(all_scores):
        if s >= 70.0:
            if incorrect_streak == 0:
                correct_streak += 1
            else:
                break
        else:
            if correct_streak == 0:
                incorrect_streak += 1
            else:
                break

    # Timing and recency
    latest_ts = None
    if evidences:
        latest_ts = evidences[-1].created_at
    if assessment_attempts and (latest_ts is None or assessment_attempts[-1].completed_at > latest_ts):
        latest_ts = assessment_attempts[-1].completed_at
    if latest_ts is None and user_skill and user_skill.last_assessed_at:
        latest_ts = user_skill.last_assessed_at

    if latest_ts:
        days_since_prev = max(0.0, (now - latest_ts).total_seconds() / 86400.0)
    else:
        days_since_prev = 14.0

    # --- 2. Difficulty Features ---
    diff_map = {"Beginner": 35.0, "Intermediate": 65.0, "Advanced": 90.0, "Hard": 90.0}
    diff_label = user_skill.difficulty if user_skill and hasattr(user_skill, "difficulty") else "Intermediate"
    skill_diff_score = diff_map.get(diff_label, 65.0)

    hard_exp = sum(1 for ev in evidences if ev.score < 50.0)  # proxy or difficulty
    med_exp = max(0, prev_attempts_count - hard_exp)
    easy_exp = 0

    # --- 3. Evidence Features ---
    assessment_ev_cnt = sum(1 for ev in evidences if ev.evidence_type == "ASSESSMENT") + len(assessment_attempts)
    practice_ev_cnt = sum(1 for ev in evidences if ev.evidence_type in ["PRACTICE", "REAL_WORLD_TASK"])
    project_ev_cnt = sum(1 for ev in evidences if ev.evidence_type == "PROJECT")
    practical_ev_cnt = practice_ev_cnt + (project_ev_cnt * 2)

    days_since_last_ev = days_since_prev
    evidence_recency = math.exp(-0.05 * min(days_since_last_ev, 60.0)) * 100.0

    # --- 4. Skill Features ---
    if user_skill:
        current_skill_lvl = float(user_skill.skill_level)
        current_conf = float(user_skill.confidence)
        current_acc = float(user_skill.accuracy)
        current_ev_score = float(user_skill.evidence_score)
    else:
        current_skill_lvl = rolling_acc * 0.7
        current_conf = 30.0
        current_acc = rolling_acc
        current_ev_score = float(min(100.0, prev_attempts_count * 15.0))

    has_practical = 1 if practical_ev_cnt > 0 else 0

    # --- 5. Career Context Features ---
    role_importance = float(role_skill.importance_score) if role_skill else 75.0
    role_req = float(role_skill.required_level) if role_skill else 80.0

    features = {
        "previous_attempts": int(prev_attempts_count),
        "total_attempts": int(total_learner_attempts),
        "previous_accuracy": round(float(previous_acc), 2),
        "recent_accuracy": round(float(recent_acc), 2),
        "rolling_accuracy": round(float(rolling_acc), 2),
        "correct_streak": int(correct_streak),
        "incorrect_streak": int(incorrect_streak),
        "average_response_time": 15.0,
        "recent_response_time": 15.0,
        "days_since_previous_attempt": round(float(days_since_prev), 2),
        "average_difficulty_exposure": round(float(skill_diff_score), 2),
        "recent_difficulty": round(float(skill_diff_score), 2),
        "hard_question_exposure": int(hard_exp),
        "medium_question_exposure": int(med_exp),
        "easy_question_exposure": int(easy_exp),
        "assessment_evidence_count": int(assessment_ev_cnt),
        "practice_evidence_count": int(practice_ev_cnt),
        "project_evidence_count": int(project_ev_cnt),
        "practical_evidence_count": int(practical_ev_cnt),
        "days_since_last_evidence": round(float(days_since_last_ev), 2),
        "evidence_recency": round(float(evidence_recency), 2),
        "current_skill_level": round(float(current_skill_lvl), 2),
        "current_confidence": round(float(current_conf), 2),
        "current_accuracy": round(float(current_acc), 2),
        "current_evidence_score": round(float(current_ev_score), 2),
        "current_practical_evidence": int(has_practical),
        "role_skill_importance": round(float(role_importance), 2),
        "role_requirement_level": round(float(role_req), 2),
    }

    return features


def predict_skill_mastery(db: Session, user_id: int, skill_id: int) -> MLPredictionResponse:
    """
    Computes an advisory ML mastery prediction for learner and skill.
    Stores prediction in database for observability.
    Does NOT modify deterministic engine states.
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill with ID {skill_id} not found")

    # Check if learner has sufficient evidence/attempts before generating a prediction
    user_evidence_count = db.query(SkillEvidence).filter(SkillEvidence.user_id == user_id).count()
    user_attempt_count = db.query(AssessmentAttempt).filter(AssessmentAttempt.user_id == user_id).count()
    user_lab_count = db.query(IndustryLabAttempt).filter(IndustryLabAttempt.user_id == user_id).count()

    if user_evidence_count == 0 and user_attempt_count == 0 and user_lab_count == 0:
        return MLPredictionResponse(
            skill_id=skill_id,
            skill_name=skill.name,
            mastery_probability=0.0,
            risk_level="UNKNOWN",
            model_version="1.0.0",
            prediction_timestamp=datetime.utcnow(),
            feature_schema_version="2.0",
            top_signals=[],
            advisory_explanation="Not enough learning evidence yet. Complete your diagnostic assessment to begin predictive modeling.",
            is_advisory=True,
        )

    features = extract_learner_features(db, user_id, skill_id)
    predictor = get_mastery_predictor()
    prediction = predictor.predict(
        features=features,
        skill_id=skill_id,
        skill_name=skill.name,
        user_id=user_id
    )

    # Observability log to database
    try:
        record = MLPrediction(
            user_id=user_id,
            skill_id=skill_id,
            model_version=prediction.model_version,
            mastery_probability=prediction.mastery_probability,
            risk_level=prediction.risk_level,
            prediction_timestamp=prediction.prediction_timestamp,
            feature_schema_version=prediction.feature_schema_version,
        )
        db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        # Logging error should not crash advisory prediction

    return prediction


def get_model_info() -> Dict[str, Any]:
    """
    Returns public metadata and audit information for the loaded ML model.
    Never exposes internal secrets or raw data.
    """
    predictor = get_mastery_predictor()
    if not METADATA_PATH.exists():
        return {
            "model_version": predictor.model_version,
            "feature_schema_version": predictor.feature_schema_version,
            "status": "loaded" if predictor.is_loaded else "unavailable",
            "is_advisory": True,
            "training_source": "General learner progression model",
        }

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    return {
        "model_name": meta.get("model_name", "skillpath_mastery_predictor"),
        "model_version": meta.get("model_version", "1.0.0"),
        "status": "active",
        "is_advisory": True,
        "training_source": meta.get("training_source", "EdNet-derived progression benchmark"),
        "training_date": meta.get("training_date"),
        "sklearn_version": meta.get("sklearn_version"),
        "feature_count": meta.get("feature_count", len(predictor.feature_names)),
        "dataset_summary": meta.get("dataset_summary", {}),
        "validation_metrics": meta.get("validation_metrics", {}),
        "final_test_metrics": meta.get("final_test_metrics", {}),
        "top_feature_signals": meta.get("top_feature_signals", []),
    }
