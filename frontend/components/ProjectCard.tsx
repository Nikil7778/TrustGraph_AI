'use client';

import React from 'react';
import { ProjectData } from '../types';
import { FolderGit2, CheckCircle2, FileCode, ArrowUpRight } from 'lucide-react';

interface ProjectCardProps {
  project: ProjectData;
  onViewDetails?: () => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onViewDetails,
}) => {
  const isVerified = project.status === 'verified';
  const isInProgress = project.status === 'in_progress';

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 sm:p-5 shadow-sm hover:border-slate-300 transition-all flex flex-col justify-between min-w-0">
      <div>
        <div className="flex items-center justify-between mb-2 gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-blue-600 shrink-0" />
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Real-World Project
            </span>
          </div>

          {isVerified && (
            <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 flex items-center gap-1 shrink-0">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Score: {project.score}%
            </span>
          )}
          {isInProgress && (
            <span className="text-xs font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 shrink-0">
              In Progress
            </span>
          )}
          {project.status === 'not_started' && (
            <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 shrink-0">
              Not Started
            </span>
          )}
        </div>

        <h4 className="font-bold text-slate-900 text-base mb-1.5">{project.title}</h4>
        <p className="text-xs text-slate-600 leading-relaxed mb-3">{project.description}</p>

        <div className="mb-4">
          <span className="text-[11px] font-semibold text-slate-500 block mb-1.5">Demonstrated Skills:</span>
          <div className="flex flex-wrap gap-1.5">
            {project.skillsDemonstrated.map((skill) => (
              <span key={skill} className="text-xs font-medium bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="border-t border-slate-100 pt-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-500">
        <span className="flex items-center gap-1 truncate">
          <FileCode className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span className="truncate">{project.evidenceGenerated}</span>
        </span>

        <button
          onClick={onViewDetails}
          className="inline-flex items-center justify-center gap-1 font-semibold text-blue-600 hover:text-blue-800 transition-colors min-h-[44px] px-2 py-1"
        >
          View Evidence <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
