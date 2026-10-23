from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


# Canonical platform identifiers - used as authoritative values in the database.
SUPPORTED_PLATFORMS = [
    "geeksforgeeks",
    "w3schools",
    "youtube",
    "khanacademy",
    "khan_academy",
    "coursera",
    "datacamp",
    "no_preference",
]


class LearnerResourcePreference(Base):
    """
    Persists a learner's preferred external learning platforms.

    Architecture contract:
      - Resource preference NEVER changes Skill DNA, Skill Debt, Career Value,
        Next-Best-Proof, roadmap order, or mastery status.
      - It only influences WHICH verified external resource is recommended
        when a learning module is displayed.
      - primary_platform: single most-preferred platform key (or 'no_preference')
      - preferred_platforms: comma-separated additional platform keys (may be empty)
      - secondary_platforms: mirrored column/alias for backwards-compatibility
    """
    __tablename__ = "user_resource_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,  # One preference record per learner
    )
    primary_platform = Column(
        String(50),
        default="no_preference",
        nullable=False,
    )
    preferred_platforms = Column(
        String(255),
        default="",
        nullable=False,
    )  # Comma-separated canonical platform keys
    secondary_platforms = Column(
        String(255),
        default="",
        nullable=False,
    )  # Kept in sync with preferred_platforms

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_resource_preference"),
    )

    # Relationships
    user = relationship("User")


# Alias for compatibility across codebase
UserResourcePreference = LearnerResourcePreference
