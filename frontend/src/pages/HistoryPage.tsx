import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { Search, FileText, ArrowRight, Trash2, ChevronLeft, ChevronRight, Lock, UserCheck, Shield } from 'lucide-react';
import { fetchUserHistory, fetchHistoryById, deleteHistoryRecord, fetchAdminHistory, fetchTestAccounts } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { usePipeline } from '../context/PipelineContext';
import type { AnalysisRecordItem } from '../types';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { setActiveResult, setPipelineData, setActiveStep } = usePipeline();

  const [records, setRecords] = useState<AnalysisRecordItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [limit] = useState<number>(10);
  const [filter, setFilter] = useState<string>('ALL');
  const [search, setSearch] = useState<string>('');

  // Admin view states
  const [isAdminMode, setIsAdminMode] = useState<boolean>(false);
  const [adminUsers, setAdminUsers] = useState<any[]>([]);
  const [filterUserId, setFilterUserId] = useState<string>('');

  // Error & loading states
  const [forbiddenError, setForbiddenError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (isAdminMode && user?.role === 'ADMIN') {
        const res = await fetchAdminHistory({
          page,
          limit,
          filterUserId: filterUserId || undefined
        });
        setRecords(res.records || []);
        setTotal(res.total || 0);
        setTotalPages(res.totalPages || 1);
      } else {
        const res = await fetchUserHistory({
          page,
          limit,
          search: search || undefined,
          riskLevel: filter !== 'ALL' ? filter : undefined
        });
        setRecords(res.records || []);
        setTotal(res.total || 0);
        setTotalPages(res.totalPages || 1);
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  }, [isAdminMode, user, page, limit, search, filter, filterUserId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (user?.role === 'ADMIN') {
      fetchTestAccounts().then(data => {
        setAdminUsers(data.users || []);
      }).catch(err => console.error('Failed to fetch test accounts:', err));
    }
  }, [user]);

  const handleInspect = async (id: string) => {
    setLoading(true);
    setForbiddenError(null);
    try {
      const res = await fetchHistoryById(id);
      if (res && res.dashboard) {
        setActiveResult(res.dashboard);
        setPipelineData(res.pipelineSteps || {});
        setActiveStep(9);
        navigate('/new-analysis');
      } else {
        navigate('/new-analysis');
      }
    } catch (err: any) {
      console.error('Inspect error:', err);
      if (err.response?.status === 403 || err.status === 403) {
        setForbiddenError("You don't have permission to access this investigation. (403 Forbidden)");
      } else {
        setForbiddenError('Unable to access requested analysis record.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, title: string) => {
    if (!window.confirm(`Are you sure you want to delete investigation "${title}"?`)) return;
    try {
      await deleteHistoryRecord(id);
      loadData();
    } catch (err: any) {
      if (err.response?.status === 403) {
        setForbiddenError("403 Forbidden: You cannot delete another user's history.");
      } else {
        alert('Failed to delete record.');
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/50 pb-12">
      <Header title={isAdminMode ? 'System Admin History' : 'My Investigations'} />

      <main className="max-w-6xl mx-auto px-6 pt-8 space-y-6">
        {/* 403 Forbidden Modal Alert */}
        {forbiddenError && (
          <div className="p-4 rounded-2xl bg-red-50 border-2 border-red-200 flex items-center justify-between gap-4 text-red-900 shadow-md">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-red-100 text-red-600 shrink-0">
                <Lock className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-extrabold text-sm text-red-900">Access Denied (403 Forbidden)</h4>
                <p className="text-xs text-red-700 font-medium">{forbiddenError}</p>
              </div>
            </div>
            <button
              onClick={() => setForbiddenError(null)}
              className="px-3 py-1.5 rounded-xl bg-red-600 text-white font-bold text-xs hover:bg-red-700 transition-colors shrink-0"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Page Title Header & Admin Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-extrabold text-slate-900">
                {isAdminMode ? 'System-Wide Case History' : 'My Investigations'}
              </h2>
              {user?.role === 'ADMIN' && (
                <span className="px-2.5 py-1 rounded-md bg-purple-100 text-purple-700 font-bold text-[10px] uppercase tracking-wider flex items-center gap-1">
                  <Shield className="w-3 h-3" />
                  <span>Admin Mode</span>
                </span>
              )}
            </div>
            <p className="text-sm text-slate-500 font-medium mt-1">
              {isAdminMode
                ? 'Full cross-user database inspection and audit trail.'
                : `Private investigation records for ${user?.name || 'Authenticated User'}. strictly filtered by your session.`}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Admin toggle if authenticated user is ADMIN */}
            {user?.role === 'ADMIN' && (
              <button
                onClick={() => {
                  setIsAdminMode(!isAdminMode);
                  setPage(1);
                }}
                className={`px-3.5 py-2 rounded-xl font-bold text-xs transition-all flex items-center gap-2 border shadow-sm ${
                  isAdminMode
                    ? 'bg-purple-600 text-white border-purple-600 hover:bg-purple-700'
                    : 'bg-white text-purple-700 border-purple-200 hover:bg-purple-50'
                }`}
              >
                <UserCheck className="w-4 h-4" />
                <span>{isAdminMode ? 'Switch to My Personal View' : 'Switch to Admin Database View'}</span>
              </button>
            )}

            {!isAdminMode && (
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={search}
                  onChange={e => {
                    setSearch(e.target.value);
                    setPage(1);
                  }}
                  placeholder="Search my cases..."
                  className="pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 rounded-xl w-48 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
            )}

            {/* Admin User Filter */}
            {isAdminMode && (
              <select
                value={filterUserId}
                onChange={e => {
                  setFilterUserId(e.target.value);
                  setPage(1);
                }}
                className="px-3 py-2 text-xs bg-white border border-purple-200 rounded-xl font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
              >
                <option value="">All Users Records</option>
                {adminUsers.map(u => (
                  <option key={u.id} value={u.id}>
                    {u.name} ({u.role})
                  </option>
                ))}
              </select>
            )}

            {/* Risk Filters for normal mode */}
            {!isAdminMode && (
              <div className="flex items-center gap-1 bg-white p-1 rounded-xl border border-slate-200 text-xs font-bold">
                {[
                  { label: 'ALL', val: 'ALL' },
                  { label: 'GENUINE', val: 'VERIFIED_GENUINE' },
                  { label: 'SCAM', val: 'CRITICAL_SCAM' }
                ].map(f => (
                  <button
                    key={f.val}
                    onClick={() => {
                      setFilter(f.val);
                      setPage(1);
                    }}
                    className={`px-3 py-1.5 rounded-lg transition-colors ${
                      filter === f.val ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Record Table */}
        <div className="bg-white rounded-3xl border border-slate-200/80 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-4 px-6">Recruitment Notice Title</th>
                  {isAdminMode && <th className="py-4 px-6">Owner User</th>}
                  <th className="py-4 px-6">Input Type</th>
                  <th className="py-4 px-6">Trust Score</th>
                  <th className="py-4 px-6">Classification</th>
                  <th className="py-4 px-6">Scan Date</th>
                  <th className="py-4 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {loading ? (
                  <tr>
                    <td colSpan={isAdminMode ? 7 : 6} className="py-12 text-center text-slate-400 font-medium">
                      Loading investigation history...
                    </td>
                  </tr>
                ) : records.length === 0 ? (
                  <tr>
                    <td colSpan={isAdminMode ? 7 : 6} className="py-12 text-center text-slate-400 font-medium">
                      No investigation records found for this view.
                    </td>
                  </tr>
                ) : (
                  records.map(r => (
                    <tr key={r.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-4 px-6 font-bold text-slate-900 flex items-center gap-3">
                        <FileText className="w-4 h-4 text-blue-600 shrink-0" />
                        <div>
                          <span className="block truncate max-w-xs">{r.title}</span>
                          {r.organization && (
                            <span className="text-[11px] font-normal text-slate-400 block">{r.organization}</span>
                          )}
                        </div>
                      </td>
                      {isAdminMode && (
                        <td className="py-4 px-6 text-xs text-purple-700 font-bold">
                          {(r as any).user?.name || (r as any).userId || 'Unknown'}
                        </td>
                      )}
                      <td className="py-4 px-6 font-mono text-xs text-slate-600">{r.inputType}</td>
                      <td className="py-4 px-6 font-black font-mono text-slate-900">{r.trustScore} / 100</td>
                      <td className="py-4 px-6">
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${
                            r.riskLevel === 'VERIFIED_GENUINE'
                              ? 'bg-emerald-100 text-emerald-800'
                              : r.riskLevel === 'MEDIUM_RISK'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {r.riskLevel?.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-xs text-slate-400 font-medium">
                        {new Date(r.createdAt).toLocaleDateString()} {new Date(r.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </td>
                      <td className="py-4 px-6 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleInspect(r.id)}
                            className="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-600 font-bold text-xs hover:bg-blue-100 transition-colors inline-flex items-center gap-1"
                          >
                            <span>Inspect</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                          {!isAdminMode && (
                            <button
                              onClick={() => handleDelete(r.id, r.title)}
                              title="Delete history item"
                              className="p-1.5 rounded-lg bg-slate-100 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 font-medium">
            <div>
              Showing <span className="font-bold text-slate-800">{records.length}</span> of{' '}
              <span className="font-bold text-slate-800">{total}</span> total records
            </div>

            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1 || loading}
                onClick={() => setPage(prev => Math.max(1, prev - 1))}
                className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 font-bold text-slate-700 disabled:opacity-50 hover:bg-slate-100 transition-colors flex items-center gap-1"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Prev</span>
              </button>
              <span className="font-mono text-slate-700 font-bold">
                Page {page} of {totalPages}
              </span>
              <button
                disabled={page >= totalPages || loading}
                onClick={() => setPage(prev => Math.min(totalPages, prev + 1))}
                className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 font-bold text-slate-700 disabled:opacity-50 hover:bg-slate-100 transition-colors flex items-center gap-1"
              >
                <span>Next</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

