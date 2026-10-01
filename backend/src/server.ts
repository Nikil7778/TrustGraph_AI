import cors from 'cors';
import dotenv from 'dotenv';
import express from 'express';
import helmet from 'helmet';
import path from 'path';

import analysisRoutes from './routes/analysisRoutes';
import fingerprintRoutes from './routes/fingerprintRoutes';
import registryRoutes from './routes/registryRoutes';
import settingsRoutes from './routes/settingsRoutes';
import authRoutes from './routes/authRoutes';
import historyRoutes from './routes/historyRoutes';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors({ origin: '*' }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve uploads directory
app.use('/uploads', express.static(path.join(__dirname, '../uploads')));

// Routes
app.use('/api/auth', authRoutes);
app.use('/api', historyRoutes);
app.use('/api/analysis', analysisRoutes);
app.use('/api/official-registry', registryRoutes);
app.use('/api/threat-intelligence', fingerprintRoutes);
app.use('/api/settings', settingsRoutes);

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'TRUST AI Backend API', timestamp: new Date() });
});

app.listen(PORT, () => {
  console.log(`🚀 TRUST AI Backend running at http://localhost:${PORT}`);
});
