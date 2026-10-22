'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, Bell, ChevronDown, User, Settings, LogOut } from 'lucide-react';
import { useLearner } from '../context/LearnerContext';
import { getInitials } from '../lib/utils';

interface TopBarProps {
  onOpenMobileMenu?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({ onOpenMobileMenu }) => {
  const pathname = usePathname();
  const { activeUserId, activeUser, logout } = useLearner();
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close profile dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setProfileMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Display user information — always derived from the authenticated activeUser
  const displayName = activeUser?.name || (activeUser?.email ? activeUser.email.split('@')[0] : `Learner #${activeUserId}`);
  const initials = getInitials(activeUser?.name || displayName);

  // Breadcrumb logic matching Stitch reference
  const getBreadcrumb = () => {
    if (pathname === '/') return 'Target Role • ' + (activeUser?.target_role?.name || 'Dashboard');
    if (pathname?.startsWith('/skill-debt')) return 'SkillPath AI / Skill Debt';
    if (pathname?.startsWith('/skill-dna')) return 'SkillPath AI / Competence Matrix';
    if (pathname?.startsWith('/roadmap')) return 'SkillPath AI / Analytics Console';
    if (pathname?.startsWith('/career-gap')) return 'SkillPath AI / Career Gap';
    if (pathname?.startsWith('/assessments')) return 'SkillPath AI / Assessments';
    if (pathname?.startsWith('/practice-lab')) return 'SkillPath AI / Practice Lab';
    if (pathname?.startsWith('/projects')) return 'SkillPath AI / Projects';
    if (pathname?.startsWith('/skill-passport')) return 'SkillPath AI / Skill Passport';
    if (pathname?.startsWith('/coach')) return 'SkillPath AI / Career Coach';
    if (pathname?.startsWith('/profile')) return 'SkillPath AI / Profile';
    if (pathname?.startsWith('/settings')) return 'SkillPath AI / Settings';
    return 'SkillPath AI / Overview';
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 fixed top-0 right-0 left-0 lg:left-64 z-20 px-3 sm:px-6 lg:px-8 flex items-center justify-between shadow-2xs">
      <div className="flex items-center gap-3 min-w-0">
        {/* Mobile menu trigger */}
        <button
          onClick={onOpenMobileMenu}
          className="lg:hidden min-h-[44px] min-w-[44px] flex items-center justify-center p-2 text-slate-600 hover:text-slate-900 rounded-md hover:bg-slate-100 transition-colors focus:ring-2 focus:ring-blue-500"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Breadcrumb Context from Stitch Reference */}
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 truncate">
          <span className="text-slate-800" suppressHydrationWarning>{getBreadcrumb()}</span>
        </div>
      </div>

      {/* Right Action Icons & Profile */}
      <div className="flex items-center gap-2 sm:gap-3 shrink-0">

        {/* Notifications Button */}
        <button
          className="relative min-h-[44px] min-w-[44px] flex items-center justify-center p-2 text-slate-500 hover:text-slate-800 rounded-full hover:bg-slate-100 transition-colors focus:ring-2 focus:ring-blue-500"
          aria-label="View notifications"
        >
          <Bell className="w-4.5 h-4.5" />
          <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white" />
        </button>

        <div className="h-5 w-px bg-slate-200" />

        {/* Profile Avatar Dropdown Trigger */}
        <div className="relative" ref={menuRef}>
          <button
            id="user-profile-menu-button"
            onClick={() => setProfileMenuOpen(!profileMenuOpen)}
            className="flex items-center gap-2 p-1.5 rounded-md hover:bg-slate-50 transition-colors focus:ring-2 focus:ring-blue-500 min-h-[44px] cursor-pointer"
            aria-expanded={profileMenuOpen}
            aria-haspopup="true"
          >
            {activeUser?.avatar_url ? (
              <img
                src={activeUser.avatar_url}
                alt={displayName}
                className="w-8 h-8 rounded-full border border-slate-200 object-cover shadow-2xs shrink-0"
              />
            ) : (
              <div className="w-8 h-8 rounded-full bg-slate-900 text-white font-bold text-xs flex items-center justify-center border border-slate-700 shadow-2xs shrink-0">
                {initials}
              </div>
            )}
            <div className="hidden xl:block text-left">
              <span className="text-xs font-bold text-slate-900 block leading-tight truncate max-w-[120px]">
                {displayName}
              </span>
              <span className="text-[10px] text-slate-500 block leading-tight">
                {activeUser?.target_role?.name || 'Active Learner'}
              </span>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden sm:block" />
          </button>

          {profileMenuOpen && (
            <div
              id="user-profile-dropdown"
              className="absolute right-0 mt-1.5 w-48 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-50 text-xs font-medium text-slate-700"
            >
              <div className="px-3.5 py-2 border-b border-slate-100 xl:hidden">
                <span className="font-bold text-slate-900 block truncate">{displayName}</span>
                <span className="text-[10px] text-slate-500 block truncate">{activeUser?.email || ''}</span>
              </div>
              <Link
                href="/profile"
                onClick={() => setProfileMenuOpen(false)}
                className="flex items-center gap-2 px-3.5 py-2 hover:bg-slate-50 hover:text-slate-900 transition-colors"
              >
                <User className="w-4 h-4 text-slate-500" />
                <span>Profile</span>
              </Link>
              <Link
                href="/settings"
                onClick={() => setProfileMenuOpen(false)}
                className="flex items-center gap-2 px-3.5 py-2 hover:bg-slate-50 hover:text-slate-900 transition-colors"
              >
                <Settings className="w-4 h-4 text-slate-500" />
                <span>Settings</span>
              </Link>
              <div className="my-1 border-t border-slate-100" />
              <button
                id="avatar-logout-button"
                type="button"
                onClick={async () => {
                  setProfileMenuOpen(false);
                  await logout();
                }}
                className="w-full flex items-center gap-2 px-3.5 py-2 text-rose-600 hover:bg-rose-50 hover:text-rose-700 transition-colors text-left font-semibold cursor-pointer"
              >
                <LogOut className="w-4 h-4 text-rose-500" />
                <span>Log out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
