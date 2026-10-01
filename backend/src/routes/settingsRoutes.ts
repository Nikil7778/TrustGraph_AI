import { Router } from 'express';
import { getWeights, updateWeights } from '../controllers/settingsController';

const router = Router();

router.get('/weights', getWeights);
router.put('/weights', updateWeights);

export default router;
