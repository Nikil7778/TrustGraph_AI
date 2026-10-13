from datetime import datetime
from typing import List, Dict, Any, Optional


class NextBestProofEngine:
    """
    Deterministic Next-Best-Proof Engine for SkillPath AI.

    Answers: "What is the single most valuable thing this learner should prove next
    to move closer to their target role?"

    Formula:
    next_best_proof_score = (
        0.35 * career_value_score +
        0.20 * skill_debt_score +
        0.15 * evidence_gap +
        0.10 * confidence_gap +
        0.10 * practical_evidence_gap +
        0.10 * action_readiness
    )
    Clamped strictly to [0.0, 100.0].
    """

    PREREQUISITES_MAP: Dict[str, List[str]] = {
        "SQL JOINs": ["SQL"],
        "EDA": ["Python", "Statistics"],
        "Data Visualization": ["EDA"],
        "Power BI": ["Data Visualization"],
        "Machine Learning": ["Python", "Statistics", "EDA"],
    }

    ACTION_LABELS = {
        "LEARN": "Foundational Learning",
        "PRACTICE": "Targeted Practice",
        "REASSESS": "Diagnostic Reassessment",
        "PRACTICAL_TASK": "Practical Task",
        "PROJECT": "Portfolio Project",
        "REVIEW_PREREQUISITE": "Prerequisite Review",
    }

    def check_prerequisites(
        self, skill_name: str, skills_dna_map: Dict[str, Dict[str, Any]], role_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines whether required prerequisites for a skill are healthy.
        A prerequisite is healthy if demonstrated proficiency >= 65.0% and has evidence.
        """
        if role_name:
            from app.engines.role_curriculum import role_curriculum_engine
            role_prereqs = role_curriculum_engine.get_prerequisite_graph_for_role(role_name)
            required_prereqs = role_prereqs.get(skill_name, self.PREREQUISITES_MAP.get(skill_name, []))
        else:
            required_prereqs = self.PREREQUISITES_MAP.get(skill_name, [])

        if not required_prereqs:
            return {"status": "NONE", "healthy": True, "blocking": [], "prereqs": []}

        blocking = []
        for p_name in required_prereqs:
            p_dna = skills_dna_map.get(p_name)
            if not p_dna:
                blocking.append(p_name)
                continue

            p_level = float(p_dna.get("skill_level", 0.0))
            p_ev_count = int(p_dna.get("evidence_count", 0))

            if p_level < 65.0 or p_ev_count == 0:
                blocking.append(p_name)

        is_healthy = len(blocking) == 0
        return {
            "status": "HEALTHY" if is_healthy else "BLOCKED",
            "healthy": is_healthy,
            "blocking": blocking,
            "prereqs": required_prereqs,
        }

    def calculate_action_readiness(
        self, prereq_healthy: bool, evidence_count: int, current_level: float
    ) -> float:
        """
        Determines action readiness score (0-100).
        - 100.0: Prerequisites healthy & conceptual foundation exists
        - 70.0: Prerequisites healthy, but limited evidence
        - 30.0: Prerequisites blocked
        """
        if not prereq_healthy:
            return 30.0
        if evidence_count > 0 and current_level >= 40.0:
            return 100.0
        return 70.0

    def select_action_type(
        self,
        skill_name: str,
        current_level: float,
        required_level: float,
        accuracy: float,
        confidence: float,
        evidence_count: int,
        practical_evidence_count: int,
        debt_status: str,
        prereq_info: Dict[str, Any],
        recent_evidence_types: List[str],
    ) -> Dict[str, Any]:
        """
        Evidence-aware decision rules selecting action type, title, expected proof,
        and effort estimation.
        """
        # Rule 1: Prerequisite Blocked
        if not prereq_info["healthy"] and prereq_info["blocking"]:
            blocking_skill = prereq_info["blocking"][0]
            return {
                "action_type": "REVIEW_PREREQUISITE",
                "title": f"Review {blocking_skill} Prerequisites",
                "estimated_minutes": 20,
                "expected_proof": f"Achieve >= 70% demonstrated proficiency in {blocking_skill} to unblock {skill_name}.",
                "why_this_action": f"Foundational mastery in {blocking_skill} is required before attempting reliable demonstration of {skill_name}.",
            }

        # Rule 2: Zero Evidence / Missing Skill
        if evidence_count == 0 or debt_status == "MISSING":
            return {
                "action_type": "LEARN",
                "title": f"{skill_name} Foundations & Core Principles",
                "estimated_minutes": 30,
                "expected_proof": f"Complete guided walkthrough and pass the foundational checkpoint for {skill_name}.",
                "why_this_action": f"No baseline evidence exists for {skill_name}; initial conceptual grounding is required.",
            }

        # Rule 3: Conceptual Strength but Missing Practical Proof (Section 8 example: level 75, weak practical -> PRACTICAL_TASK)
        if current_level >= 65.0 and practical_evidence_count == 0:
            return {
                "action_type": "PRACTICAL_TASK",
                "title": f"Real-World {skill_name} Analysis Task",
                "estimated_minutes": 45,
                "expected_proof": f"Execute complete multi-step dataset transformation applying {skill_name} logic.",
                "why_this_action": f"Your theoretical understanding is strong ({current_level}%), but employer-grade practical proof is missing.",
            }

        # Rule 4: Recent Practice Submitted -> Reassess to Update DNA (Section 8 & 9: Avoid redundant practice)
        if "PRACTICE" in recent_evidence_types and confidence < 80.0:
            return {
                "action_type": "REASSESS",
                "title": f"{skill_name} Diagnostic Reassessment",
                "estimated_minutes": 15,
                "expected_proof": f"Score at least 80% on 10 assessment questions to verify retention.",
                "why_this_action": f"Practice completed; an updated diagnostic verification is needed to validate baseline retention.",
            }

        # Rule 5: Skill Debt / Low Demonstrated Performance (Section 8 example: level 45, weak assessment -> PRACTICE)
        if debt_status == "SKILL_DEBT" or (current_level < required_level and accuracy <= 65.0):
            # If recent action was already assessment, enforce PRACTICE to avoid redundant testing
            return {
                "action_type": "PRACTICE",
                "title": f"{skill_name} Rescue Practice",
                "estimated_minutes": 25,
                "expected_proof": f"Solve 8/10 targeted {skill_name} problems across core difficulty scenarios.",
                "why_this_action": f"You have previously studied {skill_name} but current evidence shows active Skill Debt. Targeted practice directly repairs weak performance.",
            }

        # Rule 6: High Mastery -> Portfolio Project
        if current_level >= 75.0:
            return {
                "action_type": "PROJECT",
                "title": f"End-to-End {skill_name} Portfolio Project",
                "estimated_minutes": 90,
                "expected_proof": f"Build and document a production-ready data pipeline demonstrating {skill_name}.",
                "why_this_action": f"Benchmark level achieved. A capstone portfolio project provides high-impact employer verification.",
            }

        # Default fallback: Targeted Practice
        return {
            "action_type": "PRACTICE",
            "title": f"{skill_name} Reinforcement Practice",
            "estimated_minutes": 25,
            "expected_proof": f"Complete 8 practice exercises covering {skill_name}.",
            "why_this_action": f"Reinforce core competencies to close the remaining gap to target benchmark.",
        }

    def calculate_score(
        self,
        career_value_score: float,
        skill_debt_score: float,
        evidence_gap: float,
        confidence_gap: float,
        practical_evidence_gap: float,
        action_readiness: float,
    ) -> float:
        """
        Deterministic Next-Best-Proof Score Formula (0 to 100):
        0.35 * career_value_score +
        0.20 * skill_debt_score +
        0.15 * evidence_gap +
        0.10 * confidence_gap +
        0.10 * practical_evidence_gap +
        0.10 * action_readiness
        """
        raw_score = (
            (0.35 * career_value_score)
            + (0.20 * skill_debt_score)
            + (0.15 * evidence_gap)
            + (0.10 * confidence_gap)
            + (0.10 * practical_evidence_gap)
            + (0.10 * action_readiness)
        )
        return round(min(100.0, max(0.0, raw_score)), 1)

    def classify_priority(
        self, nbp_score: float, career_value_priority: str, debt_status: str
    ) -> str:
        """Classifies priority into CRITICAL, HIGH, MEDIUM, LOW."""
        if nbp_score >= 60.0 or (career_value_priority in ("CRITICAL", "HIGH") and debt_status == "SKILL_DEBT"):
            return "CRITICAL"
        elif nbp_score >= 48.0 or career_value_priority in ("HIGH", "MEDIUM"):
            return "HIGH"
        elif nbp_score >= 35.0:
            return "MEDIUM"
        else:
            return "LOW"

    def generate_explanations(
        self,
        skill_name: str,
        role_name: str,
        action_type: str,
        current_level: float,
        required_level: float,
        gap_score: float,
        debt_status: str,
        practical_evidence_count: int,
    ) -> Dict[str, str]:
        """
        Generates structured, deterministic explanations:
        - reason: overall justification
        - why_now: urgency justification
        - why_this_action: action selection rationale
        """
        reason = (
            f"{skill_name} is recommended because it is a critical competency for {role_name}, "
            f"your current demonstrated level is {current_level}% versus required {required_level}% "
            f"({gap_score:.0f}% deficit), and existing evidence indicates {debt_status}."
        )

        why_now = (
            f"Closing your deficit in {skill_name} yields the highest immediate Career Value gain "
            f"toward qualifying for {role_name} benchmark roles."
        )

        if action_type == "PRACTICE":
            why_this_action = (
                f"You have prior exposure to {skill_name}, but current performance is inconsistent. "
                f"Targeted problem practice is the fastest path to rebuild reliable demonstration."
            )
        elif action_type == "PRACTICAL_TASK":
            why_this_action = (
                f"Your conceptual assessment baseline is established, but hands-on project evidence "
                f"is required to satisfy employer proof standards."
            )
        elif action_type == "LEARN":
            why_this_action = (
                f"No baseline evidence has been recorded for {skill_name}. Foundational concept "
                f"acquisition is required before diagnostic testing."
            )
        elif action_type == "REASSESS":
            why_this_action = (
                f"Recent practice exercises were completed; an adaptive verification reassessment "
                f"will confirm that your Skill DNA has stabilized."
            )
        elif action_type == "REVIEW_PREREQUISITE":
            why_this_action = (
                f"A foundational prerequisite skill is currently weak. Addressing the prerequisite "
                f"ensures you can master {skill_name} without compounding skill debt."
            )
        else:
            why_this_action = (
                f"Deliver portfolio-level evidence to demonstrate end-to-end industry readiness."
            )

        return {
            "reason": reason,
            "why_now": why_now,
            "why_this_action": why_this_action,
        }

    def evaluate_candidate(
        self,
        user_id: int,
        role_id: int,
        role_name: str,
        career_value_item: Dict[str, Any],
        skill_dna: Dict[str, Any],
        all_skills_dna_map: Dict[str, Dict[str, Any]],
        evidences: List[Any],
    ) -> Dict[str, Any]:
        """
        Generates and scores a single Next-Best-Proof candidate action for a role skill.
        """
        skill_id = career_value_item["skill_id"]
        skill_name = career_value_item["skill_name"]
        skill_category = career_value_item.get("skill_category", "Core Competency")

        curr_level = float(career_value_item.get("current_skill_level", 0.0))
        req_level = float(career_value_item.get("required_skill_level", 80.0))
        cv_score = float(career_value_item.get("career_value_score", 0.0))
        debt_score = float(career_value_item.get("skill_debt_score", 0.0))
        debt_status = career_value_item.get("skill_debt_status", "UNKNOWN")
        cv_priority = career_value_item.get("priority", "MEDIUM")

        confidence = float(skill_dna.get("confidence", 0.0))
        accuracy = float(skill_dna.get("accuracy", 0.0))
        evidence_score = float(skill_dna.get("evidence_score", 0.0))
        evidence_count = int(skill_dna.get("evidence_count", 0))

        # Practical evidence inspection
        practical_evs = [
            e for e in evidences
            if getattr(e, "evidence_type", "") in ("PRACTICE", "PROJECT", "TASK", "LAB")
        ]
        practical_count = len(practical_evs)
        practical_gap = 0.0 if practical_count > 0 else 100.0

        conf_gap = max(0.0, min(100.0, 100.0 - confidence))
        ev_gap = max(0.0, min(100.0, 100.0 - evidence_score))

        recent_types = [getattr(e, "evidence_type", "") for e in evidences[:3]]

        # Prerequisites check
        prereq_info = self.check_prerequisites(skill_name, all_skills_dna_map, role_name=role_name)

        # Action readiness
        action_readiness = self.calculate_action_readiness(
            prereq_healthy=prereq_info["healthy"],
            evidence_count=evidence_count,
            current_level=curr_level,
        )

        readiness_label = "HIGH" if action_readiness >= 90 else "MEDIUM" if action_readiness >= 60 else "LOW"

        # Action selection
        action_plan = self.select_action_type(
            skill_name=skill_name,
            current_level=curr_level,
            required_level=req_level,
            accuracy=accuracy,
            confidence=confidence,
            evidence_count=evidence_count,
            practical_evidence_count=practical_count,
            debt_status=debt_status,
            prereq_info=prereq_info,
            recent_evidence_types=recent_types,
        )

        # Calculate Next-Best-Proof Score
        nbp_score = self.calculate_score(
            career_value_score=cv_score,
            skill_debt_score=debt_score,
            evidence_gap=ev_gap,
            confidence_gap=conf_gap,
            practical_evidence_gap=practical_gap,
            action_readiness=action_readiness,
        )

        priority = self.classify_priority(nbp_score, cv_priority, debt_status)

        explanations = self.generate_explanations(
            skill_name=skill_name,
            role_name=role_name,
            action_type=action_plan["action_type"],
            current_level=curr_level,
            required_level=req_level,
            gap_score=float(career_value_item.get("gap_score", 0.0)),
            debt_status=debt_status,
            practical_evidence_count=practical_count,
        )

        action_type_key = action_plan["action_type"]
        action_label = self.ACTION_LABELS.get(action_type_key, action_type_key)

        return {
            "user_id": user_id,
            "role_id": role_id,
            "role_name": role_name,
            "skill_id": skill_id,
            "skill_name": skill_name,
            "skill_category": skill_category,
            "action_type": action_type_key,
            "action_type_label": action_label,
            "title": action_plan["title"],
            "priority": priority,
            "next_best_proof_score": nbp_score,
            "current_skill_level": curr_level,
            "required_skill_level": req_level,
            "career_value_score": cv_score,
            "skill_debt_score": debt_score,
            "skill_debt_status": debt_status,
            "confidence": confidence,
            "evidence_score": evidence_score,
            "practical_evidence_score": 100.0 - practical_gap,
            "estimated_minutes": action_plan["estimated_minutes"],
            "expected_proof": action_plan["expected_proof"],
            "reason": explanations["reason"],
            "why_now": explanations["why_now"],
            "why_this_action": explanations["why_this_action"],
            "prerequisites": prereq_info["prereqs"],
            "action_readiness": readiness_label,
            "rank": None,
            "created_at": datetime.utcnow(),
        }


next_best_proof_engine = NextBestProofEngine()
