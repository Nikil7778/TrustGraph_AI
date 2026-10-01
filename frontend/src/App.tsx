import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useParams } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { AuthProvider, useAuth } from './context/AuthContext';
import { PipelineProvider } from './context/PipelineContext';
import { AuthPage } from './pages/AuthPage';
import { Home } from './pages/Home';
import { NewAnalysis } from './pages/NewAnalysis';
import { HistoryPage } from './pages/HistoryPage';
import { ThreatIntelligencePage } from './pages/ThreatIntelligencePage';
import { SettingsPage } from './pages/SettingsPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { fetchHistoryById } from './services/api';
import { usePipeline } from './context/PipelineContext';

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <PipelineProvider>
          <AppRoutes />
        </PipelineProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

function AppRoutes() {
  const { user, isLoading } = useAuth();

  if (isLoading) return <div className="grid min-h-screen place-items-center text-sm font-semibold text-slate-500">Restoring secure session...</div>;
  if (!user) {
    return <Routes><Route path="/login" element={<AuthPage />} /><Route path="*" element={<Navigate to="/login" replace />} /></Routes>;
  }

  const dashboardPath = user.role === 'ADMIN' ? '/admin/dashboard' : '/dashboard';
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="min-w-0 flex-1 overflow-x-hidden">
        <Routes>
          <Route path="/login" element={<Navigate to={dashboardPath} replace />} />
          <Route path="/" element={<Navigate to={dashboardPath} replace />} />
          <Route path="/dashboard" element={user.role === 'ADMIN' ? <Navigate to="/admin/dashboard" replace /> : <Home />} />
          <Route path="/new-analysis" element={<NewAnalysis />} />
          <Route path="/analysis/new" element={<NewAnalysis />} />
          <Route path="/analysis/:id" element={<AnalysisDeepLink />} />
          <Route path="/evidence" element={<NewAnalysis initialStep={2} />} />
          <Route path="/recruitment-dna" element={<NewAnalysis initialStep={3} />} />
          <Route path="/evidence-graph" element={<NewAnalysis initialStep={4} />} />
          <Route path="/official-verification" element={<NewAnalysis initialStep={5} />} />
          <Route path="/fingerprint-matching" element={<NewAnalysis initialStep={6} />} />
          <Route path="/risk-reasoning" element={<NewAnalysis initialStep={7} />} />
          <Route path="/trust-score" element={<NewAnalysis initialStep={8} />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/threat-intel" element={<ThreatIntelligencePage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={user.role === 'ADMIN' ? <SettingsPage /> : <Navigate to="/dashboard" replace />} />
          <Route path="/admin/dashboard" element={user.role === 'ADMIN' ? <AdminDashboardPage /> : <AccessDenied />} />
          <Route path="/admin/users" element={user.role === 'ADMIN' ? <AdminDashboardPage /> : <AccessDenied />} />
          <Route path="/admin/analyses" element={user.role === 'ADMIN' ? <AdminDashboardPage /> : <AccessDenied />} />
          <Route path="/admin/recruitment-dna" element={user.role === 'ADMIN' ? <AdminDashboardPage /> : <AccessDenied />} />
          <Route path="/admin/fingerprints" element={user.role === 'ADMIN' ? <AdminDashboardPage /> : <AccessDenied />} />
          <Route path="/admin/risk-statistics" element={user.role === 'ADMIN' ? <AdminDashboardPage /> : <AccessDenied />} />
          <Route path="/admin/system-activity" element={user.role === 'ADMIN' ? <AdminDashboardPage /> : <AccessDenied />} />
          <Route path="*" element={<Navigate to={dashboardPath} replace />} />
        </Routes>
      </div>
    </div>
  );
}

function AccessDenied() {
  return <main className="mx-auto max-w-xl p-12 text-center"><h1 className="text-2xl font-extrabold text-slate-900">Access Denied</h1><p className="mt-2 text-slate-600">You do not have permission to access this page.</p></main>;
}

function ProfilePage() {
  const { user } = useAuth();
  return (
    <main className="min-h-screen bg-slate-50/50 pb-12">
      <div className="border-b border-slate-200 bg-white px-6 py-5"><h1 className="text-xl font-extrabold text-slate-900">My Profile</h1></div>
      <section className="mx-auto mt-8 max-w-2xl rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <dl className="divide-y divide-slate-100">
          <div className="flex justify-between gap-4 py-4"><dt className="text-sm font-semibold text-slate-500">Username</dt><dd className="text-sm font-bold text-slate-900">{user?.username}</dd></div>
          <div className="flex justify-between gap-4 py-4"><dt className="text-sm font-semibold text-slate-500">Role</dt><dd className="text-sm font-bold text-slate-900">{user?.role}</dd></div>
        </dl>
      </section>
    </main>
  );
}

function AnalysisDeepLink() {
  const { id = '' } = useParams();
  const navigate = useNavigate();
  const { setActiveResult, setPipelineData, setActiveStep } = usePipeline();
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistoryById(id)
      .then(result => {
        setActiveResult(result.dashboard);
        setPipelineData(result.pipelineSteps || {});
        setActiveStep(9);
        navigate('/new-analysis', { replace: true });
      })
      .catch((requestError: any) => setError(requestError.response?.status === 403 ? 'You do not have permission to view this analysis.' : 'This analysis could not be found.'));
  }, [id, navigate, setActiveResult, setPipelineData, setActiveStep]);

  return <main className="p-12 text-center text-sm font-semibold text-slate-600">{error || 'Loading analysis...'}</main>;
}

export default App;
