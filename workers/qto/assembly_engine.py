"""
Planwise Enterprise — Construction Assembly Engine
Delta Specification & M3 Master Specification §6

Manages parametric construction assemblies that decompose building elements into
constituent materials, labour trades, and equipment allocations.
"""

from typing import Dict, List, Optional
from packages.schemas.assembly_model import ConstructionAssembly, AssemblyComponent


CONSTRUCTION_ASSEMBLIES_REGISTRY: Dict[str, ConstructionAssembly] = {
    "EXT_WALL_230_BRICK": ConstructionAssembly(
        assemblyId="EXT_WALL_230_BRICK",
        name="230mm External Brick Masonry Assembly",
        discipline="ARCHITECTURAL",
        category="MASONRY",
        baseUnit="m³",
        version="2026.Q4-V1",
        specification="230mm thick traditional clay brick masonry in CM 1:6 with curing & jointing",
        components=[
            AssemblyComponent(
                componentId="CMP-EXT-BRICK",
                materialId="MAT_BRICK_RED",
                description="First class red clay bricks (approx 500 nos/m³)",
                unit="no.",
                consumptionFormula="takeoff_qty * 490",
                consumptionFactor=490.0,
                wastagePercent=5.0,
                rateReferenceId="RATE_BRICK_MASONRY"
            ),
            AssemblyComponent(
                componentId="CMP-EXT-MORTAR",
                materialId="MAT_CEMENT_MORTAR_1_6",
                description="Cement mortar 1:6 (cement + coarse sand)",
                unit="m³",
                consumptionFormula="takeoff_qty * 0.25",
                consumptionFactor=0.25,
                wastagePercent=4.0,
                rateReferenceId="RATE_BRICK_MASONRY"
            )
        ]
    ),
    "INT_WALL_115_BLOCK": ConstructionAssembly(
        assemblyId="INT_WALL_115_BLOCK",
        name="100-115mm Internal AAC Block Partition Assembly",
        discipline="ARCHITECTURAL",
        category="MASONRY",
        baseUnit="m³",
        version="2026.Q4-V1",
        specification="100/115mm Autoclaved Aerated Concrete (AAC) blocks with polymer thin-bed adhesive",
        components=[
            AssemblyComponent(
                componentId="CMP-INT-AAC",
                materialId="MAT_AAC_BLOCK_100",
                description="Grade 1 AAC blocks (IS 2185 Part 3)",
                unit="m³",
                consumptionFormula="takeoff_qty * 1.0",
                consumptionFactor=1.0,
                wastagePercent=4.0,
                rateReferenceId="RATE_AAC_BLOCK"
            ),
            AssemblyComponent(
                componentId="CMP-INT-ADHESIVE",
                materialId="MAT_BLOCK_ADHESIVE",
                description="Polymer-modified block jointing mortar",
                unit="kg",
                consumptionFormula="takeoff_qty * 35.0",
                consumptionFactor=35.0,
                wastagePercent=3.0,
                rateReferenceId="RATE_AAC_BLOCK"
            )
        ]
    ),
    "RCC_COLUMN_M25": ConstructionAssembly(
        assemblyId="RCC_COLUMN_M25",
        name="M25 RCC Column Assembly with Shuttering & Rebar",
        discipline="CIVIL_STRUCTURAL",
        category="CONCRETE",
        baseUnit="m³",
        version="2026.Q4-V1",
        specification="Design mix concrete M25 in columns including steel shuttering and Fe500D rebar allowance",
        components=[
            AssemblyComponent(
                componentId="CMP-COL-CONC",
                materialId="MAT_M25_CONCRETE",
                description="Design mix M25 ready-mix / site-batched concrete",
                unit="m³",
                consumptionFormula="takeoff_qty * 1.0",
                consumptionFactor=1.0,
                wastagePercent=3.0,
                rateReferenceId="RATE_RCC_M25"
            ),
            AssemblyComponent(
                componentId="CMP-COL-STEEL",
                materialId="MAT_STEEL_FE500D",
                description="Thermo-mechanically treated reinforcement steel Fe500D (approx 160 kg/m³)",
                unit="kg",
                consumptionFormula="takeoff_qty * 160.0",
                consumptionFactor=160.0,
                wastagePercent=4.0,
                rateReferenceId="RATE_STEEL_REBAR"
            ),
            AssemblyComponent(
                componentId="CMP-COL-FORMWORK",
                materialId="MAT_STEEL_FORMWORK",
                description="Plywood / steel shuttering with props and bracing (approx 12 m²/m³)",
                unit="m²",
                consumptionFormula="takeoff_qty * 12.0",
                consumptionFactor=12.0,
                wastagePercent=2.0,
                rateReferenceId="RATE_FORMWORK"
            )
        ]
    ),
    "RCC_SLAB_M25": ConstructionAssembly(
        assemblyId="RCC_SLAB_M25",
        name="M25 RCC Suspended Slab Assembly with Shuttering & Rebar",
        discipline="CIVIL_STRUCTURAL",
        category="CONCRETE",
        baseUnit="m³",
        version="2026.Q4-V1",
        specification="M25 reinforced concrete in floor and roof slabs including shuttering and rebar allowance",
        components=[
            AssemblyComponent(
                componentId="CMP-SLAB-CONC",
                materialId="MAT_M25_CONCRETE",
                description="M25 grade pumpable concrete",
                unit="m³",
                consumptionFormula="takeoff_qty * 1.0",
                consumptionFactor=1.0,
                wastagePercent=3.0,
                rateReferenceId="RATE_RCC_M25"
            ),
            AssemblyComponent(
                componentId="CMP-SLAB-STEEL",
                materialId="MAT_STEEL_FE500D",
                description="High yield strength deformed bars Fe500D (approx 95 kg/m³)",
                unit="kg",
                consumptionFormula="takeoff_qty * 95.0",
                consumptionFactor=95.0,
                wastagePercent=3.0,
                rateReferenceId="RATE_STEEL_REBAR"
            ),
            AssemblyComponent(
                componentId="CMP-SLAB-FORMWORK",
                materialId="MAT_FILM_FACED_PLY",
                description="Centering and shuttering with film faced shuttering plywood & cup-lock staging",
                unit="m²",
                consumptionFormula="takeoff_qty * 6.67", # 0.15m slab -> ~6.67 m² per m³
                consumptionFactor=6.67,
                wastagePercent=2.0,
                rateReferenceId="RATE_FORMWORK"
            )
        ]
    ),
    "FLOOR_TILE_VITRIFIED": ConstructionAssembly(
        assemblyId="FLOOR_TILE_VITRIFIED",
        name="800x800mm Vitrified Floor Tile Assembly",
        discipline="FINISHES",
        category="FLOORING",
        baseUnit="m²",
        version="2026.Q4-V1",
        specification="800x800mm double charged vitrified tiles laid on 20mm adhesive bedding with epoxy grout",
        components=[
            AssemblyComponent(
                componentId="CMP-TILE-VIT",
                materialId="MAT_VITRIFIED_TILE_800",
                description="Premium vitrified tiles 800x800mm nano-polished",
                unit="m²",
                consumptionFormula="takeoff_qty * 1.0",
                consumptionFactor=1.0,
                wastagePercent=5.0,
                rateReferenceId="RATE_FLOOR_TILES"
            ),
            AssemblyComponent(
                componentId="CMP-TILE-ADHESIVE",
                materialId="MAT_TILE_ADHESIVE",
                description="High polymer tile adhesive mortar",
                unit="kg",
                consumptionFormula="takeoff_qty * 5.5",
                consumptionFactor=5.5,
                wastagePercent=3.0,
                rateReferenceId="RATE_FLOOR_TILES"
            ),
            AssemblyComponent(
                componentId="CMP-TILE-GROUT",
                materialId="MAT_EPOXY_GROUT",
                description="Stain-resistant epoxy tile grout",
                unit="kg",
                consumptionFormula="takeoff_qty * 0.4",
                consumptionFactor=0.4,
                wastagePercent=2.0,
                rateReferenceId="RATE_FLOOR_TILES"
            )
        ]
    ),
    "PLASTER_INTERNAL_12MM": ConstructionAssembly(
        assemblyId="PLASTER_INTERNAL_12MM",
        name="12mm Internal Smooth Plaster Assembly",
        discipline="ARCHITECTURAL",
        category="PLASTER",
        baseUnit="m²",
        version="2026.Q4-V1",
        specification="12mm cement plaster 1:4 with fine river sand finished smooth with neeru / lime wash float",
        components=[
            AssemblyComponent(
                componentId="CMP-PLAST-MORTAR",
                materialId="MAT_CEMENT_MORTAR_1_4",
                description="Cement mortar 1:4 (12mm nominal thickness)",
                unit="m³",
                consumptionFormula="takeoff_qty * 0.015",
                consumptionFactor=0.015,
                wastagePercent=5.0,
                rateReferenceId="RATE_PLASTER_INT"
            )
        ]
    ),
    "PLASTER_EXTERNAL_20MM": ConstructionAssembly(
        assemblyId="PLASTER_EXTERNAL_20MM",
        name="20mm External Sand-Faced Waterproof Plaster Assembly",
        discipline="ARCHITECTURAL",
        category="PLASTER",
        baseUnit="m²",
        version="2026.Q4-V1",
        specification="20mm double coat cement plaster 1:4 with waterproofing compound and sponge/sand-faced texture",
        components=[
            AssemblyComponent(
                componentId="CMP-EXT-PLAST-MORTAR",
                materialId="MAT_CEMENT_MORTAR_1_4",
                description="Cement mortar 1:4 double coat (20mm nominal)",
                unit="m³",
                consumptionFormula="takeoff_qty * 0.024",
                consumptionFactor=0.024,
                wastagePercent=6.0,
                rateReferenceId="RATE_PLASTER_EXT"
            ),
            AssemblyComponent(
                componentId="CMP-EXT-PLAST-WP",
                materialId="MAT_WP_COMPOUND",
                description="Integral liquid waterproofing compound (IS 2645)",
                unit="litre",
                consumptionFormula="takeoff_qty * 0.15",
                consumptionFactor=0.15,
                wastagePercent=2.0,
                rateReferenceId="RATE_PLASTER_EXT"
            )
        ]
    ),
    "DOOR_FLUSH_PREHUNG": ConstructionAssembly(
        assemblyId="DOOR_FLUSH_PREHUNG",
        name="Factory-Finished Engineered Flush Door Assembly",
        discipline="ARCHITECTURAL",
        category="JOINERY",
        baseUnit="no.",
        version="2026.Q4-V1",
        specification="35mm thick BWP flush door shutter with engineered hardwood frame and architectural ironmongery",
        components=[
            AssemblyComponent(
                componentId="CMP-DOOR-LEAF",
                materialId="MAT_FLUSH_SHUTTER_35MM",
                description="Solid core flush door shutter",
                unit="no.",
                consumptionFormula="takeoff_qty * 1.0",
                consumptionFactor=1.0,
                wastagePercent=0.0,
                rateReferenceId="RATE_DOORS"
            ),
            AssemblyComponent(
                componentId="CMP-DOOR-FRAME",
                materialId="MAT_HARDWOOD_FRAME",
                description="Section 100x65mm hardwood frame",
                unit="no.",
                consumptionFormula="takeoff_qty * 1.0",
                consumptionFactor=1.0,
                wastagePercent=0.0,
                rateReferenceId="RATE_DOORS"
            ),
            AssemblyComponent(
                componentId="CMP-DOOR-HARDWARE",
                materialId="MAT_SS_HARDWARE_SET",
                description="SS 304 hinges (3 nos), mortise lock, lever handles, tower bolts",
                unit="set",
                consumptionFormula="takeoff_qty * 1.0",
                consumptionFactor=1.0,
                wastagePercent=0.0,
                rateReferenceId="RATE_DOORS"
            )
        ]
    ),
    "WINDOW_UPVC_SLIDING": ConstructionAssembly(
        assemblyId="WINDOW_UPVC_SLIDING",
        name="UPVC 3-Track Sliding Glazed Window Assembly",
        discipline="ARCHITECTURAL",
        category="JOINERY",
        baseUnit="no.",
        version="2026.Q4-V1",
        specification="UPVC 3-track sliding window with 2 glass sashes (5mm toughened) and 1 SS mosquito mesh sash",
        components=[
            AssemblyComponent(
                componentId="CMP-WIN-FRAME-GLASS",
                materialId="MAT_UPVC_WINDOW_UNIT",
                description="Complete multi-chamber UPVC window unit with glass & hardware",
                unit="no.",
                consumptionFormula="takeoff_qty * 1.0",
                consumptionFactor=1.0,
                wastagePercent=0.0,
                rateReferenceId="RATE_WINDOWS"
            )
        ]
    )
}


def get_assembly(assembly_id: str) -> ConstructionAssembly:
    """Returns construction assembly by identifier."""
    if assembly_id not in CONSTRUCTION_ASSEMBLIES_REGISTRY:
        raise KeyError(f"Assembly {assembly_id} not registered in assembly engine.")
    return CONSTRUCTION_ASSEMBLIES_REGISTRY[assembly_id]


def list_assemblies() -> List[ConstructionAssembly]:
    """Returns all available assemblies."""
    return list(CONSTRUCTION_ASSEMBLIES_REGISTRY.values())
