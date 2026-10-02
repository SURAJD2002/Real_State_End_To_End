"""
Planwise Enterprise — Cost Change Propagation Engine
Delta Specification & M3 Master Specification §15

Maintains cache invalidation dependency DAG:
- Geometry Change: DESIGN_CHANGED → QTO_STALE → BOQ_STALE → COST_STALE → SCHEDULE_STALE
- Rate Snapshot Change: RATE_CHANGED → COST_STALE (QTO preserved!)
- Measurement Rule Change: MEASUREMENT_RULE_CHANGED → QTO_STALE → BOQ_STALE → COST_STALE

Ensures released / frozen estimates are never mutated.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class InvalidationTrigger(str, Enum):
    GEOMETRY_CHANGED = "GEOMETRY_CHANGED"
    RATE_SNAPSHOT_CHANGED = "RATE_SNAPSHOT_CHANGED"
    MEASUREMENT_RULE_CHANGED = "MEASUREMENT_RULE_CHANGED"
    ASSEMBLY_CHANGED = "ASSEMBLY_CHANGED"
    MANUAL_RECALCULATE = "MANUAL_RECALCULATE"


class EntityStaleState(BaseModel):
    designVersionId: str
    qtoStale: bool = False
    boqStale: bool = False
    costStale: bool = False
    scheduleStale: bool = False
    lastTrigger: Optional[InvalidationTrigger] = None
    reason: str = ""
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ChangePropagationEngine:
    """Tracks and evaluates cache invalidations across design versions."""

    def __init__(self):
        self._states: Dict[str, EntityStaleState] = {}
        self._released_versions: set = set()

    def mark_version_released(self, design_version_id: str) -> None:
        """Freezes version so changes cannot alter historical baseline."""
        self._released_versions.add(design_version_id)

    def is_version_released(self, design_version_id: str) -> bool:
        return design_version_id in self._released_versions

    def propagate_change(
        self,
        design_version_id: str,
        trigger: InvalidationTrigger,
        detail: str = ""
    ) -> EntityStaleState:
        """
        Calculates downstream stale states according to the dependency DAG.
        If version is released, raises an exception to preserve immutability.
        """
        if self.is_version_released(design_version_id):
            raise ValueError(f"Cannot mutate released design version {design_version_id}. Create a new DesignVersion branch.")

        state = self._states.get(design_version_id) or EntityStaleState(designVersionId=design_version_id)
        state.lastTrigger = trigger
        state.updatedAt = datetime.utcnow().isoformat()

        if trigger == InvalidationTrigger.GEOMETRY_CHANGED:
            # Full geometric invalidation
            state.qtoStale = True
            state.boqStale = True
            state.costStale = True
            state.scheduleStale = True
            state.reason = f"Geometry changed: {detail}. QTO, BOQ, Cost, and Schedule invalidated."

        elif trigger == InvalidationTrigger.RATE_SNAPSHOT_CHANGED:
            # QTO remains intact! Only pricing is invalidated.
            state.qtoStale = False
            state.boqStale = True
            state.costStale = True
            state.scheduleStale = False
            state.reason = f"Rate snapshot updated: {detail}. QTO preserved; BOQ amounts and Cost recalculated."

        elif trigger in [InvalidationTrigger.MEASUREMENT_RULE_CHANGED, InvalidationTrigger.ASSEMBLY_CHANGED]:
            # Rule or assembly changed
            state.qtoStale = True
            state.boqStale = True
            state.costStale = True
            state.scheduleStale = False
            state.reason = f"Rules/Assemblies modified: {detail}. QTO and Cost invalidated."

        elif trigger == InvalidationTrigger.MANUAL_RECALCULATE:
            state.qtoStale = False
            state.boqStale = False
            state.costStale = False
            state.reason = f"Manual recalculation triggered: {detail}."

        self._states[design_version_id] = state
        return state

    def get_state(self, design_version_id: str) -> EntityStaleState:
        return self._states.get(design_version_id) or EntityStaleState(designVersionId=design_version_id)

    def mark_clean(self, design_version_id: str) -> EntityStaleState:
        state = EntityStaleState(
            designVersionId=design_version_id,
            qtoStale=False,
            boqStale=False,
            costStale=False,
            scheduleStale=False,
            reason="All pipelines up to date"
        )
        self._states[design_version_id] = state
        return state


GLOBAL_CHANGE_PROPAGATION = ChangePropagationEngine()
