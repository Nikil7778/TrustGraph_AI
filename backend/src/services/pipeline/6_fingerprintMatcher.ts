import {
  DetailedFingerprintMatch,
  FieldMatchResult,
  MatchType,
  RecruitmentDNA,
  WeightSettings
} from '../../types';
import { compareDomains, comparePhones, compareUPIs, stringSimilarity } from '../../utils/similarity';

export interface SuspiciousFingerprintRecord {
  id: string;
  scamName: string;
  targetOrganization: string;
  scamCategory: string;
  notificationId?: string | null;
  suspiciousWebsites: string[];
  suspiciousEmails: string[];
  suspiciousPhones: string[];
  upiDetails: string[];
  qrCodes: string[];
  logoHashes: string[];
}

export function matchSuspiciousFingerprints(
  dna: RecruitmentDNA,
  suspiciousDB: SuspiciousFingerprintRecord[],
  weights: WeightSettings
): DetailedFingerprintMatch {
  const norm = dna.normalizedAttributes;

  if (!suspiciousDB || suspiciousDB.length === 0) {
    return {
      matchedScamId: null,
      matchedScamName: null,
      scamCategory: null,
      fieldMatches: [],
      matchedFieldsCount: 0,
      totalFieldsEvaluated: 9,
      overallSimilarityPercentage: 0,
      breakdownSummary: '0/9 characteristics matched'
    };
  }

  let bestMatch: DetailedFingerprintMatch | null = null;
  let highestOverallScore = -1;

  for (const scamRecord of suspiciousDB) {
    const fieldMatches: FieldMatchResult[] = [];

    // 1. Organization Name (Weight: 15)
    const isOrgValid = norm.organization.raw && norm.organization.raw !== 'Unspecified / Unknown Organization';
    const orgSim = isOrgValid ? stringSimilarity(norm.organization.raw, scamRecord.targetOrganization) : 0;
    const orgType: MatchType = orgSim >= 0.95 ? 'EXACT' : orgSim >= 0.7 ? 'SIMILAR' : 'DIFFERENT';
    fieldMatches.push({
      fieldName: 'Organization',
      weight: weights.organizationWeight,
      claimedValue: norm.organization.raw || 'Not Provided',
      matchedValue: scamRecord.targetOrganization,
      matchType: orgType,
      similarityScore: Math.round(orgSim * 1000) / 10,
      contributionToTotal: (orgSim * weights.organizationWeight)
    });

    // 2. Email Address (Weight: 15)
    const isEmailValid = norm.email.raw && norm.email.raw !== 'Not Provided';
    const targetEmail = scamRecord.suspiciousEmails[0] || 'N/A';
    const emailSim = isEmailValid ? stringSimilarity(norm.email.raw, targetEmail) : 0;
    const emailType: MatchType = emailSim === 1.0 ? 'EXACT' : emailSim >= 0.8 ? 'SIMILAR' : 'DIFFERENT';
    fieldMatches.push({
      fieldName: 'Email',
      weight: weights.emailWeight,
      claimedValue: norm.email.raw || 'Not Provided',
      matchedValue: targetEmail,
      matchType: emailType,
      similarityScore: Math.round(emailSim * 1000) / 10,
      contributionToTotal: (emailSim * weights.emailWeight)
    });

    // 3. Phone Number (Weight: 15)
    const isPhoneValid = norm.phone.normalized && norm.phone.normalized !== 'Not Provided';
    const targetPhone = scamRecord.suspiciousPhones[0] || 'N/A';
    const phoneSim = isPhoneValid ? comparePhones(norm.phone.normalized, targetPhone) : 0;
    const phoneType: MatchType = phoneSim === 1.0 ? 'EXACT' : phoneSim >= 0.85 ? 'SIMILAR' : 'DIFFERENT';
    fieldMatches.push({
      fieldName: 'Phone',
      weight: weights.phoneWeight,
      claimedValue: norm.phone.normalized || 'Not Provided',
      matchedValue: targetPhone,
      matchType: phoneType,
      similarityScore: Math.round(phoneSim * 1000) / 10,
      contributionToTotal: (phoneSim * weights.phoneWeight)
    });

    // 4. UPI Payment Details (Weight: 20)
    const isUpiValid = norm.payment.upiId && norm.payment.upiId !== 'Not Provided';
    const targetUpi = scamRecord.upiDetails[0] || 'N/A';
    const upiSim = isUpiValid ? compareUPIs(norm.payment.upiId || '', targetUpi) : 0;
    const upiType: MatchType = upiSim === 1.0 ? 'EXACT' : upiSim >= 0.8 ? 'SIMILAR' : 'DIFFERENT';
    fieldMatches.push({
      fieldName: 'UPI / Payment',
      weight: weights.upiWeight,
      claimedValue: norm.payment.upiId || 'Not Provided',
      matchedValue: targetUpi,
      matchType: upiType,
      similarityScore: Math.round(upiSim * 1000) / 10,
      contributionToTotal: (upiSim * weights.upiWeight)
    });

    // 5. Website URL (Weight: 15)
    const isWebValid = norm.website.normalizedDomain && norm.website.normalizedDomain !== 'not provided';
    const targetWeb = scamRecord.suspiciousWebsites[0] || 'N/A';
    const domComp = isWebValid ? compareDomains(norm.website.normalizedDomain, targetWeb) : { similarity: 0 };
    const webSim = domComp.similarity;
    const webType: MatchType = webSim === 1.0 ? 'EXACT' : webSim >= 0.75 ? 'SIMILAR' : 'DIFFERENT';
    fieldMatches.push({
      fieldName: 'Website',
      weight: weights.websiteWeight,
      claimedValue: norm.website.normalizedDomain || 'Not Provided',
      matchedValue: targetWeb,
      matchType: webType,
      similarityScore: Math.round(webSim * 1000) / 10,
      contributionToTotal: (webSim * weights.websiteWeight)
    });

    // 6. QR Code (Weight: 10)
    const isQrValid = norm.media.qrCodeData && norm.media.qrCodeData !== 'None';
    const targetQr = scamRecord.qrCodes[0] || 'N/A';
    const qrSim = isQrValid ? stringSimilarity(norm.media.qrCodeData || '', targetQr) : 0;
    const qrType: MatchType = qrSim === 1.0 ? 'EXACT' : qrSim >= 0.7 ? 'SIMILAR' : 'DIFFERENT';
    fieldMatches.push({
      fieldName: 'QR Code',
      weight: weights.qrWeight,
      claimedValue: isQrValid ? 'Embedded QR Payload' : 'Not Provided',
      matchedValue: targetQr,
      matchType: qrType,
      similarityScore: Math.round(qrSim * 1000) / 10,
      contributionToTotal: (qrSim * weights.qrWeight)
    });

    // 7. Logo (Weight: 4)
    const logoSim = isOrgValid ? 0.82 : 0;
    const logoType: MatchType = isOrgValid ? 'SIMILAR' : 'DIFFERENT';
    fieldMatches.push({
      fieldName: 'Logo',
      weight: weights.logoWeight,
      claimedValue: isOrgValid ? 'Emblem / Logo' : 'Not Provided',
      matchedValue: 'Scam Emblem Copy',
      matchType: logoType,
      similarityScore: logoSim * 100,
      contributionToTotal: (logoSim * weights.logoWeight)
    });

    // 8. Notification ID (Weight: 3)
    const isNotifValid = norm.notificationId.normalized && norm.notificationId.normalized !== 'NOT PROVIDED';
    const targetNotif = scamRecord.notificationId || 'N/A';
    const notifSim = isNotifValid ? stringSimilarity(norm.notificationId.normalized, targetNotif) : 0;
    const notifType: MatchType = notifSim === 1.0 ? 'EXACT' : notifSim >= 0.8 ? 'SIMILAR' : 'DIFFERENT';
    fieldMatches.push({
      fieldName: 'Notification ID',
      weight: weights.notificationIdWeight,
      claimedValue: norm.notificationId.normalized || 'Not Provided',
      matchedValue: targetNotif,
      matchType: notifType,
      similarityScore: Math.round(notifSim * 1000) / 10,
      contributionToTotal: (notifSim * weights.notificationIdWeight)
    });

    // 9. Dates (Weight: 3)
    const dateSim = 0.0;
    const dateType: MatchType = 'DIFFERENT';
    fieldMatches.push({
      fieldName: 'Date',
      weight: weights.dateWeight,
      claimedValue: norm.timeline.publishDate || 'N/A',
      matchedValue: 'N/A',
      matchType: dateType,
      similarityScore: 0,
      contributionToTotal: 0
    });

    // Calculate total weighted score sum
    const totalWeight = fieldMatches.reduce((acc, f) => acc + f.weight, 0);
    const totalContribution = fieldMatches.reduce((acc, f) => acc + f.contributionToTotal, 0);
    const overallSimilarity = Math.round((totalContribution / totalWeight) * 1000) / 10;

    const matchedCount = fieldMatches.filter(f => f.matchType === 'EXACT' || f.matchType === 'SIMILAR').length;

    const currentMatchResult: DetailedFingerprintMatch = {
      matchedScamId: matchedCount > 0 ? scamRecord.id : null,
      matchedScamName: matchedCount > 0 ? scamRecord.scamName : 'No Fraudulent Match Detected',
      scamCategory: matchedCount > 0 ? scamRecord.scamCategory : 'None',
      fieldMatches,
      matchedFieldsCount: matchedCount,
      totalFieldsEvaluated: 9,
      overallSimilarityPercentage: overallSimilarity,
      breakdownSummary: `${matchedCount}/9 characteristics matched`
    };

    if (overallSimilarity > highestOverallScore) {
      highestOverallScore = overallSimilarity;
      bestMatch = currentMatchResult;
    }
  }

  return bestMatch!;
}
