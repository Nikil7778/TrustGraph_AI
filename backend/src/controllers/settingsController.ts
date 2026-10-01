import { PrismaClient } from '@prisma/client';
import { Request, Response } from 'express';

const prisma = new PrismaClient();

export async function getWeights(req: Request, res: Response): Promise<void> {
  try {
    let weights = await prisma.systemWeights.findUnique({ where: { id: 'default_weights' } });
    if (!weights) {
      weights = await prisma.systemWeights.create({
        data: {
          id: 'default_weights',
          organizationWeight: 15.0,
          emailWeight: 15.0,
          phoneWeight: 15.0,
          upiWeight: 20.0,
          websiteWeight: 15.0,
          qrWeight: 10.0,
          logoWeight: 4.0,
          notificationIdWeight: 3.0,
          dateWeight: 3.0
        }
      });
    }

    res.json({ success: true, data: weights });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
}

export async function updateWeights(req: Request, res: Response): Promise<void> {
  try {
    const {
      organizationWeight,
      emailWeight,
      phoneWeight,
      upiWeight,
      websiteWeight,
      qrWeight,
      logoWeight,
      notificationIdWeight,
      dateWeight
    } = req.body;

    const updated = await prisma.systemWeights.upsert({
      where: { id: 'default_weights' },
      update: {
        organizationWeight,
        emailWeight,
        phoneWeight,
        upiWeight,
        websiteWeight,
        qrWeight,
        logoWeight,
        notificationIdWeight,
        dateWeight
      },
      create: {
        id: 'default_weights',
        organizationWeight,
        emailWeight,
        phoneWeight,
        upiWeight,
        websiteWeight,
        qrWeight,
        logoWeight,
        notificationIdWeight,
        dateWeight
      }
    });

    res.json({ success: true, data: updated });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
}
