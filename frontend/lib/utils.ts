import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { SkillStatus, SkillPriority } from '../types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getStatusBadgeStyles(status: SkillStatus) {
  switch (status) {
    case 'healthy':
      return {
        bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        dot: 'bg-emerald-500',
        label: 'Healthy',
      };
    case 'developing':
      return {
        bg: 'bg-amber-50 text-amber-700 border-amber-200',
        dot: 'bg-amber-500',
        label: 'Developing',
      };
    case 'critical':
      return {
        bg: 'bg-rose-50 text-rose-700 border-rose-200',
        dot: 'bg-rose-500',
        label: 'Critical / Skill Debt',
      };
    case 'unknown':
    default:
      return {
        bg: 'bg-slate-100 text-slate-600 border-slate-200',
        dot: 'bg-slate-400',
        label: 'Not Assessed',
      };
  }
}

export function getPriorityBadgeStyles(priority: SkillPriority) {
  switch (priority) {
    case 'Critical':
      return 'bg-rose-100 text-rose-800 font-semibold border-rose-200';
    case 'High':
      return 'bg-amber-100 text-amber-800 font-medium border-amber-200';
    case 'Medium':
      return 'bg-slate-100 text-slate-700 font-medium border-slate-200';
    case 'Low':
      return 'bg-emerald-50 text-emerald-700 font-normal border-emerald-200';
  }
}
