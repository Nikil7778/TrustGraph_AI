import React from 'react';
import { NavLink } from 'react-router-dom';
import { ShieldCheck, PlusCircle, History, ShieldAlert, Settings, Users, Files, Activity, Fingerprint, Dna, BarChart3, UserRound } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { usePipeline } from '../../context/PipelineContext';

export const Sidebar: React.FC = () => {
  const { resetAnalysis } = usePipeline();
  const { user } = useAuth();
  const isAdmin = user?.role === 'ADMIN';

  const navItems = [
    { label: 'Dashboard', path: isAdmin ? '/admin/dashboard' : '/dashboard', icon: ShieldCheck },
    { label: 'New Analysis', path: '/new-analysis', icon: PlusCircle },
    { label: 'History', path: '/history', icon: History },
    { label: 'Profile', path: '/profile', icon: UserRound },
    { label: 'Threat Intelligence', path: '/threat-intel', icon: ShieldAlert },
    ...(isAdmin ? [
      { label: 'Users', path: '/admin/users', icon: Users },
      { label: 'All Analyses', path: '/admin/analyses', icon: Files },
      { label: 'Recruitment DNA', path: '/admin/recruitment-dna', icon: Dna },
      { label: 'Suspicious Fingerprints', path: '/admin/fingerprints', icon: Fingerprint },
      { label: 'Risk Statistics', path: '/admin/risk-statistics', icon: BarChart3 },
      { label: 'System Activity', path: '/admin/system-activity', icon: Activity },
      { label: 'Settings', path: '/settings', icon: Settings }
    ] : []),
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between h-screen sticky top-0 z-30 select-none">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-100 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-200">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-extrabold text-slate-900 text-lg leading-tight tracking-tight">JobGuard</h1>
            <p className="text-xs text-blue-600 font-semibold tracking-wide uppercase">Detect Fake Recruitments</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => {
                  if (item.path === '/new-analysis') {
                    resetAnalysis();
                  }
                }}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
                    isActive
                      ? 'bg-blue-50 text-blue-600 font-semibold shadow-sm border border-blue-100/60'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Branding */}
      <div className="p-5 border-t border-slate-100">
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/60 text-center">
          <p className="text-xs font-bold text-slate-800">TRUST AI Engine v2.4</p>
          <p className="text-[11px] text-slate-500 mt-0.5 font-medium">Safer Jobs. Stronger Futures.</p>
        </div>
      </div>
    </aside>
  );
};
