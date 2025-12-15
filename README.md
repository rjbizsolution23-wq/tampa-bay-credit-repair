# 🔥 Tampa Bay Credit Repair - Full Production Build

> **Professional Credit Repair Platform** | Built by Rick Jefferson, RJ Business Solutions

A comprehensive, production-ready credit repair platform featuring Next.js 15, FastAPI backend, AI-powered dispute generation, and full integration with MyFreeScoreNow and DisputeFox.

---

## 🚀 Features

### 🎯 Core Functionality
- **Credit Report Monitoring** - Real-time credit score tracking via MyFreeScoreNow API
- **AI Dispute Generation** - Automated dispute letter creation using OpenAI/Anthropic
- **Multi-Bureau Support** - TransUnion, Equifax, and Experian integration
- **Document Management** - Secure file upload and storage (Cloudflare R2)
- **Payment Processing** - Stripe integration for subscriptions and payments
- **SMS/Email Notifications** - Twilio and Resend integration

### 💼 Business Features
- **Client Portal** - Modern Next.js 15 dashboard
- **Admin Dashboard** - Complete CRM and case management
- **Subscription Plans** - Flexible pricing with Stripe
- **Affiliate Program** - MyFreeScoreNow affiliate integration
- **Analytics** - Comprehensive tracking and reporting

### 🛠️ Technical Stack
- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python), Prisma ORM
- **Database**: PostgreSQL (Supabase)
- **Storage**: Cloudflare R2
- **Auth**: NextAuth.js
- **Payments**: Stripe
- **Email**: Resend
- **SMS**: Twilio
- **Deployment**: Vercel (frontend), Railway (backend)

---

## 📋 Prerequisites

- **Node.js** 20+
- **Python** 3.12+
- **PostgreSQL** 15+
- **Git**
- API keys for integrated services (see `.env.example`)

---

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/rjbizsolution23-wq/tampa-bay-credit-repair.git
cd tampa-bay-credit-repair
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

### 3. Install Dependencies

**Frontend (Next.js):**
```bash
cd apps/web
npm install
```

**Backend (FastAPI):**
```bash
cd services/api
pip install -r requirements.txt
```

### 4. Database Setup

```bash
# Run Prisma migrations
cd packages/database
npx prisma migrate dev
npx prisma generate
```

### 5. Run Development Servers

**Frontend:**
```bash
cd apps/web
npm run dev
# Opens at http://localhost:3000
```

**Backend:**
```bash
cd services/api
uvicorn app.main:app --reload
# Opens at http://localhost:8000
```

---

## 📁 Project Structure

```
tampa-bay-credit-repair/
├── apps/
│   ├── web/                    # Next.js 15 Client Portal
│   └── admin/                  # Admin Dashboard
├── packages/
│   ├── database/               # Prisma + Supabase
│   ├── email-templates/        # React Email
│   ├── dispute-engine/         # AI Dispute Generator
│   └── credit-api/             # MyFreeScoreNow Integration
├── services/
│   ├── api/                    # FastAPI Backend
│   └── workers/                # Background Jobs
├── infrastructure/
│   ├── terraform/              # Infrastructure as Code
│   └── docker-compose.yml      # Local development
├── docs/                       # Documentation
└── PROJECT_BUILD.md            # Complete build specifications
```

---

## 🔐 Environment Variables

See `.env.example` for complete list. Key variables:

### Database
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
DIRECT_URL=postgresql://user:pass@host:5432/db
```

### Authentication
```env
NEXTAUTH_SECRET=your_secret_here
NEXTAUTH_URL=http://localhost:3000
```

### Stripe
```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### MyFreeScoreNow
```env
MFSN_EMAIL=your_email@example.com
MFSN_PASSWORD=your_password
MFSN_AID=YourAffiliateID
```

### DisputeFox
```env
DISPUTEFOX_API_KEY=Fox_...
DISPUTEFOX_EMAIL=your_email@example.com
DISPUTEFOX_PASSWORD=your_password
```

### AI Services
```env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-api03-...
```

---

## 🚀 Deployment

### Vercel (Frontend)
```bash
vercel --prod
```

### Railway (Backend)
```bash
railway up
```

### Docker
```bash
docker-compose up -d
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## 📊 API Documentation

### REST API
- **Base URL**: `http://localhost:8000/api/v1`
- **Docs**: `http://localhost:8000/docs` (Swagger)
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /credit-reports` - Fetch credit reports
- `POST /disputes` - Create dispute
- `GET /disputes/{id}` - Get dispute status
- `POST /payments` - Process payment

---

## 🧪 Testing

**Frontend:**
```bash
cd apps/web
npm test
npm run test:e2e
```

**Backend:**
```bash
cd services/api
pytest
pytest --cov
```

---

## 📝 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System architecture and design
- [API Reference](docs/API.md) - Complete API documentation
- [Deployment](docs/DEPLOYMENT.md) - Deployment guide
- [Security](docs/SECURITY.md) - Security best practices
- [Compliance](docs/COMPLIANCE.md) - FCRA/CFPB compliance

---

## 🔒 Security

- **Encryption**: All sensitive data encrypted at rest
- **HTTPS**: Enforced in production
- **Authentication**: JWT-based with refresh tokens
- **Rate Limiting**: API rate limiting enabled
- **FCRA Compliant**: Follows Fair Credit Reporting Act guidelines
- **PCI DSS**: Payment processing compliant

---

## 📄 License

Copyright © 2025 RJ Business Solutions. All rights reserved.

---

## 👤 Author

**Rick Jefferson**
- 🌐 Website: [rickjeffersonsolutions.com](https://rickjeffersonsolutions.com)
- 📧 Email: rickjefferson@rickjeffersonsolutions.com
- 💼 LinkedIn: [Rick Jefferson](https://linkedin.com/in/rick-jefferson-314998235)
- 🐙 GitHub: [@rjbizsolution23-wq](https://github.com/rjbizsolution23-wq)
- 📱 Phone: +1 (414) 430-4277

---

## 🤝 Support

For technical support or business inquiries:
- 📧 Email: rickjefferson@rickjeffersonsolutions.com
- 🌐 Website: https://rickjeffersonsolutions.com
- 📞 Phone: +1 (414) 430-4277

---

## 📝 Changelog

### v1.0.0 (2025-12-15)
- Initial production release
- Complete credit repair platform
- MyFreeScoreNow integration
- DisputeFox integration
- AI-powered dispute generation
- Stripe payment processing
- Full admin dashboard

---

**Built with ❤️ by RJ Business Solutions**
