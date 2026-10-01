import { Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { AuthRequest } from '../middleware/authMiddleware';

const prisma = new PrismaClient();

export async function getAdminDashboard(_req: AuthRequest, res: Response) {
  try {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const [totalUsers, totalAnalyses, analysesToday, suspicious, genuine, needsReview, recentActivity] = await Promise.all([
      prisma.user.count(),
      prisma.analysisRecord.count(),
      prisma.analysisRecord.count({ where: { createdAt: { gte: today } } }),
      prisma.analysisRecord.count({ where: { riskLevel: { in: ['HIGH_RISK', 'CRITICAL_SCAM'] } } }),
      prisma.analysisRecord.count({ where: { riskLevel: { in: ['VERIFIED_GENUINE', 'LOW_RISK'] } } }),
      prisma.analysisRecord.count({ where: { riskLevel: 'MEDIUM_RISK' } }),
      prisma.analysisRecord.findMany({
        take: 10,
        orderBy: { createdAt: 'desc' },
        select: {
          id: true,
          title: true,
          inputType: true,
          riskLevel: true,
          trustScore: true,
          status: true,
          createdAt: true,
          user: { select: { username: true } }
        }
      })
    ]);

    return res.json({
      overview: { totalUsers, totalAnalyses, analysesToday, suspicious, genuine, needsReview },
      recentActivity: recentActivity.map(record => ({
        ...record,
        username: record.user?.username || 'Unknown user',
        user: undefined
      }))
    });
  } catch {
    return res.status(500).json({ error: 'Unable to load the admin dashboard.' });
  }
}

export async function getAdminUsers(req: AuthRequest, res: Response) {
  try {
    const page = Math.max(1, Number(req.query.page) || 1);
    const limit = Math.min(100, Math.max(1, Number(req.query.limit) || 50));
    const [users, total] = await Promise.all([
      prisma.user.findMany({
        skip: (page - 1) * limit,
        take: limit,
        orderBy: { createdAt: 'desc' },
        select: {
          id: true,
          username: true,
          role: true,
          createdAt: true,
          lastLogin: true,
          _count: { select: { analyses: true } }
        }
      }),
      prisma.user.count()
    ]);
    return res.json({ users, total, page, limit });
  } catch {
    return res.status(500).json({ error: 'Unable to load users.' });
  }
}

export async function getAdminAnalyses(req: AuthRequest, res: Response) {
  try {
    const page = Math.max(1, Number(req.query.page) || 1);
    const limit = Math.min(100, Math.max(1, Number(req.query.limit) || 50));
    const [records, total] = await Promise.all([
      prisma.analysisRecord.findMany({
        skip: (page - 1) * limit,
        take: limit,
        orderBy: { createdAt: 'desc' },
        select: {
          id: true,
          title: true,
          inputType: true,
          status: true,
          trustScore: true,
          riskLevel: true,
          createdAt: true,
          recruitmentDna: true,
          fingerprintMatches: true,
          user: { select: { username: true } }
        }
      }),
      prisma.analysisRecord.count()
    ]);
    return res.json({
      records: records.map(record => {
        let dna: any = {};
        let fingerprintMatches: any = {};
        try { dna = JSON.parse(record.recruitmentDna || '{}'); } catch { /* Keep malformed legacy records inspectable. */ }
        try { fingerprintMatches = JSON.parse(record.fingerprintMatches || '{}'); } catch { /* Keep malformed legacy records inspectable. */ }
        const attributes = dna.normalizedAttributes || {};
        return {
          id: record.id,
          title: record.title,
          username: record.user?.username || 'Unknown user',
          inputType: record.inputType,
          status: record.status,
          organization: attributes.organization?.normalized || 'N/A',
          trustScore: record.trustScore,
          riskLevel: record.riskLevel,
          createdAt: record.createdAt,
          dna: {
            dnaId: dna.dnaId || 'N/A',
            organization: attributes.organization?.normalized || 'N/A',
            notificationId: attributes.notificationId?.normalized || 'N/A',
            website: attributes.website?.normalizedDomain || 'N/A',
            email: attributes.email?.raw || 'N/A',
            phone: attributes.phone?.normalized || 'N/A',
            upi: attributes.payment?.upiId || 'N/A',
            qr: attributes.media?.qrCodeData || 'N/A',
            logo: attributes.media?.logoHash || 'N/A',
            similarity: fingerprintMatches.overallSimilarityPercentage ?? 'N/A',
            matchedFingerprint: fingerprintMatches.matchedScamName || 'N/A'
          },
          similarity: fingerprintMatches.overallSimilarityPercentage ?? 'N/A'
        };
      }),
      total,
      page,
      limit
    });
  } catch {
    return res.status(500).json({ error: 'Unable to load analyses.' });
  }
}

export async function getAdminFingerprints(_req: AuthRequest, res: Response) {
  try {
    const fingerprints = await prisma.knownSuspiciousFingerprint.findMany({ orderBy: { createdAt: 'desc' } });
    return res.json({ fingerprints: fingerprints.map(fingerprint => ({
      id: fingerprint.id,
      scamName: fingerprint.scamName,
      organization: fingerprint.targetOrganization,
      source: fingerprint.notes || 'Threat intelligence registry',
      riskClassification: fingerprint.threatLevel,
      riskScore: fingerprint.threatLevel === 'CRITICAL_SCAM' ? 100 : fingerprint.threatLevel === 'HIGH_RISK' ? 80 : 60,
      matchedCharacteristics: {
        websites: JSON.parse(fingerprint.suspiciousWebsites || '[]'),
        emails: JSON.parse(fingerprint.suspiciousEmails || '[]'),
        phones: JSON.parse(fingerprint.suspiciousPhones || '[]'),
        payments: JSON.parse(fingerprint.upiDetails || '[]'),
        qrCodes: JSON.parse(fingerprint.qrCodes || '[]'),
        logos: JSON.parse(fingerprint.logoHashes || '[]')
      },
      createdAt: fingerprint.createdAt
    })) });
  } catch {
    return res.status(500).json({ error: 'Unable to load suspicious fingerprints.' });
  }
}