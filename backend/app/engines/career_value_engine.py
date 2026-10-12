from typing import Dict, Any, Optional


class CareerValueEngine:
    """
    Deterministic Career Value Engine for SkillPath AI.

    Answers: "Which weak skill matters most for the learner's target career?"
    Priority is determined not simply by which skill has the largest gap, but by
    the intersection of role benchmark importance, labor market relevance,
    evidence gaps, and Skill Debt.

    Formula:
    career_value_score = (
        0.30 * gap_score +
        0.25 * role_importance +
        0.15 * industry_relevance +
        0.10 * confidence_gap +
        0.10 * recency_gap +
        0.10 * evidence_gap
    ) + debt_boost

    Where:
    - gap_score = max(0, min(100, required_skill_level - current_skill_level))
    - confidence_gap = max(0, min(100, 100 - confidence))
    - recency_gap = max(0, min(100, 100 - recency))
    - evidence_gap = max(0, min(100, 100 - evidence_score))
    - debt_boost: HIGH debt = +10, MEDIUM debt = +5, LOW debt = +2, otherwise = 0
    - Clamped strictly to [0.0, 100.0]
    """

    INDUSTRY_RELEVANCE_MAP = {
        "CRITICAL": 100.0,
        "HIGH": 80.0,
        "MEDIUM": 60.0,
        "LOW": 40.0,
    }

    def parse_industry_relevance(self, relevance_input: Any) -> float:
        """Parses string or numeric industry relevance into normalized 0-100 float."""
        if isinstance(relevance_input, (int, float)):
            return round(min(100.0, max(0.0, float(relevance_input))), 1)

        if isinstance(relevance_input, str):
            clean = relevance_input.strip().upper()
            return self.INDUSTRY_RELEVANCE_MAP.get(clean, 80.0)

        return 80.0

    def calculate_career_value_score(
        self,
        gap_score: float,
        role_importance: float,
        industry_relevance: float,
        confidence_gap: float,
        recency_gap: float,
        evidence_gap: float,
        debt_boost: float,
    ) -> float:
        """
        Calculates normalized, deterministic career value score clamped to [0.0, 100.0].
        """
        base_score = (
            (0.30 * gap_score)
            + (0.25 * role_importance)
            + (0.15 * industry_relevance)
            + (0.10 * confidence_gap)
            + (0.10 * recency_gap)
            + (0.10 * evidence_gap)
        )
        final_score = base_score + debt_boost
        return round(min(100.0, max(0.0, final_score)), 1)

    def determine_debt_boost(self, debt_status: str, debt_severity: str) -> float:
        """
        Deterministic boost awarded for existing Skill Debt:
        HIGH debt: +10, MEDIUM debt: +5, LOW debt: +2, otherwise: 0.0
        """
        if debt_status == "SKILL_DEBT":
            if debt_severity == "HIGH":
                return 10.0
            elif debt_severity == "MEDIUM":
                return 5.0
            elif debt_severity == "LOW":
                return 2.0
        return 0.0

    def classify_priority(self, career_value_score: float) -> str:
        """
        Converts career value score into deterministic priority tier:
        - CRITICAL: 70 - 100
        - HIGH: 55 - 69.9
        - MEDIUM: 40 - 54.9
        - LOW: 0 - 39.9
        """
        if career_value_score >= 70.0:
            return "CRITICAL"
        elif career_value_score >= 55.0:
            return "HIGH"
        elif career_value_score >= 40.0:
            return "MEDIUM"
        else:
            return "LOW"

    def generate_explanation(
        self,
        skill_name: str,
        role_name: str,
        current_level: float,
        required_level: float,
        gap_score: float,
        role_importance: float,
        industry_relevance: float,
        debt_status: str,
        debt_severity: str,
        career_value_score: float,
        priority: str,
    ) -> str:
        """
        Generates deterministic, explainable rationale without using LLMs.
        Covers both "Why focus on this?" and "Why can this be postponed?".
        """
        # Case 1: Low role importance / low industry relevance ("Why not this?")
        if role_importance < 50.0 or industry_relevance < 50.0:
            return (
                f"{skill_name} is currently lower priority (Career Value: {career_value_score}) "
                f"because it has lower importance ({role_importance:.0f}%) and lower industry relevance for {role_name}, "
                f"despite your demonstrated proficiency of {current_level}%. It can be safely postponed."
            )

        # Case 2: Skill is already mastered / healthy
        if current_level >= required_level:
            return (
                f"{skill_name} is in strong standing (Proficiency: {current_level}% vs required {required_level}%). "
                f"No remediation needed for the {role_name} benchmark."
            )

        # Case 3: High/Critical priority with Skill Debt
        if debt_status == "SKILL_DEBT" and debt_severity in ("HIGH", "MEDIUM"):
            return (
                f"{skill_name} is a high-priority career gap because it is highly important for the {role_name} role "
                f"({role_importance}%), your current proficiency is {current_level}% versus required {required_level}%, "
                f"and it carries {debt_severity} Skill Debt requiring immediate re-validation."
            )

        # Case 4: General high or medium career gap
        return (
            f"{skill_name} requires development for {role_name} ({gap_score:.0f}% deficit). "
            f"Role importance is {role_importance}% with {industry_relevance:.0f}% industry market relevance."
        )

    def determine_recommended_focus(
        self, priority: str, current_level: float, required_level: float
    ) -> str:
        """
        Determines deterministic intervention/action recommendation.
        """
        if current_level >= required_level:
            return "Maintain & Verify Periodically"

        if priority == "CRITICAL":
            return "Immediate Re-validation & Targeted Practice"
        elif priority == "HIGH":
            return "Priority Skill Reinforcement & Assessment"
        elif priority == "MEDIUM":
            return "Targeted Development in Next Sprint"
        else:
            return "Safely Postpone (Low Target Role Priority)"

    def evaluate_career_value(
        self,
        skill_id: int,
        skill_name: str,
        skill_category: str,
        role_id: int,
        role_name: str,
        current_skill_level: float,
        required_skill_level: float,
        role_importance: float,
        industry_relevance_raw: Any,
        confidence: float,
        recency: float,
        evidence_score: float,
        skill_debt_item: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates full multidimensional career value for a single role skill.
        """
        # Normalize inputs
        curr_lvl = round(max(0.0, min(100.0, float(current_skill_level))), 1)
        req_lvl = round(max(0.0, min(100.0, float(required_skill_level))), 1)
        role_imp = round(max(0.0, min(100.0, float(role_importance))), 1)
        ind_rel = self.parse_industry_relevance(industry_relevance_raw)

        # Industry relevance label
        if ind_rel >= 90.0:
            ind_rel_label = "Critical"
        elif ind_rel >= 75.0:
            ind_rel_label = "High"
        elif ind_rel >= 55.0:
            ind_rel_label = "Medium"
        else:
            ind_rel_label = "Low"

        # Gaps
        gap_score = round(max(0.0, min(100.0, req_lvl - curr_lvl)), 1)
        conf_gap = round(max(0.0, min(100.0, 100.0 - float(confidence))), 1)
        rec_gap = round(max(0.0, min(100.0, 100.0 - float(recency))), 1)
        ev_gap = round(max(0.0, min(100.0, 100.0 - float(evidence_score))), 1)

        # Skill Debt integration
        debt_status = "UNKNOWN"
        debt_score = 0.0
        debt_severity = "NONE"
        if skill_debt_item:
            debt_status = skill_debt_item.get("debt_status", "UNKNOWN")
            debt_score = float(skill_debt_item.get("debt_score", 0.0))
            debt_severity = skill_debt_item.get("severity", "NONE")

        debt_boost = self.determine_debt_boost(debt_status, debt_severity)

        # Final Score & Priority
        career_value_score = self.calculate_career_value_score(
            gap_score=gap_score,
            role_importance=role_imp,
            industry_relevance=ind_rel,
            confidence_gap=conf_gap,
            recency_gap=rec_gap,
            evidence_gap=ev_gap,
            debt_boost=debt_boost,
        )

        priority = self.classify_priority(career_value_score)

        reason = self.generate_explanation(
            skill_name=skill_name,
            role_name=role_name,
            current_level=curr_lvl,
            required_level=req_lvl,
            gap_score=gap_score,
            role_importance=role_imp,
            industry_relevance=ind_rel,
            debt_status=debt_status,
            debt_severity=debt_severity,
            career_value_score=career_value_score,
            priority=priority,
        )

        recommended_focus = self.determine_recommended_focus(
            priority=priority,
            current_level=curr_lvl,
            required_level=req_lvl,
        )

        return {
            "skill_id": skill_id,
            "skill_name": skill_name,
            "skill_category": skill_category,
            "role_id": role_id,
            "role_name": role_name,
            "current_skill_level": curr_lvl,
            "required_skill_level": req_lvl,
            "gap_score": gap_score,
            "role_importance": role_imp,
            "industry_relevance": ind_rel,
            "industry_relevance_label": ind_rel_label,
            "confidence": round(float(confidence), 1),
            "confidence_gap": conf_gap,
            "recency": round(float(recency), 1),
            "recency_gap": rec_gap,
            "evidence_score": round(float(evidence_score), 1),
            "evidence_gap": ev_gap,
            "skill_debt_status": debt_status,
            "skill_debt_score": debt_score,
            "debt_boost": debt_boost,
            "career_value_score": career_value_score,
            "priority": priority,
            "reason": reason,
            "recommended_focus": recommended_focus,
            "rank": None,
        }


career_value_engine = CareerValueEngine()
