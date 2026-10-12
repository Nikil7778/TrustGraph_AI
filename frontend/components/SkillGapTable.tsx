'use client';

import React from 'react';
import { SkillGapItem } from '../types';
import { SkillStatusBadge } from './SkillStatusBadge';
import { getPriorityBadgeStyles } from '../lib/utils';
import { ArrowUpRight, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface SkillGapTableProps {
  skills: SkillGapItem[];
  onSelectSkill?: (skill: SkillGapItem) => void;
  compact?: boolean;
}

export const SkillGapTable: React.FC<SkillGapTableProps> = ({
  skills,
  onSelectSkill,
  compact = false,
}) => {
  return (
    <div className="w-full bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
      {/* 1. Desktop & Tablet View (Heatmap Table) */}
      <div className="hidden md:block w-full overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-700 min-w-[600px]">
          <thead className="bg-slate-50 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200 tracking-wider">
            <tr>
              <th scope="col" className="px-4 py-3">Skill</th>
              {!compact && <th scope="col" className="px-4 py-3">Category</th>}
              <th scope="col" className="px-4 py-3 text-right">Current</th>
              <th scope="col" className="px-4 py-3 text-right">Required</th>
              <th scope="col" className="px-4 py-3 text-right">Gap</th>
              <th scope="col" className="px-4 py-3 text-center">Status</th>
              <th scope="col" className="px-4 py-3 text-center">Priority</th>
              <th scope="col" className="px-4 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-normal">
            {skills.map((item) => {
              const isDeficit = item.gap < 0;
              const gapFormatted = isDeficit ? `${item.gap}%` : `+${item.gap}%`;

              let gapColor = 'text-emerald-700 font-semibold bg-emerald-50';
              if (item.status === 'critical') {
                gapColor = 'text-rose-700 font-semibold bg-rose-50';
              } else if (item.status === 'developing') {
                gapColor = 'text-amber-700 font-semibold bg-amber-50';
              }

              return (
                <tr
                  key={item.id}
                  onClick={() => onSelectSkill && onSelectSkill(item)}
                  className={`hover:bg-slate-50/80 transition-colors cursor-pointer ${
                    item.status === 'critical' ? 'bg-rose-50/20' : ''
                  }`}
                >
                  <td className="px-4 py-3 font-semibold text-slate-900 flex items-center gap-2">
                    {item.status === 'critical' && (
                      <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                    )}
                    {item.status === 'healthy' && (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    )}
                    {item.name}
                  </td>
                  {!compact && (
                    <td className="px-4 py-3 text-xs text-slate-500">{item.category}</td>
                  )}
                  <td className="px-4 py-3 text-right font-medium text-slate-900">{item.currentLevel}%</td>
                  <td className="px-4 py-3 text-right text-slate-500">{item.requiredLevel}%</td>
                  <td className="px-4 py-3 text-right">
                    <span className={`inline-block px-2 py-0.5 text-xs rounded border border-transparent ${gapColor}`}>
                      {gapFormatted}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <SkillStatusBadge status={item.status} />
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-block px-2 py-0.5 text-xs rounded border ${getPriorityBadgeStyles(item.priority)}`}>
                      {item.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onSelectSkill) onSelectSkill(item);
                      }}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors min-h-[36px] px-2 rounded"
                    >
                      View <ArrowUpRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* 2. Mobile Responsive Skill Cards View (320px – 767px) */}
      <div className="block md:hidden divide-y divide-slate-100">
        {skills.map((item) => {
          const isDeficit = item.gap < 0;
          const gapFormatted = isDeficit ? `${item.gap}%` : `+${item.gap}%`;

          let gapColor = 'text-emerald-700 bg-emerald-50 border-emerald-200';
          if (item.status === 'critical') {
            gapColor = 'text-rose-700 bg-rose-50 border-rose-200';
          } else if (item.status === 'developing') {
            gapColor = 'text-amber-700 bg-amber-50 border-amber-200';
          }

          return (
            <div
              key={item.id}
              onClick={() => onSelectSkill && onSelectSkill(item)}
              className={`p-4 space-y-2.5 hover:bg-slate-50 transition-colors cursor-pointer ${
                item.status === 'critical' ? 'bg-rose-50/20' : ''
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-1.5 font-bold text-slate-900 text-sm truncate">
                  {item.status === 'critical' && (
                    <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                  )}
                  {item.status === 'healthy' && (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  )}
                  <span className="truncate">{item.name}</span>
                </div>
                <SkillStatusBadge status={item.status} />
              </div>

              {/* Skill Capability Progress Gauge */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-600">Demonstrated: <strong className="text-slate-900">{item.currentLevel}%</strong></span>
                  <span className="text-slate-500">Target: {item.requiredLevel}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden relative">
                  <div
                    className={`h-full rounded-full ${
                      item.status === 'healthy'
                        ? 'bg-emerald-500'
                        : item.status === 'critical'
                        ? 'bg-rose-500'
                        : 'bg-amber-500'
                    }`}
                    style={{ width: `${item.currentLevel}%` }}
                  />
                </div>
              </div>

              {/* Bottom Card Footer */}
              <div className="flex items-center justify-between pt-1 text-xs">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 text-xs font-bold rounded border ${gapColor}`}>
                    Gap: {gapFormatted}
                  </span>
                  <span className={`px-2 py-0.5 text-[11px] rounded border ${getPriorityBadgeStyles(item.priority)}`}>
                    {item.priority}
                  </span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onSelectSkill) onSelectSkill(item);
                  }}
                  className="inline-flex items-center gap-1 font-semibold text-blue-600 min-h-[44px] px-2 py-1"
                >
                  Analyze <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
