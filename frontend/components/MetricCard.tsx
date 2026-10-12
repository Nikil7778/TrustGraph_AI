'use client';

import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  trend?: string;
  icon?: LucideIcon;
  variant?: 'default' | 'accent' | 'warning' | 'alert';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtext,
  trend,
  icon: Icon,
  variant = 'default',
}) => {
  let borderColor = 'border-slate-200';
  let accentBar = 'bg-slate-300';

  if (variant === 'accent') {
    borderColor = 'border-slate-200';
    accentBar = 'bg-blue-600';
  } else if (variant === 'warning') {
    borderColor = 'border-amber-200 bg-amber-50/30';
    accentBar = 'bg-amber-500';
  } else if (variant === 'alert') {
    borderColor = 'border-rose-200 bg-rose-50/30';
    accentBar = 'bg-rose-500';
  }

  return (
    <div className={`p-4 bg-white border ${borderColor} rounded-lg shadow-sm relative overflow-hidden flex flex-col justify-between`}>
      <div className={`absolute top-0 left-0 bottom-0 w-1 ${accentBar}`} />
      
      <div className="pl-2 flex items-start justify-between">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</span>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900 tracking-tight">{value}</span>
            {trend && (
              <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                {trend}
              </span>
            )}
          </div>
        </div>
        {Icon && <Icon className="w-5 h-5 text-slate-400 stroke-[1.75]" />}
      </div>

      {subtext && (
        <div className="pl-2 mt-3 pt-2 border-t border-slate-100 text-xs text-slate-500">
          {subtext}
        </div>
      )}
    </div>
  );
};
