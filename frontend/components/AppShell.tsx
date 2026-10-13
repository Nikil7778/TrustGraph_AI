'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { FloatingCareerCoach } from './FloatingCareerCoach';
import { useLearner } from '../context/LearnerContext';
import { Loader2 } from 'lucide-react';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const router = useRouter();
  const { isAuthenticated, isAuthLoading } = useLearner();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (!isAuthLoading && !isAuthenticated) {
      router.replace('/login');
    }
  }, [isAuthLoading, isAuthenticated, router]);

  // Prevent flash of protected dashboard/routes while session verification is resolving
  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="flex items-center gap-3 text-slate-600 text-sm font-semibold">
          <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
          <span>Verifying learner session...</span>
        </div>
      </div>
    );
  }

  // If not authenticated, render nothing while route redirect executes
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-50/70 font-sans text-slate-900 antialiased flex flex-col relative">
      {/* Sidebar */}
      <Sidebar
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />

      {/* TopBar */}
      <TopBar onOpenMobileMenu={() => setMobileOpen(true)} />

      {/* Main Content Viewport */}
      <main className="flex-1 lg:pl-64 pt-16 min-w-0 transition-all">
        <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
          {children}
        </div>
      </main>

      {/* Global Floating Career Coach */}
      <React.Suspense fallback={null}>
        <FloatingCareerCoach />
      </React.Suspense>
    </div>
  );
};
