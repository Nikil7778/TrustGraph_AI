import { Router } from 'express';
import rateLimit from 'express-rate-limit';
import { checkUsername, register, login, logout, getMe } from '../controllers/authController';
import { authenticateToken } from '../middleware/authMiddleware';

const router = Router();
const authLimiter = rateLimit({ windowMs: 15 * 60 * 1000, limit: 20, standardHeaders: true, legacyHeaders: false });
router.get('/check-username/:username', checkUsername);
router.post('/signup', authLimiter, register);
router.post('/register', authLimiter, register);
router.post('/login', authLimiter, login);
router.post('/logout', logout);
router.get('/me', authenticateToken, getMe);

export default router;
