import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, AlertTriangle, BadgeCheck, Fingerprint, Files, Users } from 'lucide-react';
import { Header } from '../components/layout/Header';
import { fetchAdminAnalyses, fetchAdminDashboard, fetchAdminFingerprints, fetchAdminUsers } from '../services/api';

type AdminView = 'overview' | 'users' | 'analyses' | 'dna' | 'fingerprints' | 'risks' | 'activity';

export const AdminDashboardPage = () => {
  const location = useLocation();
  const pathView: Record<string, AdminView> = {
    '/admin/users': 'users',
    '/admin/analyses': 'analyses',
    '/admin/recruitment-dna': 'dna',
    '/admin/fingerprints': 'fingerprints',
    '/admin/risk-statistics': 'risks',
    '/admin/system-activity': 'activity'
  };
  const view = pathView[location.pathname] || 'overview';
  const [overview, setOverview] = useState<any>(null);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [fingerprints, setFingerprints] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');
    Promise.all([fetchAdminDashboard(), fetchAdminUsers(), fetchAdminAnalyses(), fetchAdminFingerprints()])
      .then(([dashboardData, userData, analysisData, fingerprintData]) => {
        if (!active) return;
        setOverview(dashboardData.overview);
        setRecentActivity(dashboardData.recentActivity || []);
        setUsers(userData.users || []);
        setAnalyses(analysisData.records || []);
        setFingerprints(fingerprintData.fingerprints || []);
      })
      .catch(() => { if (active) setError('Admin data could not be loaded. Verify your administrator session and try again.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const titleByView: Record<AdminView, string> = {
    overview: 'Admin Dashboard',
    users: 'User Management',
    analyses: 'All Analyses',
    dna: 'Recruitment DNA',
    fingerprints: 'Suspicious Fingerprints',
    risks: 'Risk Statistics',
    activity: 'System Activity'
  };
  const title = titleByView[view] || titleByView.overview;

  return (
    <div className="min-h-screen bg-slate-50/50 pb-12">
      <Header title={title} />
      <main className="mx-auto max-w-7xl space-y-6 px-5 pt-7 sm:px-8">
        <div className="flex flex-wrap items-end justify-between gap-4 border-b border-slate-200 pb-5">
          <div>
            <p className="text-xs font-extrabold uppercase tracking-[0.14em] text-indigo-700">JobGuard Administration</p>
            <h1 className="mt-1 text-2xl font-black text-slate-950">{title}</h1>
          </div>
          <Link to="/settings" className="rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm font-bold text-slate-700 hover:border-indigo-400 hover:text-indigo-800">Engine settings</Link>
        </div>

        {error && <p role="alert" className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-800">{error}</p>}
        {loading ? <p className="py-16 text-center text-sm font-semibold text-slate-500">Loading administrative data...</p> : !error && (
          <>
            {(view === 'overview' || view === 'risks') && overview && <Overview data={overview} showRiskOnly={view === 'risks'} />}
            {view === 'users' && <UsersTable users={users} />}
            {view === 'analyses' && <AnalysesTable analyses={analyses} />}
            {view === 'dna' && <DnaTable analyses={analyses} />}
            {view === 'fingerprints' && <FingerprintsTable fingerprints={fingerprints} />}
            {view === 'activity' && <ActivityTable records={recentActivity} />}
          </>
        )}
      </main>
    </div>
  );
};

function Overview({ data, showRiskOnly }: { data: any; showRiskOnly: boolean }) {
  const stats = [
    { label: 'Total users', value: data.totalUsers, icon: Users, color: 'text-blue-800 bg-blue-100' },
    { label: 'Total analyses', value: data.totalAnalyses, icon: Files, color: 'text-indigo-800 bg-indigo-100' },
    { label: 'Analyses today', value: data.analysesToday, icon: Activity, color: 'text-emerald-800 bg-emerald-100' },
    { label: 'Suspicious', value: data.suspicious, icon: AlertTriangle, color: 'text-rose-800 bg-rose-100' },
    { label: 'Likely genuine', value: data.genuine, icon: BadgeCheck, color: 'text-teal-800 bg-teal-100' },
    { label: 'Needs review', value: data.needsReview, icon: Fingerprint, color: 'text-amber-900 bg-amber-100' }
  ];
  const shown = showRiskOnly ? stats.slice(3) : stats;
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {shown.map(item => {
        const Icon = item.icon;
        return <div key={item.label} className="flex min-h-32 items-center justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div><p className="text-sm font-semibold text-slate-500">{item.label}</p><p className="mt-2 text-3xl font-black tabular-nums text-slate-950">{item.value ?? 0}</p></div>
          <span className={`grid h-11 w-11 place-items-center rounded-xl ${item.color}`}><Icon size={21} /></span>
        </div>;
      })}
    </section>
  );
}

function UsersTable({ users }: { users: any[] }) {
  return <DataTable headers={['Username', 'Role', 'Created', 'Last login', 'Analyses', 'Status']}>
    {users.map(user => <tr key={user.id} className="border-t border-slate-100">
      <Cell strong>{user.username}</Cell><Cell>{user.role}</Cell><Cell>{formatDate(user.createdAt)}</Cell>
      <Cell>{user.lastLogin ? formatDate(user.lastLogin) : 'Never'}</Cell><Cell>{user._count?.analyses ?? 0}</Cell>
      <Cell><span className={`rounded-full px-2.5 py-1 text-xs font-bold ${user.lastLogin ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'}`}>{user.lastLogin ? 'Active' : 'Not signed in'}</span></Cell>
    </tr>)}
  </DataTable>;
}

function AnalysesTable({ analyses }: { analyses: any[] }) {
  return <DataTable headers={['Analysis', 'Username', 'Input', 'Organization', 'Risk level', 'Trust score', 'Status', 'Created']}>
    {analyses.map(record => <tr key={record.id} className="border-t border-slate-100">
      <td className="max-w-64 truncate px-4 py-3 font-bold text-slate-900"><Link className="hover:text-blue-700" to={`/analysis/${record.id}`}>{record.title}</Link></td><Cell>{record.username}</Cell><Cell>{record.inputType}</Cell><Cell>{record.organization}</Cell><Cell>{record.riskLevel?.replace(/_/g, ' ')}</Cell>
      <Cell>{record.trustScore}/100</Cell><Cell>{record.status}</Cell><Cell>{formatDate(record.createdAt)}</Cell>
    </tr>)}
  </DataTable>;
}

function DnaTable({ analyses }: { analyses: any[] }) {
  return <DataTable headers={['DNA ID', 'Organization', 'Notification ID', 'Website', 'Email', 'Phone', 'UPI', 'QR', 'Logo', 'Similarity', 'Created']}>
    {analyses.map(record => <tr key={record.id} className="border-t border-slate-100">
      <Cell>{record.dna?.dnaId}</Cell><Cell strong>{record.dna?.organization}</Cell><Cell>{record.dna?.notificationId}</Cell><Cell>{record.dna?.website}</Cell>
      <Cell>{record.dna?.email}</Cell><Cell>{record.dna?.phone}</Cell><Cell>{record.dna?.upi}</Cell><Cell>{record.dna?.qr}</Cell><Cell>{record.dna?.logo}</Cell><Cell>{record.similarity === 'N/A' ? 'N/A' : `${record.similarity}%`}</Cell><Cell>{formatDate(record.createdAt)}</Cell>
    </tr>)}
  </DataTable>;
}

function FingerprintsTable({ fingerprints }: { fingerprints: any[] }) {
  return <DataTable headers={['Fingerprint', 'Organization', 'Source', 'Risk', 'Score', 'Matched characteristics', 'Created']}>
    {fingerprints.map(item => <tr key={item.id} className="border-t border-slate-100">
      <Cell strong>{item.scamName}</Cell><Cell>{item.organization}</Cell><Cell>{item.source}</Cell><Cell>{item.riskClassification}</Cell><Cell>{item.riskScore}</Cell>
      <Cell>{Object.values(item.matchedCharacteristics || {}).flat().join(', ') || 'None'}</Cell><Cell>{formatDate(item.createdAt)}</Cell>
    </tr>)}
  </DataTable>;
}

function ActivityTable({ records }: { records: any[] }) {
  return <DataTable headers={['Activity', 'Username', 'Input type', 'Risk', 'Score', 'Date']}>
    {records.map(record => <tr key={record.id} className="border-t border-slate-100">
      <Cell strong>{record.title}</Cell><Cell>{record.username}</Cell><Cell>{record.inputType}</Cell><Cell>{record.riskLevel?.replace(/_/g, ' ')}</Cell>
      <Cell>{record.trustScore}/100</Cell><Cell>{formatDate(record.createdAt)}</Cell>
    </tr>)}
  </DataTable>;
}

function DataTable({ headers, children }: { headers: string[]; children: React.ReactNode }) {
  return <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"><div className="overflow-x-auto"><table className="w-full min-w-[720px] text-left text-sm">
    <thead className="bg-slate-50 text-[11px] uppercase tracking-wide text-slate-500"><tr>{headers.map(header => <th key={header} className="px-4 py-3 font-extrabold">{header}</th>)}</tr></thead>
    <tbody>{children || <tr><td colSpan={headers.length} className="px-4 py-12 text-center text-slate-500">No records found.</td></tr>}</tbody>
  </table></div></div>;
}

function Cell({ children, strong = false }: { children: React.ReactNode; strong?: boolean }) {
  return <td className={`max-w-64 truncate px-4 py-3 ${strong ? 'font-bold text-slate-900' : 'text-slate-600'}`}>{children || 'N/A'}</td>;
}

function formatDate(value?: string | Date | null) {
  return value ? new Date(value).toLocaleString() : 'Never';
}