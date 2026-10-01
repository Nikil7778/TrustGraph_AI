import { Router } from 'express';
import { register, login, getMe, getTestAccounts } from '../controllers/authController';
import { authenticateToken } from '../middleware/authMiddleware';

const router = Router();

router.post('/register', register);
router.post('/login', login);
router.get('/me', authenticateToken, getMe);
router.get('/test-accounts', getTestAccounts);

export default router;
