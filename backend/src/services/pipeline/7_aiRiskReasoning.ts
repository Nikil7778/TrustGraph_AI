import { AIRiskReasoning, DetailedFingerprintMatch, OfficialVerificationResult, RecruitmentDNA } from '../../types';

export function runAIRiskReasoning(
  dna: RecruitmentDNA,
  verification: OfficialVerificationResult,
  match: DetailedFingerprintMatch
): AIRiskReasoning {
  const norm = dna.normalizedAttributes;
  const redFlags: AIRiskReasoning['redFlags'] = [];
  const anomalies: string[] = [];
  const chainOfThought: string[] = [];

  const isOrgProvided = norm.organization.raw && norm.organization.raw !== 'Unspecified / Unknown Organization';
  const isWebProvided = norm.website.normalizedDomain && norm.website.normalizedDomain !== 'not provided';
  const isEmailProvided = norm.email.raw && norm.email.raw !== 'Not Provided';

  chainOfThought.push(`Analyzed submitted content (${isOrgProvided ? norm.organization.raw : 'Unspecified Entity'}).`);

  if (!isOrgProvided && !isWebProvided && !isEmailProvided && !norm.payment.upiId) {
    redFlags.push({
      category: 'Input Validation',
      title: 'Non-Recruitment / Arbitrary Text Input',
      description: 'The submitted text does not contain any recognizable job recruitment offer parameters, notification identifiers, or official contact handles.',
      severity: 'MEDIUM'
    });
    anomalies.push('Missing recruitment notice parameters in submitted input.');
    chainOfThought.push('Validation warning: Input text does not resemble a formal job recruitment notice.');

    return {
      overallRiskSummary: 'Notice: The submitted content does not contain recognizable recruitment offer parameters or official notice identifiers.',
      redFlags,
      anomaliesIdentified: anomalies,
      chainOfThought,
      confidenceScore: 99.0
    };
  }

  // Flag 1: Public Free Email Provider (Gmail/Yahoo)
  if (isEmailProvided && norm.email.isFreeProvider) {
    redFlags.push({
      category: 'Contact Channel',
      title: 'Government Emblem + Gmail/Yahoo Address',
      description: `The recruitment notice claims to represent an official authority (${norm.organization.raw}), but uses a public ${norm.email.domain} email address (${norm.email.raw}). Official communications are strictly issued from verified government domains (.gov.in / .nic.in).`,
      severity: 'HIGH'
    });
    anomalies.push(`Free email provider used: ${norm.email.raw}`);
    chainOfThought.push(`Identified high risk anomaly: Claimed government authority using public ${norm.email.domain} domain.`);
  }

  // Flag 2: Private UPI VPA for Application Fee
  if (norm.payment.isPrivateUpi && norm.payment.upiId && norm.payment.upiId !== 'Not Provided') {
    redFlags.push({
      category: 'Payment Endpoint',
      title: 'Private UPI VPA for Fee Collection',
      description: `Application fee${norm.payment.applicationFee ? ` of ₹${norm.payment.applicationFee}` : ''} is requested via private UPI address (${norm.payment.upiId}). Official recruitment fees are collected exclusively through accredited treasury gateways (e.g. SBI e-Pay, Bharatkosh), never private VPAs.`,
      severity: 'CRITICAL'
    });
    anomalies.push(`Private UPI VPA payment target: ${norm.payment.upiId}`);
    chainOfThought.push(`Identified critical fraud vector: Direct private UPI transfer request (${norm.payment.upiId}).`);
  }

  // Flag 3: Unverified Domain / Typosquatting
  if (isWebProvided && !norm.website.isGovDomain) {
    redFlags.push({
      category: 'Web Portal',
      title: 'Suspicious Non-Government Domain',
      description: `Website domain (${norm.website.normalizedDomain}) lacks valid .gov.in or .nic.in government TLD extensions. Scam portals frequently mimic government site layouts on cheap TLDs.`,
      severity: 'HIGH'
    });
    anomalies.push(`Non-government domain host: ${norm.website.normalizedDomain}`);
    chainOfThought.push(`Domain verification failed: Host ${norm.website.normalizedDomain} is not registered under official TLD.`);
  }

  // Flag 4: High Match with Known Suspicious Fingerprints
  if (match.overallSimilarityPercentage >= 70) {
    redFlags.push({
      category: 'Threat Intelligence Match',
      title: `Match with Known Fraudulent Fingerprint (${match.matchedScamName || 'RF Scam Record'})`,
      description: `Extracted entities exhibit a ${match.overallSimilarityPercentage}% field-by-field similarity match with previously reported scam fingerprint (${match.breakdownSummary}).`,
      severity: match.overallSimilarityPercentage >= 85 ? 'CRITICAL' : 'HIGH'
    });
    anomalies.push(`Threat DB Match: ${match.matchedScamName} (${match.overallSimilarityPercentage}%)`);
    chainOfThought.push(`Fingerprint cross-comparison matched active threat intelligence record ${match.matchedScamId}.`);
  }

  // Summary logic
  const criticalCount = redFlags.filter(f => f.severity === 'CRITICAL').length;
  const highCount = redFlags.filter(f => f.severity === 'HIGH').length;

  let overallSummary = 'This recruitment notice displays classic fraud markers associated with advance-fee job scams.';
  if (criticalCount >= 2 || (criticalCount >= 1 && highCount >= 2)) {
    overallSummary = `CRITICAL ALERT: High probability fake recruitment. Identified ${redFlags.length} severe red flags including private UPI payments and suspicious domains.`;
  } else if (redFlags.length === 0) {
    overallSummary = 'No significant structural anomalies or suspicious fingerprint matches were identified.';
  }

  return {
    overallRiskSummary: overallSummary,
    redFlags,
    anomaliesIdentified: anomalies,
    chainOfThought,
    confidenceScore: 96.5
  };
}

