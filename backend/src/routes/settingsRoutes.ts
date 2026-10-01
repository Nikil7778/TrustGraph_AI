import { Router } from 'express';
import { getWeights, updateWeights } from '../controllers/settingsController';
import { authenticateToken, requireAdmin } from '../middleware/authMiddleware';

const router = Router();

router.get('/weights', authenticateToken, requireAdmin, getWeights);
router.put('/weights', authenticateToken, requireAdmin, updateWeights);

export default router;
