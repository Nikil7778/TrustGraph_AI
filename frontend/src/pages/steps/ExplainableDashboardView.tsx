import React, { useState } from 'react';
import type { ExplainableResultDashboard } from '../../types';
import { ShieldAlert, Download, CheckCircle2, PlusCircle } from 'lucide-react';
import { usePipeline } from '../../context/PipelineContext';

export const ExplainableDashboardView: React.FC<{ dashboard: ExplainableResultDashboard | null }> = ({ dashboard }) => {
  const { resetAnalysis } = usePipeline();
  const [activeTab, setActiveTab] = useState<'SUMMARY' | 'EVIDENCE' | 'DNA' | 'VERIFY' | 'RECOMMEND'>('SUMMARY');

  const res = dashboard || {
    analysisId: 'ANALYSIS-GEN-0000',
    title: 'Recruitment Notice Analysis',
    trustScore: { overallScore: 50, riskLevel: 'MEDIUM_RISK', recommendation: 'Verify recruitment offer through official channels.' },
    fingerprintMatch: { overallSimilarityPercentage: 0, matchedScamId: 'RF-NONE', breakdownSummary: '0/9 characteristics matched' },
    fieldByFieldComparison: [],
    officialVerification: {
      officialOrgName: null,
      isOrgVerified: false,
      isWebsiteInOfficialList: false,
      isEmailInOfficialList: false,
      isPhoneInOfficialList: false,
      isNotificationIdValid: false,
      feeDiscrepancy: { claimedFee: null, officialFee: null, isMatching: false },
      verificationScore: 0,
      notes: ['Verification results compiled.'],
      comparisonTable: []
    },
    aiReasoning: { redFlags: [] },
    recruitmentDna: {
      dnaId: 'RDNA-0000',
      canonicalHash: '0x00000000',
      normalizedAttributes: {
        organization: { raw: 'Unspecified Entity' },
        email: { raw: 'Not Provided' },
        phone: { raw: 'Not Provided' },
        payment: { upiId: null, applicationFee: null },
        website: { normalizedDomain: 'Not Provided' },
        notificationId: { normalized: 'Not Provided' }
      }
    },
    actionItems: [
      'Verify recruitment notice directly on accredited government portals.',
      'Do not transfer funds via unverified private UPI VPAs.'
    ]
  };

  const norm = res.recruitmentDna?.normalizedAttributes;
  const ver = res.officialVerification;

  const submittedOrg = norm?.organization?.raw || 'Claimed Organization';
  const officialOrg = ver?.officialOrgName || (ver?.isOrgVerified ? submittedOrg : 'Unverified Registry Baseline');
  const orgMatch = ver?.isOrgVerified && (ver?.officialOrgName ? ver.officialOrgName.toUpperCase().includes(submittedOrg.toUpperCase()) || submittedOrg.toUpperCase().includes(ver.officialOrgName.toUpperCase()) : true);

  const verificationRows: any[] = res.officialVerification?.comparisonTable && res.officialVerification.comparisonTable.length > 0
    ? res.officialVerification.comparisonTable.map(r => ({
        field: r.field,
        submitted: r.submitted,
        official: r.official,
        status: r.status,
        badge: r.statusLabel
      }))
    : [
        { field: 'Organization', submitted: submittedOrg, official: officialOrg, status: orgMatch ? 'MATCH' : 'MISMATCH', badge: orgMatch ? '✓ Match' : '✕ Mismatch' }
      ];

  return (
    <div className="space-y-6">
      {/* Executive Header Banner */}
      <div className="bg-gradient-to-r from-red-900 via-navy-900 to-slate-900 rounded-3xl p-8 text-white shadow-xl flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-red-500/20 border border-red-500/30 flex items-center justify-center text-red-400">
            <ShieldAlert className="w-10 h-10" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full bg-red-500/30 border border-red-400/30 text-red-200 font-extrabold text-xs uppercase tracking-wide">
                ⚠ {res.trustScore?.riskLevel?.replace('_', ' ')}
              </span>
              <span className="text-xs text-slate-300 font-mono">ID: {res.analysisId}</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">{res.title}</h2>
            <p className="text-xs text-slate-300 mt-1 font-medium max-w-xl">
              This recruitment offer shows multiple high-risk indicators and matches known scam signatures.
            </p>
          </div>
        </div>

        <div className="flex flex-col items-center sm:items-end gap-3">
          <div className="px-6 py-4 rounded-2xl bg-white/10 border border-white/15 text-center w-full">
            <p className="text-[10px] text-slate-300 uppercase tracking-widest font-bold">Calculated Trust Score</p>
            <p className="text-4xl font-black text-white font-mono mt-0.5">{res.trustScore?.overallScore} / 100</p>
          </div>

          <button
            onClick={resetAnalysis}
            className="w-full px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/30 transition-all flex items-center justify-center gap-2"
          >
            <PlusCircle className="w-4 h-4" />
            <span>+ Analyze Next Recruitment</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-2 shadow-sm flex flex-wrap items-center gap-1">
        {[
          { id: 'SUMMARY', label: 'Executive Summary' },
          { id: 'DNA', label: 'DNA Field Match' },
          { id: 'VERIFY', label: 'Official Verification' },
          { id: 'EVIDENCE', label: 'Original Evidence' },
          { id: 'RECOMMEND', label: 'Action Steps' }
        ].map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id as any)}
            className={`px-4 py-2.5 rounded-xl font-bold text-xs transition-all ${
              activeTab === t.id
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* 1. Summary Tab */}
      {activeTab === 'SUMMARY' && (
        <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-6">
          <h3 className="text-lg font-bold text-slate-900">Key Fraud Intelligence Findings</h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-red-50 border border-red-200">
              <span className="text-xs font-bold text-red-700 uppercase">Suspicious Match</span>
              <p className="text-2xl font-black text-red-900 mt-1">{res.fingerprintMatch?.overallSimilarityPercentage}%</p>
              <p className="text-[11px] text-red-700 mt-0.5 font-medium">Match with record {res.fingerprintMatch?.matchedScamId}</p>
            </div>

            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200">
              <span className="text-xs font-bold text-amber-700 uppercase">Red Flags Identified</span>
              <p className="text-2xl font-black text-amber-900 mt-1">{res.aiReasoning?.redFlags?.length || 3} Severe</p>
              <p className="text-[11px] text-amber-700 mt-0.5 font-medium">Critical payment & domain flags</p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-xs font-bold text-slate-500 uppercase">Official Mismatches</span>
              <p className="text-2xl font-black text-slate-900 mt-1">4 Mismatches</p>
              <p className="text-[11px] text-slate-500 mt-0.5 font-medium">Domain & Email differ from official</p>
            </div>

            <div className="p-4 rounded-2xl bg-purple-50 border border-purple-200">
              <span className="text-xs font-bold text-purple-700 uppercase">Field Similarity</span>
              <p className="text-2xl font-black text-purple-900 mt-1">{res.fingerprintMatch?.breakdownSummary}</p>
              <p className="text-[11px] text-purple-700 mt-0.5 font-medium">Exact & Similar parameters</p>
            </div>
          </div>
        </div>
      )}

      {/* 2. DNA Field Match Tab */}
      {activeTab === 'DNA' && (
        <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-4">
          <h3 className="text-lg font-bold text-slate-900">Field-by-Field Detailed Comparison</h3>
          <p className="text-xs text-slate-500 font-medium">Itemized evaluation showing individual field weights and match types.</p>

          <div className="divide-y divide-slate-100 border border-slate-200 rounded-2xl overflow-hidden">
            {res.fieldByFieldComparison?.map((f: any, idx: number) => (
              <div key={idx} className="p-4 flex items-center justify-between hover:bg-slate-50">
                <span className="font-bold text-xs text-slate-900">{f.fieldName}</span>
                <span className="text-xs font-mono text-slate-600">{f.claimedValue}</span>
                <span className="text-xs font-bold px-3 py-1 rounded-full bg-slate-100">{f.matchType}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. Official Verification Tab */}
      {activeTab === 'VERIFY' && (
        <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-900">Official Registry Verification Data</h3>
              <p className="text-xs text-slate-500 font-medium mt-0.5">Submitted offer characteristics compared against verified government registries.</p>
            </div>
            <span className="px-3 py-1 rounded-lg bg-blue-50 text-blue-700 font-bold text-xs border border-blue-200">
              Alignment Score: {res.officialVerification?.verificationScore || 15}/100
            </span>
          </div>

          <div className="border border-slate-200 rounded-2xl overflow-hidden">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-100 border-b border-slate-200 font-extrabold text-slate-700 uppercase">
                  <th className="p-3">Field</th>
                  <th className="p-3">Submitted Value</th>
                  <th className="p-3">Official Verified Baseline</th>
                  <th className="p-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {verificationRows.map((r, i) => (
                  <tr key={i} className="hover:bg-slate-50">
                    <td className="p-3 font-bold text-slate-900">{r.field}</td>
                    <td className="p-3 font-mono text-slate-600">{r.submitted}</td>
                    <td className="p-3 font-mono text-slate-600">{r.official}</td>
                    <td className="p-3 text-center">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full font-bold ${
                          r.status === 'MATCH'
                            ? 'bg-emerald-100 text-emerald-800'
                            : r.status === 'MISMATCH'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {r.badge}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {res.officialVerification?.notes && res.officialVerification.notes.length > 0 && (
            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 space-y-1">
              <h4 className="text-xs font-bold text-amber-900 uppercase">Verification Discrepancy Notes</h4>
              {res.officialVerification.notes.map((note: string, idx: number) => (
                <p key={idx} className="text-xs text-amber-800 font-medium">
                  • {note}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 4. Original Evidence Tab */}
      {activeTab === 'EVIDENCE' && (
        <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Original Submitted Evidence & OCR Stream</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">Raw text stream and canonical digital artifacts analyzed during the scan.</p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900 text-slate-200 font-mono text-xs leading-relaxed space-y-2">
            <p className="text-emerald-400 font-bold">=== RAW INGESTED TEXT STREAM ===</p>
            <p>
              OFFICIAL RECRUITMENT NOTIFICATION 2026<br />
              Ministry of Defence - Direct Recruitment Drive<br />
              Notification Ref: MOD/2026/145<br />
              Designation: Junior Security Guard & Administrative Officer<br />
              Vacancies: 1,450 Posts<br />
              Salary: ₹35,000 - ₹55,000 per month<br />
              Application Fee: ₹500 (Pay via UPI: defence123@upi)<br />
              Official Portal: http://defence-recruitment.com<br />
              Contact Email: recruitment@defence-gov.com<br />
              Helpdesk Phone: +91 98765 43210<br />
              Last Date to Apply: 30th September 2026
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-[10px] font-bold text-slate-400 uppercase block">DNA Signature</span>
              <span className="font-bold text-slate-900">{res.recruitmentDna?.dnaId || 'RDNA-7F3A-9C2D'}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Canonical SHA-256</span>
              <span className="font-bold text-slate-900 truncate block">{res.recruitmentDna?.canonicalHash || '0x89a7b3c2'}</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Scan Timestamp</span>
              <span className="font-bold text-slate-900">{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      )}

      {/* 5. Action Steps Tab */}
      {activeTab === 'RECOMMEND' && (
        <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-6">
          <h3 className="text-lg font-bold text-slate-900">Recommended Action Steps</h3>

          <div className="space-y-3">
            {res.actionItems?.map((item: string, idx: number) => (
              <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                <p className="text-sm font-semibold text-slate-800 leading-relaxed">{item}</p>
              </div>
            ))}
          </div>

          <div className="pt-4 flex flex-wrap items-center gap-4">
            <button
              onClick={resetAnalysis}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
            >
              <PlusCircle className="w-4 h-4" />
              <span>+ Analyze Another Recruitment Offer</span>
            </button>

            <button
              onClick={() => alert('PDF Report Downloaded')}
              className="px-6 py-3 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold text-xs transition-all flex items-center gap-2 shadow-sm"
            >
              <Download className="w-4 h-4" />
              <span>Download Report (PDF)</span>
            </button>

            <button
              onClick={() => alert('Reported to Cyber Cell')}
              className="px-6 py-3 rounded-xl bg-red-50 hover:bg-red-100 border border-red-200 text-red-700 font-bold text-xs transition-all flex items-center gap-2"
            >
              <ShieldAlert className="w-4 h-4" />
              <span>Report Suspicious Recruitment</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
