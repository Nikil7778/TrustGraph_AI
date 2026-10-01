import { Router } from 'express';
import { getOfficialRegistry } from '../controllers/registryController';

const router = Router();

router.get('/', getOfficialRegistry);

export default router;
