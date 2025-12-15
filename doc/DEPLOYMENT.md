# Deployment Guide for Tampa Bay Credit Repair

## Overview
This platform consists of two main components that should be deployed separately for optimal performance and scalability:
1.  **Frontend**: Next.js 15 application.
    - **Recommended Host**: Cloudflare Pages.
2.  **Backend**: FastAPI Python application + Postgres Database.
    - **Recommended Host**: Render, Railway, or AWS.

## 1. Deploying Frontend to Cloudflare Pages

### Prerequisites
- A Cloudflare account.
- The repository pushed to GitHub.

### Steps
1.  **Log in to Cloudflare Dashboard** > **Workers & Pages** > **Create Application** > **Pages** > **Connect to Git**.
2.  Select the `tampa-bay-credit-repair` repository.
3.  **Configure Build Settings**:
    - **Framework Preset**: `Next.js`
    - **Build Command**: `npx @cloudflare/next-on-pages@1`
    - **Build Output Directory**: `.vercel/output/static` (handled by adapter)
    - **Root Directory**: `apps/web` (IMPORTANT)
4.  **Environment Variables**:
    - Add `NEXT_PUBLIC_API_URL`: The URL of your deployed backend (e.g., `https://api.tampabaycreditrepair.com`).
5.  **Deploy**: Click "Save and Deploy".

### Local Preview
To test the Cloudflare build locally:
```bash
cd apps/web
npm run build
npx wrangler pages dev .vercel/output/static
```

## 2. Deploying Backend (FastAPI) & Database

### Option A: Render (Easiest)
1.  **Create New Web Service** connected to your GitHub repo.
2.  **Root Directory**: `.` (Root of repo).
3.  **Build Context**: `.` (Root of repo).
4.  **Dockerfile Path**: `services/api/Dockerfile`.
5.  **Environment Variables**:
    - Copy all values from `.env.example`.
    - Set `DATABASE_URL` to your production Postgres URL.
6.  **Create Database**: Use Render's managed PostgreSQL or external (Supabase/Neon).

### Option B: Railway
1.  **New Project** > **Deploy from GitHub Repo**.
2.  Add **PostgreSQL** plugin.
3.  Configure variables. Railway automatically detects the Dockerfile.

## 3. Database Migration
After deploying the backend, run the schema push command from your local machine (connecting to production DB) or from the production console:
```bash
npx prisma db push
```

## 4. DNS Configuration
Once both are deployed:
1.  Point `tampabaycreditrepair.com` to Cloudflare Pages.
2.  Point `api.tampabaycreditrepair.com` to your Backend URL.
