import {
  AIRiskReasoning,
  DetailedFingerprintMatch,
  EvidenceGraphData,
  ExplainableResultDashboard,
  OfficialVerificationResult,
  RecruitmentDNA,
  TrustScoreBreakdown
} from '../../types';

export function composeExplainableResult(
  analysisId: string,
  title: string,
  dna: RecruitmentDNA,
  graph: EvidenceGraphData,
  verification: OfficialVerificationResult,
  match: DetailedFingerprintMatch,
  reasoning: AIRiskReasoning,
  trustScore: TrustScoreBreakdown
): ExplainableResultDashboard {
  const actionItems: string[] = [];

  if (trustScore.overallScore < 40) {
    actionItems.push('Do not transfer money to the provided UPI handle or QR code under any circumstances.');
    actionItems.push(`Verify official notifications directly on the accredited portal (${verification.officialOrgName || 'Official Portal'}).`);
    actionItems.push('Report this fraudulent recruitment notification to Cyber Crime Helpline (1930) or PIB Fact Check.');
  } else if (trustScore.overallScore < 75) {
    actionItems.push('Double check email domain suffix (.gov.in / .nic.in).');
    actionItems.push('Contact official recruitment helpline before submitting documents.');
  } else {
    actionItems.push('Ensure you submit your application only through the verified domain URL.');
    actionItems.push('Keep transaction receipt of fee paid via official e-pay gateway.');
  }

  return {
    analysisId,
    title,
    trustScore,
    recruitmentDna: dna,
    fingerprintMatch: match,
    officialVerification: verification,
    aiReasoning: reasoning,
    evidenceGraph: graph,
    fieldByFieldComparison: match.fieldMatches,
    actionItems
  };
}
