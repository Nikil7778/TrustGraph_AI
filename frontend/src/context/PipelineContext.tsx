import React, { createContext, useContext, useState } from 'react';
import type { ExplainableResultDashboard } from '../types';

interface PipelineContextType {
  activeStep: number;
  setActiveStep: (step: number) => void;
  isAnalyzing: boolean;
  setIsAnalyzing: (loading: boolean) => void;
  activeResult: ExplainableResultDashboard | null;
  setActiveResult: (res: ExplainableResultDashboard | null) => void;
  pipelineData: any;
  setPipelineData: (data: any) => void;
  resetAnalysis: () => void;
}

const PipelineContext = createContext<PipelineContextType | undefined>(undefined);

export const PipelineProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeStep, setActiveStep] = useState<number>(1);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [activeResult, setActiveResult] = useState<ExplainableResultDashboard | null>(null);
  const [pipelineData, setPipelineData] = useState<any>(null);

  const resetAnalysis = () => {
    setActiveStep(1);
    setIsAnalyzing(false);
    setActiveResult(null);
    setPipelineData(null);
  };

  return (
    <PipelineContext.Provider
      value={{
        activeStep,
        setActiveStep,
        isAnalyzing,
        setIsAnalyzing,
        activeResult,
        setActiveResult,
        pipelineData,
        setPipelineData,
        resetAnalysis
      }}
    >
      {children}
    </PipelineContext.Provider>
  );
};

export const usePipeline = () => {
  const ctx = useContext(PipelineContext);
  if (!ctx) throw new Error('usePipeline must be used within PipelineProvider');
  return ctx;
};
