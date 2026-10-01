import { PrismaClient } from '@prisma/client';
import { Request, Response } from 'express';

const prisma = new PrismaClient();

export async function getThreatIntelligence(req: Request, res: Response): Promise<void> {
  try {
    const records = await prisma.knownSuspiciousFingerprint.findMany({
      orderBy: { updatedAt: 'desc' }
    });

    const formatted = records.map(r => ({
      ...r,
      suspiciousWebsites: JSON.parse(r.suspiciousWebsites || '[]'),
      suspiciousEmails: JSON.parse(r.suspiciousEmails || '[]'),
      suspiciousPhones: JSON.parse(r.suspiciousPhones || '[]'),
      upiDetails: JSON.parse(r.upiDetails || '[]'),
      qrCodes: JSON.parse(r.qrCodes || '[]'),
      logoHashes: JSON.parse(r.logoHashes || '[]')
    }));

    res.json({ success: true, data: formatted });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
}
