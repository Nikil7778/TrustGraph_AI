from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.evidence import SkillEvidence


class SkillDebtEngine:
    """
    Deterministic engine for detecting Skill Debt (previously encountered skills
    whose current evidence is too weak, low, or old for target role performance).

    Classification Logic:
    - UNKNOWN: No evidence and no role benchmark.
    - MISSING: Role requires the skill AND learner has 0 evidence of learning/exposure.
    - SKILL_DEBT: Evidence of exposure exists (>0 artifacts), BUT current skill level
      is below role requirement, OR confidence is low, OR evidence is stale.
    - HEALTHY: Current demonstrated Skill DNA matches or exceeds role requirement
      with fresh evidence.
    """

    def calculate_debt_score(
        self,
        role_requirement: float,
        skill_level: float,
        confidence: float,
        recency: float,
        evidence_score: float,
        has_practical_evidence: bool,
        debt_status: str,
    ) -> float:
        """
        Deterministic Debt Score Formula (0 to 100):
        debt_score = 0.40 * role_gap + 0.20 * confidence_gap + 0.15 * recency_gap + 0.15 * evidence_gap + 0.10 * practical_gap
        """
        if debt_status == "HEALTHY":
            return 0.0

        if debt_status == "MISSING":
            role_gap = max(0.0, min(100.0, role_requirement - skill_level))
            return round(min(100.0, max(0.0, (0.50 * role_gap) + 50.0)), 1)

        role_gap = max(0.0, min(100.0, role_requirement - skill_level))
        confidence_gap = max(0.0, min(100.0, 100.0 - confidence))
        recency_gap = max(0.0, min(100.0, 100.0 - recency))
        evidence_gap = max(0.0, min(100.0, 100.0 - evidence_score))
        practical_gap = 0.0 if has_practical_evidence else 100.0

        raw_score = (
            (0.40 * role_gap)
            + (0.20 * confidence_gap)
            + (0.15 * recency_gap)
            + (0.15 * evidence_gap)
            + (0.10 * practical_gap)
        )
        return round(min(100.0, max(0.0, raw_score)), 1)

    def determine_severity(
        self, debt_status: str, debt_score: float, role_gap: float, importance_score: float
    ) -> str:
        if debt_status == "HEALTHY":
            return "NONE"
        if debt_status == "MISSING":
            return "HIGH"

        if debt_score >= 60.0 or (role_gap >= 20.0 and importance_score >= 70.0):
            return "HIGH"
        elif debt_score >= 35.0 or role_gap >= 10.0:
            return "MEDIUM"
        else:
            return "LOW"

    def generate_explanation(
        self,
        skill_name: str,
        role_name: str,
        role_requirement: float,
        skill_level: float,
        evidence_count: int,
        recency_label: str,
        debt_status: str,
        severity: str,
    ) -> str:
        if debt_status == "SKILL_DEBT":
            art_text = "artifact" if evidence_count == 1 else "artifacts"
            return (
                f"{skill_name} is classified as Skill Debt because you have previously demonstrated exposure "
                f"({evidence_count} proof {art_text}), but your current demonstrated proficiency is {skill_level:.1f}%, "
                f"below the {role_name} requirement of {role_requirement:.1f}%, with {recency_label.lower()} evidence."
            )
        elif debt_status == "MISSING":
            return (
                f"{skill_name} is required for the {role_name} position ({role_requirement:.1f}% benchmark), "
                f"but no verified learning evidence has been logged yet."
            )
        elif debt_status == "HEALTHY":
            return (
                f"{skill_name} meets the {role_name} position benchmark ({skill_level:.1f}% demonstrated vs "
                f"{role_requirement:.1f}% required) supported by verified recent evidence."
            )
        else:
            return f"No benchmark or evidence recorded for {skill_name}."

    def determine_intervention(self, debt_status: str, severity: str) -> str:
        if debt_status == "HEALTHY":
            return "Maintain & verify on portfolio project"
        if debt_status == "MISSING":
            return "Baseline assessment + intro course"

        if severity == "HIGH":
            return "Reassess + targeted practice"
        elif severity == "MEDIUM":
            return "Practice + practical task"
        else:
            return "Refresh + reassess"

    def evaluate_skill_debt(
        self,
        skill_id: int,
        skill_name: str,
        skill_category: str,
        role_id: int,
        role_name: str,
        role_requirement: float,
        importance_score: float,
        skill_dna: Dict[str, Any],
        evidences: List[SkillEvidence],
    ) -> Dict[str, Any]:
        """
        Calculates deterministic Skill Debt item for a specific skill and role benchmark.
        """
        skill_level = float(skill_dna.get("skill_level", 0.0))
        confidence = float(skill_dna.get("confidence", 0.0))
        accuracy = float(skill_dna.get("accuracy", 0.0))
        recency = float(skill_dna.get("recency", 0.0))
        recency_label = skill_dna.get("recency_label", "Not assessed yet")
        evidence_score = float(skill_dna.get("evidence_score", 0.0))
        evidence_count = int(skill_dna.get("evidence_count", 0))
        last_assessed_at = skill_dna.get("last_assessed_at")

        # Count practical / project evidence
        practical_types = {"PRACTICE", "PROJECT", "REAL_WORLD_TASK"}
        practical_count = sum(1 for e in evidences if (e.evidence_type or "").upper() in practical_types)
        has_practical = practical_count > 0

        role_gap = max(0.0, role_requirement - skill_level)

        # 1. Determine Status
        if evidence_count == 0:
            debt_status = "MISSING" if role_requirement > 0 else "UNKNOWN"
        else:
            # Evidence exists: check if proficiency / confidence / recency is weak
            is_proficient = role_gap <= 0.0 and accuracy >= (role_requirement - 10.0) and recency >= 50.0
            if is_proficient:
                debt_status = "HEALTHY"
            else:
                debt_status = "SKILL_DEBT"

        # 2. Debt Score
        debt_score = self.calculate_debt_score(
            role_requirement=role_requirement,
            skill_level=skill_level,
            confidence=confidence,
            recency=recency,
            evidence_score=evidence_score,
            has_practical_evidence=has_practical,
            debt_status=debt_status,
        )

        # 3. Severity
        severity = self.determine_severity(
            debt_status=debt_status,
            debt_score=debt_score,
            role_gap=role_gap,
            importance_score=importance_score,
        )

        # 4. Reason Explanation
        reason = self.generate_explanation(
            skill_name=skill_name,
            role_name=role_name,
            role_requirement=role_requirement,
            skill_level=skill_level,
            evidence_count=evidence_count,
            recency_label=recency_label,
            debt_status=debt_status,
            severity=severity,
        )

        # 5. Intervention
        intervention = self.determine_intervention(debt_status, severity)

        return {
            "skill_id": skill_id,
            "skill_name": skill_name,
            "skill_category": skill_category,
            "role_id": role_id,
            "role_name": role_name,
            "role_requirement": role_requirement,
            "current_skill_level": skill_level,
            "confidence": confidence,
            "accuracy": accuracy,
            "recency": recency,
            "recency_label": recency_label,
            "evidence_count": evidence_count,
            "practical_evidence_count": practical_count,
            "latest_evidence_at": last_assessed_at,
            "debt_status": debt_status,
            "debt_score": debt_score,
            "severity": severity,
            "reason": reason,
            "recommended_intervention": intervention,
        }


skill_debt_engine = SkillDebtEngine()
