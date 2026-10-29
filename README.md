# Authentication & Profile Manager

Secure web application with user registration, JWT authentication, and dynamic profile editing.

## Tech Stack
- **Backend:** Node.js (v20 LTS) + Express.js + Prisma + PostgreSQL
- **Frontend:** React + Vite + Tailwind CSS
- **Auth:** JWT + Bcrypt

## Setup

```bash
# Backend
cd server
npm install
cp .env.example .env
npx prisma migrate dev
npm run dev

# Frontend
cd client
npm install
npm run dev
```

## Database
PostgreSQL is the production database. For local dev without PostgreSQL:
- Swap `schema.prisma` to use `sqlite` and remove `DATABASE_URL` from `.env`
- Remember to swap back before production deployment.
