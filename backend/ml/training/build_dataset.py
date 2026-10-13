"""
Dataset generation and validation pipeline for SkillPath AI's ML Skill Mastery Prediction.
Generates a realistic learner-behavior progression dataset (EdNet-derived methodology)
with strict anti-leakage guarantees. Every row represents a learner state strictly BEFORE
the next proof attempt.
"""

import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd

# Path definitions
BASE_DIR = Path(__file__).resolve().parent.parent
TRAINING_DIR = Path(__file__).resolve().parent
FEATURE_SCHEMA_PATH = BASE_DIR / "feature_schema.json"
DATASET_OUTPUT_PATH = TRAINING_DIR / "dataset.csv"
REPORT_OUTPUT_PATH = TRAINING_DIR / "dataset_validation_report.json"


def load_feature_schema() -> List[str]:
    with open(FEATURE_SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return [feat["name"] for feat in schema["features"]]


def generate_learner_interaction_series(seed: int = 42) -> pd.DataFrame:
    """
    Simulates sequential proof attempts across 120 diverse learners and 8 competencies
    over a 180-day timeline.
    Anti-leakage guarantee: Row t features are strictly computed from attempts 0..t-1.
    Target next_attempt_success is the binary outcome of attempt t.
    """
    random.seed(seed)
    np.random.seed(seed)

    num_learners = 120
    skills = [
        {"skill_id": 1, "name": "Python Fundamentals", "base_difficulty": 50.0, "importance": 85.0, "req_level": 75.0},
        {"skill_id": 2, "name": "Data Modeling", "base_difficulty": 65.0, "importance": 80.0, "req_level": 70.0},
        {"skill_id": 3, "name": "SQL JOINs", "base_difficulty": 70.0, "importance": 95.0, "req_level": 85.0},
        {"skill_id": 4, "name": "Statistical Analysis", "base_difficulty": 75.0, "importance": 90.0, "req_level": 80.0},
        {"skill_id": 5, "name": "Git & Version Control", "base_difficulty": 45.0, "importance": 70.0, "req_level": 65.0},
        {"skill_id": 6, "name": "API Design & Integration", "base_difficulty": 68.0, "importance": 75.0, "req_level": 70.0},
        {"skill_id": 7, "name": "Docker & Deployment", "base_difficulty": 72.0, "importance": 65.0, "req_level": 60.0},
        {"skill_id": 8, "name": "Query Optimization", "base_difficulty": 80.0, "importance": 88.0, "req_level": 80.0},
    ]

    learner_archetypes = [
        {"type": "fast_learner", "base_ability": 0.75, "learning_rate": 0.12, "decay_rate": 0.02, "weight": 0.25},
        {"type": "steady_learner", "base_ability": 0.55, "learning_rate": 0.08, "decay_rate": 0.04, "weight": 0.40},
        {"type": "struggling_learner", "base_ability": 0.35, "learning_rate": 0.05, "decay_rate": 0.06, "weight": 0.25},
        {"type": "inconsistent_learner", "base_ability": 0.50, "learning_rate": 0.06, "decay_rate": 0.12, "weight": 0.10},
    ]

    base_start_date = datetime(2026, 1, 1, 9, 0, 0)
    dataset_rows: List[Dict[str, Any]] = []

    for learner_idx in range(1, num_learners + 1):
        learner_id = f"learner_{learner_idx:03d}"
        archetype = random.choices(
            learner_archetypes,
            weights=[a["weight"] for a in learner_archetypes],
            k=1
        )[0]

        learner_ability = np.clip(
            archetype["base_ability"] + np.random.normal(0.0, 0.08),
            0.15,
            0.92
        )
        learning_rate = archetype["learning_rate"]
        decay_rate = archetype["decay_rate"]

        total_learner_attempts = 0
        learner_current_time = base_start_date + timedelta(days=random.uniform(0, 30))

        # Select 3-6 skills for this learner
        assigned_skills = random.sample(skills, k=random.randint(4, 7))

        for skill in assigned_skills:
            skill_id = skill["skill_id"]
            num_attempts_for_skill = random.randint(4, 12)

            history_attempts: List[Dict[str, Any]] = []
            skill_time = learner_current_time + timedelta(days=random.uniform(0, 5))

            for attempt_idx in range(num_attempts_for_skill):
                # Calculate pre-attempt state from history_attempts (0 .. attempt_idx - 1)
                days_gap = random.uniform(1.0, 18.0) if history_attempts else 0.0
                skill_time += timedelta(days=days_gap, hours=random.uniform(0.5, 4.0))

                # --- 1. Behavioral Features strictly before this attempt ---
                prev_attempts_count = len(history_attempts)
                if prev_attempts_count == 0:
                    prev_acc = 0.0
                    recent_acc = 0.0
                    rolling_acc = 0.0
                    correct_streak = 0
                    incorrect_streak = 0
                    avg_resp_time = 15.0
                    recent_resp_time = 15.0
                    days_since_prev = 0.0
                else:
                    prev_acc = history_attempts[-1]["score"]
                    recent_window = [h["score"] for h in history_attempts[-3:]]
                    recent_acc = float(np.mean(recent_window))
                    all_scores = [h["score"] for h in history_attempts]
                    rolling_acc = float(np.mean(all_scores))

                    # Streaks
                    correct_streak = 0
                    for h in reversed(history_attempts):
                        if h["score"] >= 70.0:
                            correct_streak += 1
                        else:
                            break

                    incorrect_streak = 0
                    for h in reversed(history_attempts):
                        if h["score"] < 70.0:
                            incorrect_streak += 1
                        else:
                            break

                    resp_times = [h["response_time"] for h in history_attempts]
                    avg_resp_time = float(np.mean(resp_times))
                    recent_resp_time = history_attempts[-1]["response_time"]
                    days_since_prev = days_gap

                # --- 2. Difficulty Features strictly before this attempt ---
                if prev_attempts_count == 0:
                    avg_diff_exposure = skill["base_difficulty"]
                    recent_diff = skill["base_difficulty"]
                    hard_exp = 0
                    med_exp = 0
                    easy_exp = 0
                else:
                    diffs = [h["difficulty"] for h in history_attempts]
                    avg_diff_exposure = float(np.mean(diffs))
                    recent_diff = history_attempts[-1]["difficulty"]
                    hard_exp = sum(1 for d in diffs if d >= 75.0)
                    med_exp = sum(1 for d in diffs if 50.0 <= d < 75.0)
                    easy_exp = sum(1 for d in diffs if d < 50.0)

                # --- 3. Evidence Features strictly before this attempt ---
                assessment_ev = sum(1 for h in history_attempts if h["type"] == "assessment")
                practice_ev = sum(1 for h in history_attempts if h["type"] == "practice")
                project_ev = sum(1 for h in history_attempts if h["type"] == "project")
                practical_ev = practice_ev + (project_ev * 2)

                days_since_last_ev = days_since_prev if prev_attempts_count > 0 else 0.0
                # Exponential decay score
                recency_decay = math.exp(-0.05 * min(days_since_last_ev, 60.0)) * 100.0

                # --- 4. Skill Features strictly before this attempt ---
                if prev_attempts_count == 0:
                    current_skill_lvl = max(10.0, learner_ability * 40.0)
                    current_conf = 20.0
                    current_accuracy_feat = 0.0
                    current_ev_score = 10.0
                    has_practical = 0
                else:
                    current_skill_lvl = np.clip(
                        (rolling_acc * 0.6) + (learner_ability * 40.0) - (min(days_since_prev, 30.0) * 0.5),
                        5.0,
                        98.0
                    )
                    current_conf = np.clip(
                        20.0 + (prev_attempts_count * 8.0) + (practical_ev * 10.0),
                        10.0,
                        95.0
                    )
                    current_accuracy_feat = recent_acc
                    current_ev_score = np.clip(
                        (prev_attempts_count * 12.0) + (practical_ev * 15.0),
                        0.0,
                        100.0
                    )
                    has_practical = 1 if practical_ev > 0 else 0

                # --- 5. Career Context Features ---
                role_importance = skill["importance"]
                role_req = skill["req_level"]

                # --- Determine Target for this attempt ---
                # Attempt difficulty: Easy (35), Medium (65), Hard (90)
                diff_choice = random.choice([35.0, 65.0, 65.0, 90.0])
                attempt_type = random.choice(["assessment", "practice", "practice", "project"])

                # Latent mastery at moment of attempt:
                # Governed by: learner_ability, cumulative attempts, practical evidence, forgetting decay, difficulty
                forgetting = math.exp(-decay_rate * min(days_since_prev, 60.0)) if prev_attempts_count > 0 else 1.0
                practice_boost = math.log1p(prev_attempts_count) * learning_rate
                practical_boost = 0.08 if has_practical else 0.0

                success_logit = (
                    (learner_ability * 2.2)
                    + (practice_boost * 2.0)
                    + practical_boost
                    - ((diff_choice - 50.0) / 45.0 * 0.9)
                    + ((prev_acc / 100.0 - 0.5) * 0.8 if prev_attempts_count > 0 else 0.0)
                    - ((1.0 - forgetting) * 0.6)
                    + np.random.normal(0.0, 0.35)
                )

                success_prob = 1.0 / (1.0 + math.exp(-np.clip(success_logit, -5.0, 5.0)))
                # Next attempt score
                attempt_score = np.clip(success_prob * 100.0 + np.random.normal(0.0, 6.0), 10.0, 99.0)
                next_attempt_success = 1 if attempt_score >= 70.0 else 0

                resp_time = np.clip(
                    15.0 + (diff_choice / 5.0) - (learner_ability * 8.0) + np.random.normal(0.0, 3.0),
                    3.0,
                    90.0
                )

                # Record prediction row representing state BEFORE this attempt
                row = {
                    "learner_id": learner_id,
                    "skill_id": skill_id,
                    "prediction_timestamp": skill_time.isoformat(),
                    # Behavioral
                    "previous_attempts": prev_attempts_count,
                    "total_attempts": total_learner_attempts,
                    "previous_accuracy": round(float(prev_acc), 2),
                    "recent_accuracy": round(float(recent_acc), 2),
                    "rolling_accuracy": round(float(rolling_acc), 2),
                    "correct_streak": correct_streak,
                    "incorrect_streak": incorrect_streak,
                    "average_response_time": round(float(avg_resp_time), 2),
                    "recent_response_time": round(float(recent_resp_time), 2),
                    "days_since_previous_attempt": round(float(days_since_prev), 2),
                    # Difficulty
                    "average_difficulty_exposure": round(float(avg_diff_exposure), 2),
                    "recent_difficulty": round(float(recent_diff), 2),
                    "hard_question_exposure": hard_exp,
                    "medium_question_exposure": med_exp,
                    "easy_question_exposure": easy_exp,
                    # Evidence
                    "assessment_evidence_count": assessment_ev,
                    "practice_evidence_count": practice_ev,
                    "project_evidence_count": project_ev,
                    "practical_evidence_count": practical_ev,
                    "days_since_last_evidence": round(float(days_since_last_ev), 2),
                    "evidence_recency": round(float(recency_decay), 2),
                    # Skill
                    "current_skill_level": round(float(current_skill_lvl), 2),
                    "current_confidence": round(float(current_conf), 2),
                    "current_accuracy": round(float(current_accuracy_feat), 2),
                    "current_evidence_score": round(float(current_ev_score), 2),
                    "current_practical_evidence": has_practical,
                    # Career Context
                    "role_skill_importance": round(float(role_importance), 2),
                    "role_requirement_level": round(float(role_req), 2),
                    # TARGET
                    "next_attempt_success": next_attempt_success,
                }
                dataset_rows.append(row)

                # NOW append current attempt to history strictly for future iterations
                history_attempts.append({
                    "score": attempt_score,
                    "difficulty": diff_choice,
                    "type": attempt_type,
                    "response_time": resp_time,
                    "timestamp": skill_time,
                })
                total_learner_attempts += 1

    df = pd.DataFrame(dataset_rows)
    return df


def validate_dataset(df: pd.DataFrame, expected_features: List[str]) -> Dict[str, Any]:
    """
    Strict validation suite per Phase E.
    Stops and raises error if any critical validation check fails.
    """
    errors: List[str] = []

    # 1. Row count check
    if len(df) < 500:
        errors.append(f"Insufficient row count: {len(df)} < 500")

    # 2. Missing learner IDs or skill IDs
    if df["learner_id"].isnull().any() or (df["learner_id"] == "").any():
        errors.append("Dataset contains missing or empty learner_id values")
    if df["skill_id"].isnull().any():
        errors.append("Dataset contains missing skill_id values")

    # 3. Missing timestamps or invalid format
    if df["prediction_timestamp"].isnull().any():
        errors.append("Dataset contains missing prediction_timestamp")
    try:
        ts = pd.to_datetime(df["prediction_timestamp"])
    except Exception as e:
        errors.append(f"Invalid timestamp format: {e}")

    # 4. Target validation
    target_values = set(df["next_attempt_success"].unique())
    if not target_values.issubset({0, 1}):
        errors.append(f"Target contains invalid values: {target_values}. Must be binary subset of {{0, 1}}.")

    # 5. Impossible percentages (<0 or >100)
    percentage_cols = [
        "previous_accuracy", "recent_accuracy", "rolling_accuracy",
        "average_difficulty_exposure", "recent_difficulty", "evidence_recency",
        "current_skill_level", "current_confidence", "current_accuracy",
        "current_evidence_score", "role_skill_importance", "role_requirement_level"
    ]
    for col in percentage_cols:
        if (df[col] < 0.0).any() or (df[col] > 100.0).any():
            errors.append(f"Impossible percentage values found in column '{col}': min={df[col].min()}, max={df[col].max()}")

    # 6. Negative attempt counts or response times
    non_negative_cols = [
        "previous_attempts", "total_attempts", "correct_streak", "incorrect_streak",
        "average_response_time", "recent_response_time", "days_since_previous_attempt",
        "hard_question_exposure", "medium_question_exposure", "easy_question_exposure",
        "assessment_evidence_count", "practice_evidence_count", "project_evidence_count",
        "practical_evidence_count", "days_since_last_evidence"
    ]
    for col in non_negative_cols:
        if (df[col] < 0).any():
            errors.append(f"Negative values found in column '{col}': min={df[col].min()}")

    # 7. Check for missing values in features
    for col in expected_features:
        if col not in df.columns:
            errors.append(f"Missing required feature column in dataset: '{col}'")
        elif df[col].isnull().any():
            errors.append(f"Null values found in feature column '{col}': count={df[col].isnull().sum()}")

    # 8. Check for duplicate prediction rows
    dup_keys = df.duplicated(subset=["learner_id", "skill_id", "prediction_timestamp"])
    if dup_keys.any():
        errors.append(f"Found {dup_keys.sum()} duplicate prediction rows (learner_id, skill_id, timestamp)")

    # 9. Anti-leakage checks:
    # Verify no future target outcome correlation artifact exists (e.g. perfect correlation or identical columns)
    for col in expected_features:
        corr = df[col].corr(df["next_attempt_success"])
        if abs(corr) >= 0.98:
            errors.append(f"Suspected target leakage in feature '{col}': correlation with target is {corr:.4f}")

    if errors:
        msg = "DATASET VALIDATION FAILED:\n" + "\n".join(f"- {e}" for e in errors)
        raise ValueError(msg)

    # Class balance
    pos_count = int((df["next_attempt_success"] == 1).sum())
    neg_count = int((df["next_attempt_success"] == 0).sum())
    total = len(df)
    pos_ratio = pos_count / total

    report = {
        "validation_passed": True,
        "total_rows": total,
        "unique_learners": int(df["learner_id"].nunique()),
        "unique_skills": int(df["skill_id"].nunique()),
        "positive_examples": pos_count,
        "negative_examples": neg_count,
        "class_balance_positive_pct": round(pos_ratio * 100.0, 2),
        "missing_values_count": int(df.isnull().sum().sum()),
        "duplicate_rows": int(dup_keys.sum()),
        "date_range": {
            "start": str(df["prediction_timestamp"].min()),
            "end": str(df["prediction_timestamp"].max())
        },
        "feature_count": len(expected_features),
        "feature_list": expected_features,
        "target_definition": "Binary 1 if next proof score >= 70.0%, 0 otherwise (anti-leakage pre-attempt state)",
    }

    return report


def main():
    print("=== [PHASE D/E] Building SkillPath ML Training Dataset ===")
    expected_features = load_feature_schema()
    print(f"Loaded schema with {len(expected_features)} features.")

    print("Simulating learner interaction series with anti-leakage guarantees...")
    df = generate_learner_interaction_series(seed=42)

    print("Running strict data validation...")
    report = validate_dataset(df, expected_features)

    # Save dataset and report
    df.to_csv(DATASET_OUTPUT_PATH, index=False)
    with open(REPORT_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Dataset successfully created and validated!")
    print(f"Total Rows: {report['total_rows']}")
    print(f"Unique Learners: {report['unique_learners']}")
    print(f"Unique Skills: {report['unique_skills']}")
    print(f"Positive Outcomes: {report['positive_examples']} ({report['class_balance_positive_pct']}%)")
    print(f"Negative Outcomes: {report['negative_examples']}")
    print(f"Output saved to: {DATASET_OUTPUT_PATH}")
    print(f"Validation report saved to: {REPORT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
