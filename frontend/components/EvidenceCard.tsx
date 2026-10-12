'use client';

import React from 'react';
import { ShieldCheck, FileCode, CheckCircle2, Calendar } from 'lucide-react';

interface EvidenceCardProps {
  skillName: string;
  evidenceType: string;
  demonstratedScore: number;
  verifiedDate: string;
  source: string;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({
  skillName,
  evidenceType,
  demonstratedScore,
  verifiedDate,
  source,
}) => {
  return (
    <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between gap-3 text-xs">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-emerald-100 border border-emerald-300 flex items-center justify-center shrink-0">
          <ShieldCheck className="w-4 h-4 text-emerald-700" />
        </div>
        <div>
          <span className="font-bold text-slate-900 block text-sm">{skillName}</span>
          <span className="text-slate-500 font-medium flex items-center gap-1.5 mt-0.5">
            <FileCode className="w-3 h-3 text-slate-400" />
            {evidenceType} • {source}
          </span>
        </div>
      </div>

      <div className="text-right shrink-0">
        <span className="text-xs font-bold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded border border-emerald-200 block mb-1">
          {demonstratedScore}% Mastery
        </span>
        <span className="text-slate-400 text-[11px] flex items-center justify-end gap-1">
          <Calendar className="w-3 h-3 text-slate-400" />
          Verified {verifiedDate}
        </span>
      </div>
    </div>
  );
};
