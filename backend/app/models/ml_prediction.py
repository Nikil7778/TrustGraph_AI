from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class MLPrediction(Base):
    """
    Observability & audit ledger for Machine Learning skill mastery predictions.
    ML predicts learner success probability on next proof attempt (Advisory only).
    """
    __tablename__ = "ml_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    mastery_probability = Column(Float, nullable=False)  # 0.0 to 1.0
    risk_level = Column(String(20), nullable=False)      # LOW, MEDIUM, HIGH
    prediction_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    feature_schema_version = Column(String(50), default="1.0.0", nullable=False)

    # Relationships
    user = relationship("User")
    skill = relationship("Skill")
