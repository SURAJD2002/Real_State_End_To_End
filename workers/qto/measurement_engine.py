"""
Planwise Enterprise — IS 1200 Measurement Rules Engine
Delta Specification & M3 Master Specification §2, §3

Deterministic, versioned measurement rules compliant with IS 1200 principles.
Every rule declares formula, inclusions, exclusions, unit, rounding policy,
source element types, and verification status.
"""

from typing import Dict, List, Any, Optional
from packages.schemas.qto_model import MeasurementRule


MEASUREMENT_RULES_REGISTRY: Dict[str, MeasurementRule] = {
    "QTO-WALL-001": MeasurementRule(
        ruleId="QTO-WALL-001",
        standardReference="IS-1200-PART-03-BRICKWORK",
        version="2026.Q4-V1",
        discipline="CIVIL_STRUCTURAL",
        category="MASONRY",
        description="Masonry wall volume measured net of all openings (doors, windows, voids) exceeding 0.1 m²",
        unit="m³",
        formula="L × H × T - opening deductions",
        inclusions=["Bed and vertical joints", "Scaffolding", "Raking joints for pointing"],
        exclusions=["Door and window clear openings", "Embedded structural columns", "Precast lintel volume"],
        roundingPolicy="0.001",
        sourceElementTypes=["WALL"],
        verificationStatus="VERIFIED"
    ),
    "QTO-WALL-002": MeasurementRule(
        ruleId="QTO-WALL-002",
        standardReference="IS-1200-PART-03-BRICKWORK",
        version="2026.Q4-V1",
        discipline="ARCHITECTURAL",
        category="MASONRY",
        description="Wall net face surface area for thin partitions and blockwork billing",
        unit="m²",
        formula="∑ (Length × Height) − ∑ (Opening Width × Opening Height)",
        inclusions=["All face areas excluding jambs"],
        exclusions=["Openings exceeding 0.1 m²"],
        roundingPolicy="0.01",
        sourceElementTypes=["WALL"],
        verificationStatus="VERIFIED"
    ),
    "QTO-SLAB-001": MeasurementRule(
        ruleId="QTO-SLAB-001",
        standardReference="IS-1200-PART-02-CONCRETE",
        version="2026.Q4-V1",
        discipline="CIVIL_STRUCTURAL",
        category="CONCRETE",
        description="Reinforced concrete slab volume net of stair wells and MEP shafts",
        unit="m³",
        formula="(Gross slab boundary polygon area − ∑ Opening voids) × Slab thickness",
        inclusions=["Shuttering contact surfaces", "Pouring and vibratory compaction"],
        exclusions=["Cutouts and vertical service shafts exceeding 0.1 m²", "Stairwell penetrations"],
        roundingPolicy="0.001",
        sourceElementTypes=["SLAB"],
        verificationStatus="VERIFIED"
    ),
    "QTO-SLAB-002": MeasurementRule(
        ruleId="QTO-SLAB-002",
        standardReference="IS-1200-PART-02-CONCRETE",
        version="2026.Q4-V1",
        discipline="CIVIL_STRUCTURAL",
        category="CONCRETE",
        description="Net horizontal structural slab area",
        unit="m²",
        formula="Gross slab boundary polygon area − ∑ Opening voids",
        inclusions=["Perimeter slab projections up to 150mm"],
        exclusions=["Stairwell openings", "Shaft openings"],
        roundingPolicy="0.01",
        sourceElementTypes=["SLAB"],
        verificationStatus="VERIFIED"
    ),
    "QTO-COL-001": MeasurementRule(
        ruleId="QTO-COL-001",
        standardReference="IS-1200-PART-02-CONCRETE",
        version="2026.Q4-V1",
        discipline="CIVIL_STRUCTURAL",
        category="CONCRETE",
        description="Structural column concrete solid volume measured from top of floor to bottom of next slab",
        unit="m³",
        formula="∑ (Cross-sectional Width × Cross-sectional Depth × Clear Height)",
        inclusions=["Column core", "Surface finishes preparation"],
        exclusions=["Embedded conduits", "Slab intersection volume"],
        roundingPolicy="0.001",
        sourceElementTypes=["COLUMN"],
        verificationStatus="VERIFIED"
    ),
    "QTO-STAIR-001": MeasurementRule(
        ruleId="QTO-STAIR-001",
        standardReference="IS-1200-PART-02-CONCRETE",
        version="2026.Q4-V1",
        discipline="CIVIL_STRUCTURAL",
        category="CONCRETE",
        description="Parametric concrete volume of staircase flights including waist slab, risers, treads and mid-landings",
        unit="m³",
        formula="Flight waist slab volume + (0.5 × Riser × Tread × Width × Steps) + Landing volume",
        inclusions=["Waist slab", "Steps", "Landings"],
        exclusions=["Handrails and metal balustrades"],
        roundingPolicy="0.001",
        sourceElementTypes=["STAIR"],
        verificationStatus="VERIFIED"
    ),
    "QTO-PLASTER-INT-001": MeasurementRule(
        ruleId="QTO-PLASTER-INT-001",
        standardReference="IS-1200-PART-12-PLASTERING",
        version="2026.Q4-V1",
        discipline="ARCHITECTURAL",
        category="PLASTER",
        description="Internal cement plaster (12mm smooth float finish) to interior wall faces and ceiling soffits",
        unit="m²",
        formula="∑ (Internal wall faces net of openings) + ∑ (Usable room ceiling areas)",
        inclusions=["Curing", "Corner beading", "Scaffolding up to 3.5m"],
        exclusions=["Deductions for openings exceeding 0.5 m² per IS 1200 Part 12 clause 4.2"],
        roundingPolicy="0.01",
        sourceElementTypes=["WALL", "SPACE"],
        verificationStatus="VERIFIED"
    ),
    "QTO-PLASTER-EXT-001": MeasurementRule(
        ruleId="QTO-PLASTER-EXT-001",
        standardReference="IS-1200-PART-12-PLASTERING",
        version="2026.Q4-V1",
        discipline="ARCHITECTURAL",
        category="PLASTER",
        description="External double-coat sand-faced waterproofing plaster (20mm) to exterior exposed walls",
        unit="m²",
        formula="∑ (External wall face area) − ∑ (External window & door opening areas)",
        inclusions=["Waterproofing admixture", "Grooves and drip moulds"],
        exclusions=["Window openings"],
        roundingPolicy="0.01",
        sourceElementTypes=["WALL"],
        verificationStatus="VERIFIED"
    ),
    "QTO-FLOOR-001": MeasurementRule(
        ruleId="QTO-FLOOR-001",
        standardReference="IS-1200-PART-11-PAVING-AND-FLOOR-FINISHES",
        version="2026.Q4-V1",
        discipline="FINISHES",
        category="FLOORING",
        description="Finished floor tiling measured over clear room carpet polygon area",
        unit="m²",
        formula="∑ (Net room carpet area polygon)",
        inclusions=["Adhesive or cement mortar bedding", "Epoxy grouting", "Surface cleaning"],
        exclusions=["Skirting height", "Door threshold step marble"],
        roundingPolicy="0.01",
        sourceElementTypes=["SPACE"],
        verificationStatus="VERIFIED"
    ),
    "QTO-SKIRTING-001": MeasurementRule(
        ruleId="QTO-SKIRTING-001",
        standardReference="IS-1200-PART-11-PAVING-AND-FLOOR-FINISHES",
        version="2026.Q4-V1",
        discipline="FINISHES",
        category="FLOORING",
        description="100mm matching tile skirting measured along room perimeter less door opening widths",
        unit="m",
        formula="∑ (Room perimeter) − ∑ (Door opening widths opening into space)",
        inclusions=["Top edge rounded profiling", "Adhesive bedding"],
        exclusions=["Door opening thresholds"],
        roundingPolicy="0.01",
        sourceElementTypes=["SPACE", "OPENING"],
        verificationStatus="VERIFIED"
    ),
    "QTO-DOOR-001": MeasurementRule(
        ruleId="QTO-DOOR-001",
        standardReference="IS-1200-PART-15-JOINERY",
        version="2026.Q4-V1",
        discipline="ARCHITECTURAL",
        category="JOINERY",
        description="Pre-hung engineered door leaf and frame units counted by size specification",
        unit="no.",
        formula="count(CBM openings where type == 'DOOR')",
        inclusions=["Door frame", "Flush shutter", "Hinges, locks, tower bolts, door stopper"],
        exclusions=["Painting/polishing (billed separately under finishes)"],
        roundingPolicy="1",
        sourceElementTypes=["OPENING"],
        verificationStatus="VERIFIED"
    ),
    "QTO-WINDOW-001": MeasurementRule(
        ruleId="QTO-WINDOW-001",
        standardReference="IS-1200-PART-15-JOINERY",
        version="2026.Q4-V1",
        discipline="ARCHITECTURAL",
        category="JOINERY",
        description="Window units with glazed panels and mosquito screens counted by specification",
        unit="no.",
        formula="count(CBM openings where type == 'WINDOW')",
        inclusions=["UPVC/Aluminium frame", "5mm toughened glass", "Hardware & silicone weather seal"],
        exclusions=["External safety MS grill"],
        roundingPolicy="1",
        sourceElementTypes=["OPENING"],
        verificationStatus="VERIFIED"
    ),
    "QTO-EXC-001": MeasurementRule(
        ruleId="QTO-EXC-001",
        standardReference="IS-1200-PART-01-EARTHWORK",
        version="2026.Q4-V1",
        discipline="CIVIL_STRUCTURAL",
        category="EARTHWORK",
        description="Preliminary foundation trench excavation based on structural column locations with 10% working space allowance",
        unit="m³",
        formula="count(Columns) × Nominal Footing Base Area (1.8m × 1.8m) × Foundation Depth (1.5m) × 1.10",
        inclusions=["Excavation in ordinary soil", "Trimming of sides and bottoms", "Dewatering buffer"],
        exclusions=["Rock blasting", "Deep pile foundations"],
        roundingPolicy="0.01",
        sourceElementTypes=["COLUMN"],
        verificationStatus="REQUIRES_SOURCE_VERIFICATION"
    ),
    "QTO-WATERPROOF-001": MeasurementRule(
        ruleId="QTO-WATERPROOF-001",
        standardReference="IS-1200-PART-08-WATERPROOFING",
        version="2026.Q4-V1",
        discipline="ARCHITECTURAL",
        category="WATERPROOFING",
        description="Elastomeric waterproofing coating to terrace roof and toilet sunken slabs with 300mm vertical coving",
        unit="m²",
        formula="Terrace Roof Slab Area + ∑ (Toilet/Bath floor areas + perimeter × 0.30m coving)",
        inclusions=["Surface preparation", "Polymer modified slurry coats", "Protective screed"],
        exclusions=["Structural concrete slab"],
        roundingPolicy="0.01",
        sourceElementTypes=["SPACE", "SLAB"],
        verificationStatus="REQUIRES_SOURCE_VERIFICATION"
    ),
    "QTO-PAINT-001": MeasurementRule(
        ruleId="QTO-PAINT-001",
        standardReference="IS-1200-PART-13-PAINTING",
        version="2026.Q4-V1",
        discipline="FINISHES",
        category="PAINTING",
        description="Premium emulsion painting (2 coats over 1 coat primer & 2 coats wall putty) to plastered wall and ceiling surfaces",
        unit="m²",
        formula="Total Net Plastered Area (Internal + External)",
        inclusions=["Surface sanding", "Primer", "Acrylic putty", "Two coats topcoat finish"],
        exclusions=["Joinery and metal finishes"],
        roundingPolicy="0.01",
        sourceElementTypes=["WALL", "SPACE"],
        verificationStatus="VERIFIED"
    ),
    "QTO-MEP-ELEC-001": MeasurementRule(
        ruleId="QTO-MEP-ELEC-001",
        standardReference="IS-732-ELECTRICAL-WIRING",
        version="2026.Q4-V1",
        discipline="MEP_PRELIMINARY",
        category="ELECTRICAL",
        description="Preliminary electrical point wiring count for lighting, sockets, fans, and power circuits",
        unit="points",
        formula="∑ (MEP System electrical components count) or max(28, round(Gross BUA × 0.45))",
        inclusions=["FRLS copper conduits in slab/walls", "Modular switch and box", "Circuit wire to DB"],
        exclusions=["Light fixtures", "Ceiling fans"],
        roundingPolicy="1",
        sourceElementTypes=["SYSTEM"],
        verificationStatus="REQUIRES_SOURCE_VERIFICATION"
    ),
    "QTO-MEP-PLUMB-001": MeasurementRule(
        ruleId="QTO-MEP-PLUMB-001",
        standardReference="IS-1200-PART-16-PLUMBING",
        version="2026.Q4-V1",
        discipline="MEP_PRELIMINARY",
        category="PLUMBING",
        description="Preliminary plumbing wet stack installations for bathrooms and kitchen wet areas",
        unit="stacks",
        formula="count(Bathrooms & Toilets) + count(Kitchens)",
        inclusions=["Water supply manifold", "Drainage stack", "CP fittings allowance", "Sanitary ware allowance"],
        exclusions=["Solar water heater", "Borewell piping"],
        roundingPolicy="1",
        sourceElementTypes=["SPACE"],
        verificationStatus="REQUIRES_SOURCE_VERIFICATION"
    )
}


def get_measurement_rule(rule_id: str) -> MeasurementRule:
    """Returns rule definition from registry, raising KeyError if unknown."""
    if rule_id not in MEASUREMENT_RULES_REGISTRY:
        raise KeyError(f"Measurement rule {rule_id} not registered in IS 1200 engine.")
    return MEASUREMENT_RULES_REGISTRY[rule_id]


def list_measurement_rules() -> List[MeasurementRule]:
    """Returns all available measurement rules."""
    return list(MEASUREMENT_RULES_REGISTRY.values())
