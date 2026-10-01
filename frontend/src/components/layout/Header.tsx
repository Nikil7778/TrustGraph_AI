import React, { useState } from 'react';
import { Bell, Search, UserCheck, LogOut, ChevronDown } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface HeaderProps {
  title?: string;
}

export const Header: React.FC<HeaderProps> = ({ title = 'Dashboard Overview' }) => {
  const { user, switchUser, logout } = useAuth();
  const [showUserDropdown, setShowUserDropdown] = useState(false);

  return (
    <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-6 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">{title}</h2>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative hidden md:block">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search Notification ID, Phone, UPI..."
            className="pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg w-64 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>

        <button className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="w-2 h-2 rounded-full bg-blue-600 absolute top-2 right-2 ring-2 ring-white"></span>
        </button>

        {/* User Identity & Quick User Switcher for Prototype Testing */}
        <div className="relative pl-3 border-l border-slate-200">
          <button
            onClick={() => setShowUserDropdown(!showUserDropdown)}
            className="flex items-center gap-2.5 p-1.5 rounded-xl hover:bg-slate-100 transition-colors"
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-black text-xs ${
              user?.role === 'ADMIN' ? 'bg-purple-100 text-purple-700 border border-purple-200' : 'bg-blue-100 text-blue-700 border border-blue-200'
            }`}>
              {user?.name ? user.name.substring(0, 2).toUpperCase() : 'UA'}
            </div>

            <div className="hidden sm:block text-left">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold text-slate-900 leading-tight">{user?.name || 'User A'}</span>
                <span className={`text-[9px] font-black px-1.5 py-0.2 rounded ${
                  user?.role === 'ADMIN' ? 'bg-purple-600 text-white' : 'bg-blue-100 text-blue-800'
                }`}>
                  {user?.role || 'USER'}
                </span>
              </div>
              <p className="text-[10px] text-slate-500 font-mono font-medium">{user?.email || 'userA@example.com'}</p>
            </div>

            <ChevronDown className="w-4 h-4 text-slate-400" />
          </button>

          {showUserDropdown && (
            <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl border border-slate-200 shadow-xl py-2 z-50 text-left">
              <div className="px-4 py-2 border-b border-slate-100">
                <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Authenticated Account</p>
                <p className="text-xs font-bold text-slate-900 mt-0.5">{user?.name}</p>
                <p className="text-[11px] text-slate-500 font-mono">{user?.email}</p>
              </div>

              <div className="px-3 py-2 border-b border-slate-100">
                <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-1 px-1">Switch Test Account</p>
                <div className="space-y-1">
                  {[
                    { name: 'User A', email: 'userA@example.com', role: 'USER' },
                    { name: 'User B', email: 'userB@example.com', role: 'USER' },
                    { name: 'System Admin', email: 'admin@example.com', role: 'ADMIN' }
                  ].map(acc => (
                    <button
                      key={acc.email}
                      onClick={async () => {
                        setShowUserDropdown(false);
                        await switchUser(acc.email);
                      }}
                      className={`w-full px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-between transition-colors ${
                        user?.email === acc.email ? 'bg-blue-50 text-blue-700 font-bold' : 'text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <UserCheck className="w-3.5 h-3.5 text-blue-600" />
                        <span>{acc.name}</span>
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">{acc.role}</span>
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={() => { setShowUserDropdown(false); logout(); }}
                className="w-full px-4 py-2 text-xs font-bold text-red-600 hover:bg-red-50 transition-colors flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                <span>Log Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
