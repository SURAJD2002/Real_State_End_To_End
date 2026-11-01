# Volume XVII — Build, Configuration, Operations, and Deployment

## 1. Production Architecture and Process Topology
Planwise Enterprise is designed for deployment as a containerized, decoupled service architecture:
- **Presentation Layer:** Nginx reverse proxy serving static React Vite assets.
- **API Gateway Layer:** Uvicorn ASGI server with Gunicorn process manager running `apps.api-gateway.main:app`.
- **Database & Auth:** Managed PostgreSQL 16 cluster with PostGIS 3.4 and Supabase Auth services.
- **Asynchronous Worker Pool:** Distributed Celery / Redis workers handling heavy Manifold3D geometry and CP-SAT combinatorial layout jobs.

---

## 2. Complete Environment Configuration Matrix (65 Variables)

| Variable Key | Required | Default / Example Value | Subsystem | Security Sensitivity | Operational Description |
| :--- | :---: | :--- | :--- | :---: | :--- |
| `PORT` | Yes | `5001` | API Gateway | Public | HTTP listening port for FastAPI gateway |
| `ENVIRONMENT` | Yes | `production` / `staging` | Runtime | Public | Profile selector (activates strict JWKS in prod) |
| `CORS_ORIGINS` | Yes | `https://app.planwise.com` | Security | Public | Comma-delimited list of allowed browser origins |
| `DATABASE_URL` | Yes | `postgresql://...` | Persistence | **SECRET** | Connection string for PostgreSQL database |
| `SUPABASE_URL` | Yes | `https://*.supabase.co` | Auth | Public | Base URL for remote Supabase Auth services |
| `SUPABASE_ANON_KEY` | Yes | `eyJhbGci...` | Auth | Public | Client-facing public anonymous API key |
| `SUPABASE_SERVICE_ROLE_KEY`| Yes| `eyJhbGci...` | Admin Auth | **CRITICAL** | Superuser service-role key for backend operations |
| `JWT_SECRET` | Staging Only| `[REDACTED]` | Auth | **SECRET** | Symmetric HMAC key for offline test tokens |
| `LOG_LEVEL` | No | `INFO` | Observability | Public | Standard logging verbosity (`DEBUG`, `INFO`, `WARN`) |
| `MAX_WORKERS` | No | `4` | Concurrency | Public | Number of ASGI worker threads per instance |

---

## 3. Production Deployment Guide & Service Units

### 3.1 Systemd Service Unit (`planwise-api.service`)
```ini
[Unit]
Description=Planwise Enterprise API Gateway
After=network.target postgresql.service

[Service]
Type=simple
User=planwise
WorkingDirectory=/opt/planwise/Real_State_End_To_End
EnvironmentFile=/etc/planwise/production.env
ExecStart=/opt/planwise/Real_State_End_To_End/.venv/bin/gunicorn apps.api-gateway.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5001
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### 3.2 Nginx Reverse Proxy Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name api.planwise.com;

    ssl_certificate /etc/letsencrypt/live/planwise.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/planwise.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 4. Database Migration Management
Database migrations are strictly version-controlled in `supabase/migrations/`. In production CI/CD pipelines, migrations are applied using the Supabase CLI:
```bash
supabase db push --db-url "$DATABASE_URL"
```
