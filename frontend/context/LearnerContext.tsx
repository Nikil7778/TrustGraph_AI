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
  ApiUserCreate,
  ApiAuthResponse,
} from '../services/api';

interface LearnerContextType {
  isAuthenticated: boolean;
  isAuthLoading: boolean;
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
  login: (email: string, password?: string) => Promise<ApiUser>;
  googleLogin: (payload: { credential?: string; code?: string; redirect_uri?: string }) => Promise<ApiAuthResponse>;
  logout: () => Promise<void>;
  registerLearner: (payload: ApiUserCreate & { password?: string }) => Promise<ApiUser>;
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

const DEMO_USER_ID = 1; // Convenience flag: user #1 is treated as demo mode

export const LearnerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isAuthLoading, setIsAuthLoading] = useState<boolean>(true);
  const [activeUserId, setActiveUserIdState] = useState<number>(0);
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
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const clearSessionData = useCallback(() => {
    setIsAuthenticated(false);
    setActiveUserIdState(0);
    setActiveUser(null);
    setUserSkills([]);
    setSkillDnaList([]);
    setSkillDebts([]);
    setCareerValues([]);
    setNextBestProof(null);
    setNextBestProofCandidates([]);
    setRoadmap(null);
    setUserEvidence([]);
    setProjects([]);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('active_learner_id');
    }
  }, []);

  // Check initial session on client mount
  useEffect(() => {
    let isMounted = true;
    async function checkSession() {
      try {
        const storedToken = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
        const storedLearnerId = typeof window !== 'undefined' ? localStorage.getItem('active_learner_id') : null;

        // Try resolving authenticated user via /api/auth/me
        let resolvedUser: ApiUser | null = null;
        try {
          resolvedUser = await api.getMe();
        } catch {
          // If getMe failed, check if storedToken and storedLearnerId exist
          if (storedToken && storedLearnerId) {
            const parsedId = parseInt(storedLearnerId, 10);
            if (!isNaN(parsedId) && parsedId > 0) {
              resolvedUser = await api.getUser(parsedId).catch(() => null);
            }
          }
        }

        if (isMounted) {
          if (resolvedUser && resolvedUser.id > 0) {
            setActiveUser(resolvedUser);
            setActiveUserIdState(resolvedUser.id);
            setIsAuthenticated(true);
            if (typeof window !== 'undefined') {
              localStorage.setItem('active_learner_id', resolvedUser.id.toString());
            }
          } else {
            clearSessionData();
          }
        }
      } catch {
        if (isMounted) {
          clearSessionData();
        }
      } finally {
        if (isMounted) {
          setIsAuthLoading(false);
        }
      }
    }

    checkSession();
    return () => {
      isMounted = false;
    };
  }, [clearSessionData]);

  const setActiveUserId = (id: number) => {
    setActiveUserIdState(id);
    if (typeof window !== 'undefined') {
      localStorage.setItem('active_learner_id', id.toString());
    }
  };

  const login = async (email: string, password?: string): Promise<ApiUser> => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.login({ email, password });
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', res.token);
        localStorage.setItem('active_learner_id', res.user.id.toString());
      }
      setActiveUserIdState(res.user.id);
      setActiveUser(res.user);
      setIsAuthenticated(true);
      return res.user;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Login failed.';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const googleLogin = async (payload: { credential?: string; code?: string; redirect_uri?: string }): Promise<ApiAuthResponse> => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.googleAuth(payload);
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', res.token);
        localStorage.setItem('active_learner_id', res.user.id.toString());
      }
      setActiveUserIdState(res.user.id);
      setActiveUser(res.user);
      setIsAuthenticated(true);
      return res;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Google sign-in failed.';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const registerLearner = async (payload: ApiUserCreate & { password?: string }): Promise<ApiUser> => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.register(payload);
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', res.token);
        localStorage.setItem('active_learner_id', res.user.id.toString());
      }
      setActiveUserIdState(res.user.id);
      setActiveUser(res.user);
      setIsAuthenticated(true);
      return res.user;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Registration failed.';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await api.logout().catch(() => null);
    } finally {
      clearSessionData();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
  };

  const loadLearnerData = useCallback(async () => {
    if (!isAuthenticated || !activeUserId || activeUserId <= 0) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
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
  }, [isAuthenticated, activeUserId]);

  useEffect(() => {
    if (isAuthenticated && activeUserId > 0) {
      loadLearnerData();
    }
  }, [isAuthenticated, activeUserId, loadLearnerData]);

  const completeProof = async (
    skillId: number,
    actionType: string,
    score: number,
    description: string,
    source?: string
  ) => {
    if (!activeUserId) return;
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
    if (!activeUserId) return;
    try {
      const updated = await api.rebuildRoadmap(activeUserId);
      setRoadmap(updated);
    } catch (err) {
      console.error('Failed to rebuild roadmap:', err);
      throw err;
    }
  };

  const updateTargetRole = async (roleId: number) => {
    if (!activeUserId) return;
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
    if (!activeUserId) return;
    try {
      await api.submitProjectAttempt({
        user_id: activeUserId,
        project_id: projectId,
        score,
        feedback: feedback || 'Completed portfolio project evaluation.',
      });
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
        isAuthenticated,
        isAuthLoading,
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
        login,
        googleLogin,
        logout,
        registerLearner,
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
