import React, { useState } from 'react';
import { FileText, FileUp, Image as ImageIcon, Link as LinkIcon, Sparkles, ArrowRight, Loader2, PlusCircle, RotateCcw, ShieldCheck } from 'lucide-react';
import { Header } from '../components/layout/Header';
import { PipelineStepper } from '../components/pipeline/PipelineStepper';
import { usePipeline } from '../context/PipelineContext';
import { submitNewAnalysis } from '../services/api';
import type { InputType } from '../types';

import { EvidenceExtractionView } from './steps/EvidenceExtractionView';
import { RecruitmentDNAView } from './steps/RecruitmentDNAView';
import { EvidenceGraphView } from './steps/EvidenceGraphView';
import { OfficialVerificationView } from './steps/OfficialVerificationView';
import { SuspiciousMatchingView } from './steps/SuspiciousMatchingView';
import { AIRiskReasoningView } from './steps/AIRiskReasoningView';
import { TrustScoreView } from './steps/TrustScoreView';
import { ExplainableDashboardView } from './steps/ExplainableDashboardView';

const PIPELINE_PROGRESS_STAGES = [
  'Ingesting & Validating Offer Parameters',
  'Extracting Multi-Modal Recruitment Entities',
  'Generating Canonical Recruitment DNA & Hashes',
  'Constructing Evidence Relationship Graph',
  'Cross-Referencing Official Government Registries',
  'Performing Field-by-Field Similarity Matching',
  'Running AI Risk Reasoning & Anomaly Detection',
  'Computing Multi-Factor Trust Score',
  'Synthesizing Explainable Final Dashboard'
];

export const NewAnalysis: React.FC = () => {
  const { activeStep, setActiveStep, isAnalyzing, setIsAnalyzing, setActiveResult, setPipelineData, activeResult, pipelineData, resetAnalysis } = usePipeline();

  const [inputType, setInputType] = useState<InputType>('TEXT');
  const [textContent, setTextContent] = useState<string>('');
  const [urlContent, setUrlContent] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [currentProcessingStage, setCurrentProcessingStage] = useState<number>(0);

  const sampleScam = `OFFICIAL RECRUITMENT NOTIFICATION 2026
Ministry of Defence - Direct Recruitment Drive
Notification Ref: MOD/2026/145
Designation: Junior Security Guard & Administrative Officer
Vacancies: 1,450 Posts
Salary: ₹35,000 - ₹55,000 per month
Application Fee: ₹500 (Pay via UPI: defence123@upi)
Official Portal: http://defence-recruitment.com
Contact Email: recruitment@defence-gov.com
Helpdesk Phone: +91 98765 43210
Last Date to Apply: 30th September 2026`;

  const sampleGenuine = `STAFF SELECTION COMMISSION (SSC)
COMBINED GRADUATE LEVEL EXAMINATION 2026
Notification No. SSC-CGL-2026
Web Portal: https://ssc.gov.in
Email: helpdesk-ssc@gov.in
Phone: +91 11 24361806
Application Fee: ₹100 payable through SBI e-Pay Treasury portal.
Last Date: 15th October 2026`;

  const handleResetForNew = () => {
    resetAnalysis();
    setTextContent('');
    setUrlContent('');
    setSelectedFile(null);
    setCurrentProcessingStage(0);
  };

  const handleStartAnalysis = async () => {
    setIsAnalyzing(true);
    setCurrentProcessingStage(0);
    setActiveStep(1);

    const interval = setInterval(() => {
      setCurrentProcessingStage(prev => {
        const next = prev < PIPELINE_PROGRESS_STAGES.length - 1 ? prev + 1 : prev;
        setActiveStep(next + 1);
        return next;
      });
    }, 280);

    try {
      const res = await submitNewAnalysis({
        type: inputType,
        content: inputType === 'TEXT' ? textContent || sampleScam : undefined,
        url: inputType === 'URL' ? urlContent : undefined,
        file: selectedFile || undefined
      });

      clearInterval(interval);
      setCurrentProcessingStage(PIPELINE_PROGRESS_STAGES.length - 1);
      setPipelineData(res.pipelineSteps);
      setActiveResult(res.dashboard);

      setTimeout(() => {
        setActiveStep(9);
        setIsAnalyzing(false);
      }, 400);
    } catch (err) {
      console.error('Error running analysis:', err);
      clearInterval(interval);
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/50 pb-12">
      <Header title="New Recruitment Analysis" />

      <main className="max-w-6xl mx-auto px-6 pt-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900">Recruitment Verification Pipeline</h2>
            <p className="text-xs text-slate-500 font-medium">9-step automated fraud detection engine</p>
          </div>

          {activeStep > 1 && !isAnalyzing && (
            <button
              type="button"
              onClick={handleResetForNew}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
            >
              <PlusCircle className="w-4 h-4" />
              <span>+ Upload Next Recruitment</span>
            </button>
          )}
        </div>

        <PipelineStepper />

        {isAnalyzing ? (
          <div className="bg-white rounded-3xl border border-slate-200/80 p-12 shadow-sm text-center space-y-6 max-w-2xl mx-auto my-8">
            <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center mx-auto shadow-sm">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>

            <div>
              <h3 className="text-xl font-extrabold text-slate-900">Running TRUST AI Fraud Analysis</h3>
              <p className="text-xs text-slate-500 font-medium mt-1">
                Executing 9-factor verification pipeline and calculating trust score...
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 text-left space-y-2">
              <div className="flex items-center justify-between text-xs font-bold">
                <span className="text-blue-600 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Stage {currentProcessingStage + 1} of 9: {PIPELINE_PROGRESS_STAGES[currentProcessingStage]}</span>
                </span>
                <span className="font-mono text-slate-400">{Math.round(((currentProcessingStage + 1) / 9) * 100)}%</span>
              </div>

              <div className="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
                <div
                  className="h-full bg-blue-600 rounded-full transition-all duration-300"
                  style={{ width: `${((currentProcessingStage + 1) / 9) * 100}%` }}
                />
              </div>
            </div>
          </div>
        ) : (
          <>
            {activeStep === 1 && (
              <div className="bg-white rounded-3xl border border-slate-200/80 p-8 shadow-sm space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-extrabold text-slate-900">Check a Recruitment Offer</h2>
                    <p className="text-sm text-slate-500 font-medium mt-1">
                      Upload a message, document, image or URL to verify whether it is genuine or suspicious.
                    </p>
                  </div>

                  {(textContent || urlContent || selectedFile) && (
                    <button
                      type="button"
                      onClick={handleResetForNew}
                      className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors flex items-center gap-1.5"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      <span>Clear Input</span>
                    </button>
                  )}
                </div>

                <div className="p-4 rounded-2xl bg-blue-50/60 border border-blue-100 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-blue-900 font-semibold text-xs">
                    <Sparkles className="w-4 h-4 text-blue-600" />
                    <span>Quick Test Samples:</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => { setInputType('TEXT'); setTextContent(sampleScam); }}
                      className="px-3 py-1.5 rounded-lg bg-white border border-blue-200 text-blue-700 text-xs font-bold hover:bg-blue-100 transition-colors"
                    >
                      Load Scam MOD Notice
                    </button>
                    <button
                      type="button"
                      onClick={() => { setInputType('TEXT'); setTextContent(sampleGenuine); }}
                      className="px-3 py-1.5 rounded-lg bg-white border border-emerald-200 text-emerald-700 text-xs font-bold hover:bg-emerald-50 transition-colors"
                    >
                      Load Genuine SSC Notice
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {[
                    { type: 'TEXT', label: 'Message / Text', icon: FileText },
                    { type: 'PDF', label: 'PDF Document', icon: FileUp },
                    { type: 'IMAGE', label: 'Image / Screenshot', icon: ImageIcon },
                    { type: 'URL', label: 'Web Portal URL', icon: LinkIcon }
                  ].map(opt => {
                    const Icon = opt.icon;
                    const isSel = inputType === opt.type;
                    return (
                      <button
                        key={opt.type}
                        type="button"
                        onClick={() => setInputType(opt.type as InputType)}
                        className={`p-4 rounded-2xl border text-left transition-all flex flex-col items-center justify-center gap-2 ${
                          isSel
                            ? 'border-blue-600 bg-blue-50/60 text-blue-700 font-bold shadow-sm ring-2 ring-blue-100'
                            : 'border-slate-200 hover:border-slate-300 text-slate-600'
                        }`}
                      >
                        <Icon className="w-6 h-6" />
                        <span className="text-xs font-semibold">{opt.label}</span>
                      </button>
                    );
                  })}
                </div>

                {inputType === 'TEXT' && (
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Paste Recruitment Offer Text / Message</label>
                    <textarea
                      rows={8}
                      value={textContent}
                      onChange={(e) => setTextContent(e.target.value)}
                      placeholder="Paste WhatsApp job notification, SMS message, or hiring email copy..."
                      className="w-full p-4 text-sm bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-mono text-slate-800"
                    />
                  </div>
                )}

                {inputType === 'URL' && (
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Paste Recruitment Portal URL</label>
                    <input
                      type="url"
                      value={urlContent}
                      onChange={(e) => setUrlContent(e.target.value)}
                      placeholder="https://defence-recruitment.com/apply-2026"
                      className="w-full p-4 text-sm bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-slate-800"
                    />
                  </div>
                )}

                {(inputType === 'PDF' || inputType === 'IMAGE') && (
                  <div className="border-2 border-dashed border-slate-300 rounded-2xl p-8 text-center bg-slate-50/50 hover:bg-slate-50 transition-colors">
                    <FileUp className="w-10 h-10 text-slate-400 mx-auto mb-2" />
                    <p className="text-sm font-bold text-slate-800">Drag & Drop {inputType} Document Here</p>
                    <p className="text-xs text-slate-500 mt-1 mb-4">Supported formats: PDF, PNG, JPG (Max 10MB)</p>
                    <input
                      type="file"
                      onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                      className="hidden"
                      id="file-upload-input"
                    />
                    <label
                      htmlFor="file-upload-input"
                      className="px-4 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 font-bold text-xs hover:bg-slate-100 cursor-pointer shadow-sm"
                    >
                      {selectedFile ? selectedFile.name : 'Browse Local Files'}
                    </label>
                  </div>
                )}

                <div className="pt-4 flex justify-end">
                  <button
                    type="button"
                    disabled={isAnalyzing}
                    onClick={handleStartAnalysis}
                    className="px-8 py-4 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-sm shadow-lg shadow-blue-600/30 transition-all flex items-center gap-2 disabled:opacity-50"
                  >
                    <span>Analyze Now</span>
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}

            {activeStep === 2 && <EvidenceExtractionView data={pipelineData?.[2]} onNext={() => setActiveStep(3)} />}
            {activeStep === 3 && <RecruitmentDNAView data={pipelineData?.[3]} onNext={() => setActiveStep(4)} />}
            {activeStep === 4 && <EvidenceGraphView data={pipelineData?.[4]} onNext={() => setActiveStep(5)} />}
            {activeStep === 5 && <OfficialVerificationView data={pipelineData?.[5]} onNext={() => setActiveStep(6)} />}
            {activeStep === 6 && <SuspiciousMatchingView data={pipelineData?.[6]} onNext={() => setActiveStep(7)} />}
            {activeStep === 7 && <AIRiskReasoningView data={pipelineData?.[7]} onNext={() => setActiveStep(8)} />}
            {activeStep === 8 && <TrustScoreView data={pipelineData?.[8]} onNext={() => setActiveStep(9)} />}
            {activeStep === 9 && <ExplainableDashboardView dashboard={activeResult} />}
          </>
        )}
      </main>
    </div>
  );
};
