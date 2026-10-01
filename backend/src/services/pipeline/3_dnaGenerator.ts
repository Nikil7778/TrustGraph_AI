import crypto from 'crypto';
import { ExtractedEntities, RecruitmentDNA } from '../../types';
import { isOfficialGovDomain, normalizePhone, normalizeUPI } from '../../utils/similarity';

export function generateRecruitmentDNA(entities: ExtractedEntities, rawText: string): RecruitmentDNA {
  const orgRaw = entities.organization || 'Unknown Organization';
  const orgNorm = orgRaw.toUpperCase().trim();
  
  const notifRaw = entities.notificationId || 'N/A';
  const notifNorm = notifRaw.toUpperCase().trim();

  const webRaw = entities.website || '';
  const domainNorm = webRaw.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0].toLowerCase();
  const isGovDomain = isOfficialGovDomain(domainNorm);

  const emailRaw = entities.email || '';
  const emailDomain = emailRaw.split('@')[1] ? emailRaw.split('@')[1].toLowerCase() : '';
  const isFreeProvider = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'rediffmail.com'].includes(emailDomain);

  const phoneRaw = entities.phone || '';
  const phoneNorm = normalizePhone(phoneRaw);

  const upiRaw = entities.upiDetails || '';
  const upiNorm = normalizeUPI(upiRaw);
  const isPrivateUpi = Boolean(upiNorm && !upiNorm.includes('gov') && !upiNorm.includes('nic'));

  // Generate cryptographic signatures
  const docHash = crypto.createHash('sha256').update(rawText || 'sample').digest('hex').substring(0, 16);
  const fingerprintHash = crypto.createHash('sha256')
    .update(`${orgNorm}|${domainNorm}|${emailDomain}|${phoneNorm}|${upiNorm}`)
    .digest('hex')
    .substring(0, 24);

  const dnaId = `RDNA-${docHash.substring(0, 4).toUpperCase()}-${fingerprintHash.substring(0, 4).toUpperCase()}-${Date.now().toString(36).substring(2, 6).toUpperCase()}`;

  return {
    dnaId,
    canonicalHash: `0x${docHash}${fingerprintHash.substring(0, 8)}`,
    createdAt: new Date().toISOString(),
    normalizedAttributes: {
      organization: {
        raw: orgRaw,
        normalized: orgNorm,
        alias: orgNorm.replace(/[^A-Z]/g, '').substring(0, 6)
      },
      notificationId: {
        raw: notifRaw,
        normalized: notifNorm
      },
      website: {
        raw: webRaw,
        normalizedDomain: domainNorm,
        isGovDomain: isGovDomain
      },
      email: {
        raw: emailRaw,
        domain: emailDomain,
        isFreeProvider: isFreeProvider
      },
      phone: {
        raw: phoneRaw,
        normalized: phoneNorm
      },
      payment: {
        upiId: upiNorm || null,
        applicationFee: entities.applicationFee,
        paymentGateway: 'Direct UPI / QR Code',
        isPrivateUpi: isPrivateUpi
      },
      media: {
        qrCodeData: entities.qrCode || null,
        logoHash: 'emblem_phash_89a7b'
      },
      timeline: {
        publishDate: entities.publishDate,
        lastDateToApply: entities.lastDateToApply
      },
      jobMetadata: {
        designation: entities.jobDetails.designation || 'Staff Recruitment',
        totalVacancies: entities.jobDetails.totalVacancies,
        salaryRange: entities.jobDetails.salaryRange
      }
    },
    fingerprintHash
  };
}
