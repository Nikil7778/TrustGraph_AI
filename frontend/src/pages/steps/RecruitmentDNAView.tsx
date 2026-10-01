import React from 'react';
import { ArrowRight, Dna, Fingerprint } from 'lucide-react';
import type { RecruitmentDNA } from '../../types';

export const RecruitmentDNAView: React.FC<{ data: RecruitmentDNA; onNext: () => void }> = ({ data, onNext }) => {
  const dna = data || {
    dnaId: 'RDNA-GEN-0000',
    canonicalHash: '0x0000000000000000',
    createdAt: new Date().toISOString(),
    normalizedAttributes: {
      organization: { raw: 'Unspecified Entity', normalized: 'UNSPECIFIED', alias: 'N/A' },
      notificationId: { raw: 'Not Provided', normalized: 'NOT PROVIDED' },
      website: { raw: 'Not Provided', normalizedDomain: 'Not Provided', isGovDomain: false },
      email: { raw: 'Not Provided', domain: 'Not Provided', isFreeProvider: false },
      phone: { raw: 'Not Provided', normalized: 'Not Provided' },
      payment: { upiId: null, applicationFee: null, paymentGateway: 'None', isPrivateUpi: false },
      media: { qrCodeData: null, logoHash: null },
      timeline: { publishDate: 'N/A', lastDateToApply: 'N/A' },
      jobMetadata: { designation: 'Unspecified Position', totalVacancies: null, salaryRange: 'N/A' }
    },
    fingerprintHash: 'hash_000000'
  };

  const norm = dna.normalizedAttributes;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900">Recruitment DNA Generated</h2>
          <p className="text-sm text-slate-500 font-medium mt-1">
            All extracted characteristics are normalized and combined to create a unique digital fingerprint.
          </p>
        </div>
        <button
          onClick={onNext}
          className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
        >
          <span>Next: Build Graph</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      <div className="bg-gradient-to-r from-blue-900 via-navy-900 to-indigo-900 rounded-3xl p-6 text-white shadow-lg flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-white/10 border border-white/15 flex items-center justify-center text-blue-300">
            <Fingerprint className="w-8 h-8" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-blue-300 uppercase tracking-widest">Canonical Recruitment Signature</span>
            </div>
            <h3 className="text-2xl font-black font-mono text-white mt-0.5">{dna.dnaId}</h3>
            <p className="text-xs text-slate-300 font-mono mt-1">SHA-256: {dna.canonicalHash}</p>
          </div>
        </div>

        <div className="px-4 py-2 rounded-xl bg-white/10 border border-white/15 text-right">
          <p className="text-[10px] text-slate-300 uppercase tracking-wide font-bold">Fingerprint Signature</p>
          <p className="text-xs font-mono font-bold text-emerald-300">{dna.fingerprintHash}</p>
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100 flex items-center gap-2">
          <Dna className="w-5 h-5 text-blue-600" />
          <span>Normalized Fingerprint Components</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase">Normalized Organization</span>
            <p className="text-sm font-bold text-slate-900">{norm?.organization?.normalized}</p>
            <p className="text-[10px] text-slate-400 font-mono">Alias: {norm?.organization?.alias}</p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase">Normalized Domain</span>
            <p className="text-sm font-bold text-slate-900">{norm?.website?.normalizedDomain}</p>
            <p className={`text-[10px] font-bold ${norm?.website?.isGovDomain ? 'text-emerald-600' : 'text-amber-600'}`}>
              {norm?.website?.isGovDomain ? '✓ Official .gov.in' : '⚠ Non-Government Domain'}
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase">Normalized Contact Email</span>
            <p className="text-sm font-bold text-slate-900">{norm?.email?.raw}</p>
            <p className="text-[10px] text-slate-400 font-mono">Domain: {norm?.email?.domain}</p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase">Normalized Phone</span>
            <p className="text-sm font-bold text-slate-900">{norm?.phone?.normalized}</p>
            <p className="text-[10px] text-slate-400 font-mono">Standard E.164 Format</p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase">UPI / VPA Payment Signature</span>
            <p className="text-sm font-bold text-slate-900">{norm?.payment?.upiId}</p>
            <p className={`text-[10px] font-bold ${norm?.payment?.isPrivateUpi ? 'text-red-600' : 'text-emerald-600'}`}>
              {norm?.payment?.isPrivateUpi ? '⚠ Private UPI (High Risk)' : 'Verified Gateway'}
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-1">
            <span className="text-[11px] font-bold text-slate-500 uppercase">Notification Identifier</span>
            <p className="text-sm font-bold text-slate-900">{norm?.notificationId?.normalized}</p>
            <p className="text-[10px] text-slate-400 font-mono">Normalized Pattern</p>
          </div>
        </div>
      </div>
    </div>
  );
};
