# Volume XIX — Error Handling, Troubleshooting, and Recovery

## 1. Exhaustive Diagnostic & Remediation Guide for 15 Production Failure Scenarios

### Scenario 1: Port 5001 Already in Use
- **Symptom:** `uvicorn: error: [Errno 48] Address already in use`.
- **Diagnosis:** `lsof -i:5001`.
- **Remediation:** `kill -9 $(lsof -ti:5001)`.

### Scenario 2: Cross-Tenant HTTP 403 Forbidden Error
- **Symptom:** Client receives `HTTP 403 Forbidden: Tenant boundary violation`.
- **Diagnosis:** Inspect JWT payload claims (`sub`, `organization_id`) using `jwt.io` or python script.
- **Remediation:** Confirm caller's active organization matches project's owning organization in database.

### Scenario 3: Statutory Infeasibility Error (DCPR 2034)
- **Symptom:** `HTTP 422: Plot envelope infeasible under DCPR 2034 setbacks`.
- **Diagnosis:** Review plot frontage road width and plot depth. Plots under $8.0	ext{ m}$ width cannot satisfy mandatory $1.5	ext{ m}$ side setbacks.
- **Remediation:** Apply for municipal setback relaxation variance or switch to compact plot bypass rules.

### Scenario 4: CP-SAT Layout Solver Timeout
- **Symptom:** Solver returns status `INFEASIBLE` or `MODEL_INVALID`.
- **Diagnosis:** Check total requested room program area against permissible ground coverage.
- **Remediation:** Reduce BHK room count or increase target plot boundary dimensions.

### Scenario 5: Review Gate Out-of-Order Sequence Violation
- **Symptom:** `HTTP 400: Gate G2 cannot be approved before G1`.
- **Diagnosis:** Query `/api/v1/projects/{id}/reviews` to check active gate statuses.
- **Remediation:** Approvals must strictly follow the sequential chain: G0 $\rightarrow$ G1 $\rightarrow$ G2 $\rightarrow$ G3 $\rightarrow$ G4 $\rightarrow$ G5 $\rightarrow$ G6.

### Scenario 6: Non-Manifold Geometry Assertion Failure
- **Symptom:** `SolidValidationError: NON_MANIFOLD_EDGE at wall segment W-04`.
- **Diagnosis:** Overlapping door openings or wall thickness $< 0.1	ext{ m}$ causing self-intersecting polygon prisms.
- **Remediation:** Verify opening offsets in CBM model; ensure opening width is less than wall segment length.

### Scenario 7: Database Connection Pool Exhaustion
- **Symptom:** `psycopg2.OperationalError: FATAL: remaining connection slots are reserved`.
- **Diagnosis:** Check PostgreSQL `pg_stat_activity`.
- **Remediation:** Increase `max_connections` in `postgresql.conf` or configure PgBouncer connection pooling.

### Scenario 8: Expired JWT Token Rejection
- **Symptom:** `HTTP 401 Unauthorized: Signature has expired`.
- **Diagnosis:** Verify system clock drift and token `exp` claim.
- **Remediation:** Trigger client token refresh via Supabase Auth `refresh_token` flow.

### Scenario 9: Missing Material Rate in Catalog
- **Symptom:** `CostCalculationError: Rate not found for item QTO-04 in tier LUXURY`.
- **Diagnosis:** Inspect active rate snapshot in `workers/qto/rate_snapshot_engine.py`.
- **Remediation:** Add fallback default rate or select supported rate catalog tier.

### Scenario 10: Headless Chrome Puppeteer Timeout
- **Symptom:** `Navigation timeout of 120000 ms exceeded`.
- **Diagnosis:** Inspect memory usage during PDF rendering; ensure Chrome has sufficient RAM.
- **Remediation:** Launch Chrome with `--disable-dev-shm-usage` and `--no-sandbox` flags.
