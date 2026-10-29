# Authentication & Profile Manager

Secure web application with user registration, JWT authentication, and dynamic profile editing.

## Tech Stack
- **Backend:** Node.js (v20 LTS) + Express.js + Prisma + PostgreSQL
- **Frontend:** React + Vite + Tailwind CSS
- **Auth:** JWT + Bcrypt

## Quick Start

> ⚠️ **Important:** Do not double-click `index.html` in your browser. This is a Single Page Application (SPA) that must be served by the Vite development server.

Open **two terminal windows** and run the following:

### Terminal 1 — Backend

```bash
cd server
npm install
# Ensure DATABASE_URL in .env points to a running PostgreSQL instance
npx prisma generate
npx prisma db push
npm run dev
# Server runs on http://localhost:4000
```

### Terminal 2 — Frontend

```bash
cd client
npm install
npm run dev
# App opens at http://localhost:5173
```

Open your browser to **http://localhost:5173** (the Vite dev server address).

## Database

PostgreSQL is the production database. For local dev without PostgreSQL:
- Swap `schema.prisma` to use `sqlite` and set `DATABASE_URL="file:./dev.db"`
- Remember to swap back before production deployment.

See [DEPLOY.md](DEPLOY.md) for full deployment instructions, environment variables, and PostgreSQL/SQLite swap steps.

## Testing

```bash
cd server
python3 run_tests.py
# Expected: 20/20 PASS
```
