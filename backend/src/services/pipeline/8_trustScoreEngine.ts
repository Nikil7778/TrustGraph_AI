import { AIRiskReasoning, DetailedFingerprintMatch, OfficialVerificationResult, RiskLevel, TrustScoreBreakdown } from '../../types';

export function calculateTrustScore(
  verification: OfficialVerificationResult,
  match: DetailedFingerprintMatch,
  reasoning: AIRiskReasoning
): TrustScoreBreakdown {
  // 1. Official Registry Alignment Sub-Score (0 - 40 points)
  let officialScore = Math.min(40, Math.round((verification.verificationScore / 100) * 40));

  // 2. Suspicious Fingerprint Penalty (0 - 35 points score remaining)
  // Higher match similarity to a scam reduces the score
  const scamSimilarityFraction = match.overallSimilarityPercentage / 100;
  let suspiciousScore = Math.max(0, Math.round(35 * (1 - scamSimilarityFraction)));

  // 3. Risk Anomaly Penalty (0 - 25 points remaining)
  let riskPenalty = 0;
  reasoning.redFlags.forEach(flag => {
    if (flag.severity === 'CRITICAL') riskPenalty += 12;
    else if (flag.severity === 'HIGH') riskPenalty += 8;
    else if (flag.severity === 'MEDIUM') riskPenalty += 4;
  });
  let anomalyScore = Math.max(0, 25 - riskPenalty);

  // Total Score (0 - 100)
  const totalScore = Math.min(100, Math.max(0, officialScore + suspiciousScore + anomalyScore));

  // Classification
  let riskLevel: RiskLevel = 'CRITICAL_SCAM';
  let recommendation = 'DO NOT proceed with this recruitment offer. High risk of financial and data fraud.';

  if (totalScore >= 80) {
    riskLevel = 'VERIFIED_GENUINE';
    recommendation = 'Recruitment offer matches official government registry records. Verified authentic.';
  } else if (totalScore >= 60) {
    riskLevel = 'LOW_RISK';
    recommendation = 'Mostly genuine details, but cross-check application fee links on the official portal.';
  } else if (totalScore >= 40) {
    riskLevel = 'MEDIUM_RISK';
    recommendation = 'Suspicious elements detected. Verify directly through official government helpline.';
  } else if (totalScore >= 20) {
    riskLevel = 'HIGH_RISK';
    recommendation = 'High probability of job scam. Do not pay any fee or share personal identity documents.';
  }

  return {
    overallScore: totalScore,
    riskLevel,
    subScores: {
      officialRegistryAlignment: officialScore,
      suspiciousSimilarityPenalty: suspiciousScore,
      riskAnomalyPenalty: anomalyScore
    },
    recommendation
  };
}
