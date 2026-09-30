"""
API Gateway Service (FastAPI)
Stateless transactional API for project CRUD, CAD parcel geometry auto-save,
and deterministic Feasibility DAG orchestration.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add project root to sys.path to import worker modules
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from workers.geometry.engine import compute_parcel_metrics
from workers.regulation.evaluator import evaluate_mumbai_dcpr_2034
from workers.financial.proforma import calculate_financial_proforma

app = FastAPI(
    title="Planwise Enterprise Feasibility API",
    description="Stateless API Gateway for Real Estate Feasibility & Mumbai DCPR 2034 Underwriting",
    version="1.0.0"
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Data Contracts ---

class GeometryAutoSavePayload(BaseModel):
    version: int = 1
    coordinates: List[List[float]] = Field(..., description="[[lng, lat], ...] coordinates in WGS84")
    existingRoadWidthM: float = 12.0
    proposedRoadWidthM: float = 18.0
    tenureType: str = "PRIVATE_FREEHOLD"
    cadastralSurveyNumber: str = "CTS-DEMO-101"

class ProjectCreateRequest(BaseModel):
    name: str = "Bandra East Transit Mixed-Use Development"
    description: Optional[str] = "Statutory feasibility evaluation under Mumbai DCPR 2034"
    jurisdiction: str = "MUMBAI_DCPR_2034"

# --- In-Memory Repository for Dev Mode ---
PROJECTS_DB: Dict[str, Dict[str, Any]] = {}

def get_or_create_default_project() -> Dict[str, Any]:
    if not PROJECTS_DB:
        default_id = "proj-mumbai-default-01"
        PROJECTS_DB[default_id] = {
            "id": default_id,
            "name": "Bandra East Transit Corridor Benchmark",
            "description": "10,000 sqm Mumbai Suburban Development Feasibility",
            "jurisdiction": "MUMBAI_DCPR_2034",
            "status": "DRAFT",
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat(),
            "parcel": {
                "coordinates": [
                    [72.86850, 19.11280],
                    [72.86950, 19.11400],
                    [72.87100, 19.11330],
                    [72.87000, 19.11210],
                    [72.86850, 19.11280]
                ],
                "cadastralNumber": "CTS-1842-BANDRA",
                "tenureType": "PRIVATE_FREEHOLD",
                "existingRoadWidthM": 12.0,
                "proposedRoadWidthM": 18.0,
                "version": 1
            },
            "latestFeasibility": None
        }
    return next(iter(PROJECTS_DB.values()))

# Initialize default project
get_or_create_default_project()


# --- Endpoints ---

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/v1/projects")
def list_projects():
    return list(PROJECTS_DB.values())

@app.post("/api/v1/projects", status_code=status.HTTP_201_CREATED)
def create_project(req: ProjectCreateRequest):
    proj_id = f"proj-{uuid.uuid4().hex[:8]}"
    project = {
        "id": proj_id,
        "name": req.name,
        "description": req.description,
        "jurisdiction": req.jurisdiction,
        "status": "DRAFT",
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "parcel": None,
        "latestFeasibility": None
    }
    PROJECTS_DB[proj_id] = project
    return project

@app.get("/api/v1/projects/{project_id}")
def get_project(project_id: str):
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    return PROJECTS_DB[project_id]

@app.put("/api/v1/projects/{project_id}/geometries")
def auto_save_geometries(project_id: str, payload: GeometryAutoSavePayload):
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = PROJECTS_DB[project_id]
    project["parcel"] = {
        "coordinates": payload.coordinates,
        "cadastralNumber": payload.cadastralSurveyNumber,
        "tenureType": payload.tenureType,
        "existingRoadWidthM": payload.existingRoadWidthM,
        "proposedRoadWidthM": payload.proposedRoadWidthM,
        "version": payload.version + 1,
        "updatedAt": datetime.utcnow().isoformat()
    }
    project["updatedAt"] = datetime.utcnow().isoformat()
    
    return {
        "status": "SAVED",
        "version": project["parcel"]["version"],
        "timestamp": project["updatedAt"]
    }

@app.post("/api/v1/projects/{project_id}/calculate-feasibility")
def run_feasibility_dag(project_id: str):
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = PROJECTS_DB[project_id]
    parcel = project.get("parcel")
    if not parcel or not parcel.get("coordinates") or len(parcel["coordinates"]) < 3:
        raise HTTPException(status_code=400, detail="Cannot run feasibility without valid parcel polygon coordinates.")

    coords = parcel["coordinates"]
    existing_road = parcel.get("existingRoadWidthM", 12.0)
    proposed_road = parcel.get("proposedRoadWidthM", 18.0)

    # 1. Geometry Worker Pipeline
    geom_metrics = compute_parcel_metrics(
        coordinates=coords,
        existing_road_width_m=existing_road,
        proposed_road_width_m=proposed_road
    )

    # 2. Regulation Worker Pipeline (Mumbai DCPR 2034)
    reg_metrics = evaluate_mumbai_dcpr_2034(
        net_developable_area_sqm=geom_metrics["netDevelopableAreaSqm"],
        effective_road_width_m=proposed_road
    )

    # 3. Financial Feasibility Pipeline (Pro-Forma Underwriting)
    fin_metrics = calculate_financial_proforma(
        permissible_bua_sqm=reg_metrics["permissibleBUASqm"],
        premium_fsi=reg_metrics["premiumFSI"]
    )

    result = {
        "runId": f"run-{uuid.uuid4().hex[:8]}",
        "projectId": project_id,
        "timestamp": datetime.utcnow().isoformat(),
        "regulationVersionId": reg_metrics["regulationVersionId"],
        "engineVersion": "1.0.0",
        "grossPlotAreaSqm": geom_metrics["grossAreaSqm"],
        "roadWideningDeductionSqm": geom_metrics["roadWideningDeductionSqm"],
        "amenityReservationSqm": geom_metrics["amenityReservationSqm"],
        "netDevelopableAreaSqm": geom_metrics["netDevelopableAreaSqm"],
        "baseFSI": reg_metrics["baseFSI"],
        "premiumFSI": reg_metrics["premiumFSI"],
        "tdrFSI": reg_metrics["tdrFSI"],
        "totalPermissibleFSI": reg_metrics["totalPermissibleFSI"],
        "permissibleBUASqm": reg_metrics["permissibleBUASqm"],
        "carpetAreaSqm": reg_metrics["carpetAreaSqm"],
        "maxBuildingHeightM": reg_metrics["maxBuildingHeightM"],
        "frontSetbackM": reg_metrics["frontSetbackM"],
        "standardParkingStalls": reg_metrics["standardParkingStalls"],
        "accessibleParkingStalls": reg_metrics["accessibleParkingStalls"],
        "financials": fin_metrics,
        "buildableCoordinates": geom_metrics["buildableCoordinates"]
    }

    project["latestFeasibility"] = result
    project["status"] = "COMPLETED"
    project["updatedAt"] = datetime.utcnow().isoformat()

    return result

@app.post("/api/v1/projects/load-golden-dataset")
def load_golden_dataset():
    """Loads the canonical 10,000 sqm Mumbai benchmark parcel from seed file."""
    seed_file = ROOT_DIR / "database" / "seeds" / "golden_mumbai_10000sqm.json"
    if not seed_file.exists():
        raise HTTPException(status_code=500, detail="Seed file not found")

    with open(seed_file, "r") as f:
        data = json.load(f)

    proj_id = "proj-mumbai-golden-10000"
    project = {
        "id": proj_id,
        "name": data["name"],
        "description": "Statutory benchmark walkthrough: 10,000 sqm plot on 18m road",
        "jurisdiction": data["jurisdiction"],
        "status": "DRAFT",
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "parcel": {
            "coordinates": data["coordinates"],
            "cadastralNumber": data["cadastralNumber"],
            "tenureType": data["tenureType"],
            "existingRoadWidthM": data["roadFrontage"]["existingWidthM"],
            "proposedRoadWidthM": data["roadFrontage"]["proposedWidthM"],
            "version": 1
        },
        "latestFeasibility": None
    }
    PROJECTS_DB[proj_id] = project

    # Immediately execute feasibility run for the golden dataset
    res = run_feasibility_dag(proj_id)
    return {
        "project": project,
        "feasibility": res
    }

@app.get("/api/v1/regulations/MUMBAI_DCPR_2034")
def get_mumbai_regulations():
    rule_file = ROOT_DIR / "packages" / "rules" / "mumbai_dcpr_2034.json"
    if not rule_file.exists():
        raise HTTPException(status_code=404, detail="Ruleset not found")
    with open(rule_file, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
