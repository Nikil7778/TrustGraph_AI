import { Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { AuthRequest } from '../middleware/authMiddleware';

const prisma = new PrismaClient();

export async function getUserHistory(req: AuthRequest, res: Response) {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Unauthorized.' });
    }

    const userId = req.user.id;
    const page = parseInt(req.query.page as string || '1', 10);
    const limit = parseInt(req.query.limit as string || '20', 10);
    const search = (req.query.search as string || '').trim();
    const riskLevel = req.query.riskLevel as string || '';

    const skip = (page - 1) * limit;

    const whereCondition: any = {
      userId: userId
    };

    if (search) {
      whereCondition.OR = [
        { title: { contains: search } },
        { rawInputContent: { contains: search } }
      ];
    }

    if (riskLevel && riskLevel !== 'ALL') {
      whereCondition.riskLevel = riskLevel;
    }

    const [records, total] = await Promise.all([
      prisma.analysisRecord.findMany({
        where: whereCondition,
        orderBy: { createdAt: 'desc' },
        skip,
        take: limit,
        select: {
          id: true,
          userId: true,
          title: true,
          inputType: true,
          status: true,
          trustScore: true,
          riskLevel: true,
          createdAt: true,
          updatedAt: true,
          rawInputContent: true,
          extractedData: true,
          verificationResult: true
        }
      }),
      prisma.analysisRecord.count({ where: whereCondition })
    ]);

    const formattedRecords = records.map(r => {
      let extractedObj: any = {};
      try { extractedObj = JSON.parse(r.extractedData || '{}'); } catch (e) {}

      return {
        id: r.id,
        userId: r.userId,
        title: r.title,
        inputType: r.inputType,
        status: r.status,
        trustScore: r.trustScore,
        riskLevel: r.riskLevel,
        createdAt: r.createdAt,
        updatedAt: r.updatedAt,
        organization: extractedObj.entities?.organization || 'Unspecified Entity',
        notificationId: extractedObj.entities?.notificationId || 'N/A'
      };
    });

    return res.json({
      records: formattedRecords,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit) || 1
    });
  } catch (err: any) {
    console.error('Error fetching user history:', err);
    return res.status(500).json({ error: 'Failed to retrieve analysis history.' });
  }
}

export async function getHistoryItemById(req: AuthRequest, res: Response) {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Unauthorized.' });
    }

    const { id } = req.params;
    const record = await prisma.analysisRecord.findUnique({
      where: { id }
    });

    if (!record) {
      return res.status(404).json({ error: 'Investigation record not found.' });
    }

    // Strict Ownership Enforcement: Must belong to authenticated user OR user must be ADMIN
    if (record.userId !== req.user.id && req.user.role !== 'ADMIN') {
      return res.status(403).json({ error: "Forbidden: You don't have permission to access this investigation." });
    }

    let explainableDashboard: any = {};
    try {
      explainableDashboard = JSON.parse(record.explainableResult || '{}');
    } catch (e) {}

    let pipelineSteps: any = {};
    try {
      pipelineSteps = {
        1: { title: record.title, rawText: record.rawInputContent, inputType: record.inputType },
        2: JSON.parse(record.extractedData || '{}'),
        3: JSON.parse(record.recruitmentDna || '{}'),
        4: JSON.parse(record.evidenceGraph || '{}'),
        5: JSON.parse(record.verificationResult || '{}'),
        6: JSON.parse(record.fingerprintMatches || '{}'),
        7: JSON.parse(record.aiReasoning || '{}'),
        8: { overallScore: record.trustScore, riskLevel: record.riskLevel },
        9: explainableDashboard
      };
    } catch (e) {}

    return res.json({
      recordId: record.id,
      userId: record.userId,
      title: record.title,
      inputType: record.inputType,
      createdAt: record.createdAt,
      trustScore: record.trustScore,
      riskLevel: record.riskLevel,
      dashboard: explainableDashboard,
      pipelineSteps
    });
  } catch (err: any) {
    console.error('Error fetching history item:', err);
    return res.status(500).json({ error: 'Failed to retrieve investigation record.' });
  }
}

export async function deleteHistoryItem(req: AuthRequest, res: Response) {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Unauthorized.' });
    }

    const { id } = req.params;
    const record = await prisma.analysisRecord.findUnique({ where: { id } });

    if (!record) {
      return res.status(404).json({ error: 'Investigation record not found.' });
    }

    // Strict Ownership Enforcement
    if (record.userId !== req.user.id && req.user.role !== 'ADMIN') {
      return res.status(403).json({ error: "Forbidden: You don't have permission to access this investigation." });
    }

    await prisma.analysisRecord.delete({ where: { id } });
    return res.json({ success: true, message: 'Investigation record deleted successfully.' });
  } catch (err: any) {
    console.error('Error deleting history item:', err);
    return res.status(500).json({ error: 'Failed to delete investigation record.' });
  }
}

export async function getAdminHistory(req: AuthRequest, res: Response) {
  try {
    const page = parseInt(req.query.page as string || '1', 10);
    const limit = parseInt(req.query.limit as string || '20', 10);
    const filterUserId = req.query.filterUserId as string || '';
    const skip = (page - 1) * limit;

    const whereCondition: any = {};
    if (filterUserId) {
      whereCondition.userId = filterUserId;
    }

    const [records, total, totalUsers, totalScamsCount] = await Promise.all([
      prisma.analysisRecord.findMany({
        where: whereCondition,
        orderBy: { createdAt: 'desc' },
        skip,
        take: limit,
        include: {
          user: {
            select: { id: true, username: true, role: true }
          }
        }
      }),
      prisma.analysisRecord.count({ where: whereCondition }),
      prisma.user.count(),
      prisma.analysisRecord.count({ where: { riskLevel: 'CRITICAL_SCAM' } })
    ]);

    return res.json({
      records: records.map(r => ({
        id: r.id,
        user: r.user ? { id: r.user.id, username: r.user.username } : { id: 'unknown', username: 'Unassigned' },
        title: r.title,
        inputType: r.inputType,
        trustScore: r.trustScore,
        riskLevel: r.riskLevel,
        createdAt: r.createdAt
      })),
      stats: {
        totalAnalyses: total,
        totalRegisteredUsers: totalUsers,
        criticalScamsDetected: totalScamsCount
      },
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit) || 1
    });
  } catch (err: any) {
    console.error('Admin history error:', err);
    return res.status(500).json({ error: 'Failed to retrieve admin history.' });
  }
}
