import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

import { signup, login } from './controllers/authController.js';
import { getProfile, updateProfile } from './controllers/profileController.js';
import { authenticate } from './middleware/auth.js';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// --- Auth Routes (Public) ---
app.post('/api/auth/signup', signup);
app.post('/api/auth/login', login);

// --- Profile Routes (Protected: requires Bearer JWT) ---
app.get('/api/profile', authenticate, getProfile);
app.put('/api/profile', authenticate, updateProfile);

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Auth API server running on port ${PORT}`);
});
