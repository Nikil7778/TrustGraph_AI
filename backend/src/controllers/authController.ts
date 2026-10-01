import { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import { AuthRequest } from '../middleware/authMiddleware';
import { clearSessionCookie, isValidUsername, issueSessionCookie, normalizeUsername, safeUser } from '../utils/auth';

const prisma = new PrismaClient();

export async function checkUsername(req: Request, res: Response) {
  try {
    const username = String(req.params.username || '').trim();
    if (!isValidUsername(username)) {
      return res.status(200).json({ available: false, reason: 'INVALID_USERNAME' });
    }

    const usernameNormalized = normalizeUsername(username);
    if (usernameNormalized === 'admin') {
      return res.json({ available: false, reason: 'RESERVED_USERNAME' });
    }

    const existing = await prisma.user.findUnique({ where: { usernameNormalized } });
    return res.json(existing
      ? { available: false, reason: 'USERNAME_EXISTS' }
      : { available: true });
  } catch {
    return res.status(500).json({ error: 'Unable to check username availability.' });
  }
}

export async function register(req: Request, res: Response) {
  try {
    const username = typeof req.body.username === 'string' ? req.body.username.trim() : '';
    const password = typeof req.body.password === 'string' ? req.body.password : '';
    if (!isValidUsername(username)) {
      return res.status(400).json({ error: 'Username must be 3-24 characters using letters, numbers, or underscores.' });
    }
    const usernameNormalized = normalizeUsername(username);
    if (usernameNormalized === 'admin') {
      return res.status(400).json({ error: 'This username is reserved. Please try another username.' });
    }
    if (password.length < 8 || Buffer.byteLength(password, 'utf8') > 72) {
      return res.status(400).json({ error: 'Password must be at least 8 characters and no more than 72 bytes.' });
    }

    const passwordHash = await bcrypt.hash(password, 12);
    const user = await prisma.user.create({
      data: {
        username,
        usernameNormalized,
        passwordHash,
        role: 'USER'
      }
    });
    issueSessionCookie(res, user.id);
    return res.status(201).json({ user: safeUser(user), message: 'Account created successfully.' });
  } catch (error: any) {
    if (error?.code === 'P2002') return res.status(409).json({ error: 'Username already exists. Please try another username.' });
    return res.status(500).json({ error: 'Unable to create account.' });
  }
}

export async function login(req: Request, res: Response) {
  try {
    const username = typeof req.body.username === 'string' ? req.body.username.trim() : '';
    const password = typeof req.body.password === 'string' ? req.body.password : '';
    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required.' });
    }
    const user = await prisma.user.findUnique({ where: { usernameNormalized: normalizeUsername(username) } });
    if (!user || !user.passwordHash || !(await bcrypt.compare(password, user.passwordHash))) {
      return res.status(401).json({ error: 'Incorrect username or password.' });
    }

    const updatedUser = await prisma.user.update({
      where: { id: user.id },
      data: { lastLogin: new Date() }
    });
    issueSessionCookie(res, updatedUser.id);
    return res.json({ user: safeUser(updatedUser), message: 'Login successful.' });
  } catch {
    return res.status(500).json({ error: 'Unable to log in.' });
  }
}

export function logout(_req: Request, res: Response) {
  clearSessionCookie(res);
  return res.json({ success: true });
}

export async function getMe(req: AuthRequest, res: Response) {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Unauthorized.' });
    }

    const user = await prisma.user.findUnique({ where: { id: req.user.id } });

    if (!user) {
      return res.status(404).json({ error: 'User not found.' });
    }

    return res.json(safeUser(user));
  } catch {
    return res.status(500).json({ error: 'Failed to fetch user profile.' });
  }
}
