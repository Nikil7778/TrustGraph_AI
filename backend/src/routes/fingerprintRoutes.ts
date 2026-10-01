import { Router } from 'express';
import { getThreatIntelligence } from '../controllers/fingerprintController';

const router = Router();

router.get('/', getThreatIntelligence);

export default router;
