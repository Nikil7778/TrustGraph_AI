'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useCoach } from '../../context/CoachContext';
import { useLearner } from '../../context/LearnerContext';
import { Loader2 } from 'lucide-react';

export default function CoachPage() {
  const router = useRouter();
  const { openCoach } = useCoach();
  const { isAuthenticated, isAuthLoading } = useLearner();

  useEffect(() => {
    if (!isAuthLoading) {
      if (!isAuthenticated) {
        router.replace('/login');
      } else {
        openCoach();
        router.replace('/');
      }
    }
  }, [isAuthenticated, isAuthLoading, openCoach, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
        <span>Opening SkillPath Career Coach assistant...</span>
      </div>
    </div>
  );
}
