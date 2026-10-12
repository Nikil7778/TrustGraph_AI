const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

export interface ApiRoleSkill {
  id: number;
  role_id: number;
  skill_id: number;
  skill_name?: string;
  importance_score: number;
  industry_relevance: string;
  required_level: number;
}

export interface ApiRole {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  role_skills: ApiRoleSkill[];
}

export interface ApiSkill {
  id: number;
  name: string;
  category: string;
  description?: string;
  created_at: string;
}

export interface ApiUser {
  id: number;
  name: string;
  email: string;
  experience_level: string;
  target_role_id?: number;
  target_role?: ApiRole;
  weekly_learning_hours: number;
  learning_goal?: string;
  created_at: string;
  updated_at: string;
}

export interface ApiUserSkill {
  id: number;
  user_id: number;
  skill_id: number;
  skill_name?: string;
  skill_category?: string;
  skill_level: number;
  confidence: number;
  accuracy: number;
  difficulty: string;
  recency: string;
  evidence_score: number;
  last_assessed_at: string;
  updated_at: string;
}

export interface ApiUserCreate {
  name: string;
  email: string;
  experience_level: string;
  target_role_id: number;
  weekly_learning_hours: number;
  learning_goal: string;
}

export interface ApiAssessmentQuestionPublic {
  id: number;
  assessment_id: number;
  question_text: string;
  options: string[];
  difficulty: string;
}

export interface ApiAssessment {
  id: number;
  title: string;
  description?: string;
  skill_id: number;
  skill_name?: string;
  difficulty: string;
  question_count?: number;
  created_at: string;
}

export interface ApiAssessmentDetail extends ApiAssessment {
  questions: ApiAssessmentQuestionPublic[];
}

export interface ApiSingleQuestionAnswer {
  question_id: number;
  answer: string;
}

export interface ApiAssessmentSubmissionPayload {
  user_id: number;
  assessment_id: number;
  answers: ApiSingleQuestionAnswer[];
}

export interface ApiQuestionReviewResult {
  question_id: number;
  question_text: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation?: string;
}

export interface ApiAssessmentResult {
  attempt_id: number;
  user_id: number;
  assessment_id: number;
  assessment_title: string;
  skill_name: string;
  raw_score: number;
  total_questions: number;
  percentage: number;
  accuracy: number;
  difficulty: string;
  completed_at: string;
  interpretation: 'Strong' | 'Healthy' | 'Developing' | 'Critical Gap';
  question_breakdown: ApiQuestionReviewResult[];
}

export interface ApiAssessmentAttempt {
  id: number;
  user_id: number;
  assessment_id: number;
  assessment_title?: string;
  skill_name?: string;
  score: number;
  accuracy: number;
  completed_at: string;
}

export interface ApiSkillDNA {
  user_id: number;
  skill_id: number;
  skill_name: string;
  skill_category: string;
  skill_level: number;
  confidence: number;
  accuracy: number;
  difficulty: number;
  difficulty_label: string;
  recency: number;
  recency_label: string;
  evidence_score: number;
  evidence_count: number;
  last_assessed_at: string;
  status: 'HEALTHY' | 'STRONG' | 'DEVELOPING' | 'CRITICAL' | 'UNKNOWN';
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetail = 'An unexpected backend error occurred.';
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        if (typeof errJson.detail === 'string') {
          errorDetail = errJson.detail;
        } else if (Array.isArray(errJson.detail)) {
          errorDetail = errJson.detail.map((e: { msg?: string }) => e.msg || 'Invalid field').join(', ');
        }
      }
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

export const api = {
  // Roles & Skills
  async getRoles(): Promise<ApiRole[]> {
    const res = await fetch(`${API_BASE_URL}/roles`, { cache: 'no-store' });
    return handleResponse<ApiRole[]>(res);
  },

  async getSkills(): Promise<ApiSkill[]> {
    const res = await fetch(`${API_BASE_URL}/skills`, { cache: 'no-store' });
    return handleResponse<ApiSkill[]>(res);
  },

  // Users & Onboarding
  async getUsers(): Promise<ApiUser[]> {
    const res = await fetch(`${API_BASE_URL}/users`, { cache: 'no-store' });
    return handleResponse<ApiUser[]>(res);
  },

  async getUser(userId: number): Promise<ApiUser> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}`, { cache: 'no-store' });
    return handleResponse<ApiUser>(res);
  },

  async createUser(payload: ApiUserCreate): Promise<ApiUser> {
    const res = await fetch(`${API_BASE_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiUser>(res);
  },

  async getUserSkills(userId: number): Promise<ApiUserSkill[]> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/skills`, { cache: 'no-store' });
    return handleResponse<ApiUserSkill[]>(res);
  },

  // Assessments
  async getAssessments(): Promise<ApiAssessment[]> {
    const res = await fetch(`${API_BASE_URL}/assessments`, { cache: 'no-store' });
    return handleResponse<ApiAssessment[]>(res);
  },

  async getAssessmentDetail(assessmentId: number): Promise<ApiAssessmentDetail> {
    const res = await fetch(`${API_BASE_URL}/assessments/${assessmentId}`, { cache: 'no-store' });
    return handleResponse<ApiAssessmentDetail>(res);
  },

  async submitAssessment(payload: ApiAssessmentSubmissionPayload): Promise<ApiAssessmentResult> {
    const res = await fetch(`${API_BASE_URL}/assessment-attempts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiAssessmentResult>(res);
  },

  async getUserAssessmentAttempts(userId: number): Promise<ApiAssessmentAttempt[]> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/assessment-attempts`, { cache: 'no-store' });
    return handleResponse<ApiAssessmentAttempt[]>(res);
  },

  // Skill DNA
  async getSkillDna(userId: number): Promise<ApiSkillDNA[]> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/skill-dna`, { cache: 'no-store' });
    return handleResponse<ApiSkillDNA[]>(res);
  },

  async getSingleSkillDna(userId: number, skillId: number): Promise<ApiSkillDNA> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/skills/${skillId}/skill-dna`, { cache: 'no-store' });
    return handleResponse<ApiSkillDNA>(res);
  },

  async recalculateSkillDna(userId: number): Promise<ApiSkillDNA[]> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/skill-dna/recalculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse<ApiSkillDNA[]>(res);
  },

  // Skill Debt
  async getSkillDebt(userId: number, roleId?: number): Promise<ApiSkillDebt[]> {
    const url = roleId
      ? `${API_BASE_URL}/users/${userId}/skill-debt?role_id=${roleId}`
      : `${API_BASE_URL}/users/${userId}/skill-debt`;
    const res = await fetch(url, { cache: 'no-store' });
    return handleResponse<ApiSkillDebt[]>(res);
  },

  async getSingleSkillDebt(userId: number, skillId: number, roleId?: number): Promise<ApiSkillDebt> {
    const url = roleId
      ? `${API_BASE_URL}/users/${userId}/skill-debt/${skillId}?role_id=${roleId}`
      : `${API_BASE_URL}/users/${userId}/skill-debt/${skillId}`;
    const res = await fetch(url, { cache: 'no-store' });
    return handleResponse<ApiSkillDebt>(res);
  },

  async recalculateSkillDebt(userId: number, roleId?: number): Promise<ApiSkillDebt[]> {
    const url = roleId
      ? `${API_BASE_URL}/users/${userId}/skill-debt/recalculate?role_id=${roleId}`
      : `${API_BASE_URL}/users/${userId}/skill-debt/recalculate`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse<ApiSkillDebt[]>(res);
  },

  // Career Value
  async getCareerValue(userId: number, roleId?: number): Promise<ApiCareerValue[]> {
    const url = roleId
      ? `${API_BASE_URL}/users/${userId}/career-value?role_id=${roleId}`
      : `${API_BASE_URL}/users/${userId}/career-value`;
    const res = await fetch(url, { cache: 'no-store' });
    return handleResponse<ApiCareerValue[]>(res);
  },

  async getSingleCareerValue(userId: number, skillId: number, roleId?: number): Promise<ApiCareerValue> {
    const url = roleId
      ? `${API_BASE_URL}/users/${userId}/career-value/${skillId}?role_id=${roleId}`
      : `${API_BASE_URL}/users/${userId}/career-value/${skillId}`;
    const res = await fetch(url, { cache: 'no-store' });
    return handleResponse<ApiCareerValue>(res);
  },

  async recalculateCareerValue(userId: number, roleId?: number): Promise<ApiCareerValue[]> {
    const url = roleId
      ? `${API_BASE_URL}/users/${userId}/career-value/recalculate?role_id=${roleId}`
      : `${API_BASE_URL}/users/${userId}/career-value/recalculate`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse<ApiCareerValue[]>(res);
  },

  // Next-Best-Proof
  async getNextBestProof(userId: number, roleId?: number): Promise<ApiNextBestProof> {
    const url = roleId
      ? `${API_BASE_URL}/users/${userId}/next-best-proof?role_id=${roleId}`
      : `${API_BASE_URL}/users/${userId}/next-best-proof`;
    const res = await fetch(url, { cache: 'no-store' });
    return handleResponse<ApiNextBestProof>(res);
  },

  async getNextBestProofCandidates(userId: number, roleId?: number): Promise<ApiNextBestProof[]> {
    const url = roleId
      ? `${API_BASE_URL}/users/${userId}/next-best-proof/candidates?role_id=${roleId}`
      : `${API_BASE_URL}/users/${userId}/next-best-proof/candidates`;
    const res = await fetch(url, { cache: 'no-store' });
    return handleResponse<ApiNextBestProof[]>(res);
  },

  async recalculateNextBestProof(userId: number, roleId?: number): Promise<ApiNextBestProof> {
    const url = roleId
      ? `${API_BASE_URL}/users/${userId}/next-best-proof/recalculate?role_id=${roleId}`
      : `${API_BASE_URL}/users/${userId}/next-best-proof/recalculate`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse<ApiNextBestProof>(res);
  },

  async completeProofAction(
    userId: number,
    payload: {
      skill_id: number;
      action_type: string;
      score: number;
      description: string;
      source?: string;
    }
  ): Promise<ApiNextBestProof> {
    const url = `${API_BASE_URL}/users/${userId}/next-best-proof/complete`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiNextBestProof>(res);
  },

  async getRoadmap(userId: number): Promise<ApiRoadmap> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/roadmap`, { cache: 'no-store' });
    return handleResponse<ApiRoadmap>(res);
  },

  async rebuildRoadmap(userId: number): Promise<ApiRoadmap> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/roadmap/rebuild`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse<ApiRoadmap>(res);
  },

  async getRoadmapHistory(userId: number): Promise<ApiRoadmapHistory[]> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/roadmap/history`, { cache: 'no-store' });
    return handleResponse<ApiRoadmapHistory[]>(res);
  },

  async getRoadmapChanges(userId: number): Promise<ApiRoadmapChange[]> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/roadmap/changes`, { cache: 'no-store' });
    return handleResponse<ApiRoadmapChange[]>(res);
  },

  // Projects
  async getProjects(): Promise<ApiProject[]> {
    const res = await fetch(`${API_BASE_URL}/projects`, { cache: 'no-store' });
    return handleResponse<ApiProject[]>(res);
  },

  async submitProjectAttempt(payload: {
    user_id: number;
    project_id: number;
    score: number;
    feedback?: string;
  }): Promise<ApiProjectAttempt> {
    const res = await fetch(`${API_BASE_URL}/project-attempts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiProjectAttempt>(res);
  },

  // Evidence
  async getUserEvidence(userId: number): Promise<ApiSkillEvidence[]> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/evidence`, { cache: 'no-store' });
    return handleResponse<ApiSkillEvidence[]>(res);
  },

  // User Update
  async updateUser(userId: number, payload: Partial<ApiUserCreate>): Promise<ApiUser> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiUser>(res);
  },

  // Industry Labs (Phase 10)
  async getIndustryLabs(roleId?: number, skillId?: number): Promise<ApiIndustryLab[]> {
    let url = `${API_BASE_URL}/industry-labs`;
    const params = new URLSearchParams();
    if (roleId) params.append('role_id', String(roleId));
    if (skillId) params.append('skill_id', String(skillId));
    if (params.toString()) url += `?${params.toString()}`;
    const res = await fetch(url, { cache: 'no-store' });
    return handleResponse<ApiIndustryLab[]>(res);
  },

  async getIndustryLab(idOrSlug: string | number): Promise<ApiIndustryLab> {
    const res = await fetch(`${API_BASE_URL}/industry-labs/${idOrSlug}`, { cache: 'no-store' });
    return handleResponse<ApiIndustryLab>(res);
  },

  async getIndustryLabPreview(idOrSlug: string | number): Promise<ApiIndustryLabTablePreview[]> {
    const res = await fetch(`${API_BASE_URL}/industry-labs/${idOrSlug}/preview`, { cache: 'no-store' });
    return handleResponse<ApiIndustryLabTablePreview[]>(res);
  },

  async runIndustryLabQuery(idOrSlug: string | number, query: string): Promise<ApiIndustryLabQueryRunResponse> {
    const res = await fetch(`${API_BASE_URL}/industry-labs/${idOrSlug}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    return handleResponse<ApiIndustryLabQueryRunResponse>(res);
  },

  async submitIndustryLabAttempt(
    idOrSlug: string | number,
    payload: { user_id: number; query: string; submitted_answer?: string; evidence_type?: string }
  ): Promise<ApiIndustryLabSubmitResponse> {
    const res = await fetch(`${API_BASE_URL}/industry-labs/${idOrSlug}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiIndustryLabSubmitResponse>(res);
  },

  async getIndustryLabAttempts(idOrSlug: string | number, userId: number): Promise<ApiIndustryLabAttempt[]> {
    const res = await fetch(`${API_BASE_URL}/industry-labs/${idOrSlug}/attempts?user_id=${userId}`, { cache: 'no-store' });
    return handleResponse<ApiIndustryLabAttempt[]>(res);
  },

  // Phase 11 — Gemini AI Layer Methods
  async explainDecision(payload: ApiAIExplainDecisionRequest): Promise<ApiAIExplainDecisionResponse> {
    const res = await fetch(`${API_BASE_URL}/ai/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiAIExplainDecisionResponse>(res);
  },

  async getAIHint(payload: ApiAIHintRequest): Promise<ApiAIHintResponse> {
    const res = await fetch(`${API_BASE_URL}/ai/hint`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiAIHintResponse>(res);
  },

  async explainMistake(payload: ApiAIExplainMistakeRequest): Promise<ApiAIExplainMistakeResponse> {
    const res = await fetch(`${API_BASE_URL}/ai/explain-mistake`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiAIExplainMistakeResponse>(res);
  },

  async getLearningExplanation(payload: ApiAILearningExplanationRequest): Promise<ApiAILearningExplanationResponse> {
    const res = await fetch(`${API_BASE_URL}/ai/learning-explanation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiAILearningExplanationResponse>(res);
  },

  async getPracticeQuestions(payload: ApiAIPracticeQuestionsRequest): Promise<ApiAIPracticeQuestionsResponse> {
    const res = await fetch(`${API_BASE_URL}/ai/practice-questions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiAIPracticeQuestionsResponse>(res);
  },

  async getInterviewQuestions(payload: ApiAIInterviewQuestionsRequest): Promise<ApiAIInterviewQuestionsResponse> {
    const res = await fetch(`${API_BASE_URL}/ai/interview-questions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiAIInterviewQuestionsResponse>(res);
  },

  async getStudyGuidance(userId: number): Promise<ApiAIStudyGuidanceResponse> {
    const res = await fetch(`${API_BASE_URL}/ai/study-guidance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    });
    return handleResponse<ApiAIStudyGuidanceResponse>(res);
  },

  // Phase 12 — Unified Dashboard Aggregation
  async getDashboard(userId: number): Promise<ApiDashboardResponse> {
    const res = await fetch(`${API_BASE_URL}/dashboard/${userId}`, { cache: 'no-store' });
    return handleResponse<ApiDashboardResponse>(res);
  },

  // Phase 13 — Proof-of-Skill Passport
  async getSkillPassport(userId: number): Promise<ApiSkillPassportResponse> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/skill-passport`, { cache: 'no-store' });
    return handleResponse<ApiSkillPassportResponse>(res);
  },

  async getSkillPassportSkillDetail(userId: number, skillId: number): Promise<ApiSkillProofMatrixItem> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/skill-passport/${skillId}`, { cache: 'no-store' });
    return handleResponse<ApiSkillProofMatrixItem>(res);
  },

  async getSkillPassportSummary(userId: number): Promise<ApiPassportSummary> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/skill-passport/summary`, { cache: 'no-store' });
    return handleResponse<ApiPassportSummary>(res);
  },

  async getSkillPassportEvidence(userId: number): Promise<ApiEvidenceTimelineItem[]> {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/skill-passport/evidence`, { cache: 'no-store' });
    return handleResponse<ApiEvidenceTimelineItem[]>(res);
  },

  // Phase 14 — Demo & Integration
  async resetDemo(userId?: number): Promise<ApiDemoResetResponse> {
    const url = userId ? `${API_BASE_URL}/demo/reset?user_id=${userId}` : `${API_BASE_URL}/demo/reset`;
    const res = await fetch(url, { method: 'POST' });
    return handleResponse<ApiDemoResetResponse>(res);
  },

  async getDemoState(userId?: number): Promise<ApiDemoStateResponse> {
    const url = userId ? `${API_BASE_URL}/demo/state?user_id=${userId}` : `${API_BASE_URL}/demo/state`;
    const res = await fetch(url, { cache: 'no-store' });
    return handleResponse<ApiDemoStateResponse>(res);
  },

  // Part Z — AI Career Coach Chatbot
  async coachChat(payload: ApiCoachChatRequest): Promise<ApiCoachChatResponse> {
    const res = await fetch(`${API_BASE_URL}/coach/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<ApiCoachChatResponse>(res);
  },

  async getCoachSuggestedPrompts(): Promise<string[]> {
    const res = await fetch(`${API_BASE_URL}/coach/suggested-prompts`, { cache: 'no-store' });
    return handleResponse<string[]>(res);
  },
};

export interface ApiNextBestProof {
  user_id: number;
  role_id: number;
  role_name: string;
  skill_id: number;
  skill_name: string;
  skill_category: string;
  action_type: 'LEARN' | 'PRACTICE' | 'REASSESS' | 'PRACTICAL_TASK' | 'PROJECT' | 'REVIEW_PREREQUISITE';
  action_type_label: string;
  title: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  next_best_proof_score: number;
  current_skill_level: number;
  required_skill_level: number;
  career_value_score: number;
  skill_debt_score: number;
  skill_debt_status: string;
  confidence: number;
  evidence_score: number;
  practical_evidence_score: number;
  estimated_minutes: number;
  expected_proof: string;
  reason: string;
  why_now: string;
  why_this_action: string;
  prerequisites: string[];
  action_readiness: string;
  rank?: number;
  created_at: string;
}

export interface ApiCareerValue {
  skill_id: number;
  skill_name: string;
  skill_category: string;
  role_id: number;
  role_name: string;
  current_skill_level: number;
  required_skill_level: number;
  gap_score: number;
  role_importance: number;
  industry_relevance: number;
  industry_relevance_label: string;
  confidence: number;
  confidence_gap: number;
  recency: number;
  recency_gap: number;
  evidence_score: number;
  evidence_gap: number;
  skill_debt_status: string;
  skill_debt_score: number;
  debt_boost: number;
  career_value_score: number;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  reason: string;
  recommended_focus: string;
  rank: number;
}

export interface ApiSkillDebt {
  skill_id: number;
  skill_name: string;
  skill_category: string;
  role_id: number;
  role_name: string;
  role_requirement: number;
  current_skill_level: number;
  confidence: number;
  accuracy: number;
  recency: number;
  recency_label: string;
  evidence_count: number;
  practical_evidence_count: number;
  latest_evidence_at?: string;
  debt_status: 'SKILL_DEBT' | 'MISSING' | 'HEALTHY' | 'UNKNOWN';
  debt_score: number;
  severity: 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
  reason: string;
  recommended_intervention: string;
}

export interface ApiRoadmapStep {
  id: number;
  roadmap_id: number;
  skill_id: number;
  skill_name?: string;
  activity_id?: number;
  title: string;
  step_type: string;
  priority: string;
  status: string;
  reason?: string;
  order_index: number;
  estimated_minutes: number;
  prerequisite_step_ids?: string;
  evidence_required?: string;
  completed_at?: string;
}

export interface ApiRoadmap {
  id: number;
  user_id: number;
  target_role_id?: number;
  target_role_name?: string;
  version: number;
  status: string;
  regeneration_reason?: string;
  created_at: string;
  updated_at: string;
  steps: ApiRoadmapStep[];
}

export interface ApiRoadmapHistory {
  id: number;
  user_id: number;
  target_role_id?: number;
  target_role_name?: string;
  version: number;
  status: string;
  regeneration_reason?: string;
  step_count: number;
  created_at: string;
  updated_at: string;
}

export interface ApiRoadmapChange {
  id: number;
  user_id: number;
  roadmap_id: number;
  version: number;
  change_type: string;
  skill_name: string;
  title: string;
  description: string;
  created_at: string;
}

export interface ApiProject {
  id: number;
  title: string;
  description: string;
  skill_id: number;
  skill_name?: string;
  difficulty: string;
  estimated_minutes: number;
  project_type: string;
  created_at: string;
}

export interface ApiProjectAttempt {
  id: number;
  user_id: number;
  project_id: number;
  project_title?: string;
  score: number;
  feedback?: string;
  completed_at: string;
}

export interface ApiSkillEvidence {
  id: number;
  user_id: number;
  skill_id: number;
  skill_name?: string;
  source: string;
  evidence_type: string;
  score: number;
  description?: string;
  created_at: string;
}

export interface ApiIndustryLabTask {
  id: number;
  lab_id: number;
  task_order: number;
  task_type: string;
  title: string;
  prompt: string;
  requirements: string;
  expected_output_desc: string;
  weight: number;
}

export interface ApiIndustryLab {
  id: number;
  slug: string;
  title: string;
  description: string;
  target_role_id?: number;
  target_role_name?: string;
  primary_skill_id: number;
  primary_skill_name?: string;
  difficulty: string;
  estimated_minutes: number;
  business_context: string;
  datasets_info?: string;
  created_at: string;
  tasks: ApiIndustryLabTask[];
}

export interface ApiIndustryLabTableColumnInfo {
  name: string;
  type: string;
  description?: string;
}

export interface ApiIndustryLabTablePreview {
  table_name: string;
  row_count: number;
  columns: ApiIndustryLabTableColumnInfo[];
  sample_rows: Record<string, any>[];
  quality_notes: string[];
}

export interface ApiIndustryLabQueryRunResponse {
  success: boolean;
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  execution_time_ms: number;
  error_message?: string | null;
}

export interface ApiIndustryLabSectionScores {
  sql_correctness: number;
  data_quality_handling: number;
  business_result: number;
  validation_reasoning: number;
}

export interface ApiIndustryLabSubmitResponse {
  attempt_id: number;
  user_id: number;
  lab_id: number;
  lab_title: string;
  attempt_number: number;
  status: 'PASSED' | 'PARTIAL' | 'FAILED';
  total_score: number;
  section_scores: ApiIndustryLabSectionScores;
  feedback: string;
  diagnostic_failures: string[];
  evidence_generated?: {
    id: number;
    skill_id: number;
    evidence_type: string;
    score: number;
    description: string;
  } | null;
  execution_time_ms: number;
  created_at: string;
}

export interface ApiIndustryLabAttempt {
  id: number;
  lab_id: number;
  user_id: number;
  attempt_number: number;
  status: string;
  total_score: number;
  sql_score: number;
  data_quality_score: number;
  business_score: number;
  validation_score: number;
  submitted_query?: string;
  feedback?: string;
  execution_time_ms: number;
  created_at: string;
}

// Phase 11 — Gemini AI Layer Interfaces
export interface ApiAIExplainDecisionRequest {
  user_id: number;
  target_role?: string;
  skill_name: string;
  context_type: 'NEXT_BEST_PROOF' | 'SKILL_DEBT' | 'CAREER_VALUE' | 'ROADMAP_CHANGE' | 'EVIDENCE_VERIFICATION' | 'STRENGTHEN_SKILL' | string;
  structured_data: Record<string, any>;
}

export interface ApiAIExplainDecisionResponse {
  skill_name: string;
  context_type: string;
  explanation: string;
  key_takeaways: string[];
  actionable_next_step: string;
  model_used: string;
  fallback_used: boolean;
}

export interface ApiAIHintRequest {
  task_title: string;
  skill_name: string;
  context_description: string;
  hint_level: number;
  learner_query?: string;
}

export interface ApiAIHintResponse {
  task_title: string;
  skill_name: string;
  hint_level: number;
  max_hint_level: number;
  hint: string;
  focus_concept: string;
  model_used: string;
  fallback_used: boolean;
}

export interface ApiAIExplainMistakeRequest {
  skill_name: string;
  task_or_question: string;
  learner_answer: string;
  correct_answer_or_result: string;
  deterministic_evaluation: string;
  target_role?: string;
}

export interface ApiAIExplainMistakeResponse {
  skill_name: string;
  what_went_wrong: string;
  why_it_happened: string;
  how_to_recognize_next_time: string;
  small_example: string;
  short_practice_question: string;
  model_used: string;
  fallback_used: boolean;
}

export interface ApiAILearningExplanationRequest {
  skill_name: string;
  target_role?: string;
  specific_topic?: string;
}

export interface ApiAILearningExplanationResponse {
  skill_name: string;
  target_role: string;
  concept_summary: string;
  concise_example: string;
  common_pitfall: string;
  role_use_case: string;
  check_question: string;
  model_used: string;
  fallback_used: boolean;
}

export interface ApiAIPracticeQuestionItem {
  question_text: string;
  options: string[];
  expected_answer: string;
  explanation: string;
  difficulty: string;
  is_unscored_practice: boolean;
}

export interface ApiAIPracticeQuestionsRequest {
  skill_name: string;
  difficulty?: string;
  target_role?: string;
  count?: number;
}

export interface ApiAIPracticeQuestionsResponse {
  skill_name: string;
  difficulty: string;
  questions: ApiAIPracticeQuestionItem[];
  disclaimer: string;
  model_used: string;
  fallback_used: boolean;
}

export interface ApiAIInterviewQuestionItem {
  category: string;
  question: string;
  evaluation_tip: string;
}

export interface ApiAIInterviewQuestionsRequest {
  skill_name: string;
  target_role?: string;
}

export interface ApiAIInterviewQuestionsResponse {
  skill_name: string;
  target_role: string;
  questions: ApiAIInterviewQuestionItem[];
  model_used: string;
  fallback_used: boolean;
}

export interface ApiAIStudyGuidanceDayItem {
  day_name: string;
  duration_minutes: number;
  activity_type: string;
  task_focus: string;
}

export interface ApiAIStudyGuidanceResponse {
  user_id: number;
  target_role: string;
  weekly_hours: number;
  focus_headline: string;
  daily_breakdown: {
    day_name: string;
    duration_minutes: number;
    activity_type: string;
    task_focus: string;
  }[];
  coach_advice: string;
  model_used: string;
  fallback_used: boolean;
}

// Phase 12 — Unified Dashboard Interfaces
export interface ApiCareerReadinessMetric {
  score: number;
  status: string;
  trend_label?: string | null;
  formula_explanation: string;
}

export interface ApiDashboardMetrics {
  career_readiness: ApiCareerReadinessMetric;
  skills_verified: number;
  total_role_skills: number;
  active_skill_debt_count: number;
  high_debt_count: number;
  evidence_records_count: number;
  next_best_proof_title?: string | null;
}

export interface ApiDashboardSkillGapItem {
  skill_id: number;
  skill_name: string;
  category: string;
  current_level: number;
  required_level: number;
  gap: number;
  role_importance: number;
  industry_relevance: string;
  status: 'healthy' | 'developing' | 'critical' | 'unknown';
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  skill_debt_status: string;
  skill_debt_severity?: string | null;
}

export interface ApiDashboardSkillDnaItem {
  skill_id: number;
  skill_name: string;
  category: string;
  skill_level: number;
  confidence: number;
  accuracy: number;
  status: string;
  evidence_count: number;
  recency_label: string;
}

export interface ApiDashboardCareerPriorityItem {
  rank: number;
  skill_id: number;
  skill_name: string;
  priority: string;
  career_value_score: number;
  gap_score: number;
  role_importance: number;
  reason: string;
  recommended_focus: string;
}

export interface ApiDashboardSkillDebtAlert {
  skill_id: number;
  skill_name: string;
  severity: string;
  debt_score: number;
  current_level: number;
  required_level: number;
  message: string;
  cta_text: string;
  action_type: string;
}

export interface ApiDashboardEvidenceItem {
  id: number;
  skill_name: string;
  evidence_type: string;
  score: number;
  source: string;
  description?: string | null;
  verified_date: string;
}

export interface ApiDashboardRoadmapStepItem {
  id: number;
  order_index: number;
  title: string;
  step_type: string;
  status: string;
  skill_name: string;
  estimated_minutes: number;
  priority: string;
}

export interface ApiDashboardProgressPoint {
  week: string;
  score: number;
}

export interface ApiDashboardSkillProgressItem {
  skill_name: string;
  history: ApiDashboardProgressPoint[];
}

export interface ApiDashboardRoleOption {
  id: number;
  name: string;
}

export interface ApiDashboardResponse {
  user_id: number;
  learner_name: string;
  target_role_id: number;
  target_role_name: string;
  all_roles: ApiDashboardRoleOption[];
  metrics: ApiDashboardMetrics;
  next_best_proof?: ApiNextBestProof | null;
  highest_career_gap?: ApiDashboardCareerPriorityItem | null;
  skill_gap_heatmap: ApiDashboardSkillGapItem[];
  skill_dna_snapshot: ApiDashboardSkillDnaItem[];
  top_career_priorities: ApiDashboardCareerPriorityItem[];
  skill_debt_alert?: ApiDashboardSkillDebtAlert | null;
  recent_evidence: ApiDashboardEvidenceItem[];
  roadmap_preview: ApiDashboardRoadmapStepItem[];
  progress_history: ApiDashboardSkillProgressItem[];
}

// Phase 13 — Proof-of-Skill Passport Interfaces
export interface ApiPassportHeader {
  user_id: number;
  learner_name: string;
  target_role_id: number;
  target_role_name: string;
  career_readiness: number;
  career_readiness_status: string;
  skills_verified_count: number;
  total_role_skills_count: number;
  total_evidence_count: number;
  last_verified_date?: string | null;
  passport_id: string;
  created_at: string;
}

export interface ApiPassportSummary {
  headline: string;
  verified_skills_count: number;
  developing_skills_count: number;
  skill_debt_count: number;
  strongest_skills: string[];
  skills_needing_proof: string[];
}

export interface ApiSkillProofEvidenceItem {
  id: number;
  source: string;
  title: string;
  evidence_type: string;
  evidence_strength: string;
  score: number;
  verified_date: string;
  relative_date: string;
  description?: string | null;
}

export interface ApiSkillProofMatrixItem {
  skill_id: number;
  skill_name: string;
  category: string;
  skill_level: number;
  confidence: number;
  required_level: number;
  evidence_count: number;
  last_verified: string;
  status: 'VERIFIED' | 'DEVELOPING' | 'CRITICAL' | 'SKILL DEBT' | 'NOT YET PROVEN' | string;
  evidence_strength_label: string;
  is_verified: boolean;
  supporting_evidences: ApiSkillProofEvidenceItem[];
}

export interface ApiEvidenceTimelineItem {
  id: number;
  skill_id: number;
  skill_name: string;
  evidence_type: string;
  score: number;
  source: string;
  verified_date: string;
  relative_date: string;
  description?: string | null;
}

export interface ApiStrongestProofItem {
  id: number;
  title: string;
  evidence_type: string;
  evidence_strength: string;
  score: number;
  skills_demonstrated: string[];
  verified_date: string;
  description: string;
}

export interface ApiSkillNeedingProofItem {
  skill_id: number;
  skill_name: string;
  status: string;
  severity: string;
  current_level: number;
  required_level: number;
  evidence_gap_reason: string;
  recommended_proof_title: string;
  action_type: string;
}

export interface ApiPassportProjectItem {
  id: number;
  title: string;
  skills_demonstrated: string[];
  evidence_type: string;
  status: string;
  score?: number | null;
  verified_date: string;
}

export interface ApiPassportAssessmentItem {
  id: number;
  assessment_id: number;
  assessment_title: string;
  skill_name: string;
  score: number;
  accuracy: number;
  difficulty: string;
  completed_at: string;
}

export interface ApiCareerRelevanceItem {
  skill_name: string;
  importance: number;
  evidence_status_label: string;
  career_priority: string;
}

export interface ApiSkillPassportResponse {
  header: ApiPassportHeader;
  summary: ApiPassportSummary;
  skill_proof_matrix: ApiSkillProofMatrixItem[];
  evidence_timeline: ApiEvidenceTimelineItem[];
  strongest_proof?: ApiStrongestProofItem | null;
  skills_needing_proof: ApiSkillNeedingProofItem[];
  next_best_proof?: Record<string, any> | null;
  projects: ApiPassportProjectItem[];
  assessment_history: ApiPassportAssessmentItem[];
  career_relevance: ApiCareerRelevanceItem[];
}

// Phase 14 — Demo & Integration Interfaces
export interface ApiDemoResetResponse {
  success: boolean;
  message: string;
  user_id: number;
  learner_name: string;
  target_role: string;
  sql_joins_level: number;
  sql_joins_debt: string;
  sql_joins_severity: string;
  next_best_proof_title: string;
  career_readiness: number;
}

export interface ApiDemoPathSnapshotItem {
  skill_name: string;
  baseline_level: number;
  current_level: number;
  baseline_status: string;
  current_status: string;
  baseline_debt: string;
  current_debt: string;
}

export interface ApiDemoStateResponse {
  user_id: number;
  learner_name: string;
  target_role: string;
  has_completed_proof: boolean;
  career_readiness_initial: number;
  career_readiness_current: number;
  sql_joins_snapshot: ApiDemoPathSnapshotItem;
  roadmap_version: number;
  roadmap_steps_count: number;
  next_best_proof_title: string;
  unlocked_next_skill: string;
}

// Part Z — AI Career Coach Interfaces
export interface ApiChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ApiChatAction {
  label: string;
  action_type: string;
  target_route: string;
  skill_id?: number;
  skill_name?: string;
}

export interface ApiCoachChatRequest {
  user_id: number;
  message: string;
  history?: ApiChatMessage[];
  context_hint?: string;
}

export interface ApiCoachChatResponse {
  reply: string;
  actions: ApiChatAction[];
  tools_used: string[];
  suggested_prompts: string[];
  fallback_used: boolean;
  model_used: string;
}





