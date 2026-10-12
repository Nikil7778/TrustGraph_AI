'use client';

import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { SkillProgressData } from '../types';

interface SkillProgressChartProps {
  data: SkillProgressData[];
  title?: string;
}

export const SkillProgressChart: React.FC<SkillProgressChartProps> = ({
  data,
  title = 'Demonstrated Skill Progression',
}) => {
  const weeks = data[0]?.history.map((h) => h.week) || [];
  const maxPoints = Math.max(...data.map((d) => d.history.length), 0);

  const chartData = weeks.map((week, index) => {
    const entry: Record<string, string | number> = { week };
    data.forEach((skillData) => {
      if (index < skillData.history.length) {
        entry[skillData.skillName] = skillData.history[index]?.score ?? 0;
      }
    });
    return entry;
  });

  const colors = ['#2563eb', '#d97706', '#059669', '#dc2626'];

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 sm:p-5 shadow-sm min-w-0">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">{title}</h3>
          <p className="text-xs text-slate-500">
            Historical proof score progression across reassessments & practical labs
          </p>
        </div>
        <span className="text-[11px] font-medium bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200 self-start sm:self-auto">
          {maxPoints <= 1 ? 'Single Evidence Baseline' : 'Recorded Evidence Trend'}
        </span>
      </div>

      {maxPoints <= 1 && (
        <div className="mb-3 p-2.5 bg-blue-50/70 border border-blue-200 rounded text-[11px] text-blue-800">
          Single baseline evidence recorded. Take reassessments or practical labs to build historical progress trend lines.
        </div>
      )}

      <div className="h-60 sm:h-64 w-full min-w-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="week" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} tickLine={false} unit="%" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                borderColor: '#cbd5e1',
                borderRadius: '6px',
                fontSize: '12px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
              }}
              formatter={(val: number) => [`${val}%`, 'Mastery Score']}
            />
            <Legend
              wrapperStyle={{ paddingTop: '10px', fontSize: '11px' }}
              iconType="circle"
            />
            {data.map((skill, index) => (
              <Line
                key={skill.skillName}
                type="monotone"
                dataKey={skill.skillName}
                stroke={colors[index % colors.length]}
                strokeWidth={2.5}
                dot={{ r: 4, strokeWidth: 2, fill: '#ffffff' }}
                activeDot={{ r: 6 }}
                connectNulls={true}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
