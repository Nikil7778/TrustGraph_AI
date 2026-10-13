"""
ML Inference Service for SkillPath AI Skill Mastery Prediction.
Guarantees:
- Safe schema validation matching feature_schema.json
- Safe failure on schema mismatch or missing model artifact
- Purely advisory output (mastery_probability, risk_level, top signals)
- Thresholds: LOW (>=0.70), MEDIUM (0.40-0.69), HIGH (<0.40)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

from ..schemas import MLPredictionResponse, MLTopSignal

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MODEL_ARTIFACT_PATH = MODELS_DIR / "skill_mastery_model.joblib"
FEATURE_SCHEMA_PATH = BASE_DIR / "feature_schema.json"
METADATA_PATH = BASE_DIR / "model_metadata.json"


class MasteryPredictor:
    """
    Advisory Skill Mastery Predictor.
    Predicts the likelihood that a learner will successfully demonstrate a skill
    on their next valid proof attempt.
    """

    def __init__(self):
        self._model = None
        self._feature_names: List[str] = []
        self._schema_version: str = "1.0.0"
        self._model_version: str = "1.0.0"
        self._feature_importances: Dict[str, float] = {}
        self._is_loaded = False
        self._load_model_and_schema()

    def _load_model_and_schema(self):
        if not FEATURE_SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Feature schema missing at {FEATURE_SCHEMA_PATH}")

        with open(FEATURE_SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_data = json.load(f)

        self._schema_version = schema_data.get("feature_schema_version", "1.0.0")
        self._feature_names = [feat["name"] for feat in schema_data["features"]]

        if not MODEL_ARTIFACT_PATH.exists():
            raise FileNotFoundError(f"Trained model artifact missing at {MODEL_ARTIFACT_PATH}")

        self._model = joblib.load(MODEL_ARTIFACT_PATH)

        if METADATA_PATH.exists():
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                meta = json.load(f)
            self._model_version = meta.get("model_version", "1.0.0")
            for sig in meta.get("top_feature_signals", []):
                self._feature_importances[sig["feature"]] = sig["importance"]

        # Validate that the model features match schema
        classifier = getattr(self._model, "named_steps", {}).get("classifier", None)
        if classifier is not None and hasattr(classifier, "n_features_in_"):
            if classifier.n_features_in_ != len(self._feature_names):
                raise ValueError(
                    f"Model feature dimension mismatch: model expects {classifier.n_features_in_}, "
                    f"schema defines {len(self._feature_names)}"
                )

        self._is_loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def feature_schema_version(self) -> str:
        return self._schema_version

    @property
    def feature_names(self) -> List[str]:
        return list(self._feature_names)

    def determine_risk_level(self, probability: float) -> str:
        if probability >= 0.70:
            return "LOW"
        elif probability >= 0.40:
            return "MEDIUM"
        else:
            return "HIGH"

    def predict(
        self,
        features: Dict[str, Any],
        skill_id: int,
        skill_name: str,
        user_id: Optional[int] = None
    ) -> MLPredictionResponse:
        """
        Executes advisory mastery prediction.
        Verifies input strictly against feature schema.
        Fails safely if required features are missing or invalid.
        """
        if not self._is_loaded:
            raise RuntimeError("MasteryPredictor is not loaded or model artifact is unavailable.")

        # Strict schema verification: check that all expected features exist
        missing_features = [col for col in self._feature_names if col not in features]
        if missing_features:
            raise ValueError(f"Feature schema mismatch! Missing required features: {missing_features[:5]}")

        # Construct row in strictly specified column order
        ordered_values = {col: [features[col]] for col in self._feature_names}
        input_df = pd.DataFrame(ordered_values)

        try:
            proba_array = self._model.predict_proba(input_df)
            # Positive class (1 = success) probability
            mastery_prob = float(proba_array[0][1])
        except Exception as e:
            raise RuntimeError(f"Model inference failed safely: {str(e)}")

        # Constrain probability between 0.0 and 1.0
        mastery_prob = float(np.clip(mastery_prob, 0.0, 1.0))
        risk_level = self.determine_risk_level(mastery_prob)

        # Identify top contributing signals for this prediction
        top_signals: List[MLTopSignal] = []
        for feat_name, imp in sorted(self._feature_importances.items(), key=lambda x: x[1], reverse=True)[:4]:
            val = float(features.get(feat_name, 0.0))
            desc = self._signal_explanation(feat_name, val, mastery_prob)
            top_signals.append(MLTopSignal(
                feature=feat_name,
                importance=imp,
                description=desc,
                learner_value=val
            ))

        # Advisory explanation
        pct_str = f"{round(mastery_prob * 100)}%"
        if risk_level == "HIGH":
            explanation = (
                f"The advisory mastery model predicts a {pct_str} likelihood of success on the next proof attempt (HIGH risk). "
                f"Recent accuracy or practical evidence exposure is limited. Targeted practice or Failure Lab simulation "
                f"is recommended before attempting high-stakes certification."
            )
        elif risk_level == "MEDIUM":
            explanation = (
                f"The advisory mastery model predicts a {pct_str} likelihood of success on the next proof attempt (MEDIUM risk). "
                f"Learner demonstrates foundational familiarity, but recency decay or question difficulty indicates additional "
                f"reinforcement is beneficial."
            )
        else:
            explanation = (
                f"The advisory mastery model predicts a {pct_str} likelihood of success on the next proof attempt (LOW risk). "
                f"Demonstrated accuracy and practical evidence history indicate strong readiness for the next proof attempt."
            )

        return MLPredictionResponse(
            skill_id=skill_id,
            skill_name=skill_name,
            mastery_probability=round(mastery_prob, 4),
            risk_level=risk_level,
            model_version=self._model_version,
            prediction_timestamp=datetime.now(),
            feature_schema_version=self._schema_version,
            top_signals=top_signals,
            advisory_explanation=explanation,
            is_advisory=True
        )

    def _signal_explanation(self, feature: str, value: float, prob: float) -> str:
        if feature == "current_skill_level":
            return f"Current demonstrated skill score is {round(value)}%."
        elif feature == "rolling_accuracy":
            return f"Cumulative accuracy across prior attempts is {round(value)}%."
        elif feature == "recent_accuracy":
            return f"Recent 3-attempt rolling accuracy is {round(value)}%."
        elif feature == "previous_accuracy":
            return f"Score on immediately preceding attempt was {round(value)}%."
        elif feature == "practical_evidence_count":
            return f"Has logged {int(value)} practical/project proof artifacts."
        elif feature == "days_since_previous_attempt":
            return f"{round(value, 1)} days have elapsed since previous attempt."
        return f"{feature.replace('_', ' ').capitalize()}: {round(value, 2)}"


# Singleton instance
_predictor_instance: Optional[MasteryPredictor] = None


def get_mastery_predictor() -> MasteryPredictor:
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = MasteryPredictor()
    return _predictor_instance
