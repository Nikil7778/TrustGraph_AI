import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { PrismaClient } from '@prisma/client';
import { JWT_SECRET, readSessionToken, clearSessionCookie } from '../utils/auth';

const prisma = new PrismaClient();

export interface AuthenticatedUser {
  id: string;
  username: string;
  role: string;
}

export interface AuthRequest extends Request {
  user?: AuthenticatedUser;
}

export async function authenticateToken(req: AuthRequest, res: Response, next: NextFunction) {
  const token = readSessionToken(req.headers.cookie);
  if (!token) {
    return res.status(401).json({ error: 'Unauthorized.' });
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as jwt.JwtPayload;
    if (typeof decoded.sub !== 'string') throw new Error('Invalid session');

    const user = await prisma.user.findUnique({
      where: { id: decoded.sub },
      select: { id: true, username: true, role: true }
    });
    if (!user?.username) {
      clearSessionCookie(res);
      return res.status(401).json({ error: 'Unauthorized.' });
    }

    req.user = { id: user.id, username: user.username, role: user.role };
    next();
  } catch {
    clearSessionCookie(res);
    return res.status(401).json({ error: 'Unauthorized.' });
  }
}

export function requireAdmin(req: AuthRequest, res: Response, next: NextFunction) {
  if (!req.user) {
    return res.status(401).json({ error: 'Unauthorized: Authentication required.' });
  }

  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: "Forbidden: Administrator access required." });
  }

  next();
}
