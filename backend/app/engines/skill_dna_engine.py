import math
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.evidence import SkillEvidence


class SkillDNAEngine:
    """
    Deterministic Engine computing multidimensional Skill DNA vector per learner & skill.
    Calculates:
    - Accuracy: Demonstrated correctness (0-100)
    - Difficulty: Mapped task difficulty (Easy=35, Medium=65, Hard=90)
    - Recency: Continuous exponential decay based on evidence age (0-100)
    - Evidence Score: Strength of available evidence considering source type & score (0-100)
    - Confidence: Trustworthiness based on evidence quantity & consistency (0-100)
    - Skill Level: 0.60*accuracy + 0.15*difficulty + 0.15*recency + 0.10*evidence_score (0-100)
    - Status: Deterministic classification (HEALTHY, STRONG, DEVELOPING, CRITICAL, UNKNOWN)
    """

    def calculate_recency(self, latest_evidence_dt: Optional[datetime]) -> float:
        if not latest_evidence_dt:
            return 0.0
        now = datetime.utcnow()
        days_old = max(0, (now - latest_evidence_dt).days)
        # Exponential decay formula: 100 * exp(-0.0044 * days)
        # Today (0d) = 100.0, 7d = 97.0, 30d = 87.6, 90d = 67.3, 180d = 45.3, 365d = 20.1
        decayed = 100.0 * math.exp(-0.0044 * days_old)
        return round(min(100.0, max(0.0, decayed)), 1)

    def format_recency_label(self, recency_score: float, latest_evidence_dt: Optional[datetime]) -> str:
        if not latest_evidence_dt:
            return "Not assessed yet"
        days_old = max(0, (datetime.utcnow() - latest_evidence_dt).days)
        if days_old == 0:
            return "Today"
        elif days_old == 1:
            return "Yesterday"
        elif days_old < 7:
            return f"{days_old} days ago"
        elif days_old < 30:
            weeks = max(1, days_old // 7)
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif days_old < 365:
            months = max(1, days_old // 30)
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = max(1, days_old // 365)
            return f"{years} year{'s' if years > 1 else ''} ago"

    def map_difficulty(self, difficulty_str: Optional[str]) -> float:
        if not difficulty_str:
            return 50.0
        d_lower = difficulty_str.strip().lower()
        if d_lower in ["easy", "beginner"]:
            return 35.0
        elif d_lower in ["medium", "intermediate"]:
            return 65.0
        elif d_lower in ["hard", "advanced"]:
            return 90.0
        return 50.0

    def format_difficulty_label(self, difficulty_score: float) -> str:
        if difficulty_score >= 80.0:
            return "Hard"
        elif difficulty_score >= 50.0:
            return "Intermediate"
        elif difficulty_score > 0.0:
            return "Easy"
        return "Unspecified"

    def calculate_evidence_score(self, evidences: List[SkillEvidence]) -> float:
        if not evidences:
            return 0.0

        source_weights = {
            "ASSESSMENT": 60.0,
            "PRACTICE": 75.0,
            "PROJECT": 90.0,
            "REAL_WORLD_TASK": 100.0,
        }

        # Evaluate each evidence strength: 50% source type weight + 50% score
        strengths = []
        for ev in evidences:
            ev_type = (ev.evidence_type or "").upper()
            w_source = source_weights.get(ev_type, 60.0)
            score_val = ev.score if ev.score is not None else 50.0
            strength = (0.5 * w_source) + (0.5 * score_val)
            strengths.append(strength)

        # Primary weight on latest/highest evidence
        max_strength = max(strengths)
        latest_strength = strengths[0]  # assumes ordered by created_at desc
        combined = (0.6 * latest_strength) + (0.4 * max_strength)
        return round(min(100.0, max(0.0, combined)), 1)

    def calculate_confidence(self, evidences: List[SkillEvidence]) -> float:
        count = len(evidences)
        if count == 0:
            return 0.0
        elif count == 1:
            base_conf = 50.0
        elif count == 2:
            base_conf = 70.0
        else:
            base_conf = min(100.0, 85.0 + (count - 3) * 5.0)

        # Consistency adjustment: examine standard deviation if 2+ records
        if count >= 2:
            scores = [ev.score for ev in evidences if ev.score is not None]
            if len(scores) >= 2:
                mean_s = sum(scores) / len(scores)
                variance = sum((s - mean_s) ** 2 for s in scores) / len(scores)
                std_dev = math.sqrt(variance)

                if std_dev <= 10.0:
                    base_conf += 5.0  # consistent performance boost
                elif std_dev >= 25.0:
                    base_conf -= 10.0  # inconsistent performance penalty

        return round(min(100.0, max(0.0, base_conf)), 1)

    def calculate_skill_level(
        self, accuracy: float, difficulty: float, recency: float, evidence_score: float
    ) -> float:
        # Phase 5 Baseline Deterministic Formula:
        # skill_level = 0.60 * accuracy + 0.15 * difficulty + 0.15 * recency + 0.10 * evidence_score
        raw_level = (
            (0.60 * accuracy)
            + (0.15 * difficulty)
            + (0.15 * recency)
            + (0.10 * evidence_score)
        )
        return round(min(100.0, max(0.0, raw_level)), 1)

    def determine_status(self, skill_level: float, evidence_count: int) -> str:
        if evidence_count == 0:
            return "UNKNOWN"
        if skill_level >= 90.0:
            return "HEALTHY"
        elif skill_level >= 75.0:
            return "STRONG"
        elif skill_level >= 50.0:
            return "DEVELOPING"
        else:
            return "CRITICAL"

    def compute_skill_dna(
        self,
        user_id: int,
        skill_id: int,
        skill_name: str,
        skill_category: str,
        evidences: List[SkillEvidence],
        user_skill_difficulty: Optional[str] = "Intermediate",
    ) -> Dict[str, Any]:
        """
        Computes full multi-dimensional Skill DNA vector for a skill based on evidence.
        """
        count = len(evidences)
        if count == 0:
            return {
                "user_id": user_id,
                "skill_id": skill_id,
                "skill_name": skill_name,
                "skill_category": skill_category,
                "skill_level": 0.0,
                "confidence": 0.0,
                "accuracy": 0.0,
                "difficulty": 0.0,
                "difficulty_label": "Unassessed",
                "recency": 0.0,
                "recency_label": "Not assessed yet",
                "evidence_score": 0.0,
                "evidence_count": 0,
                "last_assessed_at": datetime.utcnow(),
                "status": "UNKNOWN",
            }

        # Order by created_at desc if not already
        sorted_evs = sorted(evidences, key=lambda e: e.created_at, reverse=True)
        latest_ev = sorted_evs[0]

        # 1. Accuracy
        accuracy = round(float(latest_ev.score if latest_ev.score is not None else 0.0), 1)

        # 2. Difficulty
        diff_score = self.map_difficulty(user_skill_difficulty)
        diff_label = self.format_difficulty_label(diff_score)

        # 3. Recency
        recency = self.calculate_recency(latest_ev.created_at)
        recency_label = self.format_recency_label(recency, latest_ev.created_at)

        # 4. Evidence Score
        ev_score = self.calculate_evidence_score(sorted_evs)

        # 5. Confidence
        confidence = self.calculate_confidence(sorted_evs)

        # 6. Skill Level
        skill_level = self.calculate_skill_level(
            accuracy=accuracy,
            difficulty=diff_score,
            recency=recency,
            evidence_score=ev_score,
        )

        # 7. Status
        status = self.determine_status(skill_level, count)

        return {
            "user_id": user_id,
            "skill_id": skill_id,
            "skill_name": skill_name,
            "skill_category": skill_category,
            "skill_level": skill_level,
            "confidence": confidence,
            "accuracy": accuracy,
            "difficulty": diff_score,
            "difficulty_label": diff_label,
            "recency": recency,
            "recency_label": recency_label,
            "evidence_score": ev_score,
            "evidence_count": count,
            "last_assessed_at": latest_ev.created_at,
            "status": status,
        }


skill_dna_engine = SkillDNAEngine()
