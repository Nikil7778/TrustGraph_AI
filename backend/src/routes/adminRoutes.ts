import { Router } from 'express';
import { getAdminAnalyses, getAdminDashboard, getAdminFingerprints, getAdminUsers } from '../controllers/adminController';
import { authenticateToken, requireAdmin } from '../middleware/authMiddleware';

const router = Router();
router.use(authenticateToken, requireAdmin);
router.get('/dashboard', getAdminDashboard);
router.get('/users', getAdminUsers);
router.get('/analyses', getAdminAnalyses);
router.get('/fingerprints', getAdminFingerprints);

export default router;