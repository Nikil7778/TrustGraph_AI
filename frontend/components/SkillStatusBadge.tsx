'use client';

import React from 'react';
import { SkillStatus } from '../types';
import { getStatusBadgeStyles } from '../lib/utils';

interface SkillStatusBadgeProps {
  status: SkillStatus;
  customLabel?: string;
  className?: string;
}

export const SkillStatusBadge: React.FC<SkillStatusBadgeProps> = ({
  status,
  customLabel,
  className = '',
}) => {
  const styles = getStatusBadgeStyles(status);

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium border rounded-md ${styles.bg} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${styles.dot}`} />
      {customLabel || styles.label}
    </span>
  );
};
