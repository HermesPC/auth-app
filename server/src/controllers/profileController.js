import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// --- Input Sanitization ---
const PHONE_REGEX = /^[\d\s\-\(\)\+\.]+$/;
const ZIPCODE_REGEX = /^\d{5}(-\d{4})?$/;

function sanitizeProfileBody(body) {
  if (!body || typeof body !== 'object') {
    return { error: 'Request body must be a JSON object' };
  }

  const updates = {};
  const ALLOWED = [
    'firstName', 'lastName', 'phone',
    'addressLine1', 'addressLine2',
    'city', 'state', 'zipCode',
  ];

  for (const key of ALLOWED) {
    if (body[key] !== undefined) {
      // Must be string or null
      if (body[key] !== null && typeof body[key] !== 'string') {
        return { error: `Field "${key}" must be a string or null` };
      }
      updates[key] = body[key].trim() || null;
    }
  }

  // Phone sanitization: only digits, spaces, hyphens, parentheses, plus, dots
  if (updates.phone !== undefined && !PHONE_REGEX.test(updates.phone)) {
    return { error: 'Phone number may only contain digits, spaces, hyphens, parentheses, plus signs, or dots' };
  }

  // ZipCode sanitization: 5 digits or 5+4 format
  if (updates.zipCode !== undefined && !ZIPCODE_REGEX.test(updates.zipCode)) {
    return { error: 'Zip code must be 5 digits or 5-digit+4 format (e.g., 97477 or 97477-1234)' };
  }

  return { updates };
}

export async function getProfile(req, res) {
  const user = await prisma.user.findUnique({
    where: { id: req.userId },
    include: { contact: true },
  });

  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  return res.status(200).json({
    email: user.email,
    contact: user.contact || {
      id: null,
      userId: user.id,
      firstName: '',
      lastName: '',
      phone: null,
      addressLine1: null,
      addressLine2: null,
      city: null,
      state: null,
      zipCode: null,
    },
  });
}

export async function updateProfile(req, res) {
  const sanitization = sanitizeProfileBody(req.body);
  if (sanitization.error) {
    return res.status(400).json({ error: sanitization.error });
  }

  const { updates } = sanitization;

  const contact = await prisma.contactInfo.upsert({
    where: { userId: req.userId },
    update: updates,
    create: {
      userId: req.userId,
      ...updates,
      firstName: updates.firstName || '',
      lastName: updates.lastName || '',
    },
  });

  const user = await prisma.user.findUnique({
    where: { id: req.userId },
    include: { contact: true },
  });

  return res.status(200).json({
    email: user.email,
    contact: user.contact,
  });
}
