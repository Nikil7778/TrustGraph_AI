'use client';

import React, { useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { ProjectCard } from '../../components/ProjectCard';
import { useLearner } from '../../context/LearnerContext';
import { MOCK_PROJECTS } from '../../lib/mockData';
import { ProjectData } from '../../types';
import { FolderGit2, Plus, X, Play, Loader2, CheckCircle2, Award, ExternalLink } from 'lucide-react';

export default function ProjectsPage() {
  const { projects, submitProject, userEvidence, isDemoMode } = useLearner();
  const [activeProject, setActiveProject] = useState<ProjectData | null>(null);
  const [simScore, setSimScore] = useState<number>(90);
  const [feedback, setFeedback] = useState<string>('All test suite assertions passed with robust coverage.');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  // Convert live backend projects or fallback
  const displayedProjects: ProjectData[] = projects.length > 0
    ? projects.map((p) => {
        const verifiedEv = userEvidence.find(
          (e) => e.evidence_type === 'PROJECT' && e.source.includes(p.title)
        );
        return {
          id: `proj-${p.id}`,
          title: p.title,
          description: p.description,
          status: (verifiedEv ? 'verified' : 'not_started') as 'verified' | 'not_started',
          score: verifiedEv ? Math.round(verifiedEv.score) : undefined,
          skillsDemonstrated: [p.skill_name || 'Python', 'Exploratory Data Analysis', 'Data Pipelines'],
          evidenceGenerated: 'GitHub Repository & Automated CI Test Suite',
          lastUpdated: verifiedEv ? 'Verified Recently' : 'Active Benchmark',
        };
      })
    : (isDemoMode ? MOCK_PROJECTS : []);

  const handleLaunchProject = (project: ProjectData) => {
    setActiveProject(project);
    setSuccessNotice(null);
  };

  const handleSubmitEvaluation = async () => {
    if (!activeProject) return;
    setIsSubmitting(true);
    setSuccessNotice(null);
    try {
      const numericId = parseInt(activeProject.id.replace('proj-', ''), 10) || 1;
      await submitProject(numericId, simScore, feedback);
      setSuccessNotice(`Project "${activeProject.title}" evaluated and verified at ${simScore}%!`);
      setTimeout(() => {
        setActiveProject(null);
        setSuccessNotice(null);
      }, 2000);
    } catch (err) {
      console.error('Failed to submit project evaluation:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell>
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 sm:p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 shrink-0">
            <FolderGit2 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Real-World Portfolio Projects</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              End-to-end data science projects evaluated by automated test suites & evidence pipelines.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded border border-emerald-200 flex items-center gap-1.5">
            <Award className="w-4 h-4 text-emerald-600" />
            Verified on Skill Passport
          </span>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
        {displayedProjects.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
            onViewDetails={() => handleLaunchProject(project)}
          />
        ))}
      </div>

      {/* Interactive Project Submission Modal */}
      {activeProject && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
          <div className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-5 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-start justify-between gap-3 border-b border-slate-100 pb-3">
              <div>
                <span className="text-[10px] font-bold text-blue-600 uppercase tracking-widest block">
                  Project Evaluation Runner
                </span>
                <h3 className="text-lg font-bold text-slate-900">{activeProject.title}</h3>
                <span className="text-xs text-slate-500 font-medium block mt-0.5">
                  Automated test evaluation harness
                </span>
              </div>
              <button
                onClick={() => setActiveProject(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              {activeProject.description}
            </p>

            <div className="bg-slate-900 text-slate-100 p-3.5 rounded-lg font-mono text-xs space-y-1.5 border border-slate-800">
              <div className="text-slate-400">// Automated CI pipeline test suite</div>
              <div className="text-emerald-400">$ pytest tests/test_project_pipeline.py --tb=short</div>
              <div className="text-slate-300">Evaluating: Data wrangling, model accuracy & code quality</div>
            </div>

            <div className="space-y-3">
              <label htmlFor="proj-score-slider" className="block text-xs font-semibold text-slate-700">
                Evaluation Test Suite Score ({simScore}%)
              </label>
              <input
                id="proj-score-slider"
                type="range"
                min="50"
                max="100"
                step="5"
                value={simScore}
                onChange={(e) => setSimScore(parseInt(e.target.value, 10))}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <div className="flex justify-between text-[11px] text-slate-400">
                <span>Passing (50%)</span>
                <span>Proficient (80%)</span>
                <span>Excellence (100%)</span>
              </div>
            </div>

            {successNotice && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-xs font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                {successNotice}
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setActiveProject(null)}
                disabled={isSubmitting}
                className="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors cursor-pointer"
              >
                Close
              </button>
              <button
                onClick={handleSubmitEvaluation}
                disabled={isSubmitting}
                className="inline-flex items-center gap-2 px-5 py-2.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-md shadow-sm transition-colors cursor-pointer disabled:opacity-60"
              >
                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                {isSubmitting ? 'Evaluating Project...' : 'Submit & Record Evidence'}
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}

