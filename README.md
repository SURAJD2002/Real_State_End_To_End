# Real Estate Development Intelligence & Feasibility Platform

An enterprise-grade land-to-development intelligence platform and automated statutory feasibility engine modeled after the **Archonet Planwise** architecture, upgraded for institutional real estate underwriting and multi-jurisdictional compliance (**Mumbai MCGM DCPR 2034** baseline).

---

## 🏛 System Architecture Overview

The platform implements **Architecture E (Hybrid Application + Asynchronous Workers)** validated in the Engineering Master Plan:

- **Frontend CAD Workspace (`apps/web`)**: React 18/19 SPA + TypeScript + Vite + MapLibre GL JS v4 + Zustand + Lucide Icons. Features interactive parcel digitization, 60fps snapping, and a real-time statutory & financial underwriting HUD.
- **Stateless API Gateway (`apps/api-gateway`)**: FastAPI REST service with OpenAPI 3.1, handling project CRUD, debounced CAD auto-save, and deterministic Feasibility DAG execution.
- **Computational Geometry Worker (`workers/geometry`)**: Authoritative spatial calculations in metric UTM projections (EPSG:32643 for Mumbai), road widening setback deductions, and Public Open Space (POS) amenity reservations.
- **Statutory Regulation Evaluator (`workers/regulation`)**: Declarative AST/table rule evaluator for Mumbai DCPR 2034 (Regulation 30, 33, 41), computing Base FSI, Premium FSI, TDR allowances, height caps, and parking quotas.
- **Institutional Pro-Forma Engine (`workers/financial`)**: Capital budgeting engine calculating Gross Development Value (GDV), Total Development Cost (TDC), Developer Margin %, and Project Equity IRR %.
- **Spatial Database (`database/migrations`)**: PostgreSQL 16 + PostGIS 3.4 with GiST spatial indexing and validity checks.
- **Golden Benchmark Fixture (`database/seeds`)**: Canonical 10,000 m² Bandra East parcel benchmark from the Planwise reverse-engineering case study.

---

## 🚀 Quickstart & Development Setup

### Prerequisites
- **Node.js**: v20+ (`node -v`)
- **Python**: 3.12+ (`python3 -v`)
- **Docker & Docker Compose**: For local PostGIS and Redis

---

### Step 1: Start Database & Infrastructure (Docker)
To start PostgreSQL 16 with PostGIS 3.4, Redis, and MinIO S3 locally:

```bash
# Start PostGIS and Redis containers in the background
npm run docker:up

# View container logs
npm run docker:logs

# Stop containers when done
npm run docker:down
```

---

### Step 2: Set Up Python Backend & Workers
Create and activate the virtual environment and install the spatial packages:

```bash
# Activate existing virtual environment
source .venv/bin/activate

# Or create a fresh one:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the API Gateway:
```bash
# Start API on port 5001 with hot reload
cd apps/api-gateway
python3 main.py
# API is live at http://localhost:5001
# Interactive Swagger docs: http://localhost:5001/docs
```

---

### Step 3: Start the Frontend CAD Workspace
In a separate terminal:

```bash
# Start Vite development server
npm run dev:web
# Web UI is live at http://localhost:5173
```

---

## 🧪 Testing the Golden Benchmark

You can verify the entire deterministic calculation loop with a single CLI test or via the UI:

### CLI Test:
```bash
.venv/bin/python3 -c "
import sys
sys.path.insert(0, 'apps/api-gateway')
import main
res = main.load_golden_dataset()
print('Golden Dataset:', res['project']['name'])
print('Gross Area:', res['feasibility']['grossPlotAreaSqm'], 'm²')
print('Net Developable Area:', res['feasibility']['netDevelopableAreaSqm'], 'm²')
print('Permissible FSI:', res['feasibility']['totalPermissibleFSI'])
print('GDV (Revenue): ₹', f'{res[\"feasibility\"][\"financials\"][\"grossDevelopmentValue\"]:,.2f}')
print('Total Cost: ₹', f'{res[\"feasibility\"][\"financials\"][\"totalDevelopmentCost\"]:,.2f}')
print('Equity IRR:', res['feasibility']['financials']['equityIRRPercent'], '%')
"
```

### UI One-Click Benchmark:
1. Open `http://localhost:5173` in your browser.
2. Click **Load Golden Benchmark** in the top navigation bar.
3. The 10,000 m² Bandra East parcel will immediately render on the map with its net developable envelope, and the Feasibility Intelligence HUD will display the full statutory and financial underwriting breakdown.

---

## 📂 Repository Directory Layout

```
.
├── apps/
│   ├── web/                    # React 18/19 + TypeScript + Vite + MapLibre GL JS
│   │   ├── src/
│   │   │   ├── components/     # Navbar, CADToolbar, MapCanvas, FeasibilityHUD
│   │   │   ├── App.tsx         # Main CAD workspace & debounced auto-save
│   │   │   └── index.css       # Dark glassmorphism design system
│   │   └── vite.config.ts      # Proxy to API gateway on port 5001
│   └── api-gateway/            # FastAPI stateless REST service & DAG runner
│       └── main.py             # Projects CRUD, auto-save, and feasibility endpoints
├── workers/
│   ├── geometry/               # Metric UTM Zone 43N reprojection, setbacks & buffers
│   ├── regulation/             # Mumbai DCPR 2034 rule evaluator
│   └── financial/              # Real estate pro-forma engine (GDV, TDC, IRR)
├── packages/
│   ├── rules/                  # Mumbai DCPR 2034 declarative ruleset JSON
│   ├── schemas/                # Spatial payload & GeoJSON schemas
│   └── shared-types/           # Shared TypeScript interfaces & models
├── database/
│   ├── migrations/             # V001 PostGIS schema with GiST spatial indexes
│   └── seeds/                  # Golden 10,000 sqm Mumbai benchmark plot
├── infrastructure/
│   └── docker/                 # docker-compose.dev.yml (PostGIS 16, Redis 7, MinIO)
├── package.json                # Root package.json with workspace scripts
├── requirements.txt            # Python dependencies
└── .env.example                # Default dev environment variables
```

---

## ⚖️ Statutory & Feasibility Rules (DCPR 2034)

| Road Width (m) | Base FSI | Premium FSI | TDR Allowance | Total Permissible FSI | Max Height |
|---|:---:|:---:|:---:|:---:|:---:|
| **< 9.0 m** | 1.00 | — | — | **1.00** | 16.0 m |
| **9.0 – 12.0 m** | 1.00 | 0.50 | 0.50 | **2.00** | 32.0 m |
| **12.0 – 18.0 m** | 1.00 | 0.50 | 0.75 | **2.25** | 50.0 m |
| **18.0 – 27.0 m** | 1.00 | 0.50 | 1.00 | **2.50** | 70.0 m |
| **≥ 27.0 m** | 1.00 | 0.50 | 1.25 | **2.75** | 120.0 m |
