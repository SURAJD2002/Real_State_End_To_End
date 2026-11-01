# Volume XXII — Developer Onboarding and Change Impact

## 1. Practical Developer Modification Guides

### 1.1 How to Add a New REST API Endpoint
1. Open `apps/api-gateway/main.py`.
2. Define the route handler with appropriate Pydantic input/output schemas:
   ```python
   @app.post("/api/v1/projects/{project_id}/custom-analysis", response_model=AnalysisResponse)
   async def run_custom_analysis(
       project_id: str,
       payload: AnalysisRequest,
       current_user: dict = Depends(get_current_user)
   ):
       project = await get_project_by_id(project_id, current_user["organization_id"])
       result = compute_analysis(project, payload)
       return result
   ```
3. Add a corresponding test in `tests/test_api_gateway.py` verifying status codes, schema validation, and cross-tenant isolation.
4. Run tests: `.venv/bin/python3 -m unittest tests/test_api_gateway.py`.

### 1.2 How to Add a Field to the Canonical Building Model (CBM)
1. Open `packages/schemas/building_model.py`.
2. Add the field to the relevant Pydantic model with a default value to maintain backward compatibility:
   ```python
   class Room(BaseModel):
       id: str
       name: str
       type: RoomType
       polygon_2d: List[Point2D]
       finish_material: Optional[str] = "vitrified_tiles" # New field
   ```
3. Update `workers/qto/qto_engine.py` if the field affects quantity takeoff or cost calculations.
4. Update `tests/test_cbm_schema_validation.py` to assert correct serialization and SHA-256 hashing.

### 1.3 How to Add a New Municipal Statutory Rule Pack
1. Create a new JSON definition in `packages/rules/` (e.g. `pune_pmc_2026.json`).
2. Register the rule pack in `workers/regulation/rule_engine.py`:
   ```python
   RULE_PACK_MAPPINGS["PUNE_PMC_2026"] = RULES_DIR / "pune_pmc_2026.json"
   ```
3. Add unit tests in `tests/test_statutory_rules.py` covering boundary plot sizes under Pune regulations.
