"""
Planwise Enterprise — M3 Async QTO & Cost DAG Pipeline
Delta Specification & M3 Master Specification §18

Executes the 11-node deterministic job DAG:
DESIGN_RELEASED
      ↓
LOAD_CBM
      ↓
LOAD_MEASUREMENT_RULES
      ↓
EXTRACT_GEOMETRY
      ↓
RUN_QTO
      ↓
COMPILE_ASSEMBLIES
      ↓
LOAD_RATE_SNAPSHOT
      ↓
GENERATE_BOQ
      ↓
CALCULATE_COST
      ↓
VALIDATE_TRACEABILITY
      ↓
GENERATE_COST_ARTIFACTS
      ↓
COMPLETED

Every node records nodeId, name, inputHash, outputHash, engineVersion, status, timing, and errors.
"""

import time
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from packages.schemas.building_model import CanonicalBuildingModel
from packages.schemas.cost_model import CostEstimate
from workers.qto.measurement_engine import list_measurement_rules
from workers.qto.assembly_engine import list_assemblies
from workers.qto.rate_snapshot_engine import get_rate_snapshot
from workers.qto.qto_engine import ModelLinkedQTOEngine
from workers.qto.cost_engine import DeterministicCostEngine


class DAGNodeRecord(BaseModel):
    nodeId: str
    name: str
    status: str = "PENDING" # PENDING, RUNNING, COMPLETED, FAILED
    engineVersion: str = "3.0.0-M3"
    inputHash: str = ""
    outputHash: str = ""
    durationMs: float = 0.0
    errors: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class M3CostPipelineJob(BaseModel):
    jobId: str
    designVersionId: str
    projectId: str
    rateSnapshotId: str
    qualityTier: str = "STANDARD"
    status: str = "PENDING"
    startedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completedAt: Optional[str] = None
    nodes: List[DAGNodeRecord] = Field(default_factory=list)
    costEstimate: Optional[Dict[str, Any]] = None
    qtoHash: str = ""
    boqHash: str = ""
    costHash: str = ""


class M3AsyncCostDAGPipeline:
    """Orchestrates sequential, reproducible execution of the M3 QTO & Cost DAG."""

    def __init__(
        self,
        model: CanonicalBuildingModel,
        rate_snapshot_id: str = "INDIA-MUMBAI-2026-Q4-V1",
        quality_tier: str = "STANDARD"
    ):
        self.model = model
        self.rate_snapshot_id = rate_snapshot_id
        self.quality_tier = quality_tier
        self.job_id = f"job-m3-{model.designVersionId}-{int(time.time())}"

    def run_pipeline(self) -> M3CostPipelineJob:
        """Executes all 11 nodes sequentially, producing verified artifacts."""
        job = M3CostPipelineJob(
            jobId=self.job_id,
            designVersionId=self.model.designVersionId,
            projectId=self.model.projectId,
            rateSnapshotId=self.rate_snapshot_id,
            qualityTier=self.quality_tier,
            status="RUNNING",
            startedAt=datetime.utcnow().isoformat()
        )

        state: Dict[str, Any] = {}
        nodes_def = [
            ("NODE-01", "DESIGN_RELEASED"),
            ("NODE-02", "LOAD_CBM"),
            ("NODE-03", "LOAD_MEASUREMENT_RULES"),
            ("NODE-04", "EXTRACT_GEOMETRY"),
            ("NODE-05", "RUN_QTO"),
            ("NODE-06", "COMPILE_ASSEMBLIES"),
            ("NODE-07", "LOAD_RATE_SNAPSHOT"),
            ("NODE-08", "GENERATE_BOQ"),
            ("NODE-09", "CALCULATE_COST"),
            ("NODE-10", "VALIDATE_TRACEABILITY"),
            ("NODE-11", "GENERATE_COST_ARTIFACTS"),
            ("NODE-12", "COMPLETED")
        ]

        for nid, name in nodes_def:
            t0 = time.time()
            in_hash = hashlib.sha256(f"{nid}_{name}_{self.model.designVersionId}".encode()).hexdigest()[:16]
            node_rec = DAGNodeRecord(
                nodeId=nid,
                name=name,
                status="RUNNING",
                inputHash=in_hash,
                timestamp=datetime.utcnow().isoformat()
            )

            try:
                out_hash = self._execute_node(name, state)
                node_rec.status = "COMPLETED"
                node_rec.outputHash = out_hash
            except Exception as e:
                node_rec.status = "FAILED"
                node_rec.errors.append(str(e))
                node_rec.durationMs = round((time.time() - t0) * 1000.0, 2)
                job.nodes.append(node_rec)
                job.status = "FAILED"
                job.completedAt = datetime.utcnow().isoformat()
                return job

            node_rec.durationMs = round((time.time() - t0) * 1000.0, 2)
            job.nodes.append(node_rec)

        job.status = "COMPLETED"
        job.completedAt = datetime.utcnow().isoformat()
        if "estimate" in state:
            est: CostEstimate = state["estimate"]
            job.costEstimate = est.dict()
            job.qtoHash = est.qtoHash
            job.boqHash = est.boqHash
            job.costHash = est.costHash

        return job

    def _execute_node(self, node_name: str, state: Dict[str, Any]) -> str:
        if node_name == "DESIGN_RELEASED":
            return hashlib.sha256(self.model.designVersionId.encode()).hexdigest()

        elif node_name == "LOAD_CBM":
            state["model"] = self.model
            return self.model.metadata.modelHash or hashlib.sha256(self.model.modelId.encode()).hexdigest()

        elif node_name == "LOAD_MEASUREMENT_RULES":
            rules = list_measurement_rules()
            state["rules"] = rules
            return hashlib.sha256(str(len(rules)).encode()).hexdigest()

        elif node_name == "EXTRACT_GEOMETRY":
            qto_engine = ModelLinkedQTOEngine(self.model)
            state["qto_engine"] = qto_engine
            return hashlib.sha256(f"{len(self.model.elements)}_{len(self.model.openings)}".encode()).hexdigest()

        elif node_name == "RUN_QTO":
            qto_engine: ModelLinkedQTOEngine = state["qto_engine"]
            takeoffs = qto_engine.run_full_takeoff()
            state["takeoffs"] = takeoffs
            qto_hash = hashlib.sha256(json.dumps([t.outputHash for t in takeoffs], sort_keys=True).encode()).hexdigest()
            state["qtoHash"] = qto_hash
            return qto_hash

        elif node_name == "COMPILE_ASSEMBLIES":
            assemblies = list_assemblies()
            state["assemblies"] = assemblies
            return hashlib.sha256(str(len(assemblies)).encode()).hexdigest()

        elif node_name == "LOAD_RATE_SNAPSHOT":
            snapshot = get_rate_snapshot(self.rate_snapshot_id)
            state["snapshot"] = snapshot
            return snapshot.hash

        elif node_name == "GENERATE_BOQ":
            cost_engine = DeterministicCostEngine(
                model=self.model,
                rate_snapshot_id=self.rate_snapshot_id,
                quality_tier=self.quality_tier
            )
            estimate = cost_engine.calculate_cost_estimate(state["takeoffs"])
            state["cost_engine"] = cost_engine
            state["estimate"] = estimate
            return estimate.boqHash

        elif node_name == "CALCULATE_COST":
            estimate: CostEstimate = state["estimate"]
            return estimate.costHash

        elif node_name == "VALIDATE_TRACEABILITY":
            estimate: CostEstimate = state["estimate"]
            # Validate every BOQ line resolves to at least one valid CBM object
            all_canonical_ids = {e.elementId for e in self.model.elements} | \
                                {o.openingId for o in self.model.openings} | \
                                {s.spaceId for s in self.model.spaces} | \
                                {sys.systemId for sys in self.model.systems}

            for line in estimate.boqLines:
                if not line.sourceElementIds:
                    raise ValueError(f"Traceability violation: BOQ line {line.itemCode} has no sourceElementIds.")
                for eid in line.sourceElementIds:
                    if eid not in all_canonical_ids:
                        raise ValueError(f"Traceability violation: element {eid} referenced in {line.itemCode} does not exist in CBM.")
            return hashlib.sha256(b"TRACEABILITY_VERIFIED").hexdigest()

        elif node_name == "GENERATE_COST_ARTIFACTS":
            estimate: CostEstimate = state["estimate"]
            return hashlib.sha256(f"ARTIFACTS_{estimate.estimateId}".encode()).hexdigest()

        elif node_name == "COMPLETED":
            return hashlib.sha256(b"M3_PIPELINE_COMPLETE").hexdigest()

        return hashlib.sha256(node_name.encode()).hexdigest()
