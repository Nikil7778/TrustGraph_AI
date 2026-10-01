import React, { useEffect, useState } from 'react';
import { Header } from '../components/layout/Header';
import { ShieldAlert } from 'lucide-react';
import { fetchThreatIntelligence } from '../services/api';

export const ThreatIntelligencePage: React.FC = () => {
  const [intel, setIntel] = useState<any[]>([]);

  useEffect(() => {
    fetchThreatIntelligence().then(setIntel);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50/50 pb-12">
      <Header title="Threat Intelligence Database" />

      <main className="max-w-6xl mx-auto px-6 pt-8 space-y-6">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900">Threat Intelligence Database</h2>
          <p className="text-sm text-slate-500 font-medium mt-1">
            Global registry of reported fake recruitment fingerprints, fraudulent UPI VPAs, and typosquatted job portals.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {intel.map((item: any, idx: number) => (
            <div key={idx} className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-red-600" />
                  <span className="font-mono text-xs font-bold text-slate-400">{item.id}</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full bg-red-100 text-red-800 text-[10px] font-black uppercase">
                  {item.threatLevel}
                </span>
              </div>

              <div>
                <h3 className="text-base font-extrabold text-slate-900">{item.scamName}</h3>
                <p className="text-xs text-slate-500 font-medium mt-0.5">Target: {item.targetOrganization}</p>
              </div>

              <div className="space-y-2 text-xs font-mono bg-slate-50 p-3 rounded-2xl border border-slate-200/60">
                <p className="text-slate-600"><span className="font-bold text-slate-900">Websites:</span> {item.suspiciousWebsites?.join(', ')}</p>
                <p className="text-slate-600"><span className="font-bold text-slate-900">Emails:</span> {item.suspiciousEmails?.join(', ')}</p>
                <p className="text-slate-600"><span className="font-bold text-slate-900">UPI Handles:</span> {item.upiDetails?.join(', ')}</p>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-500 font-medium pt-1">
                <span>Reported by {item.reportedCount} victims</span>
                <span>Detected: {item.createdAt}</span>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};
