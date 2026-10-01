import { Router } from 'express';
import { getUserHistory, getHistoryItemById, deleteHistoryItem, getAdminHistory } from '../controllers/historyController';
import { authenticateToken, requireAdmin } from '../middleware/authMiddleware';

const router = Router();

// User-scoped history routes (All require authentication & filter by req.user.id)
router.get('/history', authenticateToken, getUserHistory);
router.get('/history/:id', authenticateToken, getHistoryItemById);
router.delete('/history/:id', authenticateToken, deleteHistoryItem);

// Admin-only history route
router.get('/admin/history', authenticateToken, requireAdmin, getAdminHistory);

export default router;
