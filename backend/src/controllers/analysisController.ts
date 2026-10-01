import { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { AuthRequest } from '../middleware/authMiddleware';
import { runFullPipeline } from '../services/pipelineEngine';

const prisma = new PrismaClient();

export async function createAnalysis(req: AuthRequest, res: Response): Promise<void> {
  try {
    if (!req.user) {
      res.status(401).json({ success: false, error: 'Unauthorized.' });
      return;
    }
    const { type, content, url } = req.body;
    const file = req.file;

    const inputType = type || (file ? (file.mimetype.includes('pdf') ? 'PDF' : 'IMAGE') : url ? 'URL' : 'TEXT');

    const result = await runFullPipeline({
      type: inputType,
      content,
      file,
      url,
      userId: req.user.id
    });

    res.status(201).json({
      success: true,
      data: result
    });
  } catch (error: any) {
    console.error('Error creating analysis:', error);
    res.status(500).json({ success: false, error: error.message || 'Internal Server Error' });
  }
}

export async function getAnalysisById(req: AuthRequest, res: Response): Promise<void> {
  try {
    const { id } = req.params;
    const record = await prisma.analysisRecord.findUnique({ where: { id } });

    if (!record) {
      res.status(404).json({ success: false, error: 'Analysis record not found' });
      return;
    }

    if (record.userId !== req.user?.id && req.user?.role !== 'ADMIN') {
      res.status(403).json({ success: false, error: "Forbidden: You don't have permission to access this investigation." });
      return;
    }

    const dashboard = JSON.parse(record.explainableResult || '{}');

    res.json({
      success: true,
      data: {
        id: record.id,
        title: record.title,
        inputType: record.inputType,
        trustScore: record.trustScore,
        riskLevel: record.riskLevel,
        createdAt: record.createdAt,
        dashboard
      }
    });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
}

export async function getAnalysisHistory(req: AuthRequest, res: Response): Promise<void> {
  try {
    const userId = req.user?.id;
    const records = await prisma.analysisRecord.findMany({
      where: userId ? { userId } : {},
      orderBy: { createdAt: 'desc' },
      take: 50
    });

    const history = records.map((r: any) => ({
      id: r.id,
      title: r.title,
      inputType: r.inputType,
      trustScore: r.trustScore,
      riskLevel: r.riskLevel,
      status: r.status,
      createdAt: r.createdAt
    }));

    res.json({ success: true, data: history });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
}
