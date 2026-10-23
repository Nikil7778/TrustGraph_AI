"""
Phase 21 - Learning Platform Preferences & Recommendation API

Endpoints:
  GET /api/preferences/resources             - Return authenticated learner preference record
  PUT /api/preferences/resources             - Upsert authenticated learner preference record
  GET /api/resources/recommended/{concept}    - Return recommended resource for authenticated learner
  GET /api/users/{user_id}/resource-preferences - User-specific resource preference (with auth validation)
  PUT /api/users/{user_id}/resource-preferences - User-specific resource preference upsert

Architecture contract:
  - Authenticated session strictly determines the current learner.
  - User A never receives User B preferences.
  - Zero effect on Skill DNA, Skill Debt, Career Value, Next-Best-Proof, or roadmap sequence.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import List, Optional

from app.core.database import get_db
from app.core.auth import require_current_user, get_current_user_optional
from app.models.user import User
from app.models.resource_preference import LearnerResourcePreference, SUPPORTED_PLATFORMS
from app.services.resource_recommendation_service import resource_recommendation_service

router = APIRouter(tags=["Learning Platform Preferences"])


# ----------------------------------------------
# Pydantic Schemas
# ----------------------------------------------

class ResourcePreferenceResponse(BaseModel):
    user_id: int
    primary_platform: str
    preferred_platforms: List[str]
    secondary_platforms: List[str]

    model_config = {"from_attributes": True}


class ResourcePreferenceUpdate(BaseModel):
    primary_platform: str = "no_preference"
    preferred_platforms: Optional[List[str]] = None
    secondary_platforms: Optional[List[str]] = None

    @field_validator("primary_platform")
    @classmethod
    def validate_primary(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in SUPPORTED_PLATFORMS:
            raise ValueError(
                f"'{v}' is not a supported platform. Choose from: {SUPPORTED_PLATFORMS}"
            )
        return v

    def get_cleaned_secondaries(self) -> List[str]:
        raw_list = self.preferred_platforms if self.preferred_platforms is not None else (self.secondary_platforms or [])
        cleaned = []
        for item in raw_list:
            v = item.strip().lower()
            if v and v not in SUPPORTED_PLATFORMS:
                raise ValueError(
                    f"'{v}' is not a supported platform. Choose from: {SUPPORTED_PLATFORMS}"
                )
            if v and v != "no_preference" and v != self.primary_platform and v not in cleaned:
                cleaned.append(v)
        return cleaned


class RecommendedResourceResponse(BaseModel):
    id: int
    title: str
    provider: str
    url: str
    description: Optional[str]
    concept_slug: str
    concept_name: str
    skill_name: Optional[str]
    difficulty: str
    resource_type: str
    estimated_minutes: int
    verified: bool
    selection_reason: str
    is_preferred_platform: bool
    platform_match_type: str


def _to_response(pref: LearnerResourcePreference) -> ResourcePreferenceResponse:
    raw_str = pref.preferred_platforms or pref.secondary_platforms or ""
    secondaries = [p.strip() for p in raw_str.split(",") if p.strip()]
    return ResourcePreferenceResponse(
        user_id=pref.user_id,
        primary_platform=pref.primary_platform,
        preferred_platforms=secondaries,
        secondary_platforms=secondaries,
    )


# ----------------------------------------------
# Authenticated Current-User Endpoints
# ----------------------------------------------

@router.get(
    "/preferences/resources",
    response_model=ResourcePreferenceResponse,
    summary="Get authenticated learner platform preferences",
)
def get_current_user_preferences(
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the authenticated learner's preferred external learning platforms.
    Enforces strict user isolation.
    """
    pref = db.query(LearnerResourcePreference).filter(
        LearnerResourcePreference.user_id == current_user.id
    ).first()

    if not pref:
        return ResourcePreferenceResponse(
            user_id=current_user.id,
            primary_platform="no_preference",
            preferred_platforms=[],
            secondary_platforms=[],
        )

    return _to_response(pref)


@router.put(
    "/preferences/resources",
    response_model=ResourcePreferenceResponse,
    summary="Update authenticated learner platform preferences",
)
def update_current_user_preferences(
    body: ResourcePreferenceUpdate,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
):
    """
    Persist the authenticated learner's preferred external learning platforms.
    """
    cleaned_secondaries = body.get_cleaned_secondaries()
    secondary_str = ",".join(cleaned_secondaries)

    pref = db.query(LearnerResourcePreference).filter(
        LearnerResourcePreference.user_id == current_user.id
    ).first()

    if pref:
        pref.primary_platform = body.primary_platform
        pref.preferred_platforms = secondary_str
        pref.secondary_platforms = secondary_str
    else:
        pref = LearnerResourcePreference(
            user_id=current_user.id,
            primary_platform=body.primary_platform,
            preferred_platforms=secondary_str,
            secondary_platforms=secondary_str,
        )
        db.add(pref)

    db.commit()
    db.refresh(pref)
    return _to_response(pref)


@router.get(
    "/resources/recommended/{concept}",
    response_model=RecommendedResourceResponse,
    summary="Get recommended external resource for a learning concept",
)
def get_recommended_resource_for_concept(
    concept: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
):
    """
    Returns the recommended verified external resource for the given concept,
    taking into account the authenticated learner's level and platform preferences.
    """
    result = resource_recommendation_service.get_recommended_resource(
        db=db,
        user=current_user,
        concept_slug=concept,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No verified learning resource found for concept '{concept}'.",
        )

    return RecommendedResourceResponse(**result)


# ----------------------------------------------
# Backward-Compatible User-ID Endpoints
# ----------------------------------------------

@router.get(
    "/users/{user_id}/resource-preferences",
    response_model=ResourcePreferenceResponse,
    summary="Get learner learning platform preferences by user ID",
)
def get_resource_preference_by_id(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Return platform preferences for the specified user.
    If authenticated, enforces that a user cannot access another user's preferences unless authorized.
    """
    caller = get_current_user_optional(request, db)
    if caller and caller.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot view another learner's resource preferences.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    pref = db.query(LearnerResourcePreference).filter(
        LearnerResourcePreference.user_id == user_id
    ).first()

    if not pref:
        return ResourcePreferenceResponse(
            user_id=user_id,
            primary_platform="no_preference",
            preferred_platforms=[],
            secondary_platforms=[],
        )

    return _to_response(pref)


@router.put(
    "/users/{user_id}/resource-preferences",
    response_model=ResourcePreferenceResponse,
    summary="Upsert learner learning platform preferences by user ID",
)
def update_resource_preference_by_id(
    user_id: int,
    body: ResourcePreferenceUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Create or update the specified learner's preferred external learning platforms.
    """
    caller = get_current_user_optional(request, db)
    if caller and caller.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot modify another learner's resource preferences.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    cleaned_secondaries = body.get_cleaned_secondaries()
    secondary_str = ",".join(cleaned_secondaries)

    pref = db.query(LearnerResourcePreference).filter(
        LearnerResourcePreference.user_id == user_id
    ).first()

    if pref:
        pref.primary_platform = body.primary_platform
        pref.preferred_platforms = secondary_str
        pref.secondary_platforms = secondary_str
    else:
        pref = LearnerResourcePreference(
            user_id=user_id,
            primary_platform=body.primary_platform,
            preferred_platforms=secondary_str,
            secondary_platforms=secondary_str,
        )
        db.add(pref)

    db.commit()
    db.refresh(pref)
    return _to_response(pref)
