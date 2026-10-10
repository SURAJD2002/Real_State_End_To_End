# Contributing to Planwise Enterprise

Thank you for your interest in contributing to **Planwise Enterprise** — an institutional-grade, end-to-end Land-to-Home Development & Construction Platform.

Please review this guide before submitting issues, creating branches, or opening pull requests.

---

## 1. Code of Conduct & Core Principles

- **Deterministic Engineering:** All statutory calculations, geometric clippings, and costing rollups must be mathematically deterministic and reproducible.
- **Zero-Trust Security:** Never commit real secrets, API keys, service-role tokens, or credentials. Always use `.env.example` templates.
- **Professional Responsibility Boundary:** Computational validation is an automated engineering tool, not a substitute for statutory municipal permits or wet-ink/digital stamps from licensed professional engineers.
- **Branch Protection:** Direct commits to `main` are strictly prohibited. All changes must go through reviewed feature branches and pass CI/CD regressions.

---

## 2. Development Prerequisites

Ensure your local development environment has:

- **Python:** 3.12+ (tested through 3.14) with `venv` or `poetry`
- **Node.js:** 20.x or later (LTS recommended)
- **Package Managers:** `npm` (v10+)
- **PostgreSQL & PostGIS:** PostgreSQL 16+ with PostGIS 3.3+ (local Docker Compose or linked Supabase project)
- **Supabase CLI:** v2.100+ for database migrations and schema reconciliation
- **Docker & Docker Compose:** For running local Redis and PostGIS services

---

## 3. Local Setup & Quickstart

### Step 1: Clone the Repository
```bash
git clone https://github.com/SURAJD2002/Real_State_End_To_End.git
cd Real_State_End_To_End
```

### Step 2: Environment Configuration
Copy the template configuration files:
```bash
cp .env.example .env
cp .env.example apps/web/.env
```
> [!IMPORTANT]
> Keep real database credentials, Supabase keys, and JWT secrets in your local `.env` files. Ensure they match your local or sandbox environment. Never commit `.env` or `apps/web/.env` to Git.

### Step 3: Python Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Web Application Dependencies
```bash
npm install
cd apps/web && npm install && cd ../..
```

### Step 5: Database & Infrastructure
To run local Docker containers for PostGIS and Redis:
```bash
npm run docker:up
```

Alternatively, if developing against a linked Supabase project:
```bash
npx supabase migration list
```

---

## 4. Running the Development Services

### Start API Gateway (FastAPI)
```bash
source .venv/bin/activate
cd apps/api-gateway
python3 main.py
# API will run on http://127.0.0.1:5001 (Swagger docs at /docs)
```

### Start Web Client (Vite + React)
In a separate terminal:
```bash
npm --prefix apps/web run dev
# Web application will run on http://localhost:5173
```

---

## 5. Development & Branching Workflow

1. **Branch Naming:**
   - Feature: `feature/<descriptive-name>` (e.g., `feature/complete-project-documentation`)
   - Bug fix: `fix/<issue-name>`
   - Documentation: `docs/<topic>`
2. **Never Commit Secrets:**
   - Run `git status` before committing. Ensure `.env`, cache directories (`__pycache__`, `node_modules`, `.venv`), and build artifacts (`dist`) are untracked.
3. **Commit Messages:**
   - Follow Conventional Commits:
     - `feat: add parametric setbacks for Bangalore BBMP`
     - `fix: resolve JWT expiration handling in auth gateway`
     - `docs: update pilot readiness report`
     - `chore: bump dependencies`
4. **Pull Requests:**
   - Open a PR targeting `main`.
   - Provide a clear summary of changes, motivation, and test evidence.
   - Reference any related issues.

---

## 6. Testing & Quality Verification

Before submitting any pull request, ensure all test suites pass:

### Python Unit & Regression Tests
```bash
# Negative Security & Token Verification (11 tests)
./.venv/bin/python -m unittest tests/test_auth_security_negative.py

# Multi-Tenant & RLS Isolation (7 tests)
./.venv/bin/python -m unittest tests/test_cross_tenant_isolation.py

# Persistence & Process Restart Workflow (6 tests)
./.venv/bin/python -m unittest tests/test_persistence_and_auth_workflow.py

# PostgreSQL Persistence Unit Suite (7 tests)
./.venv/bin/python -m unittest tests/test_phase8_1_persistence.py

# Real Plot End-to-End Pipeline (13 tests)
./.venv/bin/python -m unittest tests/test_real_plot_end_to_end.py
```

### Frontend Typecheck & Build
```bash
npm --prefix apps/web run build
```

### Git Whitespace & Hygiene Check
```bash
git diff --check
```

---

## 7. Reporting Issues

- For bug reports or feature requests, open an issue on GitHub with reproduction steps, system environment, and observed vs expected behavior.
- For security vulnerabilities, please refer to [SECURITY.md](SECURITY.md) for responsible disclosure procedures.
