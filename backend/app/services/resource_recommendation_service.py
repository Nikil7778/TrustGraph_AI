"""
Phase 21 - Deterministic Resource Recommendation Service

Architectural Invariant:
- Evaluates verified external learning resources strictly at the presentation layer.
- Respects authenticated learner platform preferences (primary, secondary, or no-preference).
- Zero side-effects on Skill DNA, Skill Debt, Career Value, Next-Best-Proof, or roadmap sequence.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.learning import LearningModule, LearningResource
from app.models.resource_preference import LearnerResourcePreference


class ResourceRecommendationService:
    def get_recommended_resource(
        self,
        db: Session,
        user: User,
        concept_slug: str,
        level_override: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Selects the single best verified external learning resource for a given concept,
        evaluating platform preferences (primary -> secondary -> verified fallback -> automatic).
        """
        # 1. Resolve module metadata
        module = db.query(LearningModule).filter(LearningModule.slug == concept_slug).first()
        if not module:
            return None

        # Determine effective learner level
        raw_user_level = (user.experience_level or "Intermediate").strip().capitalize()
        learner_level = level_override or raw_user_level
        if learner_level not in ["Beginner", "Intermediate", "Advanced"]:
            learner_level = "Intermediate"

        user_role_name = user.target_role.name if user.target_role else "Data Analyst"

        # 2. Retrieve user preferences
        pref_record = db.query(LearnerResourcePreference).filter(
            LearnerResourcePreference.user_id == user.id
        ).first()

        primary_pref = (pref_record.primary_platform.strip().lower() if pref_record else "no_preference") or "no_preference"
        
        # Load secondary preferences from preferred_platforms or secondary_platforms
        raw_secondaries = ""
        if pref_record:
            raw_secondaries = pref_record.preferred_platforms or pref_record.secondary_platforms or ""
        secondary_prefs = [
            p.strip().lower()
            for p in raw_secondaries.split(",")
            if p.strip() and p.strip().lower() != "no_preference" and p.strip().lower() != primary_pref
        ]

        # 3. Query all active, verified candidate resources for this concept or skill
        candidates: List[LearningResource] = (
            db.query(LearningResource)
            .options(joinedload(LearningResource.skill))
            .filter(
                LearningResource.is_active.is_(True),
                (LearningResource.concept_slug == concept_slug) | (LearningResource.skill_id == module.skill_id),
            )
            .all()
        )

        # Policy: Avoid YouTube videos - prioritize structured documentation, interactive sandboxes, and accredited courseware
        candidates = [
            r for r in candidates
            if (r.provider or "").strip().lower() != "youtube"
            and "youtube.com" not in (r.url or "").lower()
            and "youtu.be" not in (r.url or "").lower()
        ]

        if not candidates:
            return None

        # Filter candidates strictly relevant to this concept
        concept_candidates = [r for r in candidates if r.concept_slug == concept_slug]
        active_pool = concept_candidates if concept_candidates else candidates

        def normalize_provider(p_str: Optional[str]) -> str:
            return (p_str or "").strip().lower().replace(" ", "").replace("_", "")

        norm_primary = normalize_provider(primary_pref)
        norm_secondaries = [normalize_provider(sp) for sp in secondary_prefs]

        # 4. Multi-tier deterministic selection logic
        selected_resource: Optional[LearningResource] = None
        match_type: str = "automatic"
        selection_reason: str = ""

        # Step 4A: Check Primary Platform Match (only if concept relevance is satisfied)
        if primary_pref != "no_preference":
            primary_matches = [
                r for r in active_pool
                if normalize_provider(r.provider) == norm_primary
            ]
            if primary_matches:
                # Rank within primary matches by: level match > role match > quality rank
                def rank_primary(r: LearningResource) -> int:
                    score = 0
                    if (r.difficulty or "").strip().capitalize() == learner_level:
                        score += 50
                    if r.role_name.lower() in [user_role_name.lower(), "all"]:
                        score += 30
                    if getattr(r, "verified", True):
                        score += 20
                    if getattr(r, "quality_rank", 1) == 1:
                        score += 10
                    return score

                primary_matches.sort(key=rank_primary, reverse=True)
                selected_resource = primary_matches[0]
                match_type = "primary"
                selection_reason = f"Matches your preferred platform ({selected_resource.provider}) and current learning level ({learner_level})."

        # Step 4B: If no primary match, check Secondary Platforms
        if not selected_resource and norm_secondaries:
            secondary_matches = [
                r for r in active_pool
                if normalize_provider(r.provider) in norm_secondaries
            ]
            if secondary_matches:
                def rank_secondary(r: LearningResource) -> int:
                    score = 0
                    if (r.difficulty or "").strip().capitalize() == learner_level:
                        score += 50
                    if r.role_name.lower() in [user_role_name.lower(), "all"]:
                        score += 30
                    if getattr(r, "verified", True):
                        score += 20
                    return score

                secondary_matches.sort(key=rank_secondary, reverse=True)
                selected_resource = secondary_matches[0]
                match_type = "secondary"
                if primary_pref != "no_preference":
                    selection_reason = (
                        f"Your preferred platform did not have a matching resource for {module.concept_name}, "
                        f"so SkillPath selected your preferred secondary platform ({selected_resource.provider})."
                    )
                else:
                    selection_reason = f"Matches your preferred secondary platform ({selected_resource.provider})."

        # Step 4C: If still no match or "no_preference", select best verified SkillPath resource
        if not selected_resource:
            def rank_fallback(r: LearningResource) -> int:
                score = 0
                if r.concept_slug == concept_slug:
                    score += 100
                if (r.difficulty or "").strip().capitalize() == learner_level:
                    score += 50
                if r.role_name.lower() in [user_role_name.lower(), "all"]:
                    score += 30
                if getattr(r, "verified", True):
                    score += 20
                if getattr(r, "quality_rank", 1) == 1:
                    score += 15
                return score

            sorted_pool = sorted(active_pool, key=rank_fallback, reverse=True)
            selected_resource = sorted_pool[0]

            if primary_pref != "no_preference" or secondary_prefs:
                match_type = "skillpath_fallback"
                selection_reason = (
                    f"Your preferred platforms did not have an aligned resource for {module.concept_name}, "
                    f"so SkillPath selected the next best verified resource ({selected_resource.provider})."
                )
            else:
                match_type = "automatic"
                selection_reason = f"Selected by SkillPath as the highest-quality verified resource for {module.concept_name}."

        return {
            "id": selected_resource.id,
            "title": selected_resource.title,
            "provider": selected_resource.provider,
            "url": selected_resource.url,
            "description": getattr(selected_resource, "description", None) or f"Learn {module.concept_name} with verified explanations and practical code examples.",
            "concept_slug": selected_resource.concept_slug,
            "concept_name": module.concept_name,
            "skill_name": selected_resource.skill.name if selected_resource.skill else (module.skill.name if module.skill else "Skill"),
            "difficulty": selected_resource.difficulty,
            "resource_type": selected_resource.resource_type,
            "estimated_minutes": selected_resource.estimated_minutes,
            "verified": getattr(selected_resource, "verified", True),
            "selection_reason": selection_reason,
            "is_preferred_platform": match_type in ["primary", "secondary"],
            "platform_match_type": match_type,
        }


resource_recommendation_service = ResourceRecommendationService()
