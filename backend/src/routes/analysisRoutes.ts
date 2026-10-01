import { Router } from 'express';
import multer from 'multer';
import { createAnalysis, getAnalysisById } from '../controllers/analysisController';
import { authenticateToken } from '../middleware/authMiddleware';

const router = Router();
const upload = multer({ dest: 'uploads/' });

router.post('/create', authenticateToken, upload.single('file'), createAnalysis);
router.get('/:id', authenticateToken, getAnalysisById);

export default router;
