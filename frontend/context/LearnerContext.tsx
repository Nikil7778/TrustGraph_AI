'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  api,
  ApiUser,
  ApiUserSkill,
  ApiSkillDNA,
  ApiSkillDebt,
  ApiCareerValue,
  ApiNextBestProof,
  ApiRoadmap,
  ApiProject,
  ApiSkillEvidence,
} from '../services/api';

interface LearnerContextType {
  activeUserId: number;
  activeUser: ApiUser | null;
  userSkills: ApiUserSkill[];
  skillDnaList: ApiSkillDNA[];
  skillDebts: ApiSkillDebt[];
  careerValues: ApiCareerValue[];
  nextBestProof: ApiNextBestProof | null;
  nextBestProofCandidates: ApiNextBestProof[];
  roadmap: ApiRoadmap | null;
  userEvidence: ApiSkillEvidence[];
  projects: ApiProject[];
  allUsers: ApiUser[];
  isLoading: boolean;
  error: string | null;
  isDemoMode: boolean;
  setActiveUserId: (id: number) => void;
  refreshUser: () => Promise<void>;
  rebuildRoadmap: () => Promise<void>;
  updateTargetRole: (roleId: number) => Promise<void>;
  completeProof: (
    skillId: number,
    actionType: string,
    score: number,
    description: string,
    source?: string
  ) => Promise<void>;
  submitProject: (projectId: number, score: number, feedback?: string) => Promise<void>;
}

const LearnerContext = createContext<LearnerContextType | undefined>(undefined);

const DEMO_USER_ID = 1; // Alex Mercer demo profile

export const LearnerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeUserId, setActiveUserIdState] = useState<number>(DEMO_USER_ID);
  const [activeUser, setActiveUser] = useState<ApiUser | null>(null);
  const [userSkills, setUserSkills] = useState<ApiUserSkill[]>([]);
  const [skillDnaList, setSkillDnaList] = useState<ApiSkillDNA[]>([]);
  const [skillDebts, setSkillDebts] = useState<ApiSkillDebt[]>([]);
  const [careerValues, setCareerValues] = useState<ApiCareerValue[]>([]);
  const [nextBestProof, setNextBestProof] = useState<ApiNextBestProof | null>(null);
  const [nextBestProofCandidates, setNextBestProofCandidates] = useState<ApiNextBestProof[]>([]);
  const [roadmap, setRoadmap] = useState<ApiRoadmap | null>(null);
  const [userEvidence, setUserEvidence] = useState<ApiSkillEvidence[]>([]);
  const [projects, setProjects] = useState<ApiProject[]>([]);
  const [allUsers, setAllUsers] = useState<ApiUser[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Read stored active learner ID on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('active_learner_id');
      if (stored) {
        const parsed = parseInt(stored, 10);
        if (!isNaN(parsed)) {
          setActiveUserIdState(parsed);
        }
      }
    }
  }, []);

  const setActiveUserId = (id: number) => {
    setActiveUserIdState(id);
    if (typeof window !== 'undefined') {
      localStorage.setItem('active_learner_id', id.toString());
    }
  };

  const loadLearnerData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch user profile, skills, dna, debt, career value, next-best-proof, roadmap, evidence, and projects
      const [user, skills, dnaList, usersList, debts, cvList, nbp, nbpCandidates, userRoadmap, evidenceList, projectList] = await Promise.all([
        api.getUser(activeUserId).catch(() => null),
        api.getUserSkills(activeUserId).catch(() => []),
        api.getSkillDna(activeUserId).catch(() => []),
        api.getUsers().catch(() => []),
        api.getSkillDebt(activeUserId).catch(() => []),
        api.getCareerValue(activeUserId).catch(() => []),
        api.getNextBestProof(activeUserId).catch(() => null),
        api.getNextBestProofCandidates(activeUserId).catch(() => []),
        api.getRoadmap(activeUserId).catch(() => null),
        api.getUserEvidence(activeUserId).catch(() => []),
        api.getProjects().catch(() => []),
      ]);

      if (user) {
        setActiveUser(user);
      } else {
        setActiveUser(null);
      }
      setUserSkills(skills);
      setSkillDnaList(dnaList);
      setSkillDebts(debts);
      setCareerValues(cvList);
      setNextBestProof(nbp);
      setNextBestProofCandidates(nbpCandidates);
      setRoadmap(userRoadmap);
      setUserEvidence(evidenceList);
      setProjects(projectList);
      setAllUsers(usersList);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load learner context.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [activeUserId]);

  useEffect(() => {
    loadLearnerData();
  }, [loadLearnerData]);

  const completeProof = async (
    skillId: number,
    actionType: string,
    score: number,
    description: string,
    source?: string
  ) => {
    try {
      await api.completeProofAction(activeUserId, {
        skill_id: skillId,
        action_type: actionType,
        score,
        description,
        source,
      });
      await loadLearnerData();
    } catch (err) {
      console.error('Failed to complete proof action:', err);
      throw err;
    }
  };

  const rebuildRoadmap = async () => {
    try {
      const updated = await api.rebuildRoadmap(activeUserId);
      setRoadmap(updated);
    } catch (err) {
      console.error('Failed to rebuild roadmap:', err);
      throw err;
    }
  };

  const updateTargetRole = async (roleId: number) => {
    try {
      await api.updateUser(activeUserId, { target_role_id: roleId });
      await loadLearnerData();
      await rebuildRoadmap();
    } catch (err) {
      console.error('Failed to update target role:', err);
      throw err;
    }
  };

  const submitProject = async (projectId: number, score: number, feedback?: string) => {
    try {
      await api.submitProjectAttempt({
        user_id: activeUserId,
        project_id: projectId,
        score,
        feedback: feedback || 'Completed portfolio project evaluation.',
      });
      // Also register verified evidence in SkillEvidence
      const projectObj = projects.find((p) => p.id === projectId);
      if (projectObj) {
        await api.completeProofAction(activeUserId, {
          skill_id: projectObj.skill_id,
          action_type: 'PROJECT',
          score,
          description: `Successfully executed real-world project: ${projectObj.title}`,
          source: `Portfolio Project: ${projectObj.title}`,
        });
      }
      await loadLearnerData();
    } catch (err) {
      console.error('Failed to submit project attempt:', err);
      throw err;
    }
  };

  const isDemoMode = activeUserId === DEMO_USER_ID;

  return (
    <LearnerContext.Provider
      value={{
        activeUserId,
        activeUser,
        userSkills,
        skillDnaList,
        skillDebts,
        careerValues,
        nextBestProof,
        nextBestProofCandidates,
        roadmap,
        userEvidence,
        projects,
        allUsers,
        isLoading,
        error,
        isDemoMode,
        setActiveUserId,
        refreshUser: loadLearnerData,
        rebuildRoadmap,
        updateTargetRole,
        completeProof,
        submitProject,
      }}
    >
      {children}
    </LearnerContext.Provider>
  );
};

export const useLearner = () => {
  const context = useContext(LearnerContext);
  if (!context) {
    throw new Error('useLearner must be used within a LearnerProvider');
  }
  return context;
};
