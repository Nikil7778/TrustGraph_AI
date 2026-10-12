'use client';

import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { FloatingCareerCoach } from './FloatingCareerCoach';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

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
