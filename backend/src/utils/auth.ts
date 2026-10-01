import 'dotenv/config';
import jwt from 'jsonwebtoken';
import { Response } from 'express';

export const SESSION_COOKIE = 'jobguard_session';
export const SESSION_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;
export const JWT_SECRET = process.env.JWT_SECRET || 'development-only-jobguard-secret-change-before-deploying';

export function normalizeUsername(username: string): string {
  return username.trim().toLocaleLowerCase('en-US');
}

export function isValidUsername(username: string): boolean {
  return /^[a-zA-Z0-9_]{3,24}$/.test(username);
}

export function issueSessionCookie(res: Response, userId: string): void {
  const token = jwt.sign({ sub: userId }, JWT_SECRET, { expiresIn: '7d' });
  const secure = process.env.NODE_ENV === 'production' ? '; Secure' : '';
  res.setHeader(
    'Set-Cookie',
    `${SESSION_COOKIE}=${token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${SESSION_MAX_AGE_MS / 1000}${secure}`
  );
}

export function clearSessionCookie(res: Response): void {
  const secure = process.env.NODE_ENV === 'production' ? '; Secure' : '';
  res.setHeader('Set-Cookie', `${SESSION_COOKIE}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0${secure}`);
}

export function readSessionToken(cookieHeader = ''): string | null {
  const item = cookieHeader.split(';').map(part => part.trim()).find(part => part.startsWith(`${SESSION_COOKIE}=`));
  return item ? decodeURIComponent(item.slice(SESSION_COOKIE.length + 1)) : null;
}

export function safeUser(user: {
  id: string;
  username: string | null;
  role: string;
  createdAt?: Date;
  lastLogin?: Date | null;
}) {
  return {
    id: user.id,
    username: user.username || '',
    role: user.role,
    ...(user.createdAt ? { createdAt: user.createdAt } : {}),
    ...(user.lastLogin ? { lastLogin: user.lastLogin } : {})
  };
}