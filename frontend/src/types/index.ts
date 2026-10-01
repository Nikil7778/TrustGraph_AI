export type InputType = 'TEXT' | 'PDF' | 'IMAGE' | 'URL';

export type RiskLevel = 
  | 'VERIFIED_GENUINE'
  | 'LOW_RISK'
  | 'MEDIUM_RISK'
  | 'HIGH_RISK'
  | 'CRITICAL_SCAM';

export type MatchType = 'EXACT' | 'SIMILAR' | 'DIFFERENT' | 'MISSING';

export interface ExtractedEntities {
  organization: string | null;
  notificationId: string | null;
  website: string | null;
  email: string | null;
  phone: string | null;
  upiDetails: string | null;
  qrCode: string | null;
  logo: string | null;
  publishDate: string | null;
  lastDateToApply: string | null;
  jobDetails: {
    designation: string | null;
    totalVacancies: number | null;
    salaryRange: string | null;
  };
  applicationFee: number | null;
  otherInformation: string[];
}

export interface RecruitmentDNA {
  dnaId: string;
  canonicalHash: string;
  createdAt: string;
  normalizedAttributes: {
    organization: {
      raw: string;
      normalized: string;
      alias: string;
    };
    notificationId: {
      raw: string;
      normalized: string;
    };
    website: {
      raw: string;
      normalizedDomain: string;
      isGovDomain: boolean;
    };
    email: {
      raw: string;
      domain: string;
      isFreeProvider: boolean;
    };
    phone: {
      raw: string;
      normalized: string;
    };
    payment: {
      upiId: string | null;
      applicationFee: number | null;
      paymentGateway: string | null;
      isPrivateUpi: boolean;
    };
    media: {
      qrCodeData: string | null;
      logoHash: string | null;
    };
    timeline: {
      publishDate: string | null;
      lastDateToApply: string | null;
    };
    jobMetadata: {
      designation: string;
      totalVacancies: number | null;
      salaryRange: string | null;
    };
  };
  fingerprintHash: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'ORGANIZATION' | 'NOTIFICATION' | 'EMAIL' | 'PHONE' | 'WEBSITE' | 'PAYMENT' | 'QR' | 'JOB';
  subText?: string;
  isHighRisk?: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
}

export interface EvidenceGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface OfficialVerificationRow {
  field: string;
  submitted: string;
  official: string;
  status: 'EXACT_MATCH' | 'MATCH' | 'LOOKALIKE_IMPERSONATION' | 'MISMATCH' | 'VERIFIED' | 'SUSPICIOUS' | 'UNKNOWN' | 'NOT_PROVIDED';
  statusLabel: string;
}

export interface OfficialVerificationResult {
  matchedRecordId: string | null;
  officialOrgName: string | null;
  officialWebsiteUrl: string | null;
  isOrgVerified: boolean;
  isWebsiteGovDomain: boolean;
  isWebsiteInOfficialList: boolean;
  isEmailInOfficialList: boolean;
  isPhoneInOfficialList: boolean;
  isNotificationIdValid: boolean;
  feeDiscrepancy: {
    claimedFee: number | null;
    officialFee: number | null;
    isMatching: boolean;
  };
  verificationScore: number;
  notes: string[];
  comparisonTable?: OfficialVerificationRow[];
}

export interface FieldMatchResult {
  fieldName: string;
  weight: number;
  claimedValue: string;
  matchedValue: string;
  matchType: MatchType;
  similarityScore: number;
  contributionToTotal: number;
}

export interface DetailedFingerprintMatch {
  matchedScamId: string | null;
  matchedScamName: string | null;
  scamCategory: string | null;
  fieldMatches: FieldMatchResult[];
  matchedFieldsCount: number;
  totalFieldsEvaluated: number;
  overallSimilarityPercentage: number;
  breakdownSummary: string;
}

export interface AIRiskReasoning {
  overallRiskSummary: string;
  redFlags: Array<{
    category: string;
    title: string;
    description: string;
    severity: 'HIGH' | 'CRITICAL' | 'MEDIUM' | 'LOW';
  }>;
  anomaliesIdentified: string[];
  chainOfThought: string[];
  confidenceScore: number;
}

export interface TrustScoreBreakdown {
  overallScore: number;
  riskLevel: RiskLevel;
  subScores: {
    officialRegistryAlignment: number;
    suspiciousSimilarityPenalty: number;
    riskAnomalyPenalty: number;
  };
  recommendation: string;
}

export interface ExplainableResultDashboard {
  analysisId: string;
  title: string;
  trustScore: TrustScoreBreakdown;
  recruitmentDna: RecruitmentDNA;
  fingerprintMatch: DetailedFingerprintMatch;
  officialVerification: OfficialVerificationResult;
  aiReasoning: AIRiskReasoning;
  evidenceGraph: EvidenceGraphData;
  fieldByFieldComparison: FieldMatchResult[];
  actionItems: string[];
}

export interface AnalysisRecordItem {
  id: string;
  title: string;
  inputType: InputType;
  trustScore: number;
  riskLevel: RiskLevel;
  status: string;
  createdAt: string;
  organization?: string;
  notificationId?: string;
  userId?: string;
}
