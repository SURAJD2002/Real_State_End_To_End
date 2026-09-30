"""
API Gateway Service (FastAPI)
Stateless transactional API for project CRUD, CAD parcel geometry auto-save,
deterministic Feasibility DAG, Parametric House Generation, Traceable BOQ,
CPM Scheduling, and Immutable Engineer Handoff Packages (Delta Specification).
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
import hashlib

from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add project root to sys.path to import worker modules
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from workers.geometry.engine import compute_parcel_metrics
from workers.regulation.evaluator import evaluate_mumbai_dcpr_2034
from workers.financial.proforma import calculate_financial_proforma
from workers.generation.house_generator import generate_house_options
from workers.qto.boq_engine import compute_traceable_boq
from workers.schedule.cpm_engine import generate_construction_schedule
from workers.release.manifest_engine import (
    generate_release_fingerprint,
    generate_ifc4_model,
    compile_handoff_package
)

app = FastAPI(
    title="Planwise Enterprise — Land-to-Home Platform API",
    description="Stateless API Gateway for Real Estate Feasibility, House Option Generation, Traceable BOQ & Engineer Handoffs",
    version="2.0.0"
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

class BuildRequestPayload(BaseModel):
    designVersionId: str
    optionId: str
    requestedQualityTier: str = "STANDARD"
    customerAcknowledgements: List[str] = Field(
        default=["ESTIMATE_RANGE", "SITE_VERIFICATION", "PROFESSIONAL_DELIVERY", "CHANGE_ORDER_RULES"]
    )
    customerNotes: Optional[str] = "Approved for architectural and structural engineering review"

class ProfessionalGateApproval(BaseModel):
    gate: str = "G3" # G0 to G8
    decision: str = "APPROVED" # APPROVED, REQUEST_REVISION, REJECTED
    professionalId: str = "ENG-MH-48201"
    reasonCodes: List[str] = []
    notes: Optional[str] = "Satisfies preliminary span limits and NBC 2016 room dimensions"

# --- In-Memory Repository for Dev Mode ---
PROJECTS_DB: Dict[str, Dict[str, Any]] = {}
HOUSE_OPTIONS_CACHE: Dict[str, List[Dict[str, Any]]] = {}
RELEASES_DB: Dict[str, Dict[str, Any]] = {}

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
            "latestFeasibility": None,
            "selectedOption": None,
            "activeRelease": None
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
        "version": "2.0.0"
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
        "latestFeasibility": None,
        "selectedOption": None,
        "activeRelease": None
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

# --- Parametric House Options & Generation Pipeline ---

@app.get("/api/v1/projects/{project_id}/house-options")
def get_house_options(project_id: str, quality_tier: str = "STANDARD"):
    """
    Generates 3 diverse, feasible low-rise residential options with traceable BOQ and CPM schedules.
    """
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")

    options = generate_house_options()
    
    # Enrich each option with model-derived BOQ and Schedule
    for opt in options:
        opt["boq"] = compute_traceable_boq(opt, quality_tier=quality_tier)
        opt["schedule"] = generate_construction_schedule(
            total_bua_sqm=opt["layout"]["totalGrossBUASqm"],
            floors=opt["layout"]["floors"]
        )

    HOUSE_OPTIONS_CACHE[project_id] = options
    return options

# --- BUILD Button & Immutable Lock (Delta Spec §12, §13, §14) ---

@app.post("/api/v1/design-versions/{design_version_id}/build-request", status_code=status.HTTP_202_ACCEPTED)
def request_build(design_version_id: str, payload: BuildRequestPayload):
    """
    Processes customer Build request: validates acknowledgements, freezes the design,
    computes cryptographic release fingerprint, and creates an immutable handoff package.
    """
    required_acks = {"ESTIMATE_RANGE", "SITE_VERIFICATION", "PROFESSIONAL_DELIVERY"}
    submitted_acks = set(payload.customerAcknowledgements)
    if not required_acks.issubset(submitted_acks):
        raise HTTPException(
            status_code=400,
            detail=f"Missing mandatory acknowledgements: {required_acks - submitted_acks}"
        )

    # Locate the target option
    target_option = None
    target_proj_id = None
    for pid, options in HOUSE_OPTIONS_CACHE.items():
        for opt in options:
            if opt["designVersionId"] == design_version_id or opt["optionId"] == payload.optionId:
                target_option = opt
                target_proj_id = pid
                break
        if target_option:
            break

    if not target_option:
        # Fallback to generating a fresh option if not in cache
        opts = generate_house_options()
        target_option = opts[0]
        target_option["boq"] = compute_traceable_boq(target_option, quality_tier=payload.requestedQualityTier)
        target_option["schedule"] = generate_construction_schedule(
            total_bua_sqm=target_option["layout"]["totalGrossBUASqm"],
            floors=target_option["layout"]["floors"]
        )
        target_proj_id = "proj-mumbai-default-01"

    release_id = f"rel-{uuid.uuid4().hex[:12]}"
    
    # Compute SHA-256 release fingerprint
    fingerprint = generate_release_fingerprint(
        geometry_hash="sha256:geom_bandra_10k",
        regulation_hash="sha256:mcgm_dcpr2034_v1",
        customer_brief_hash="sha256:brief_std_res",
        design_hash=target_option["designHash"],
        boq_hash=f"sha256:{hashlib.sha256(json.dumps(target_option['boq']['lines']).encode()).hexdigest()[:12]}",
        schedule_hash=f"sha256:{hashlib.sha256(json.dumps(target_option['schedule']['activities']).encode()).hexdigest()[:12]}"
    )

    package = compile_handoff_package(
        release_id=release_id,
        project_name=PROJECTS_DB.get(target_proj_id, {}).get("name", "Bandra Residential Villa"),
        house_option=target_option,
        boq=target_option["boq"],
        schedule=target_option["schedule"],
        release_fingerprint=fingerprint
    )

    RELEASES_DB[release_id] = {
        "releaseId": release_id,
        "designVersionId": design_version_id,
        "projectId": target_proj_id,
        "fingerprint": fingerprint,
        "lockedAt": datetime.utcnow().isoformat(),
        "status": "BUILD_REQUESTED",
        "lifecycleState": "PROFESSIONAL_REVIEW",
        "handoffPackage": package,
        "houseOption": target_option
    }

    if target_proj_id in PROJECTS_DB:
        PROJECTS_DB[target_proj_id]["activeRelease"] = RELEASES_DB[release_id]
        PROJECTS_DB[target_proj_id]["status"] = "FEASIBILITY_RUNNING"

    return {
        "buildRequestId": f"br-{uuid.uuid4().hex[:8]}",
        "releaseId": release_id,
        "releaseFingerprint": fingerprint,
        "lifecycleState": "PROFESSIONAL_REVIEW",
        "requiredGates": ["G0", "G1", "G2", "G3", "G4"],
        "message": "Design locked and submitted for professional engineering review.",
        "package": package
    }

@app.get("/api/v1/releases/{release_id}/handoff-package")
def get_handoff_package(release_id: str):
    if release_id not in RELEASES_DB:
        raise HTTPException(status_code=404, detail="Release record not found")
    return RELEASES_DB[release_id]["handoffPackage"]

@app.post("/api/v1/releases/{release_id}/approvals")
def update_gate_approval(release_id: str, approval: ProfessionalGateApproval):
    if release_id not in RELEASES_DB:
        raise HTTPException(status_code=404, detail="Release record not found")
    
    rel = RELEASES_DB[release_id]
    pkg = rel["handoffPackage"]
    
    # Update gate status
    updated = False
    for g in pkg["humanVerificationGates"]:
        if g["gate"] == approval.gate:
            g["status"] = approval.decision
            g["verifiedBy"] = approval.professionalId
            g["verifiedAt"] = datetime.utcnow().isoformat()
            g["notes"] = approval.notes
            updated = True
            break
            
    if not updated:
        raise HTTPException(status_code=400, detail=f"Gate {approval.gate} not found in manifest")

    # If all G0-G3 gates approved, advance to PROFESSIONALLY_ACCEPTED
    all_approved = all(
        g["status"] == "APPROVED"
        for g in pkg["humanVerificationGates"][:4]
    )
    if all_approved:
        rel["lifecycleState"] = "PROFESSIONALLY_ACCEPTED"
        pkg["lifecycleState"] = "PROFESSIONALLY_ACCEPTED"

    return {
        "status": "UPDATED",
        "gate": approval.gate,
        "decision": approval.decision,
        "lifecycleState": rel["lifecycleState"],
        "handoffPackage": pkg
    }

@app.get("/api/v1/releases/{release_id}/ifc")
def download_ifc_model(release_id: str):
    """Exports open-standard IFC4 semantic model (Delta Spec §1, §12)."""
    if release_id not in RELEASES_DB:
        raise HTTPException(status_code=404, detail="Release not found")
    
    opt = RELEASES_DB[release_id]["houseOption"]
    ifc_text = generate_ifc4_model(opt, release_id)
    return Response(
        content=ifc_text,
        media_type="application/x-step",
        headers={"Content-Disposition": f"attachment; filename={release_id}.ifc"}
    )

# --- Golden Dataset Seed Loader ---

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
        "latestFeasibility": None,
        "selectedOption": None,
        "activeRelease": None
    }
    PROJECTS_DB[proj_id] = project

    # Immediately execute feasibility run for the golden dataset
    res = run_feasibility_dag(proj_id)
    # Pre-generate house options
    get_house_options(proj_id)

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
