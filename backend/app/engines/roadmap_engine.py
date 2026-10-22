from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.engines.role_curriculum import role_curriculum_engine


class RoadmapEngine:
    """
    Dynamic Roadmap Engine (Phase 19).
    Core Principle: 'The learner does not follow the roadmap. The roadmap follows the learner.'
    Deterministic engine that continuously updates the career roadmap based on:
    - Target Role Curriculum & Benchmark Profile
    - Skill DNA
    - Skill Debt
    - Career Value
    - Next-Best-Proof
    - Role-Specific Prerequisite DAG dependencies
    - RoleSkill importance weights
    """

    SKILL_MODULE_MAP = {
        # Data Analyst & shared skills
        "SQL": "sql-fundamentals",
        "SQL JOINs": "sql-joins-mastery",
        "Python": "python-pandas-pipelines",
        "Statistics": "statistics-hypothesis-testing",
        "EDA": "eda-workflow-data-profiling",
        "Data Visualization": "power-bi-dax-modeling",
        "Power BI": "power-bi-dax-modeling",
        # Data Scientist skills
        "Machine Learning": "machine-learning-foundations",
        "Deep Learning": "machine-learning-foundations",
        "Feature Engineering": "feature-engineering-pipelines",
        "Model Evaluation": "model-evaluation-metrics",
        # Python Developer skills
        "Python Basics": "python-core-fundamentals",
        "Data Structures": "python-collections-functions",
        "OOP": "python-oop-architecture",
        "Exception Handling": "python-error-handling-robustness",
        "SQL Basics": "sql-fundamentals",
        "HTTP & REST APIs": "rest-api-design-architecture",
        "FastAPI": "fastapi-rest-endpoints",
        "Testing & PyTest": "pytest-automated-testing",
        "Git": "python-core-fundamentals",
        "Deployment & Docker": "docker-container-deployment",
    }

    SKILL_ALIASES = {
        "Python Basics": ["Python"],
        "Python": ["Python Basics"],
        "SQL Basics": ["SQL"],
        "SQL": ["SQL Basics"],
    }

    PREREQ_HEALTHY_THRESHOLD = 65.0
    COMPLETION_THRESHOLD = 75.0

    def generate_roadmap(
        self,
        user_id: int,
        target_role_name: str,
        role_skills: List[Dict[str, Any]],
        dna_map: Dict[int, Dict[str, Any]],
        debt_map: Dict[int, Dict[str, Any]],
        career_values: Dict[int, Dict[str, Any]],
        nbp: Optional[Dict[str, Any]],
        previous_steps: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[List[Dict[str, Any]], str, List[Dict[str, Any]]]:
        """
        Builds dynamic roadmap steps, regeneration reason, and change log.
        """
        total_evidence = sum(dna.get("evidence_count", 0) for dna in dna_map.values())
        has_demonstrated_skills = total_evidence > 0 or any(dna.get("skill_level", 0.0) > 0 for dna in dna_map.values())
        if not has_demonstrated_skills:
            first_skill_id = role_skills[0].get("skill_id", 1) if role_skills else 1
            steps = [
                {
                    "skill_id": first_skill_id,
                    "skill_name": "Diagnostic Assessment",
                    "title": "Complete Diagnostic Assessment",
                    "step_type": "ASSESSMENT",
                    "status": "RECOMMENDED",
                    "priority": "CRITICAL",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "reason": "Complete baseline diagnostic evaluation to establish your Skill DNA vector across core role competencies.",
                    "prerequisite_step_ids": None,
                    "evidence_required": "Answer foundational diagnostic assessment questions.",
                    "completed_at": None,
                },
                {
                    "skill_id": first_skill_id,
                    "skill_name": "Skill DNA Calibration",
                    "title": "Build Skill DNA",
                    "step_type": "LEARN",
                    "status": "BLOCKED",
                    "priority": "HIGH",
                    "order_index": 2,
                    "estimated_minutes": 5,
                    "reason": "Calibrate accuracy, difficulty, confidence, and recency dimensions from your assessment responses.",
                    "prerequisite_step_ids": "1",
                    "evidence_required": "Automatic calibration following diagnostic assessment completion.",
                    "completed_at": None,
                },
                {
                    "skill_id": first_skill_id,
                    "skill_name": "Personalized Roadmap",
                    "title": "Generate Personalized Roadmap",
                    "step_type": "LEARN",
                    "status": "BLOCKED",
                    "priority": "HIGH",
                    "order_index": 3,
                    "estimated_minutes": 5,
                    "reason": "Dynamically sequence learning, practice, and practical tasks based on verified gaps.",
                    "prerequisite_step_ids": "2",
                    "evidence_required": "Generated automatically once baseline Skill DNA is calibrated.",
                    "completed_at": None,
                },
            ]
            regeneration_reason = "Initial onboarding roadmap: complete diagnostic assessment to build your Skill DNA and generate your personalized career path."
            return steps, regeneration_reason, []

        # 1. Filter role skills by importance
        relevant_role_skills = [
            rs for rs in role_skills if rs.get("importance_score", 50) >= 60
        ]
        if not relevant_role_skills:
            relevant_role_skills = role_skills

        skill_req_map = {rs["skill_name"]: rs for rs in relevant_role_skills}

        # Retrieve role-specific prerequisite DAG from curriculum engine
        role_prereqs = role_curriculum_engine.get_prerequisite_graph_for_role(target_role_name)

        # Also register prerequisite skills
        for s_name, prereqs in role_prereqs.items():
            for p in prereqs:
                if p not in skill_req_map:
                    for rs in role_skills:
                        if rs.get("skill_name") == p:
                            skill_req_map[p] = rs

        # 2. Evaluate skill states
        skill_state: Dict[str, Dict[str, Any]] = {}
        for s_name, rs in skill_req_map.items():
            s_id = rs["skill_id"]
            dna = dna_map.get(s_id, {})
            debt = debt_map.get(s_id, {})
            cval = career_values.get(s_id, {})

            skill_level = dna.get("skill_level", 0.0)
            required_level = float(rs.get("required_level", 80))
            evidence_count = dna.get("evidence_count", 0)

            # Preserve learner evidence across role switches via skill aliases (e.g., Python <-> Python Basics)
            if evidence_count == 0 or skill_level < self.PREREQ_HEALTHY_THRESHOLD:
                aliases = self.SKILL_ALIASES.get(s_name, [])
                for alias in aliases:
                    for d_id, d_val in dna_map.items():
                        if d_val.get("skill_name") == alias and d_val.get("evidence_count", 0) > 0:
                            alias_level = d_val.get("skill_level", 0.0)
                            if alias_level > skill_level:
                                skill_level = alias_level
                                evidence_count = d_val.get("evidence_count", 0)

            gap = max(0.0, required_level - skill_level)

            debt_status = debt.get("debt_status", "")
            severity = debt.get("severity", "")
            debt_score = debt.get("debt_score", 0.0)

            # High Skill Debt: high/critical severity, high debt score, or deficit >= 20%
            has_debt = (
                (severity in ["CRITICAL", "HIGH"] or debt_score >= 35.0 or debt_status == "CRITICAL")
                and gap >= 20.0
            )

            is_completed = (
                evidence_count > 0
                and (skill_level >= min(required_level, self.COMPLETION_THRESHOLD) or dna.get("status") == "HEALTHY")
                and not has_debt
            )
            is_healthy_prereq = (
                evidence_count > 0
                and skill_level >= self.PREREQ_HEALTHY_THRESHOLD
                and not has_debt
            )

            skill_state[s_name] = {
                "skill_id": s_id,
                "skill_name": s_name,
                "skill_level": skill_level,
                "required_level": required_level,
                "importance_score": rs.get("importance_score", 50),
                "evidence_count": evidence_count,
                "has_debt": has_debt,
                "gap": gap,
                "debt_status": debt_status,
                "severity": severity,
                "roi_score": cval.get("career_value_score", 50.0),
                "is_completed": is_completed,
                "is_healthy_prereq": is_healthy_prereq,
                "dna_status": dna.get("status", "DEVELOPING"),
            }

        # Helper to check prerequisites based on role DAG
        def are_prereqs_satisfied(skill_name: str) -> Tuple[bool, Optional[str]]:
            prereqs = role_prereqs.get(skill_name, [])
            for p in prereqs:
                p_state = skill_state.get(p)
                if not p_state or not p_state["is_completed"]:
                    curr = p_state["skill_level"] if p_state else 0.0
                    req = p_state["required_level"] if p_state else 80.0
                    return False, f"Requires {p} to be completed (currently {curr:.0f}% / {req:.0f}%)."
            return True, None

        # 3. Role-specific baseline pathway order
        baseline_order = role_curriculum_engine.get_baseline_pathway_for_role(target_role_name)
        pathway_skills = [s for s in baseline_order if s in skill_state]
        for s in skill_state:
            if s not in pathway_skills:
                pathway_skills.append(s)

        # 4. Generate step progression
        steps: List[Dict[str, Any]] = []
        step_order = 1
        active_recommended_assigned = False
        remediation_inserted_skills: List[str] = []
        active_blocker_skill: Optional[str] = None

        for s_name in pathway_skills:
            st = skill_state[s_name]
            s_id = st["skill_id"]
            prereqs_ok, prereq_reason = are_prereqs_satisfied(s_name)
            mod_slug = self.SKILL_MODULE_MAP.get(s_name)

            # A. COMPLETED SKILL
            if st["is_completed"]:
                steps.append({
                    "skill_id": s_id,
                    "skill_name": s_name,
                    "title": f"{s_name} Verification",
                    "step_type": "FOUNDATION" if s_name in ["Python", "SQL"] else "LEARN",
                    "status": "COMPLETED",
                    "priority": "Low",
                    "order_index": step_order,
                    "estimated_minutes": 30,
                    "reason": f"Demonstrated {st['skill_level']:.1f}% proficiency exceeding role requirement ({st['required_level']:.0f}%).",
                    "prerequisite_step_ids": None,
                    "evidence_required": f"Verified with {st['evidence_count']} proof artifact(s).",
                    "module_slug": mod_slug,
                    "completed_at": datetime.utcnow().isoformat(),
                })
                step_order += 1
                continue

            # B. CRITICAL SKILL DEBT -> ADAPTIVE REMEDIATION INSERTION
            if st["has_debt"] and prereqs_ok:
                remediation_inserted_skills.append(s_name)
                active_blocker_skill = s_name

                clean_name = "SQL JOIN" if s_name == "SQL JOINs" else s_name

                # Step 1: Rescue Practice (Matches Next-Best-Proof)
                practice_order = step_order
                practice_status = "RECOMMENDED" if not active_recommended_assigned else "REMEDIATION"
                active_recommended_assigned = True

                steps.append({
                    "skill_id": s_id,
                    "skill_name": s_name,
                    "title": f"{clean_name} Rescue Practice",
                    "step_type": "PRACTICE",
                    "status": practice_status,
                    "priority": "CRITICAL",
                    "order_index": step_order,
                    "estimated_minutes": 25,
                    "reason": f"Inserted because {s_name} is currently below the {target_role_name} requirement ({st['skill_level']:.1f}% vs {st['required_level']:.0f}%) and has high Skill Debt.",
                    "prerequisite_step_ids": None,
                    "evidence_required": f"Targeted {s_name} problem resolution in learning sandbox.",
                    "module_slug": mod_slug,
                    "completed_at": None,
                })
                step_order += 1

                # Step 2: Diagnostic Reassessment
                reassess_order = step_order
                steps.append({
                    "skill_id": s_id,
                    "skill_name": s_name,
                    "title": f"{clean_name} Reassessment",
                    "step_type": "REASSESS",
                    "status": "BLOCKED",
                    "priority": "HIGH",
                    "order_index": step_order,
                    "estimated_minutes": 20,
                    "reason": f"Validate proficiency recovery on {s_name} before downstream advancement.",
                    "prerequisite_step_ids": str(practice_order),
                    "evidence_required": f"Score >= 75% on {s_name} Concept Check.",
                    "module_slug": mod_slug,
                    "completed_at": None,
                })
                step_order += 1

                # Step 3: Real-World Practical Task
                steps.append({
                    "skill_id": s_id,
                    "skill_name": s_name,
                    "title": f"Real-World {clean_name} Task",
                    "step_type": "PRACTICAL_TASK",
                    "status": "BLOCKED",
                    "priority": "HIGH",
                    "order_index": step_order,
                    "estimated_minutes": 45,
                    "reason": f"Demonstrate job-ready practical {s_name} competency on production datasets.",
                    "prerequisite_step_ids": str(reassess_order),
                    "evidence_required": f"Complete multi-table transaction query analysis on database.",
                    "module_slug": mod_slug,
                    "completed_at": None,
                })
                step_order += 1
                continue

            # Title mapping
            if s_name == "Machine Learning":
                skill_title = "Machine Learning & Predictive Modeling Lab"
            elif s_name == "Statistics":
                skill_title = "Statistics & Hypothesis Testing Lab"
            elif s_name == "Deep Learning":
                skill_title = "Deep Learning & Neural Networks Lab"
            else:
                skill_title = f"{s_name} Core Application Lab"

            # C. BLOCKED SKILL (Prerequisites insufficient OR upstream remediation active)
            if not prereqs_ok or active_blocker_skill:
                block_reason = prereq_reason or f"Blocked: Upstream {active_blocker_skill} remediation must be resolved before proceeding."
                steps.append({
                    "skill_id": s_id,
                    "skill_name": s_name,
                    "title": skill_title,
                    "step_type": "LEARN",
                    "status": "BLOCKED",
                    "priority": "Medium",
                    "order_index": step_order,
                    "estimated_minutes": 50,
                    "reason": block_reason,
                    "prerequisite_step_ids": None,
                    "evidence_required": f"Prerequisites and upstream remediations must be completed before unlocking.",
                    "module_slug": mod_slug,
                    "completed_at": None,
                })
                step_order += 1
                continue

            # D. ACTIONABLE REGULAR SKILL (Prerequisites satisfied, no upstream remediation)
            status = "RECOMMENDED" if not active_recommended_assigned else "IN_PROGRESS"
            if status == "RECOMMENDED":
                active_recommended_assigned = True

            steps.append({
                "skill_id": s_id,
                "skill_name": s_name,
                "title": skill_title,
                "step_type": "PRACTICE" if st["evidence_count"] > 0 else "LEARN",
                "status": status,
                "priority": "High" if st["importance_score"] >= 80 else "Medium",
                "order_index": step_order,
                "estimated_minutes": 50,
                "reason": f"Develop core {s_name} proficiency toward {target_role_name} benchmark ({st['skill_level']:.1f}% / {st['required_level']:.0f}%).",
                "prerequisite_step_ids": None,
                "evidence_required": f"Complete {s_name} module tasks with verified benchmark proof.",
                "module_slug": mod_slug,
                "completed_at": None,
            })
            step_order += 1

        # 5. Capstone Project tailored to Role Profile
        role_profile = role_curriculum_engine.get_role_profile(target_role_name)
        capstone_title = role_profile.get("capstone_title", f"End-to-End {target_role_name} Capstone Portfolio Project")
        capstone_desc = role_profile.get("capstone_description", f"Synthesize verified evidence across all core {target_role_name} competencies.")
        
        capstone_blocked = any(
            not st["is_completed"]
            for s_name, st in skill_state.items()
            if st["importance_score"] >= 75
        )

        capstone_skill = skill_state.get("Python", list(skill_state.values())[0]) if skill_state else {"skill_id": 1, "skill_name": "Capstone"}

        steps.append({
            "skill_id": capstone_skill["skill_id"],
            "skill_name": capstone_skill["skill_name"],
            "title": capstone_title,
            "step_type": "CAPSTONE",
            "status": "BLOCKED" if capstone_blocked else ("RECOMMENDED" if not active_recommended_assigned else "IN_PROGRESS"),
            "priority": "High",
            "order_index": step_order,
            "estimated_minutes": 240,
            "reason": capstone_desc,
            "prerequisite_step_ids": None,
            "evidence_required": f"Complete end-to-end dataset analysis project with code, visualizations, and executive presentation.",
            "module_slug": None,
            "completed_at": None,
        })

        # 6. Generate Regeneration Reason & Change Log
        reason, changes = self._detect_changes(
            previous_steps=previous_steps,
            new_steps=steps,
            remediation_skills=remediation_inserted_skills,
            target_role_name=target_role_name,
        )

        return steps, reason, changes

    def _detect_changes(
        self,
        previous_steps: Optional[List[Dict[str, Any]]],
        new_steps: List[Dict[str, Any]],
        remediation_skills: List[str],
        target_role_name: str,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        changes: List[Dict[str, Any]] = []

        if not previous_steps:
            if remediation_skills:
                skill_str = ", ".join(remediation_skills)
                reason = f"{skill_str} identified as high-priority Skill Debt; targeted remediation inserted."
                for s_name in remediation_skills:
                    changes.append({
                        "change_type": "INSERTION",
                        "skill_name": s_name,
                        "title": f"{s_name} Rescue Sequence",
                        "description": f"{s_name} was inserted before downstream skills because your latest evidence showed a significant role-relevant skill gap.",
                    })
            else:
                reason = f"Initial baseline roadmap generated for {target_role_name} target role."
            return reason, changes

        # Map previous steps by title/skill
        prev_map = {p.get("title"): p for p in previous_steps}
        prev_remediations = [
            p for p in previous_steps
            if p.get("step_type") in ["PRACTICE", "REASSESS", "PRACTICAL_TASK"]
            and ("Rescue" in p.get("title", "") or "Task" in p.get("title", "") or "Reassessment" in p.get("title", ""))
        ]

        # 1. Check for newly inserted remediation steps
        for step in new_steps:
            if "Rescue" in step["title"] and step["title"] not in prev_map:
                changes.append({
                    "change_type": "INSERTION",
                    "skill_name": step["skill_name"],
                    "title": step["title"],
                    "description": f"{step['skill_name']} was inserted before downstream skills because your latest evidence showed a significant role-relevant skill gap.",
                })

        # 2. Check for removed remediation steps (when skill improved)
        new_titles = {n["title"] for n in new_steps}
        removed_skills_set = set()
        for pr in prev_remediations:
            if pr["title"] not in new_titles and pr["skill_name"] not in removed_skills_set:
                removed_skills_set.add(pr["skill_name"])
                changes.append({
                    "change_type": "REMOVED",
                    "skill_name": pr["skill_name"],
                    "title": pr["title"],
                    "description": f"{pr['skill_name']} remediation was removed because recent practical evidence demonstrates sufficient proficiency.",
                })

        # 3. Check for newly completed steps
        for step in new_steps:
            prev = prev_map.get(step["title"])
            if step["status"] == "COMPLETED" and (not prev or prev.get("status") != "COMPLETED"):
                changes.append({
                    "change_type": "COMPLETED",
                    "skill_name": step["skill_name"],
                    "title": step["title"],
                    "description": f"{step['skill_name']} verification completed with demonstrated proficiency evidence.",
                })

        # 4. Check for newly unlocked steps (was BLOCKED, now RECOMMENDED or IN_PROGRESS)
        for step in new_steps:
            prev = prev_map.get(step["title"])
            if prev and prev.get("status") == "BLOCKED" and step["status"] in ["RECOMMENDED", "IN_PROGRESS"]:
                changes.append({
                    "change_type": "UNLOCKED",
                    "skill_name": step["skill_name"],
                    "title": step["title"],
                    "description": f"{step['skill_name']} is now unlocked because its prerequisites reached the required proficiency.",
                })

        # 5. Formulate summary regeneration reason
        if any(c["change_type"] == "REMOVED" for c in changes):
            removed_skills = {c["skill_name"] for c in changes if c["change_type"] == "REMOVED"}
            reason = f"Roadmap updated: {', '.join(removed_skills)} remediation removed after demonstrated proficiency improvement."
        elif any(c["change_type"] == "INSERTION" for c in changes):
            inserted_skills = {c["skill_name"] for c in changes if c["change_type"] == "INSERTION"}
            reason = f"{', '.join(inserted_skills)} identified as high-priority Skill Debt; targeted remediation inserted."
        elif any(c["change_type"] == "UNLOCKED" for c in changes):
            unlocked_skills = {c["skill_name"] for c in changes if c["change_type"] == "UNLOCKED"}
            reason = f"Roadmap updated: {', '.join(unlocked_skills)} unlocked following prerequisite demonstration."
        else:
            reason = f"Roadmap re-evaluated matching latest learner evidence for {target_role_name}."

        return reason, changes


roadmap_engine = RoadmapEngine()
