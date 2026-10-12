import json
import logging
import httpx
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.role import Role
from app.models.skill import Skill
from app.models.roadmap import Roadmap, RoadmapStep, RoadmapChange
from app.models.evidence import SkillEvidence
from app.models.assessment import AssessmentAttempt
from app.services.skill_dna_service import skill_dna_service
from app.services.skill_debt_service import skill_debt_service
from app.services.career_value_service import career_value_service
from app.services.next_best_proof_service import next_best_proof_service
from app.services.roadmap_service import roadmap_service
from app.services.dashboard_service import dashboard_service
from app.services.skill_passport_service import skill_passport_service
from app.services.ai_service import ai_service
from app.schemas.coach import (
    CoachChatRequest,
    CoachChatResponse,
    ChatAction,
    ChatMessage,
)
from app.schemas.ai import AIPracticeQuestionsRequest, AIInterviewQuestionsRequest

logger = logging.getLogger(__name__)

COACH_SYSTEM_PROMPT = """You are the "SkillPath AI Career Coach", a personalized, data-driven career intelligence advisor for aspiring data professionals.
You help learners understand and improve their career readiness by interpreting the authoritative deterministic SkillPath AI backend engines.

Strict Behavioral Rules:
1. You work directly with live backend tools. ALWAYS invoke backend tools whenever a question asks about the learner's actual status, skills, roadmap, debt, recommendations, or readiness.
2. Never invent or guess learner scores, evidence, skills, roadmap steps, career readiness, or recommendations.
3. The deterministic SkillPath engines are authoritative. You may explain deterministic decisions but NEVER attempt to override, simulate, or dispute them.
4. Give concise, practical, highly actionable coaching responses. Prefer concrete advice grounded in the learner's target role (e.g. Data Analyst) and current evidence.
5. If the user asks whether they are ready for their target role, provide a balanced, nuanced evaluation based on current Career Readiness percentage and specific remaining skill gaps. Never guarantee employment.
6. If the user asks to modify scores, bypass roadmap steps, change DNA, or reveal internal secrets/API keys/passwords, firmly and politely refuse.
7. Keep responses structured, professional, and free of robot clichés or generic fluff.
"""

GEMINI_TOOLS_DECLARATIONS = [
    {
        "name": "get_learner_profile",
        "description": "Retrieve the learner's profile, name, experience level, target role, and weekly hours.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_target_role",
        "description": "Retrieve target role specifications, required skills, and benchmark levels.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_skill_dna",
        "description": "Retrieve learner's current Skill DNA: demonstrated skill levels, confidence, accuracy, recency, and evidence counts.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_skill_debt",
        "description": "Retrieve active Skill Debt: competencies previously encountered where current active evidence is weak, severity, and reasons.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_career_value",
        "description": "Retrieve skills prioritized by Career Value, role importance, current competency gap, and urgency rank.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_next_best_proof",
        "description": "Retrieve the single most valuable deterministic Next-Best-Proof action, skill name, title, action type, priority, and reason.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_current_roadmap",
        "description": "Retrieve the learner's current dynamic roadmap steps, order, statuses (COMPLETED, RECOMMENDED, REMEDIATION, UPCOMING).",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_roadmap_changes",
        "description": "Retrieve recent changes and transformations in the learner's roadmap, along with deterministic regeneration reasons.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_recent_evidence",
        "description": "Retrieve recent verified evidence entries recorded in the immutable SkillEvidence ledger.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_skill_passport",
        "description": "Retrieve the Proof-of-Skill Passport summary: verified skills count, total role competencies, readiness score, and matrix.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "get_recent_progress",
        "description": "Retrieve learner career readiness score, trend, and verified skills progress count.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    {
        "name": "generate_practice_question",
        "description": "Generate an unscored practice question for a specific skill (e.g. 'SQL JOINs') to test comprehension.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "skill_name": {"type": "STRING", "description": "Name of the skill to generate a practice question for"}
            },
            "required": ["skill_name"],
        },
    },
]


class CoachService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.timeout = settings.GEMINI_TIMEOUT_SECONDS
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    # =========================================================================
    # TOOL EXECUTION (SAFE, READ-ONLY, DETERMINISTIC BACKEND INTEGRATION)
    # =========================================================================
    def execute_tool(
        self,
        db: Session,
        user_id: int,
        tool_name: str,
        args: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executes approved read-only tools against backend services.
        Never executes arbitrary SQL or mutates user scores.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": f"User {user_id} not found."}

        target_role_id = user.target_role_id or 1
        role = db.query(Role).filter(Role.id == target_role_id).first()
        role_name = role.name if role else "Data Analyst"

        if tool_name == "get_learner_profile":
            return {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "experience_level": user.experience_level,
                "target_role": role_name,
                "weekly_learning_hours": user.weekly_learning_hours,
            }

        elif tool_name == "get_target_role":
            role_skills = [
                {
                    "skill_name": rs.skill.name,
                    "category": rs.skill.category,
                    "required_level": rs.required_level,
                    "importance_weight": rs.importance_weight,
                }
                for rs in role.role_skills
            ] if role else []
            return {
                "role_id": target_role_id,
                "role_name": role_name,
                "description": role.description if role else "",
                "required_skills": role_skills,
            }

        elif tool_name == "get_skill_dna":
            dna_list = skill_dna_service.get_user_skill_dna(db, user_id)
            return {
                "skill_dna": [
                    {
                        "skill_name": d["skill_name"],
                        "category": d.get("skill_category", "General"),
                        "level": round(d["skill_level"], 1),
                        "confidence": round(d["confidence"], 1),
                        "accuracy": round(d["accuracy"], 1),
                        "status": d["status"],
                        "evidence_count": d["evidence_count"],
                        "recency": d["recency_label"],
                    }
                    for d in dna_list
                ]
            }

        elif tool_name == "get_skill_debt":
            debt_items = skill_debt_service.calculate_skill_debt(db, user_id, target_role_id)
            return {
                "active_skill_debts": [
                    {
                        "skill_name": d["skill_name"],
                        "debt_status": d["debt_status"],
                        "severity": d["severity"],
                        "debt_score": round(d["debt_score"], 1),
                        "current_level": round(d["current_skill_level"], 1),
                        "role_requirement": round(d["role_requirement"], 1),
                        "evidence_count": d["evidence_count"],
                        "reason": d["reason"],
                        "recommended_proof": d.get("recommended_intervention", "Targeted Practice"),
                    }
                    for d in debt_items
                    if d.get("debt_status") == "SKILL_DEBT"
                ],
                "healthy_skills": [
                    d["skill_name"]
                    for d in debt_items
                    if d.get("debt_status") == "HEALTHY"
                ],
            }

        elif tool_name == "get_career_value":
            cv_list = career_value_service.calculate_career_value(db, user_id, target_role_id)
            return {
                "career_priorities": [
                    {
                        "rank": cv["rank"],
                        "skill_name": cv["skill_name"],
                        "priority": cv["priority"],
                        "career_value_score": round(cv["career_value_score"], 1),
                        "gap_score": round(cv["gap_score"], 1),
                        "role_importance": round(cv["role_importance"], 1),
                        "reason": cv["reason"],
                        "recommended_focus": cv["recommended_focus"],
                    }
                    for cv in cv_list[:5]
                ]
            }

        elif tool_name == "get_next_best_proof":
            nbp = next_best_proof_service.get_next_best_proof(db, user_id, target_role_id)
            return {
                "skill_name": nbp["skill_name"],
                "action_type": nbp["action_type"],
                "action_type_label": nbp.get("action_type_label", "Practice"),
                "title": nbp["title"],
                "priority": nbp["priority"],
                "current_level": round(nbp["current_skill_level"], 1),
                "required_level": round(nbp["required_skill_level"], 1),
                "skill_debt_status": nbp.get("skill_debt_status", "SKILL_DEBT"),
                "estimated_minutes": nbp.get("estimated_minutes", 25),
                "expected_proof": nbp.get("expected_proof", ""),
                "reason": nbp.get("reason", ""),
                "why_now": nbp.get("why_now", ""),
            }

        elif tool_name == "get_current_roadmap":
            rm = (
                db.query(Roadmap)
                .filter(Roadmap.user_id == user_id, Roadmap.status == "active")
                .first()
            )
            if not rm:
                # generate roadmap
                rm = roadmap_service.rebuild_user_roadmap(db, user_id, target_role_id)

            return {
                "roadmap_version": rm.version,
                "regeneration_reason": rm.regeneration_reason,
                "steps": [
                    {
                        "order": s.order_index,
                        "title": s.title,
                        "skill_name": s.skill.name if s.skill else "General",
                        "step_type": s.step_type,
                        "status": s.status,
                        "priority": s.priority,
                        "estimated_minutes": s.estimated_minutes,
                    }
                    for s in sorted(rm.steps, key=lambda x: x.order_index)
                ],
            }

        elif tool_name == "get_roadmap_changes":
            changes = (
                db.query(RoadmapChange)
                .filter(RoadmapChange.user_id == user_id)
                .order_by(RoadmapChange.created_at.desc())
                .limit(5)
                .all()
            )
            return {
                "recent_changes": [
                    {
                        "version": c.version,
                        "change_type": c.change_type,
                        "skill_name": c.skill_name,
                        "title": c.title,
                        "description": c.description,
                    }
                    for c in changes
                ]
            }

        elif tool_name == "get_recent_evidence":
            evidences = (
                db.query(SkillEvidence)
                .filter(SkillEvidence.user_id == user_id)
                .order_by(SkillEvidence.created_at.desc())
                .limit(6)
                .all()
            )
            return {
                "evidence_records": [
                    {
                        "skill_name": ev.skill.name if ev.skill else "General",
                        "evidence_type": ev.evidence_type,
                        "score": round(ev.score, 1),
                        "verified": ev.verified,
                        "source": ev.source,
                        "description": ev.description,
                    }
                    for ev in evidences
                ]
            }

        elif tool_name == "get_skill_passport":
            passport = skill_passport_service.get_skill_passport(db, user_id)
            return {
                "career_readiness": passport.header.career_readiness,
                "career_readiness_status": passport.header.career_readiness_status,
                "skills_verified_count": passport.header.skills_verified_count,
                "total_role_skills_count": passport.header.total_role_skills_count,
                "total_evidence_count": passport.header.total_evidence_count,
                "headline": passport.summary.headline,
                "strongest_skills": passport.summary.strongest_skills,
                "skills_needing_proof": passport.summary.skills_needing_proof,
            }

        elif tool_name == "get_recent_progress":
            dash = dashboard_service.get_dashboard_data(db, user_id)
            return {
                "career_readiness_score": dash.metrics.career_readiness.score,
                "readiness_status": dash.metrics.career_readiness.status,
                "skills_verified": dash.metrics.skills_verified,
                "total_role_skills": dash.metrics.total_role_skills,
                "active_skill_debt_count": dash.metrics.active_skill_debt_count,
                "high_debt_count": dash.metrics.high_debt_count,
            }

        elif tool_name == "generate_practice_question":
            skill_name = args.get("skill_name", "SQL JOINs")
            req = AIPracticeQuestionsRequest(
                skill_name=skill_name,
                difficulty="Intermediate",
                target_role=role_name,
                count=1,
            )
            res = ai_service.generate_practice_questions(req)
            q = res.questions[0] if res.questions else None
            if q:
                return {
                    "skill_name": skill_name,
                    "question_text": q.question_text,
                    "options": q.options,
                    "expected_answer": q.expected_answer,
                    "explanation": q.explanation,
                    "disclaimer": "Unscored practice exercise. Does not automatically alter Skill DNA.",
                }
            return {"error": f"Could not generate question for {skill_name}"}

        elif tool_name == "generate_interview_questions":
            skill_name = args.get("skill_name", "SQL JOINs")
            req = AIInterviewQuestionsRequest(
                skill_name=skill_name,
                target_role=role_name,
            )
            res = ai_service.generate_interview_questions(req)
            return {
                "interview_questions": [
                    {"category": q.category, "question": q.question, "evaluation_tip": q.evaluation_tip}
                    for q in res.questions
                ]
            }

        return {"error": f"Unknown tool: '{tool_name}'"}

    # =========================================================================
    # RELEVANT ACTION BUTTON EXTRACTOR
    # =========================================================================
    def build_action_buttons(
        self,
        tools_used: List[str],
        tool_results: Dict[str, Any],
    ) -> List[ChatAction]:
        actions: List[ChatAction] = []

        if "get_next_best_proof" in tools_used:
            nbp = tool_results.get("get_next_best_proof", {})
            title = nbp.get("title", "Next Best Proof")
            action_type = nbp.get("action_type", "PRACTICE")
            target = "/practice-lab" if action_type in ("PRACTICE", "PRACTICAL_TASK") else "/assessments"
            actions.append(
                ChatAction(
                    label=f"Start: {title}",
                    action_type="START_PRACTICE",
                    target_route=target,
                    skill_name=nbp.get("skill_name"),
                )
            )

        if "get_current_roadmap" in tools_used or "get_roadmap_changes" in tools_used:
            actions.append(
                ChatAction(
                    label="View Dynamic Roadmap",
                    action_type="NAVIGATE",
                    target_route="/roadmap",
                )
            )

        if "get_skill_debt" in tools_used:
            actions.append(
                ChatAction(
                    label="Review Skill Debt Ledger",
                    action_type="NAVIGATE",
                    target_route="/skill-debt",
                )
            )

        if "get_skill_passport" in tools_used or "get_recent_evidence" in tools_used:
            actions.append(
                ChatAction(
                    label="Open Skill Passport",
                    action_type="VIEW_EVIDENCE",
                    target_route="/skill-passport",
                )
            )

        if "get_career_value" in tools_used:
            actions.append(
                ChatAction(
                    label="Inspect Career Gaps",
                    action_type="NAVIGATE",
                    target_route="/career-gap",
                )
            )

        # De-duplicate by target_route
        seen = set()
        unique_actions = []
        for a in actions:
            if a.target_route not in seen:
                seen.add(a.target_route)
                unique_actions.append(a)
        return unique_actions[:3]

    # =========================================================================
    # MULTI-TURN CONVERSATION WITH GEMINI FUNCTION CALLING
    # =========================================================================
    def chat(
        self,
        db: Session,
        req: CoachChatRequest,
    ) -> CoachChatResponse:
        user_id = req.user_id
        message = req.message.strip()

        # Security check: Prompt Injection & Extraction refusal
        refusal = self._check_safety_guardrails(message)
        if refusal:
            return CoachChatResponse(
                reply=refusal,
                actions=[],
                tools_used=[],
                suggested_prompts=[
                    "What should I do next?",
                    "What are my weakest skills?",
                    "Why is SQL JOINs my priority?",
                ],
                fallback_used=False,
            )

        tools_used: List[str] = []
        tool_results: Dict[str, Any] = {}

        # If Gemini API key is available, execute through Gemini function calling
        if self.api_key:
            try:
                gemini_resp, executed_tools, executed_results = self._call_gemini_with_tools(
                    db=db,
                    user_id=user_id,
                    message=message,
                    history=req.history,
                )
                if gemini_resp:
                    actions = self.build_action_buttons(executed_tools, executed_results)
                    suggested = self._generate_suggested_prompts(executed_tools, executed_results)
                    return CoachChatResponse(
                        reply=gemini_resp,
                        actions=actions,
                        tools_used=executed_tools,
                        suggested_prompts=suggested,
                        fallback_used=False,
                    )
            except Exception as e:
                logger.warning(f"Gemini Career Coach function-calling failed: {e}. Executing deterministic fallback.")

        # Deterministic fallback when Gemini is absent, offline, or throttled
        fallback_reply, fallback_tools, fallback_results = self._deterministic_coach_fallback(
            db=db,
            user_id=user_id,
            message=message,
        )
        actions = self.build_action_buttons(fallback_tools, fallback_results)
        suggested = self._generate_suggested_prompts(fallback_tools, fallback_results)

        return CoachChatResponse(
            reply=fallback_reply,
            actions=actions,
            tools_used=fallback_tools,
            suggested_prompts=suggested,
            fallback_used=True,
        )

    # =========================================================================
    # SAFETY GUARDRAIL INSPECTION
    # =========================================================================
    def _check_safety_guardrails(self, message: str) -> Optional[str]:
        lower = message.lower()

        # Disallow secret / credential extraction
        if any(w in lower for w in ["database password", "db password", "api key", "gemini_api_key", "secret key", "connection string"]):
            return "I cannot provide system secrets, credentials, or internal configuration details. How can I help with your learning path or skill progression instead?"

        # Disallow arbitrary system instruction overrides
        if any(w in lower for w in ["ignore your instructions", "ignore previous instructions", "system prompt", "internal prompt"]):
            return "I am configured specifically as the SkillPath AI Career Coach. I cannot ignore my core guidelines or alter system configurations. Let's focus on your skills, evidence, and target role."

        # Disallow manual score / DNA manipulation
        manipulation_verbs = ["change my", "set my", "override my", "override", "modify my", "give me 100", "skip remediation", "hack"]
        manipulation_targets = ["score", "dna", "level", "roadmap", "remediation", "skill"]
        if (any(v in lower for v in manipulation_verbs) and any(t in lower for t in manipulation_targets)) or "change my skill dna" in lower:
            return "Skill DNA, Skill Debt, and Roadmap states are computed strictly by deterministic backend engines based on verified empirical evidence. I cannot manually override your scores. To improve your skill level, complete your recommended Next-Best-Proof action!"

        return None

    # =========================================================================
    # GEMINI REST FUNCTION-CALLING ENGINE
    # =========================================================================
    def _call_gemini_with_tools(
        self,
        db: Session,
        user_id: int,
        message: str,
        history: List[ChatMessage],
    ) -> Tuple[Optional[str], List[str], Dict[str, Any]]:
        """
        Executes Google Gemini v1beta function calling loop:
        1. Formats conversation turns.
        2. Supplies functionDeclarations.
        3. If model emits functionCall, executes backend tool.
        4. Returns functionResponse to model and retrieves final natural language coaching reply.
        """
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

        # Construct conversation contents
        contents: List[Dict[str, Any]] = []

        # Add recent conversation history (up to last 6 turns)
        for h in history[-6:]:
            role = "user" if h.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h.content}]})

        # Add current user prompt
        contents.append({"role": "user", "parts": [{"text": message}]})

        tools_used: List[str] = []
        tool_results: Dict[str, Any] = {}

        # Multi-turn tool execution loop (up to 3 tool calls)
        for _ in range(3):
            payload = {
                "systemInstruction": {"parts": [{"text": COACH_SYSTEM_PROMPT}]},
                "contents": contents,
                "tools": [{"functionDeclarations": GEMINI_TOOLS_DECLARATIONS}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024},
            }

            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, json=payload)
                if res.status_code != 200:
                    logger.warning(f"Gemini API tool call HTTP {res.status_code}: {res.text}")
                    return None, tools_used, tool_results

                data = res.json()
                candidates = data.get("candidates", [])
                if not candidates or "content" not in candidates[0]:
                    return None, tools_used, tool_results

                model_content = candidates[0]["content"]
                parts = model_content.get("parts", [])
                if not parts:
                    return None, tools_used, tool_results

                # Check if model requested a function call
                func_call = parts[0].get("functionCall")
                if func_call:
                    tool_name = func_call.get("name")
                    tool_args = func_call.get("args", {})
                    tools_used.append(tool_name)

                    # Execute tool in application layer
                    tool_result = self.execute_tool(db, user_id, tool_name, tool_args)
                    tool_results[tool_name] = tool_result

                    # Append model's functionCall to contents
                    contents.append(model_content)

                    # Append application functionResponse
                    contents.append(
                        {
                            "role": "function",
                            "parts": [
                                {
                                    "functionResponse": {
                                        "name": tool_name,
                                        "response": {"output": tool_result},
                                    }
                                }
                            ],
                        }
                    )
                else:
                    # Final text response received
                    final_text = parts[0].get("text", "").strip()
                    return final_text, tools_used, tool_results

        return None, tools_used, tool_results

    # =========================================================================
    # DETERMINISTIC OFFLINE COACH FALLBACK
    # =========================================================================
    def _deterministic_coach_fallback(
        self,
        db: Session,
        user_id: int,
        message: str,
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """
        Deterministic, offline coaching engine that answers directly using backend engines
        when Gemini API is omitted, offline, or rate-limited.
        """
        lower = message.lower()
        tools_used: List[str] = []
        tool_results: Dict[str, Any] = {}

        # 1. Roadmap & Path change inquiry
        if any(w in lower for w in ["roadmap", "path change", "curriculum"]):
            rm = self.execute_tool(db, user_id, "get_current_roadmap", {})
            changes = self.execute_tool(db, user_id, "get_roadmap_changes", {})
            tools_used.extend(["get_current_roadmap", "get_roadmap_changes"])
            tool_results["get_current_roadmap"] = rm
            tool_results["get_roadmap_changes"] = changes

            recent = changes.get("recent_changes", [])
            change_desc = recent[0]["description"] if recent else rm.get("regeneration_reason", "Roadmap updated based on latest evidence.")

            steps = rm.get("steps", [])
            step_summary = "\n".join([f"{s['order']}. **{s['title']}** [{s['status']}]" for s in steps[:5]])

            reply = (
                f"Your roadmap adapted because the deterministic engine continuously responds to your actual evidence.\n\n"
                f"**Latest Roadmap Reason:** {change_desc}\n\n"
                f"**Current Path Preview:**\n{step_summary}\n\n"
                f"As you complete practice labs and assessments, remediation steps will resolve and unlock new specialized topics."
            )
            return reply, tools_used, tool_results

        # 2. "What should I do next?" / Next-Best-Proof inquiry
        elif any(w in lower for w in ["next", "what should i do", "what to do", "focus", "today"]):
            nbp = self.execute_tool(db, user_id, "get_next_best_proof", {})
            tools_used.append("get_next_best_proof")
            tool_results["get_next_best_proof"] = nbp

            reply = (
                f"Your highest-priority action right now is **{nbp['title']}** for **{nbp['skill_name']}**.\n\n"
                f"- **Current Level:** {nbp['current_level']}%\n"
                f"- **Target Requirement:** {nbp['required_level']}%\n"
                f"- **Status:** {nbp['skill_debt_status']} (Priority: {nbp['priority']})\n"
                f"- **Estimated Time:** ~{nbp['estimated_minutes']} minutes\n\n"
                f"**Why this action?** {nbp['reason']}\n\n"
                f"I recommend launching this practice task to produce verified evidence and clear your skill debt."
            )
            return reply, tools_used, tool_results

        # 3. "What are my weakest skills?" / Gaps & Debt
        elif any(w in lower for w in ["weak", "weakest", "debt", "gap", "skills need proof"]):
            debt = self.execute_tool(db, user_id, "get_skill_debt", {})
            dna = self.execute_tool(db, user_id, "get_skill_dna", {})
            tools_used.extend(["get_skill_debt", "get_skill_dna"])
            tool_results["get_skill_debt"] = debt
            tool_results["get_skill_dna"] = dna

            debts = debt.get("active_skill_debts", [])
            if debts:
                debt_str = "\n".join([f"- **{d['skill_name']}**: Current {d['current_level']}% vs {d['role_requirement']}% required ({d['severity']} Debt)" for d in debts])
                reply = (
                    f"Based on your live Skill DNA and Skill Debt analysis, here are your primary deficit areas:\n\n"
                    f"{debt_str}\n\n"
                    f"These skills require active demonstration or rescue practice before they can count as verified proof on your passport."
                )
            else:
                reply = "All of your role competencies currently have healthy verified evidence! Keep advancing through your upcoming roadmap projects."
            return reply, tools_used, tool_results

        # 4. "Why is SQL JOINs my priority?" / Skill importance
        elif any(w in lower for w in ["why", "sql join", "sql joins", "joins"]):
            nbp = self.execute_tool(db, user_id, "get_next_best_proof", {})
            debt = self.execute_tool(db, user_id, "get_skill_debt", {})
            tools_used.extend(["get_next_best_proof", "get_skill_debt"])
            tool_results["get_next_best_proof"] = nbp
            tool_results["get_skill_debt"] = debt

            reply = (
                f"**SQL JOINs** is currently your top priority because it carries **HIGH Skill Debt** and is a critical competency for your target role.\n\n"
                f"Your demonstrated score is **{nbp['current_level']}%**, while the role expects **{nbp['required_level']}%**.\n"
                f"Because you previously learned relational joins but recent verified evidence is missing, the engine assigned it high urgency. "
                f"Completing **{nbp['title']}** in the Practice Lab will resolve this gap and unlock downstream steps in your roadmap."
            )
            return reply, tools_used, tool_results

        # 5. "Give me a practice question" / Practice Question
        elif any(w in lower for w in ["practice question", "question", "quiz", "problem"]):
            q_res = self.execute_tool(db, user_id, "generate_practice_question", {"skill_name": "SQL JOINs"})
            tools_used.append("generate_practice_question")
            tool_results["generate_practice_question"] = q_res

            reply = (
                f"Here is a targeted practice check for **{q_res['skill_name']}**:\n\n"
                f"**Question:** {q_res['question_text']}\n\n"
                + "\n".join([f"- {opt}" for opt in q_res.get("options", [])])
                + f"\n\n*(Note: This is an unscored practice exercise designed to build retention. Head to the Practice Lab to submit verified code!)*"
            )
            return reply, tools_used, tool_results

        # 6. "Am I ready for Data Analyst?" / Readiness
        elif any(w in lower for w in ["ready", "readiness", "job", "career"]):
            passport = self.execute_tool(db, user_id, "get_skill_passport", {})
            tools_used.append("get_skill_passport")
            tool_results["get_skill_passport"] = passport

            score = passport.get("career_readiness", 68.4)
            status = passport.get("career_readiness_status", "Developing")
            verified_count = passport.get("skills_verified_count", 3)
            total_count = passport.get("total_role_skills_count", 6)

            reply = (
                f"Your current Career Readiness for Data Analyst is **{score:.1f}%** ({status}).\n\n"
                f"- **Verified Competencies:** {verified_count} of {total_count}\n"
                f"- **Skills Needing Proof:** {', '.join(passport.get('skills_needing_proof', ['SQL JOINs']))}\n\n"
                f"You have strong baseline competencies in foundational areas, but high skill debt in relational querying is holding your readiness back. "
                f"Once you demonstrate SQL JOIN proficiency in a realistic workplace scenario, your score will increase significantly."
            )
            return reply, tools_used, tool_results

        # Default general coaching response
        profile = self.execute_tool(db, user_id, "get_learner_profile", {})
        nbp = self.execute_tool(db, user_id, "get_next_best_proof", {})
        tools_used.extend(["get_learner_profile", "get_next_best_proof"])
        tool_results["get_learner_profile"] = profile
        tool_results["get_next_best_proof"] = nbp

        reply = (
            f"Hello {profile.get('name', 'Learner')}! I am your SkillPath AI Career Coach for the **{profile.get('target_role', 'Data Analyst')}** track.\n\n"
            f"Right now, your highest-leverage focus area is **{nbp.get('skill_name', 'SQL JOINs')}** through **{nbp.get('title', 'Targeted Practice')}**.\n\n"
            f"Feel free to ask me about your Skill DNA, why your roadmap changed, which skills have skill debt, or for interview preparation tips!"
        )
        return reply, tools_used, tool_results

    # =========================================================================
    # SUGGESTED PROMPTS GENERATOR
    # =========================================================================
    def _generate_suggested_prompts(
        self,
        tools_used: List[str],
        tool_results: Dict[str, Any],
    ) -> List[str]:
        if "get_next_best_proof" in tools_used:
            return [
                "Why is this my priority?",
                "Give me a practice question for this skill.",
                "How close am I to being ready for Data Analyst?",
                "Why did my roadmap change?",
            ]
        elif "get_skill_debt" in tools_used:
            return [
                "What should I do next?",
                "How do I clear my Skill Debt?",
                "What evidence do I currently have?",
            ]
        elif "get_current_roadmap" in tools_used or "get_roadmap_changes" in tools_used:
            return [
                "What should I do next?",
                "Why is SQL JOINs my priority?",
                "Am I ready for Data Analyst?",
            ]
        return [
            "What should I do next?",
            "What are my weakest skills?",
            "Why did my roadmap change?",
            "Give me a practice question.",
        ]


coach_service = CoachService()
