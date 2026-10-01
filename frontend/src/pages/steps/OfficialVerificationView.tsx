import React from 'react';
import { ArrowRight, ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';
import { usePipeline } from '../../context/PipelineContext';
import type { OfficialVerificationResult, OfficialVerificationRow } from '../../types';

export const OfficialVerificationView: React.FC<{ data?: OfficialVerificationResult; onNext: () => void }> = ({ data, onNext }) => {
  const { pipelineData } = usePipeline();

  const verification: OfficialVerificationResult = data || pipelineData?.[5] || {
    matchedRecordId: null,
    officialOrgName: null,
    isOrgVerified: false,
    isWebsiteGovDomain: false,
    isWebsiteInOfficialList: false,
    isEmailInOfficialList: false,
    isPhoneInOfficialList: false,
    isNotificationIdValid: false,
    feeDiscrepancy: { claimedFee: null, officialFee: null, isMatching: false },
    verificationScore: 0,
    notes: ['No official registry comparison available for submitted text.'],
    comparisonTable: []
  };

  const rows: OfficialVerificationRow[] = verification.comparisonTable || [];

  const getBadgeStyle = (status: OfficialVerificationRow['status']) => {
    switch (status) {
      case 'EXACT_MATCH':
      case 'MATCH':
      case 'VERIFIED':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'LOOKALIKE_IMPERSONATION':
      case 'MISMATCH':
      case 'SUSPICIOUS':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'UNKNOWN':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'NOT_PROVIDED':
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900">Dual-Source Verification Engine</h2>
          <p className="text-sm text-slate-500 font-medium mt-1">
            Cross-referencing submitted notice against official government registries and known scam intelligence.
          </p>
        </div>
        <button
          onClick={onNext}
          className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
        >
          <span>Next: Fingerprint Match</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Dual Source Header Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Source 1: Official Source Intelligence */}
        <div className="p-5 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-extrabold text-blue-700 uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              <span>OFFICIAL SOURCE INTELLIGENCE</span>
            </span>
            <span className="text-xs font-bold font-mono px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
              Score: {verification.verificationScore}/100
            </span>
          </div>

          <div className="space-y-1">
            <h4 className="text-sm font-black text-slate-900">
              {verification.isOrgVerified ? verification.officialOrgName : 'Unverified Registry Baseline'}
            </h4>
            <p className="text-xs text-slate-500 font-medium">
              {verification.isOrgVerified
                ? 'Matched against official government gazette allowlist.'
                : 'No matching official registry record found in database.'}
            </p>
          </div>

          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-semibold">
            <span className="text-slate-500">Domain Verification:</span>
            <span className={verification.isWebsiteInOfficialList ? 'text-emerald-700 font-bold' : (verification.isWebsiteGovDomain ? 'text-blue-700' : 'text-amber-700 font-bold')}>
              {verification.isWebsiteInOfficialList ? '✓ Official Domain Match' : (verification.isWebsiteGovDomain ? '✓ Official TLD (.gov.in)' : '⚠ Non-Government Domain')}
            </span>
          </div>
        </div>

        {/* Source 2: Known Scam Intelligence */}
        <div className="p-5 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-extrabold text-red-700 uppercase tracking-wider flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-red-600" />
              <span>KNOWN SCAM INTELLIGENCE</span>
            </span>
            <span className="text-xs font-bold font-mono px-2.5 py-0.5 rounded-full bg-red-50 text-red-800 border border-red-200">
              Pattern Scan Active
            </span>
          </div>

          <div className="space-y-1">
            <h4 className="text-sm font-black text-slate-900">
              {verification.notes.some(n => n.includes('Private UPI') || n.includes('free public email'))
                ? 'High Scam Pattern Indicators Detected'
                : 'No Direct Scam Pattern Discrepancies'}
            </h4>
            <p className="text-xs text-slate-500 font-medium">
              Evaluates private UPI VPAs, Gmail/Yahoo recruitment notices, and domain lookalikes.
            </p>
          </div>

          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-semibold">
            <span className="text-slate-500">Threat Intelligence Status:</span>
            <span className={verification.notes.some(n => n.includes('Private UPI')) ? 'text-red-700 font-bold' : 'text-emerald-700 font-bold'}>
              {verification.notes.some(n => n.includes('Private UPI')) ? '⚠ Private UPI Vector Flagged' : '✓ Clean Payment Vector'}
            </span>
          </div>
        </div>
      </div>

      {/* Dynamic Field Comparison Table */}
      <div className="bg-white rounded-3xl border border-slate-200/80 overflow-hidden shadow-sm">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wide">
            Submitted Offer Data vs Official Verified Record
          </h3>
          <span className="text-xs text-slate-500 font-medium">Dynamically generated from current input</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-100/70 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                <th className="py-3.5 px-6">Field Parameter</th>
                <th className="py-3.5 px-6">Submitted Offer Data</th>
                <th className="py-3.5 px-6">Official Verified Record</th>
                <th className="py-3.5 px-6 text-center">Status Verdict</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {rows.length > 0 ? (
                rows.map((r, i) => (
                  <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-4 px-6 font-bold text-slate-900">{r.field}</td>
                    <td className="py-4 px-6 text-slate-700 font-mono text-xs">{r.submitted}</td>
                    <td className="py-4 px-6 text-slate-700 font-mono text-xs">{r.official}</td>
                    <td className="py-4 px-6 text-center">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-extrabold border ${getBadgeStyle(r.status)}`}>
                        {r.statusLabel}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-xs text-slate-400 font-medium">
                    No field comparison rows available for current input.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Discrepancy Notes */}
      {verification.notes && verification.notes.length > 0 && (
        <div className="p-5 rounded-3xl bg-amber-50/80 border border-amber-200/80 space-y-2">
          <h4 className="text-xs font-bold text-amber-900 uppercase tracking-wider flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4 text-amber-700" />
            <span>Verification Findings & Discrepancy Notes</span>
          </h4>
          <div className="space-y-1">
            {verification.notes.map((note: string, idx: number) => (
              <p key={idx} className="text-xs text-amber-900 font-medium leading-relaxed">
                • {note}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};


