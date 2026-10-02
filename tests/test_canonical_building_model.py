"""
Planwise Enterprise — Canonical Building Model Test Suite
Delta Specification §44, §45, §46

Standard Library unittest suite for all 22 required unit tests plus critical golden test:
1. model creation
2. level creation
3. space creation
4. wall generation
5. opening-host relationship
6. column generation
7. slab generation
8. stair generation
9. material assignment
10. room adjacency
11. geometry compilation
12. validation
13. model hashing
14. reproducibility
15. versioning
16. immutable release
17. BOQ traceability
18. IFC mapping
19. floor-plan projection
20. elevation projection
21. section projection
22. 3D mapping
23. CRITICAL GOLDEN TEST: End-to-end traceability from CP-SAT to IFC & BOQ
"""

import unittest
import json
import hashlib
from typing import Dict, Any

from packages.schemas.building_model import (
    CanonicalBuildingModel,
    ElementType,
    WallType,
    OpeningType,
    BUILDING_MODEL_SCHEMA_VERSION
)
from workers.generation.model_compiler import (
    compile_canonical_building_model,
    compile_building_model
)
from workers.generation.validation_engine import validate_building_model
from workers.generation.projections import (
    generate_floor_plan,
    generate_elevation,
    generate_section,
    generate_3d
)
from workers.release.manifest_engine import generate_ifc4_model, generate_release_fingerprint
from workers.qto.boq_engine import compute_traceable_boq
from workers.generation.house_generator import solve_room_allocation, generate_house_options


class TestCanonicalBuildingModel(unittest.TestCase):

    def setUp(self):
        self.compact_2bhk = compile_building_model(archetype="compact_2bhk", design_version_id="DV-TEST-001")
        self.family_3bhk = compile_building_model(archetype="family_3bhk", design_version_id="DV-TEST-002")
        self.duplex_3bhk = compile_building_model(archetype="duplex_3bhk", design_version_id="DV-TEST-003")

    # -------------------------------------------------------------
    # 1. Model Creation Test
    # -------------------------------------------------------------
    def test_01_model_creation(self):
        model = self.compact_2bhk
        self.assertEqual(model.schemaVersion, "1.0.0")
        self.assertTrue(model.modelId.startswith("BLDG-COMPACT_2BHK-"))
        self.assertEqual(model.designVersionId, "DV-TEST-001")
        self.assertEqual(model.archetype, "compact_2bhk")
        self.assertGreater(model.totalGrossBUASqm, 0.0)

    # -------------------------------------------------------------
    # 2. Level Creation Test
    # -------------------------------------------------------------
    def test_02_level_creation(self):
        # 1-story compact 2bhk
        self.assertGreaterEqual(len(self.compact_2bhk.levels), 2)
        self.assertEqual(self.compact_2bhk.levels[0].levelId, "LVL-000")
        self.assertEqual(self.compact_2bhk.levels[0].elevationM, 0.0)

        # 2-story duplex 3bhk
        self.assertGreaterEqual(len(self.duplex_3bhk.levels), 3)
        level_ids = [lvl.levelId for lvl in self.duplex_3bhk.levels]
        self.assertIn("LVL-000", level_ids)
        self.assertIn("LVL-001", level_ids)
        self.assertIn("LVL-ROOF", level_ids)

    # -------------------------------------------------------------
    # 3. Space Creation Test
    # -------------------------------------------------------------
    def test_03_space_creation(self):
        self.assertEqual(len(self.compact_2bhk.spaces), 9)
        for sp in self.compact_2bhk.spaces:
            self.assertTrue(sp.spaceId.startswith("SPACE-"))
            self.assertIn(sp.levelId, ["LVL-000", "LVL-001"])
            self.assertGreater(sp.areaSqm, 0.0)
            self.assertGreater(sp.perimeterM, 0.0)
            self.assertGreaterEqual(len(sp.polygon), 4) # closed polygon
            self.assertGreaterEqual(sp.heightM, 2.75)

    # -------------------------------------------------------------
    # 4. Wall Generation Test
    # -------------------------------------------------------------
    def test_04_wall_generation(self):
        walls = [e for e in self.compact_2bhk.elements if e.elementType == ElementType.WALL]
        self.assertGreater(len(walls), 0)
        ext_walls = [w for w in walls if w.wallType == WallType.EXTERNAL]
        int_walls = [w for w in walls if w.wallType in [WallType.INTERNAL, WallType.PARTITION]]
        self.assertEqual(len(ext_walls), 4)
        self.assertGreater(len(int_walls), 0)
        for w in walls:
            self.assertIsNotNone(w.geometry)
            self.assertIn(w.geometry.thicknessM, [0.10, 0.20])
            self.assertGreaterEqual(len(w.geometry.footprintPolygon), 4)

    # -------------------------------------------------------------
    # 5. Opening-Host Relationship Test (§13)
    # -------------------------------------------------------------
    def test_05_opening_host_relationship(self):
        walls_dict = {w.elementId: w for w in self.compact_2bhk.elements if w.elementType == ElementType.WALL}
        self.assertGreater(len(self.compact_2bhk.openings), 0)
        for op in self.compact_2bhk.openings:
            self.assertTrue(op.openingId.startswith("DOOR-") or op.openingId.startswith("WIN-"))
            self.assertIn(op.hostWallId, walls_dict, f"Opening {op.openingId} must reference valid host wall")
            host_wall = walls_dict[op.hostWallId]
            self.assertIn(op.openingId, host_wall.openingIds, f"Host wall {host_wall.elementId} must list child opening {op.openingId}")

    # -------------------------------------------------------------
    # 6. Column Generation Test (§14)
    # -------------------------------------------------------------
    def test_06_column_generation(self):
        columns = [e for e in self.compact_2bhk.elements if e.elementType == ElementType.COLUMN]
        self.assertGreaterEqual(len(columns), 12)
        for col in columns:
            self.assertTrue(col.elementId.startswith("COL-"))
            self.assertEqual(col.properties.get("widthMm"), 300)
            self.assertEqual(col.properties.get("depthMm"), 450)
            self.assertEqual(col.materialId, "RCC_M25_FE500")

    # -------------------------------------------------------------
    # 7. Slab Generation Test (§16)
    # -------------------------------------------------------------
    def test_07_slab_generation(self):
        slabs = [e for e in self.compact_2bhk.elements if e.elementType == ElementType.SLAB]
        self.assertGreaterEqual(len(slabs), 2)
        slab_ids = [s.elementId for s in slabs]
        self.assertIn("SLAB-PLINTH", slab_ids)
        self.assertIn("SLAB-ROOF", slab_ids)

    # -------------------------------------------------------------
    # 8. Stair Generation Test (§17)
    # -------------------------------------------------------------
    def test_08_stair_generation(self):
        stairs = [e for e in self.duplex_3bhk.elements if e.elementType == ElementType.STAIR]
        self.assertEqual(len(stairs), 1)
        stair = stairs[0]
        self.assertEqual(stair.elementId, "STAIR-001")
        self.assertEqual(stair.properties.get("riserMm"), 175)
        self.assertEqual(stair.properties.get("treadMm"), 250)
        self.assertEqual(stair.properties.get("numberOfRisers"), 18)

    # -------------------------------------------------------------
    # 9. Material Assignment Test (§18)
    # -------------------------------------------------------------
    def test_09_material_assignment(self):
        catalog_ids = {m.materialId for m in self.compact_2bhk.materials}
        self.assertIn("AAC_BLOCK_200", catalog_ids)
        self.assertIn("AAC_BLOCK_100", catalog_ids)
        self.assertIn("RCC_M25_FE500", catalog_ids)
        self.assertIn("VITRIFIED_TILE_800", catalog_ids)

        for elem in self.compact_2bhk.elements:
            if elem.materialId:
                self.assertIn(elem.materialId, catalog_ids, f"Element {elem.elementId} references unlisted material {elem.materialId}")

    # -------------------------------------------------------------
    # 10. Room Adjacency Topology Test (§10)
    # -------------------------------------------------------------
    def test_10_room_adjacency(self):
        living = next((s for s in self.compact_2bhk.spaces if "LIVING" in s.spaceId), None)
        self.assertIsNotNone(living)
        self.assertGreater(len(living.adjacentSpaceIds), 0)
        space_ids = {s.spaceId for s in self.compact_2bhk.spaces}
        for adj in living.adjacentSpaceIds:
            self.assertIn(adj, space_ids)

    # -------------------------------------------------------------
    # 11. Geometry Compilation Test (§25)
    # -------------------------------------------------------------
    def test_11_geometry_compilation(self):
        solved = solve_room_allocation("compact_2bhk", 14.0, 16.0)
        model = compile_canonical_building_model(solved, design_version_id="DV-GEOM-01")
        self.assertEqual(model.buildingEnvelope["widthM"], 14.0)
        self.assertGreater(model.totalGrossBUASqm, 0)
        self.assertEqual(len(model.spaces), len(solved["rooms"]))

    # -------------------------------------------------------------
    # 12. Validation Engine Test (§26, §27)
    # -------------------------------------------------------------
    def test_12_validation_engine(self):
        summary = validate_building_model(self.compact_2bhk)
        self.assertTrue(summary.isValid)
        self.assertEqual(summary.blockersCount, 0)
        self.assertEqual(summary.errorsCount, 0)
        self.assertTrue(any("RULE CHECK" in issue.message for issue in summary.issues))

    # -------------------------------------------------------------
    # 13. Model Hashing Test (§36)
    # -------------------------------------------------------------
    def test_13_model_hashing(self):
        h = self.compact_2bhk.compute_hash()
        self.assertIsInstance(h, str)
        self.assertEqual(len(h), 64) # SHA-256 hex string
        self.assertTrue(self.compact_2bhk.metadata.modelHash.startswith("sha256:"))

    # -------------------------------------------------------------
    # 14. Deterministic Reproducibility Test (§37)
    # -------------------------------------------------------------
    def test_14_reproducibility(self):
        m1 = compile_building_model(archetype="compact_2bhk", design_version_id="DV-REP-01")
        m2 = compile_building_model(archetype="compact_2bhk", design_version_id="DV-REP-01")
        self.assertEqual(m1.compute_hash(), m2.compute_hash())
        self.assertEqual(m1.metadata.modelHash, m2.metadata.modelHash)

    # -------------------------------------------------------------
    # 15. Versioning Test (§5, §36)
    # -------------------------------------------------------------
    def test_15_versioning(self):
        m_v1 = compile_building_model(archetype="compact_2bhk", design_version_id="DV-001")
        m_v2 = compile_building_model(archetype="compact_2bhk", design_version_id="DV-002")
        self.assertNotEqual(m_v1.designVersionId, m_v2.designVersionId)
        self.assertNotEqual(m_v1.modelId, m_v2.modelId)

    # -------------------------------------------------------------
    # 16. Immutable Release Test (§38)
    # -------------------------------------------------------------
    def test_16_immutable_release(self):
        fp = generate_release_fingerprint(
            geometry_hash="sha256:geom_001",
            regulation_hash="sha256:reg_001",
            customer_brief_hash="sha256:brief_001",
            design_hash=self.compact_2bhk.metadata.modelHash,
            boq_hash="sha256:boq_001",
            schedule_hash="sha256:sch_001"
        )
        self.assertEqual(len(fp), 64)

    # -------------------------------------------------------------
    # 17. BOQ Traceability Test (§34)
    # -------------------------------------------------------------
    def test_17_boq_traceability(self):
        boq = compute_traceable_boq(self.compact_2bhk)
        self.assertEqual(boq["designVersionId"], self.compact_2bhk.designVersionId)
        self.assertEqual(boq["buildingModelId"], self.compact_2bhk.modelId)
        self.assertGreater(len(boq["lines"]), 0)

        for line in boq["lines"]:
            self.assertGreater(len(line["canonicalElementIds"]), 0, f"BOQ line {line['code']} has no linked elements")
            self.assertEqual(line["designVersionId"], self.compact_2bhk.designVersionId)
            self.assertEqual(line["takeoffRuleVersion"], "IS-1200-METHOD-OF-MEASUREMENT-2026.Q3")

    # -------------------------------------------------------------
    # 18. IFC Mapping Test (§33)
    # -------------------------------------------------------------
    def test_18_ifc_mapping(self):
        ifc_str = generate_ifc4_model(self.compact_2bhk, "REL-TEST-001")
        self.assertIn("FILE_SCHEMA(('IFC4'));", ifc_str)
        self.assertIn("IFCPROJECT", ifc_str)
        self.assertIn("IFCBUILDINGSTOREY", ifc_str)
        self.assertIn("IFCSPACE", ifc_str)
        self.assertIn("IFCWALL", ifc_str)
        self.assertIn("IFCDOOR", ifc_str)
        self.assertIn("IFCWINDOW", ifc_str)
        self.assertIn("IFCCOLUMN", ifc_str)
        self.assertIn("IFCSLAB", ifc_str)

    # -------------------------------------------------------------
    # 19. Floor Plan Projection Test (§29)
    # -------------------------------------------------------------
    def test_19_floor_plan_projection(self):
        fp = generate_floor_plan(self.compact_2bhk, "LVL-000")
        self.assertEqual(fp["level"]["levelId"], "LVL-000")
        self.assertEqual(len(fp["spaces"]), 9)
        self.assertGreater(len(fp["walls"]), 0)
        self.assertGreater(len(fp["doors"]), 0)
        self.assertGreater(len(fp["windows"]), 0)
        self.assertGreater(len(fp["columns"]), 0)

    # -------------------------------------------------------------
    # 20. Elevation Projection Test (§30)
    # -------------------------------------------------------------
    def test_20_elevation_projection(self):
        el = generate_elevation(self.compact_2bhk, "SOUTH")
        self.assertEqual(el["facadeDirection"], "SOUTH")
        self.assertIn("bounds", el)
        self.assertGreaterEqual(len(el["levelMarkers"]), 2)
        self.assertGreater(len(el["walls"]), 0)

    # -------------------------------------------------------------
    # 21. Section Projection Test (§31)
    # -------------------------------------------------------------
    def test_21_section_projection(self):
        sec = generate_section(self.compact_2bhk, cut_plane="A-A")
        self.assertEqual(sec["cutPlane"], "A-A")
        self.assertGreaterEqual(len(sec["levels"]), 2)
        self.assertGreater(len(sec["cutWalls"]), 0)
        self.assertGreater(len(sec["slabs"]), 0)

    # -------------------------------------------------------------
    # 22. 3D Mapping Test (§32)
    # -------------------------------------------------------------
    def test_22_3d_mapping(self):
        scene = generate_3d(self.compact_2bhk)
        self.assertGreater(scene["meshesCount"], 0)
        for mesh in scene["meshes"]:
            self.assertIn("canonicalElementId", mesh)
            self.assertIn("elementType", mesh)
            self.assertIn("material", mesh)

    # -------------------------------------------------------------
    # 23. CRITICAL GOLDEN TEST (§46 End-to-End Coherence)
    # -------------------------------------------------------------
    def test_23_critical_golden_end_to_end_coherence(self):
        """
        CP-SAT option
          ↓
        Canonical Model
          ↓
        Floor Plan
          ↓
        3D
          ↓
        IFC
          ↓
        QTO
          ↓
        BOQ

        All refer to the same designVersionId, buildingModelId, element IDs.
        """
        options = generate_house_options()
        self.assertGreaterEqual(len(options), 3)
        target_opt = options[0] # Golden 2BHK

        # 1. Canonical Building Model
        model_data = target_opt["buildingModel"]
        self.assertIsNotNone(model_data)
        model = CanonicalBuildingModel(**model_data)

        dv_id = target_opt["designVersionId"]
        bm_id = model.modelId
        self.assertEqual(model.designVersionId, dv_id)

        # 2. Floor Plan Projection
        fp = generate_floor_plan(model)
        self.assertEqual(fp["designVersionId"], dv_id)
        self.assertEqual(fp["modelId"], bm_id)

        # 3. 3D Scene Projection
        scene = generate_3d(model)
        self.assertEqual(scene["designVersionId"], dv_id)
        self.assertEqual(scene["modelId"], bm_id)

        # 4. IFC4 Mapping
        ifc_str = generate_ifc4_model(model, dv_id)
        self.assertIn(model.name, ifc_str)

        # 5. QTO & Traceable BOQ
        boq = compute_traceable_boq(model)
        self.assertEqual(boq["designVersionId"], dv_id)
        self.assertEqual(boq["buildingModelId"], bm_id)

        # Verify that BOQ references element IDs that actually exist in the model
        all_canonical_ids = {e.elementId for e in model.elements} | \
                            {o.openingId for o in model.openings} | \
                            {s.spaceId for s in model.spaces} | \
                            {sys.systemId for sys in model.systems}

        for line in boq["lines"]:
            for elem_id in line["canonicalElementIds"]:
                self.assertIn(elem_id, all_canonical_ids, f"BOQ item {line['code']} references non-existent element {elem_id}")

        # Golden counts
        self.assertEqual(len(model.spaces), 9)
        self.assertGreaterEqual(len(model.elements), 29)
        self.assertGreaterEqual(len(model.openings), 19)
        self.assertTrue(model.validation.isValid)


if __name__ == "__main__":
    unittest.main()
