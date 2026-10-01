import { PrismaClient } from '@prisma/client';
import { Request, Response } from 'express';

const prisma = new PrismaClient();

export async function getOfficialRegistry(req: Request, res: Response): Promise<void> {
  try {
    const records = await prisma.officialRegistry.findMany({
      orderBy: { organizationName: 'asc' }
    });

    const formatted = records.map(r => ({
      ...r,
      officialWebsites: JSON.parse(r.officialWebsites || '[]'),
      officialEmails: JSON.parse(r.officialEmails || '[]'),
      officialPhones: JSON.parse(r.officialPhones || '[]'),
      notificationIds: JSON.parse(r.notificationIds || '[]'),
      verifiedDomains: JSON.parse(r.verifiedDomains || '[]')
    }));

    res.json({ success: true, data: formatted });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
}
