export type SkillStatus = 'healthy' | 'developing' | 'critical' | 'unknown';
export type SkillPriority = 'Low' | 'Medium' | 'High' | 'Critical';
export type StepStatus =
  | 'completed'
  | 'in_progress'
  | 'recommended'
  | 'blocked'
  | 'skipped'
  | 'remediation'
  | 'verified'
  | 'current'
  | 'next'
  | 'upcoming';

export type TaskType =
  | 'foundation'
  | 'learn'
  | 'practice'
  | 'reassess'
  | 'practical_task'
  | 'project'
  | 'capstone'
  | 'lesson'
  | 'challenge'
  | 'task'
  | 'reassessment';

export interface SkillGapItem {
  id: string;
  name: string;
  category: string;
  currentLevel: number; // e.g. 85 for 85%
  requiredLevel: number; // e.g. 80 for 80%
  gap: number; // currentLevel - requiredLevel
  status: SkillStatus;
  priority: SkillPriority;
  confidence: number;
  accuracy: number;
  evidenceCount: number;
  recency: string;
}

export interface NextBestProofAction {
  id: string;
  skillId: string;
  skillName: string;
  currentEvidence: number;
  targetRequirement: number;
  priority: SkillPriority;
  status: SkillStatus;
  challengeTitle: string;
  estimatedEffort: string;
  reasonText: string;
  primaryActionText: string;
}

export interface SkillProgressPoint {
  week: string;
  score: number;
}

export interface SkillProgressData {
  skillName: string;
  history: SkillProgressPoint[];
}

export interface RoadmapStepData {
  id: string;
  stepNumber: number;
  title: string;
  type: TaskType;
  status: StepStatus;
  skillName: string;
  estimatedTime?: string;
  rationale?: string;
  priority?: string;
  evidenceRequired?: string;
  prerequisiteStepIds?: string;
  completedAt?: string;
}

export interface AssessmentData {
  id: string;
  title: string;
  skillCategory: string;
  targetSkill: string;
  durationMinutes: number;
  questionCount: number;
  latestScore?: number;
  status: 'available' | 'completed' | 'in_progress';
  lastTaken?: string;
}

export interface PracticeTaskData {
  id: string;
  title: string;
  targetSkill: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  estimatedMinutes: number;
  evidenceType: string;
  status: 'available' | 'completed' | 'in_progress';
}

export interface ProjectData {
  id: string;
  title: string;
  description: string;
  skillsDemonstrated: string[];
  status: 'verified' | 'in_review' | 'in_progress' | 'not_started';
  score?: number;
  evidenceGenerated: string;
  lastUpdated: string;
}

export interface PassportSkillData {
  name: string;
  mastery: number;
  status: 'verified' | 'developing';
  evidenceCount: number;
  lastVerifiedDate: string;
}

export interface SkillPassportProfile {
  passportId: string;
  learnerName: string;
  targetRole: string;
  readinessScore: number;
  verifiedSkills: PassportSkillData[];
  developingSkills: PassportSkillData[];
  verifiedProjectsCount: number;
  practicalEvidenceCount: number;
  issueDate: string;
}
