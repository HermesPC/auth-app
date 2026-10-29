# DEPLOY.md — Authentication & Profile Manager

## Overview

Full-stack auth application: Node.js/Express/Prisma/PostgreSQL (backend) + React/Vite/Tailwind CSS (frontend).

## Prerequisites

- **PostgreSQL 15+** running on `localhost:5432` with database `auth_app` created
- **Node.js 18+** installed
- **npm** or **npx** available

## Environment Variables

### Backend (`server/.env`)

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/auth_app?schema=public
JWT_SECRET=your-256-bit-secret-here
PORT=4000
```

### Frontend (`client/.env`)

```env
VITE_API_URL=http://localhost:4000
```

## Deployment Steps

### 1. Backend

```bash
cd server
npm install

# Set DATABASE_URL in .env for your production database
npx prisma generate
npx prisma db push    # dev / migration

node src/index.js
# Server runs on http://localhost:4000
```

### 2. Frontend

```bash
cd client
npm install
npx vite build         # produces dist/
npm run preview        # preview build locally
```

For production serving, use any static file server (nginx, Vercel, Netlify, etc.) to serve the `dist/` directory.

### 3. Reverse Proxy (optional)

Configure nginx/traefik to proxy `/api` to the backend (port 4000) and static assets to the frontend build.

## SQLite → PostgreSQL Swap

### From SQLite to PostgreSQL (default for prod)

1. Update `server/.env`:
   ```
   DATABASE_URL=postgresql://USER:PASS@localhost:5432/auth_app?schema=public
   ```
2. Update `server/prisma/schema.prisma`:
   ```
   datasource db {
     provider = "postgresql"
     url      = env("DATABASE_URL")
   }
   ```
3. Run:
   ```bash
   npx prisma generate
   npx prisma db push
   ```

### From PostgreSQL to SQLite (local dev fallback)

1. Update `server/.env`:
   ```
   DATABASE_URL="file:./dev.db"
   ```
2. Update `server/prisma/schema.prisma`:
   ```
   datasource db {
     provider = "sqlite"
     url      = env("DATABASE_URL")
   }
   ```
3. Run:
   ```bash
   npx prisma generate
   npx prisma db push
   ```

> **Warning:** The SQLite `dev.db` file is not committed to version control (listed in `.gitignore`). Do not use it for production data.

## Testing

Run the full test suite against a running server:

```bash
cd server
python3 run_tests.py
# Expected: 20/20 PASS
```

## Architecture

```
├── client/            # React + Vite + Tailwind
│   ├── src/
│   │   ├── App.jsx              # Routing (/, /dashboard)
│   │   ├── api.js               # Axios + JWT interceptor
│   │   ├── context/AuthContext.jsx  # Auth state + token persistence
│   │   ├── components/ProtectedRoute.jsx  # Route guard
│   │   └── views/
│   │       ├── LoginSignup.jsx        # Tabbed auth UI
│   │       ├── DashboardView.jsx      # Profile grid display
│   │       └── ProfileEditForm.jsx    # Editable profile form
├── server/            # Express + Prisma + PostgreSQL
│   ├── prisma/
│   │   └── schema.prisma        # User + ContactInfo models
│   ├── src/
│   │   ├── index.js             # Express app entry
│   │   ├── controllers/
│   │   │   ├── authController.js        # Signup/Login
│   │   │   └── profileController.js     # GET/PUT Profile + sanitization
│   │   └── middleware/auth.js         # JWT verification
│   └── run_tests.py               # 20-test API validation suite
```

## Security Notes

- JWT tokens stored in `localStorage` — acceptable for this scope; consider `httpOnly` cookies for higher security
- Passwords hashed with bcryptjs (10 rounds)
- Input sanitization: `phone` (digits/hyphens/parens/plus/dots only), `zipCode` (5 or 5+4 digits)
- Prisma parameterizes all queries — no SQL injection risk
- CORS enabled for `localhost:5173` (adjust for production)
