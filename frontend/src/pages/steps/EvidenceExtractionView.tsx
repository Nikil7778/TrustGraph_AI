import React from 'react';
import { ArrowRight } from 'lucide-react';
import { usePipeline } from '../../context/PipelineContext';

export const EvidenceExtractionView: React.FC<{ data: any; onNext: () => void }> = ({ data, onNext }) => {
  const { pipelineData } = usePipeline();
  const rawInputText = pipelineData?.[1]?.rawText || 'Submitted recruitment offer text stream.';

  const fields = data?.fieldDetails || pipelineData?.[2]?.fieldDetails || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900">Extracted Evidence</h2>
          <p className="text-sm text-slate-500 font-medium mt-1">
            Automated multi-modal entity extraction identified key recruitment parameters from input.
          </p>
        </div>
        <button
          onClick={onNext}
          className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
        >
          <span>Next: Generate DNA</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm">
          <h3 className="text-base font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">
            Extracted Entity Attributes
          </h3>

          {Object.keys(fields).length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {Object.entries(fields).map(([key, val]: [string, any]) => (
                <div key={key} className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                      {key.replace(/([A-Z])/g, ' $1')}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${val.confidence > 0 ? 'bg-blue-100 text-blue-700' : 'bg-slate-200 text-slate-600'}`}>
                      {val.confidence}% Conf.
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-slate-900 truncate">{String(val.value)}</p>
                  <p className="text-[10px] text-slate-400 font-medium">Source: {val.source}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400">No entity attributes extracted.</p>
          )}
        </div>

        <div className="lg:col-span-5 bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
            <h3 className="text-base font-bold text-slate-900">Original Submitted Text Preview</h3>
            <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg">Raw Text Stream</span>
          </div>

          <div className="flex-1 bg-slate-900 text-slate-100 p-4 rounded-2xl font-mono text-xs leading-relaxed overflow-y-auto max-h-[420px] whitespace-pre-wrap">
            <p className="text-emerald-400 font-bold mb-2">=== SUBMITTED INPUT STREAM ===</p>
            <p className="text-slate-300">{rawInputText}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

