"""
Evaluation script for SkillPath AI's ML Skill Mastery Prediction.
Loads the serialized model artifact and validates metrics on specified test data.
"""

import json
from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)

BASE_DIR = Path(__file__).resolve().parent.parent
TRAINING_DIR = Path(__file__).resolve().parent
FEATURE_SCHEMA_PATH = BASE_DIR / "feature_schema.json"
MODEL_ARTIFACT_PATH = BASE_DIR / "models" / "skill_mastery_model.joblib"
METADATA_PATH = BASE_DIR / "model_metadata.json"
DATASET_PATH = TRAINING_DIR / "dataset.csv"


def evaluate_saved_model():
    if not MODEL_ARTIFACT_PATH.exists():
        raise FileNotFoundError(f"Model artifact not found at {MODEL_ARTIFACT_PATH}")
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadata not found at {METADATA_PATH}")

    with open(FEATURE_SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    feature_names = [feat["name"] for feat in schema["features"]]

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    print(f"Loading model artifact: {MODEL_ARTIFACT_PATH}")
    model = joblib.load(MODEL_ARTIFACT_PATH)

    df = pd.read_csv(DATASET_PATH)
    test_learners = df["learner_id"].unique()[-18:]  # Last 18 learners corresponding to test partition
    test_df = df[df["learner_id"].isin(test_learners)]

    X_test = test_df[feature_names]
    y_test = test_df["next_attempt_success"].values

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "pr_auc": round(float(average_precision_score(y_test, y_proba)), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }

    print("\nVerified Model Evaluation on Test Split:")
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    evaluate_saved_model()
