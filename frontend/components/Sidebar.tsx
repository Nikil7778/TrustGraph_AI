'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useLearner } from '../context/LearnerContext';
import { getInitials } from '../lib/utils';
import {
  LayoutDashboard,
  Dna,
  AlertTriangle,
  GitCompare,
  MapPin,
  FileCheck2,
  Terminal,
  FolderGit2,
  Award,
  Settings,
  User,
  X,
  Compass,
  Sparkles,
  BookOpen,
} from 'lucide-react';

interface SidebarProps {
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  mobileOpen = false,
  onCloseMobile,
}) => {
  const pathname = usePathname();
  const { activeUser } = useLearner();

  const displayName = activeUser?.name || 'Learner';
  const targetRoleName = activeUser?.target_role?.name || 'No target role set';
  const initials = getInitials(activeUser?.name);

  const navSections = [
    {
      title: 'OVERVIEW',
      items: [
        { name: 'Dashboard', href: '/', icon: LayoutDashboard },
      ],
    },
    {
      title: 'LEARNING',
      items: [
        { name: 'Learning Path', href: '/learn', icon: BookOpen },
        { name: 'Skill DNA', href: '/skill-dna', icon: Dna },
        { name: 'Career Gap', href: '/career-gap', icon: GitCompare },
        { name: 'Roadmap', href: '/roadmap', icon: MapPin },
      ],
    },
    {
      title: 'PRACTICE',
      items: [
        { name: 'Assessments', href: '/assessments', icon: FileCheck2 },
        { name: 'Practice Lab', href: '/practice-lab', icon: Terminal },
        { name: 'Projects', href: '/projects', icon: FolderGit2 },
      ],
    },
    {
      title: 'PROOF',
      items: [
        { name: 'Skill Passport', href: '/skill-passport', icon: Award },
      ],
    },
    {
      title: 'ACCOUNT',
      items: [
        { name: 'Profile', href: '/profile', icon: User },
        { name: 'Settings', href: '/settings', icon: Settings },
      ],
    },
  ];

  const sidebarContent = (
    <div className="h-full flex flex-col justify-between bg-white text-slate-700 w-64 border-r border-slate-200 select-none overflow-y-auto">
      {/* Brand Header */}
      <div>
        <div className="h-16 flex items-center justify-between px-5 border-b border-slate-200 shrink-0">
          <Link href="/" className="flex items-center gap-2.5 focus:outline-none" onClick={onCloseMobile}>
            <div className="w-8 h-8 rounded-lg bg-blue-700 flex items-center justify-center text-white font-black text-sm shadow-xs">
              <Compass className="w-4.5 h-4.5 text-white" />
            </div>
            <div>
              <span className="font-bold text-slate-900 text-sm tracking-tight block leading-none">
                SkillPath AI
              </span>
            </div>
          </Link>

          {onCloseMobile && (
            <button
              onClick={onCloseMobile}
              className="lg:hidden min-h-[44px] min-w-[44px] flex items-center justify-center p-2 rounded text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition-colors"
              aria-label="Close sidebar menu"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Navigation Sections */}
        <nav className="px-3 py-3 space-y-4">
          {navSections.map((section) => (
            <div key={section.title} className="space-y-0.5">
              <div className="px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                {section.title}
              </div>
              <div className="space-y-0.5 pt-1">
                {section.items.map((item) => {
                  const isActive =
                    item.href === '/'
                      ? pathname === '/'
                      : pathname === item.href || pathname?.startsWith(item.href + '/');
                  const Icon = item.icon;

                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      onClick={onCloseMobile}
                      className={`flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                        isActive
                          ? 'bg-blue-50 text-blue-700 font-semibold'
                          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                      }`}
                    >
                      <Icon
                        className={`w-4 h-4 shrink-0 ${
                          isActive ? 'text-blue-600' : 'text-slate-400'
                        }`}
                      />
                      <span>{item.name}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </div>

      {/* Bottom Footer User Info */}
      <div className="p-3 border-t border-slate-200 shrink-0 bg-slate-50/50">
        <div className="px-2 py-1.5 flex items-center justify-between text-xs text-slate-600">
          <div className="flex items-center gap-2.5 overflow-hidden">
            {activeUser?.avatar_url ? (
              <img
                src={activeUser.avatar_url}
                alt={displayName}
                className="w-7 h-7 rounded-full border border-slate-200 object-cover shrink-0"
              />
            ) : (
              <div className="w-7 h-7 rounded-full bg-slate-800 text-white font-bold text-[11px] flex items-center justify-center shrink-0">
                {initials}
              </div>
            )}
            <div className="overflow-hidden">
              <span className="font-semibold text-slate-900 block truncate text-xs">{displayName}</span>
              <span className="text-[10px] text-slate-500 block truncate">Target: {targetRoleName}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:block fixed top-0 bottom-0 left-0 z-30 w-64">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Overlay */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex" role="dialog" aria-modal="true">
          <div
            className="fixed inset-0 bg-slate-900/70 backdrop-blur-xs transition-opacity"
            onClick={onCloseMobile}
            aria-hidden="true"
          />
          <div className="relative z-10 w-64 max-w-[80vw] h-full shadow-2xl">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
};
