import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PlusCircle, History, Sparkles, ArrowRight, FolderOpen } from 'lucide-react';
import { Header } from '../components/layout/Header';
import { useAuth } from '../context/AuthContext';
import { fetchUserHistory } from '../services/api';

export const Home: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [recentAnalyses, setRecentAnalyses] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadRecent6 = async () => {
      setIsLoading(true);
      try {
        const data = await fetchUserHistory({ limit: 6, page: 1 });
        setRecentAnalyses(data.records || []);
      } catch (err) {
        console.warn('Failed to load recent investigations:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      loadRecent6();
    }
  }, [user]);

  const getRiskBadge = (score: number, riskLevel: string) => {
    if (riskLevel === 'VERIFIED_GENUINE' || score >= 80) return { label: 'VERIFIED GENUINE', color: 'bg-emerald-100 text-emerald-800 border-emerald-200' };
    if (riskLevel === 'LOW_RISK' || score >= 60) return { label: 'LOW RISK', color: 'bg-blue-100 text-blue-800 border-blue-200' };
    if (riskLevel === 'MEDIUM_RISK' || score >= 40) return { label: 'MEDIUM RISK', color: 'bg-amber-100 text-amber-800 border-amber-200' };
    if (riskLevel === 'HIGH_RISK' || score >= 20) return { label: 'HIGH RISK', color: 'bg-orange-100 text-orange-800 border-orange-200' };
    return { label: 'CRITICAL SCAM', color: 'bg-red-100 text-red-800 border-red-200' };
  };

  return (
    <div className="min-h-screen bg-slate-50/50 pb-12">
      <Header title="JobGuard Dashboard" />

      <main className="max-w-6xl mx-auto px-6 pt-8 space-y-8">
        <div className="bg-gradient-to-r from-slate-900 via-navy-900 to-slate-800 rounded-3xl p-8 sm:p-12 text-white shadow-xl relative overflow-hidden">
          <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-blue-600/10 backdrop-blur-3xl pointer-events-none" />

          <div className="max-w-2xl relative z-10 space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Evidence-Based Fraud Detection Engine</span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
              Verify a Recruitment Offer Before You Trust It
            </h1>

            <p className="text-slate-300 text-sm sm:text-base leading-relaxed font-normal">
              Signed in as <span className="font-bold text-white">{user?.username || 'User'}</span>. Analyze job offers with multi-factor verification, canonical DNA hashing, and risk reasoning.
            </p>

            <div className="pt-4 flex flex-wrap items-center gap-4">
              <button
                onClick={() => navigate('/new-analysis')}
                className="px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-lg shadow-blue-600/30 transition-all flex items-center gap-2"
              >
                <PlusCircle className="w-5 h-5" />
                <span>Check Recruitment Offer</span>
              </button>

              <button
                onClick={() => navigate('/history')}
                className="px-6 py-3.5 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/15 font-semibold text-sm transition-all flex items-center gap-2"
              >
                <History className="w-5 h-5" />
                <span>View Full History</span>
              </button>
            </div>
          </div>
        </div>

        {/* RECENT INVESTIGATIONS (EXACTLY MAXIMUM 6 ITEMS) */}
        <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-black text-slate-900 uppercase tracking-tight">RECENT INVESTIGATIONS</h3>
                <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700">
                  {recentAnalyses.length} / Max 6
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium mt-0.5">
                Showing your latest 6 personal recruitment analysis records ({user?.username})
              </p>
            </div>

            <button
              onClick={() => navigate('/history')}
              className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-50 hover:bg-blue-100 transition-colors"
            >
              <span>VIEW ALL HISTORY</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {isLoading ? (
            <p className="text-xs text-slate-400 py-6 text-center">Loading your recent investigations...</p>
          ) : recentAnalyses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recentAnalyses.slice(0, 6).map((item, idx) => {
                const badge = getRiskBadge(item.trustScore, item.riskLevel);
                return (
                  <div
                    key={item.id || idx}
                    onClick={() => navigate('/history')}
                    className="p-4 rounded-2xl border border-slate-200/70 bg-slate-50/50 hover:bg-slate-50 hover:border-blue-300 transition-all cursor-pointer space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono font-bold text-slate-400 uppercase">
                        #{String(idx + 1).padStart(2, '0')} · {new Date(item.createdAt).toLocaleDateString()}
                      </span>
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border ${badge.color}`}>
                        {badge.label}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-sm font-extrabold text-slate-900 truncate">{item.title}</h4>
                      <p className="text-xs text-slate-500 font-medium mt-0.5">{item.organization || 'Unspecified Entity'}</p>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-200/50 text-xs">
                      <span className="font-mono text-slate-500">Input: {item.inputType}</span>
                      <span className="font-extrabold text-slate-900">Score: {item.trustScore}/100</span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-8 text-center space-y-3 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
              <FolderOpen className="w-8 h-8 text-slate-400 mx-auto" />
              <p className="text-xs font-bold text-slate-700">No personal investigations yet for {user?.username}</p>
              <button
                onClick={() => navigate('/new-analysis')}
                className="px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold shadow-sm hover:bg-blue-500 transition-colors"
              >
                + Run First Recruitment Analysis
              </button>
            </div>
          )}
        </div>

      </main>
    </div>
  );
};

