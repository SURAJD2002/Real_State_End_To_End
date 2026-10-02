"""
Planwise Enterprise — Construction Assembly Schema
Delta Specification & M3 Master Specification §6

Defines parametric assemblies that bind model takeoff quantities to
constituent material, labour, and equipment components with explicit wastage and rate references.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AssemblyComponent(BaseModel):
    componentId: str = Field(..., description="Unique component ID within assembly, e.g. CMP-BRICK-230")
    materialId: str = Field(..., description="Material identifier from catalog")
    description: str = Field(..., description="Component description")
    unit: str = Field(..., description="Component consumption unit: m³, m², kg, bag, no., m")
    consumptionFormula: str = Field("takeoff_qty * factor", description="Mathematical expression for consumption")
    consumptionFactor: float = Field(1.0, description="Multiplier per unit of base assembly")
    wastagePercent: float = Field(0.0, description="Standard statutory/practical wastage allowance %")
    rateReferenceId: str = Field(..., description="Key into CostRateSnapshot rates dictionary")


class ConstructionAssembly(BaseModel):
    assemblyId: str = Field(..., description="Unique assembly identifier, e.g. EXT_WALL_230_BRICK")
    name: str = Field(..., description="Human-readable trade assembly name")
    discipline: str = Field("ARCHITECTURAL", description="CIVIL_STRUCTURAL, ARCHITECTURAL, FINISHES, MEP_PRELIMINARY")
    category: str = Field("MASONRY", description="EARTHWORK, CONCRETE, MASONRY, PLASTER, FLOORING, FINISHES, JOINERY")
    baseUnit: str = Field("m³", description="Takeoff measurement unit for this assembly: m³, m², no.")
    version: str = Field("1.0.0", description="Assembly version")
    specification: str = Field(..., description="Engineering standard / trade specification")
    components: List[AssemblyComponent] = Field(default_factory=list, description="Constituent component items")
