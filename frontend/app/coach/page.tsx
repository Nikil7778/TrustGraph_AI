'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useCoach } from '../../context/CoachContext';

export default function CoachPage() {
  const router = useRouter();
  const { openCoach } = useCoach();

  useEffect(() => {
    openCoach();
    router.replace('/');
  }, [openCoach, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="text-center text-xs text-slate-500">
        Opening SkillPath Career Coach assistant...
      </div>
    </div>
  );
}
