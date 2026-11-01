# Volume IV — Backend and REST API Reference

## 1. API Gateway Framework and Middleware
The Planwise API Gateway is implemented in Python using **FastAPI 0.115.0** and **Pydantic 2.9.2**. It operates as an asynchronous, stateless service terminating REST requests, validating payloads, enforcing multi-tenant isolation, and delegating heavy computational jobs to specialized worker engines.

### Middleware Pipeline
1. **CORS Middleware (`CORSMiddleware`):** Configured via `CORS_ORIGINS` (`http://localhost:5173,http://localhost:3000`). Enforces credentials handling and restricts origins.
2. **Request ID & Timing Middleware:** Injects unique `X-Request-ID` and measures processing latency.
3. **Exception Handler Middleware:** Catches unhandled exceptions, logs traceback internally, and emits standard JSON error bodies (`{"detail": "...", "status_code": ...}`).

---

## 2. Complete Inventory and Specifications of All 73 REST Endpoints


### Endpoint 1: `GET /api/health`
- **Handler Function:** `health_check` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def health_check():
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 2: `GET /api/v1/auth/session`
- **Handler Function:** `get_auth_session` in `apps/api-gateway/main.py`
- **Authentication Required:** `Yes (Bearer JWT)`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_auth_session(current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 3: `GET /api/v1/projects`
- **Handler Function:** `list_projects` in `apps/api-gateway/main.py`
- **Authentication Required:** `Yes (Bearer JWT)`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def list_projects(current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 4: `POST /api/v1/projects`
- **Handler Function:** `create_project` in `apps/api-gateway/main.py`
- **Authentication Required:** `Yes (Bearer JWT)`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def create_project(req: ProjectCreateRequest, current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 5: `GET /api/v1/projects/{project_id}`
- **Handler Function:** `get_project` in `apps/api-gateway/main.py`
- **Authentication Required:** `Yes (Bearer JWT)`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_project(project_id: str, current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 6: `PUT /api/v1/projects/{project_id}/geometries`
- **Handler Function:** `auto_save_geometries` in `apps/api-gateway/main.py`
- **Authentication Required:** `Yes (Bearer JWT)`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def auto_save_geometries(project_id: str, payload: GeometryAutoSavePayload, current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 7: `POST /api/v1/projects/{project_id}/calculate-feasibility`
- **Handler Function:** `run_feasibility_dag` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def run_feasibility_dag(project_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 8: `GET /api/v1/projects/{project_id}/house-options`
- **Handler Function:** `get_house_options` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_house_options(project_id: str, quality_tier: str = "STANDARD"):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 9: `POST /api/v1/design-versions/{design_version_id}/build-request`
- **Handler Function:** `request_build` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def request_build(design_version_id: str, payload: BuildRequestPayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 10: `GET /api/v1/releases/{release_id}/handoff-package`
- **Handler Function:** `get_handoff_package` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_handoff_package(release_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 11: `POST /api/v1/releases/{release_id}/approvals`
- **Handler Function:** `update_gate_approval` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def update_gate_approval(release_id: str, approval: ProfessionalGateApproval):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 12: `GET /api/v1/releases/{release_id}/ifc`
- **Handler Function:** `download_ifc_model` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def download_ifc_model(release_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 13: `POST /api/v1/build-requests/{build_request_id}/engineer-review`
- **Handler Function:** `create_or_get_engineer_review` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def create_or_get_engineer_review(build_request_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 14: `GET /api/v1/engineer-reviews/{review_id}`
- **Handler Function:** `get_engineer_review` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_engineer_review(review_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 15: `GET /api/v1/engineer-reviews/{review_id}/gates`
- **Handler Function:** `get_engineer_review_gates` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_engineer_review_gates(review_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 16: `GET /api/v1/engineer-reviews/{review_id}/issues`
- **Handler Function:** `get_engineer_review_issues` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_engineer_review_issues(review_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 17: `POST /api/v1/engineer-reviews/{review_id}/gates/{gate_code}/verify`
- **Handler Function:** `verify_review_gate` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def verify_review_gate(review_id: str, gate_code: str, payload: GateVerificationPayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 18: `POST /api/v1/engineer-reviews/{review_id}/issues`
- **Handler Function:** `create_review_issue` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def create_review_issue(review_id: str, payload: CreateIssuePayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 19: `POST /api/v1/engineer-reviews/{review_id}/decision`
- **Handler Function:** `record_review_decision` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def record_review_decision(review_id: str, payload: ReviewDecisionPayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 20: `POST /api/v1/engineer-reviews/{review_id}/request-changes`
- **Handler Function:** `request_review_changes` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def request_review_changes(review_id: str, payload: RequestChangesPayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 21: `POST /api/v1/projects/load-golden-dataset`
- **Handler Function:** `load_golden_dataset` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def load_golden_dataset():
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 22: `GET /api/v1/regulations/MUMBAI_DCPR_2034`
- **Handler Function:** `get_mumbai_regulations` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_mumbai_regulations():
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 23: `GET /api/v1/design-versions/{design_version_id}/building-model`
- **Handler Function:** `get_canonical_building_model_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_canonical_building_model_endpoint(design_version_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 24: `GET /api/v1/design-versions/{design_version_id}/validation`
- **Handler Function:** `get_model_validation_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_model_validation_endpoint(design_version_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 25: `GET /api/v1/design-versions/{design_version_id}/floor-plan`
- **Handler Function:** `get_model_floor_plan_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_model_floor_plan_endpoint(design_version_id: str, level_id: Optional[str] = None):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 26: `GET /api/v1/design-versions/{design_version_id}/elevation`
- **Handler Function:** `get_model_elevation_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_model_elevation_endpoint(design_version_id: str, facade: str = "SOUTH"):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 27: `GET /api/v1/design-versions/{design_version_id}/section`
- **Handler Function:** `get_model_section_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_model_section_endpoint(design_version_id: str, cut_plane: str = "A-A", cut_y: Optional[float] = None):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 28: `GET /api/v1/design-versions/{design_version_id}/3d`
- **Handler Function:** `get_model_3d_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_model_3d_endpoint(design_version_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 29: `GET /api/v1/design-versions/{design_version_id}/ifc`
- **Handler Function:** `get_model_ifc_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_model_ifc_endpoint(design_version_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 30: `GET /api/v1/design-versions/{design_version_id}/drawings`
- **Handler Function:** `list_design_drawings_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def list_design_drawings_endpoint(design_version_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 31: `GET /api/v1/design-versions/{design_version_id}/drawings/{drawing_id}`
- **Handler Function:** `get_design_drawing_details_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_design_drawing_details_endpoint(design_version_id: str, drawing_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 32: `GET /api/v1/design-versions/{design_version_id}/drawings/{drawing_id}/pdf`
- **Handler Function:** `get_drawing_pdf_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_drawing_pdf_endpoint(design_version_id: str, drawing_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 33: `GET /api/v1/design-versions/{design_version_id}/drawings/{drawing_id}/svg`
- **Handler Function:** `get_drawing_svg_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_drawing_svg_endpoint(design_version_id: str, drawing_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 34: `POST /api/v1/design-versions/{design_version_id}/drawings/compile`
- **Handler Function:** `compile_design_drawings_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def compile_design_drawings_endpoint(design_version_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 35: `POST /api/v1/projects/{project_id}/design-options/{option_id}/compile`
- **Handler Function:** `compile_design_option_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def compile_design_option_endpoint(project_id: str, option_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 36: `GET /api/v1/sites/{site_id}/evidence`
- **Handler Function:** `get_site_evidence_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_site_evidence_endpoint(site_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 37: `POST /api/v1/sites/{site_id}/evidence`
- **Handler Function:** `create_site_evidence_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def create_site_evidence_endpoint(site_id: str, payload: SiteEvidenceCreatePayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 38: `POST /api/v1/sites/{site_id}/evidence/{evidence_id}/verify`
- **Handler Function:** `verify_site_evidence_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def verify_site_evidence_endpoint(site_id: str, evidence_id: str, payload: SiteEvidenceVerifyPayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 39: `GET /api/v1/sites/{site_id}/confidence`
- **Handler Function:** `get_site_confidence_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_site_confidence_endpoint(site_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 40: `GET /api/v1/sites/{site_id}/reference-frame`
- **Handler Function:** `get_site_reference_frame_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_site_reference_frame_endpoint(site_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 41: `POST /api/v1/sites/{site_id}/reference-frame`
- **Handler Function:** `set_site_reference_frame_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def set_site_reference_frame_endpoint(site_id: str, payload: SiteReferenceFramePayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 42: `GET /api/v1/regulation/rule-packs`
- **Handler Function:** `list_rule_packs_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def list_rule_packs_endpoint():
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 43: `GET /api/v1/regulation/rule-packs/{rule_pack_id}`
- **Handler Function:** `get_rule_pack_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_rule_pack_endpoint(rule_pack_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 44: `POST /api/v1/sites/{site_id}/feasibility/evaluate`
- **Handler Function:** `evaluate_site_statutory_feasibility_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def evaluate_site_statutory_feasibility_endpoint(site_id: str, payload: StatutoryFeasibilityEvaluatePayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 45: `GET /api/v1/sites/{site_id}/feasibility/explain`
- **Handler Function:** `get_feasibility_explainability_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_feasibility_explainability_endpoint(site_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 46: `POST /api/v1/sites/{site_id}/design-options/generate`
- **Handler Function:** `generate_design_options_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def generate_design_options_endpoint(site_id: str, payload: GenerateDesignOptionsPayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 47: `GET /api/v1/design-options/{design_option_id}`
- **Handler Function:** `get_design_option_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_design_option_endpoint(design_option_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 48: `GET /api/v1/design-options/{design_option_id}/validation`
- **Handler Function:** `get_design_option_validation_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_design_option_validation_endpoint(design_option_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 49: `GET /api/v1/design-options/{design_option_id}/geometry`
- **Handler Function:** `get_design_option_geometry_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_design_option_geometry_endpoint(design_option_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 50: `GET /api/v1/design-options/{design_option_id}/metrics`
- **Handler Function:** `get_design_option_metrics_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_design_option_metrics_endpoint(design_option_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 51: `POST /api/v1/design-options/{design_option_id}/compile`
- **Handler Function:** `compile_design_option_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def compile_design_option_endpoint(design_option_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 52: `POST /api/v1/design-options/{design_option_id}/freeze`
- **Handler Function:** `freeze_design_option_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def freeze_design_option_endpoint(design_option_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 53: `GET /api/v1/generation-jobs/{job_id}`
- **Handler Function:** `get_generation_job_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_generation_job_endpoint(job_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 54: `GET /api/v1/rates/snapshots`
- **Handler Function:** `get_rate_snapshots_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_rate_snapshots_endpoint():
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 55: `POST /api/v1/design-versions/{design_version_id}/qto/generate`
- **Handler Function:** `generate_qto_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def generate_qto_endpoint(design_version_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 56: `GET /api/v1/design-versions/{design_version_id}/qto`
- **Handler Function:** `get_qto_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_qto_endpoint(design_version_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 57: `GET /api/v1/design-versions/{design_version_id}/boq`
- **Handler Function:** `get_boq_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_boq_endpoint(design_version_id: str,     qualityTier: str = "STANDARD",     rateSnapshotId: str = "INDIA-MUMBAI-2026-Q4-V1"):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 58: `GET /api/v1/design-versions/{design_version_id}/cost`
- **Handler Function:** `get_cost_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_cost_endpoint(design_version_id: str,     qualityTier: str = "STANDARD",     rateSnapshotId: str = "INDIA-MUMBAI-2026-Q4-V1"):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 59: `GET /api/v1/design-versions/{design_version_id}/cost/explain/{boq_item_id}`
- **Handler Function:** `explain_cost_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def explain_cost_endpoint(design_version_id: str, boq_item_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 60: `POST /api/v1/design-versions/{design_version_id}/cost/recalculate`
- **Handler Function:** `recalculate_cost_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def recalculate_cost_endpoint(design_version_id: str, payload: RecalculateCostPayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 61: `GET /api/v1/design-versions/{design_version_id}/cost/export`
- **Handler Function:** `export_cost_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def export_cost_endpoint(design_version_id: str,     format: str = "json",     qualityTier: str = "STANDARD",     rateSnapshotId: str = "INDIA-MUMBAI-2026-Q4-V1"):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 62: `POST /api/v1/design-versions/{design_version_id}/cost/jobs`
- **Handler Function:** `start_cost_job_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def start_cost_job_endpoint(design_version_id: str, payload: RecalculateCostPayload):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 63: `POST /api/v1/intake/validate`
- **Handler Function:** `validate_real_plot_intake_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def validate_real_plot_intake_endpoint(payload: dict):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 64: `POST /api/v1/intake/real-plot`
- **Handler Function:** `execute_real_plot_pipeline_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def execute_real_plot_pipeline_endpoint(payload: dict):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 65: `POST /api/v1/design-versions/{design_version_id}/reports/home`
- **Handler Function:** `generate_customer_home_report_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def generate_customer_home_report_endpoint(design_version_id: str, project_id: Optional[str] = None):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 66: `GET /api/v1/design-versions/{design_version_id}/reports/home/{report_id}`
- **Handler Function:** `get_customer_home_report_metadata_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def get_customer_home_report_metadata_endpoint(design_version_id: str, report_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 67: `GET /api/v1/design-versions/{design_version_id}/reports/home/{report_id}/download`
- **Handler Function:** `download_customer_home_report_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def download_customer_home_report_endpoint(design_version_id: str, report_id: str):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 68: `POST /api/v1/design-versions/{design_version_id}/reports/complete-package`
- **Handler Function:** `generate_complete_package_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def generate_complete_package_endpoint(design_version_id: str, project_id: Optional[str] = None):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 69: `GET /api/v1/design-versions/{design_version_id}/reports/{report_id}/download`
- **Handler Function:** `download_generic_report_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def download_generic_report_endpoint(design_version_id: str, report_id: str, format: str = "pdf"):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 70: `GET /api/v1/design-versions/{design_version_id}/reports`
- **Handler Function:** `list_reports_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def list_reports_endpoint(design_version_id: str, project_id: Optional[str] = None):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 71: `POST /api/v1/design-versions/{design_version_id}/reports/technical`
- **Handler Function:** `generate_technical_report_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def generate_technical_report_endpoint(design_version_id: str, project_id: Optional[str] = None):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 72: `POST /api/v1/design-versions/{design_version_id}/reports/cost-boq`
- **Handler Function:** `generate_cost_boq_report_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def generate_cost_boq_report_endpoint(design_version_id: str, project_id: Optional[str] = None):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


### Endpoint 73: `POST /api/v1/design-versions/{design_version_id}/reports/professional`
- **Handler Function:** `generate_professional_report_endpoint` in `apps/api-gateway/main.py`
- **Authentication Required:** `Public`
- **Role Restriction:** `Standard Member`
- **Parameters & Dependency Signature:**
```python
def generate_professional_report_endpoint(design_version_id: str, project_id: Optional[str] = None):
    ...
```
- **Operational Behavior:** Validates tenant identity from `get_current_user`, enforces organization boundary, and executes business domain logic.


---

## 3. Request/Response Contracts & Error Handling
All endpoints enforce strict Pydantic schemas. Invalid payloads result in standard `HTTP 422 Unprocessable Entity` with detailed field violation arrays. Authentication failures emit `HTTP 401 Unauthorized` with `WWW-Authenticate: Bearer` challenge. Tenant authorization failures emit `HTTP 403 Forbidden`.
