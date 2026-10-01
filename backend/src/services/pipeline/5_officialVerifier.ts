import { OfficialVerificationResult, OfficialVerificationRow, RecruitmentDNA } from '../../types';

export interface OfficialRegistryRecord {
  id: string;
  organizationName: string;
  officialWebsites: string[];
  officialEmails: string[];
  officialPhones: string[];
  notificationIds: string[];
  officialFees: number | null;
  verifiedDomains: string[];
}

function toHttpsUrl(value?: string): string | null {
  if (!value) return null;
  const candidate = value.startsWith('http') ? value : `https://${value}`;
  try {
    const parsed = new URL(candidate);
    return parsed.protocol === 'https:' ? parsed.toString() : null;
  } catch {
    return null;
  }
}

export function verifyAgainstOfficialRegistry(
  dna: RecruitmentDNA,
  officialRegistry: OfficialRegistryRecord[]
): OfficialVerificationResult {
  const norm = dna.normalizedAttributes;
  const claimedOrg = norm.organization.normalized;
  const isOrgProvided = Boolean(
    claimedOrg &&
    claimedOrg !== 'UNSPECIFIED / UNKNOWN ORGANIZATION' &&
    claimedOrg !== 'UNSPECIFIED' &&
    claimedOrg !== 'NOT IDENTIFIED IN INPUT'
  );

  const isWebProvided = Boolean(norm.website.normalizedDomain && norm.website.normalizedDomain !== 'not provided' && norm.website.normalizedDomain !== '');
  const isEmailProvided = Boolean(norm.email.raw && norm.email.raw !== 'not provided' && norm.email.raw !== '');
  const isPhoneProvided = Boolean(norm.phone.normalized && norm.phone.normalized !== 'not provided' && norm.phone.normalized !== '');
  const isNotifProvided = Boolean(norm.notificationId.normalized && norm.notificationId.normalized !== 'NOT PROVIDED' && norm.notificationId.normalized !== '');

  // Find matching official organization in official registry allowlist
  const matchedRecord = (isOrgProvided || isWebProvided)
    ? officialRegistry.find(rec => 
        (isOrgProvided && (rec.organizationName.toUpperCase().includes(claimedOrg) || claimedOrg.includes(rec.organizationName.toUpperCase()))) ||
        (isWebProvided && rec.verifiedDomains.some(d => d.includes(norm.website.normalizedDomain) || norm.website.normalizedDomain.includes(d)))
      )
    : undefined;

  const notes: string[] = [];
  const comparisonTable: OfficialVerificationRow[] = [];

  // Helper to build standardized table row
  const createRow = (
    field: string,
    submitted: string,
    official: string,
    status: OfficialVerificationRow['status'],
    statusLabel: string
  ): OfficialVerificationRow => ({
    field,
    submitted,
    official,
    status,
    statusLabel
  });

  // 1. Organization Row
  const orgSub = isOrgProvided ? norm.organization.raw : 'Not Identified in Input';
  if (matchedRecord) {
    comparisonTable.push(createRow('Organization', orgSub, matchedRecord.organizationName, 'EXACT_MATCH', '✓ Match'));
  } else {
    comparisonTable.push(createRow(
      'Organization',
      orgSub,
      'No verified reference in official source',
      isOrgProvided ? 'UNKNOWN' : 'NOT_PROVIDED',
      isOrgProvided ? '⚠ Unverified Entity' : '— Not Provided'
    ));
  }

  // 2. Notification ID Row
  const notifSub = isNotifProvided ? norm.notificationId.raw : 'Not Provided in Input';
  if (matchedRecord) {
    const isNotifValid = matchedRecord.notificationIds.some(id => id.toUpperCase() === norm.notificationId.normalized);
    comparisonTable.push(createRow(
      'Notification ID',
      notifSub,
      isNotifValid ? norm.notificationId.raw : (matchedRecord.notificationIds[0] || 'No verified notification ID in source'),
      isNotifValid ? 'EXACT_MATCH' : (isNotifProvided ? 'MISMATCH' : 'NOT_PROVIDED'),
      isNotifValid ? '✓ Verified ID' : (isNotifProvided ? '✕ Unverified ID' : '— Not Provided')
    ));
  } else {
    comparisonTable.push(createRow(
      'Notification ID',
      notifSub,
      'No verified reference in official source',
      isNotifProvided ? 'UNKNOWN' : 'NOT_PROVIDED',
      isNotifProvided ? 'UNKNOWN' : '— Not Provided'
    ));
  }

  // 3. Website / Domain Row
  const webSub = isWebProvided ? norm.website.raw || norm.website.normalizedDomain : 'Not Provided in Input';
  let isWebOfficial = false;
  if (matchedRecord) {
    isWebOfficial = matchedRecord.officialWebsites.some(w => 
      w.toLowerCase().includes(norm.website.normalizedDomain) || norm.website.normalizedDomain.includes(w.toLowerCase())
    );
    comparisonTable.push(createRow(
      'Website Domain',
      webSub,
      matchedRecord.officialWebsites[0] || matchedRecord.verifiedDomains[0] || 'Official Domain',
      isWebOfficial ? 'EXACT_MATCH' : (isWebProvided ? 'LOOKALIKE_IMPERSONATION' : 'NOT_PROVIDED'),
      isWebOfficial ? '✓ Official Domain' : (isWebProvided ? '✕ Lookalike Impersonation' : '— Not Provided')
    ));
  } else {
    comparisonTable.push(createRow(
      'Website Domain',
      webSub,
      norm.website.isGovDomain ? 'Official .gov.in Portal' : 'No verified domain in official source',
      norm.website.isGovDomain ? 'VERIFIED' : (isWebProvided ? 'UNKNOWN' : 'NOT_PROVIDED'),
      norm.website.isGovDomain ? '✓ Official TLD' : (isWebProvided ? '⚠ Unverified Domain' : '— Not Provided')
    ));
  }

  // 4. Contact Email Row
  const emailSub = isEmailProvided ? norm.email.raw : 'Not Provided in Input';
  let isEmailOfficial = false;
  if (matchedRecord) {
    isEmailOfficial = matchedRecord.officialEmails.some(e => 
      e.toLowerCase() === norm.email.raw.toLowerCase() || norm.email.domain.endsWith(e.split('@')[1] || '')
    );
    comparisonTable.push(createRow(
      'Contact Email',
      emailSub,
      matchedRecord.officialEmails[0] || 'No verified email in source',
      isEmailOfficial ? 'EXACT_MATCH' : (norm.email.isFreeProvider ? 'SUSPICIOUS' : (isEmailProvided ? 'MISMATCH' : 'NOT_PROVIDED')),
      isEmailOfficial ? '✓ Official Email' : (norm.email.isFreeProvider ? '✕ Public Gmail/Yahoo' : (isEmailProvided ? '✕ Unverified Email' : '— Not Provided'))
    ));
  } else {
    comparisonTable.push(createRow(
      'Contact Email',
      emailSub,
      'No verified email in official source',
      norm.email.isFreeProvider ? 'SUSPICIOUS' : (isEmailProvided ? 'UNKNOWN' : 'NOT_PROVIDED'),
      norm.email.isFreeProvider ? '✕ Public Free Email' : (isEmailProvided ? 'UNKNOWN' : '— Not Provided')
    ));
  }

  // 5. Helpdesk Phone Row
  const phoneSub = isPhoneProvided ? norm.phone.raw || norm.phone.normalized : 'Not Provided in Input';
  let isPhoneOfficial = false;
  if (matchedRecord) {
    isPhoneOfficial = matchedRecord.officialPhones.some(p => p.replace(/\D/g, '').endsWith(norm.phone.normalized.slice(-10)));
    comparisonTable.push(createRow(
      'Helpdesk Phone',
      phoneSub,
      matchedRecord.officialPhones[0] || 'No verified phone in source',
      isPhoneOfficial ? 'EXACT_MATCH' : (isPhoneProvided ? 'MISMATCH' : 'NOT_PROVIDED'),
      isPhoneOfficial ? '✓ Official Phone' : (isPhoneProvided ? '✕ Unverified Phone' : '— Not Provided')
    ));
  } else {
    comparisonTable.push(createRow(
      'Helpdesk Phone',
      phoneSub,
      'No verified phone in official source',
      isPhoneProvided ? 'UNKNOWN' : 'NOT_PROVIDED',
      isPhoneProvided ? 'UNKNOWN' : '— Not Provided'
    ));
  }

  // 6. Application Fee Row
  const feeSub = norm.payment.applicationFee !== null && norm.payment.applicationFee !== undefined ? `₹${norm.payment.applicationFee}` : 'Not Mentioned in Input';
  if (matchedRecord && matchedRecord.officialFees !== null) {
    const feeMatch = norm.payment.applicationFee === matchedRecord.officialFees;
    comparisonTable.push(createRow(
      'Application Fee',
      feeSub,
      `₹${matchedRecord.officialFees} (Treasury Portal)`,
      feeMatch ? 'EXACT_MATCH' : (norm.payment.applicationFee !== null ? 'MISMATCH' : 'NOT_PROVIDED'),
      feeMatch ? '✓ Fee Matches' : (norm.payment.applicationFee !== null ? '✕ Fee Discrepancy' : '— Not Mentioned')
    ));
  } else {
    comparisonTable.push(createRow(
      'Application Fee',
      feeSub,
      'No verified fee in official source',
      norm.payment.applicationFee !== null ? 'UNKNOWN' : 'NOT_PROVIDED',
      norm.payment.applicationFee !== null ? 'UNKNOWN' : '— Not Mentioned'
    ));
  }

  // 7. Payment / UPI Method Row
  const upiSub = norm.payment.upiId ? norm.payment.upiId : 'Not Detected / Not Provided';
  comparisonTable.push(createRow(
    'Payment Method',
    upiSub,
    'Treasury Gateway Only (No Private VPA Allowed)',
    norm.payment.isPrivateUpi ? 'SUSPICIOUS' : (norm.payment.upiId ? 'VERIFIED' : 'NOT_PROVIDED'),
    norm.payment.isPrivateUpi ? '⚠ Private UPI (High Risk)' : (norm.payment.upiId ? '✓ Verified Gateway' : '— No Private VPA')
  ));

  // Compute Verification Notes & Score
  let score = 0;
  if (!matchedRecord) {
    if (norm.website.isGovDomain) {
      score = 40;
      notes.push('Website uses an accredited .gov.in domain, but no matching organization entry was found in the official registry database.');
    } else {
      notes.push('No matching official government recruitment registry record found for claimed parameters.');
    }
  } else {
    if (isWebOfficial) {
      score += 40;
      notes.push(`Website matches officially verified portal (${matchedRecord.officialWebsites[0] || matchedRecord.verifiedDomains[0]}).`);
    } else if (isWebProvided) {
      notes.push(`Website (${norm.website.normalizedDomain}) differs from official portal (${matchedRecord.officialWebsites[0] || 'N/A'}). Potential lookalike impersonation domain.`);
    }

    if (isEmailOfficial) {
      score += 20;
      notes.push('Contact email matches official department communications roster.');
    } else if (isEmailProvided && norm.email.isFreeProvider) {
      notes.push('Official government notifications never mandate payments or issue notices via free public email providers (Gmail/Yahoo).');
    }

    if (isPhoneOfficial) {
      score += 15;
      notes.push('Helpdesk phone number is listed in official government directory.');
    }

    const isNotifValid = matchedRecord.notificationIds.some(id => id.toUpperCase() === norm.notificationId.normalized);
    if (isNotifValid) {
      score += 15;
      notes.push('Notification reference ID matches official gazette notice.');
    }

    if (matchedRecord.officialFees !== null && norm.payment.applicationFee === matchedRecord.officialFees) {
      score += 10;
      notes.push('Claimed application fee matches official gazetted fee structure.');
    }

    if (norm.payment.isPrivateUpi) {
      notes.push('Official recruitment fees are deposited via treasury portals (e.g., SBI e-Pay, Bharatkosh), never via private UPI VPAs.');
    }
  }

  return {
    matchedRecordId: matchedRecord ? matchedRecord.id : null,
    officialOrgName: matchedRecord ? matchedRecord.organizationName : (isOrgProvided ? norm.organization.raw : null),
    officialWebsiteUrl: matchedRecord
      ? toHttpsUrl(matchedRecord.officialWebsites[0] || matchedRecord.verifiedDomains[0])
      : null,
    isOrgVerified: Boolean(matchedRecord),
    isWebsiteGovDomain: norm.website.isGovDomain,
    isWebsiteInOfficialList: isWebOfficial,
    isEmailInOfficialList: isEmailOfficial,
    isPhoneInOfficialList: isPhoneOfficial,
    isNotificationIdValid: matchedRecord ? matchedRecord.notificationIds.some(id => id.toUpperCase() === norm.notificationId.normalized) : false,
    feeDiscrepancy: {
      claimedFee: norm.payment.applicationFee,
      officialFee: matchedRecord ? matchedRecord.officialFees : null,
      isMatching: matchedRecord && matchedRecord.officialFees !== null ? norm.payment.applicationFee === matchedRecord.officialFees : false
    },
    verificationScore: score,
    notes,
    comparisonTable
  };
}


