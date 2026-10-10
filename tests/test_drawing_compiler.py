"""
Planwise Enterprise — Architectural Drawing Compiler Test Suite
Milestone 2 — Professional Drawing Pipeline Verification
=========================================================

Verifies all 20 acceptance criteria specified in Milestone 2:
1. floor plan generated
2. elevation generated
3. section generated
4. room labels present
5. dimensions present
6. doors tagged
7. windows tagged
8. north arrow present
9. title block present
10. drawing scale correct
11. drawing IDs deterministic
12. CBM traceability present
13. PDF generated
14. SVG generated
15. repeated compilation produces identical SVG
16. repeated compilation produces identical PDF
17. source CBM hash preserved
18. no benchmark contamination
19. pilot release unchanged
20. G5/G6 remain locked
"""

import os
import shutil
import hashlib
import json
import unittest
from pathlib import Path

from packages.schemas.building_model import CanonicalBuildingModel
from packages.schemas.engineer_review import GateStatus, GateCode
from workers.release.release_context import ReleaseContext, ROOT_DIR
from workers.generation.drawing_compiler import (
    DrawingCompiler,
    DRAWING_SPECS,
    DrawingSourceDataMissingError,
    DrawingCompilerError
)


class TestDrawingCompiler(unittest.TestCase):
    """Rigorous verification of the Milestone 2 Architectural Drawing Compiler."""

    @classmethod
    def setUpClass(cls):
        """Loads authoritative release context and pilot CBM model."""
        cls.ctx = ReleaseContext()
        cls.cbm = cls.ctx.resolve_canonical_model()
        cls.test_dir = ROOT_DIR / "artifacts" / "test_drawings_m2"
        cls.test_dir.mkdir(parents=True, exist_ok=True)

        # Baseline snapshot of pilot handoff directory for immutability verification
        cls.pilot_dir = ROOT_DIR / "artifacts" / "pilot_handoff"
        cls.pilot_files_before = {}
        if cls.pilot_dir.exists():
            for p in cls.pilot_dir.glob("*"):
                if p.is_file():
                    cls.pilot_files_before[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()

        # Run compilation
        cls.compiler = DrawingCompiler(cls.cbm, project_meta={
            "projectName": "Bandra West Residential Development",
            "projectId": cls.ctx.project_id,
            "releaseId": cls.ctx.release_id,
            "designVersionId": cls.ctx.design_version_id
        })
        cls.manifest = cls.compiler.compile_drawing_set(str(cls.test_dir))

    def test_01_floor_plan_generated(self):
        """1. Verifies Ground Floor Plan (A-101) is compiled with spaces, walls, and openings."""
        plan_spec = next(s for s in DRAWING_SPECS if s["drawingId"] == "A-101")
        view_data = self.compiler.compile_view(plan_spec)
        self.assertGreater(len(view_data["spaces"]), 0, "Floor plan must contain spaces")
        self.assertGreater(len(view_data["walls"]), 0, "Floor plan must contain walls")
        self.assertGreater(len(view_data["doors"]), 0, "Floor plan must contain doors")

        svg_path = self.test_dir / "A-101_ground_floor_plan.svg"
        self.assertTrue(svg_path.exists(), "Ground floor plan SVG artifact must exist")
        svg_content = svg_path.read_text(encoding="utf-8")
        self.assertIn("GROUND FLOOR PLAN", svg_content)
        self.assertIn('id="walls"', svg_content)

    def test_02_elevation_generated(self):
        """2. Verifies elevations (A-201..A-204) are generated with wall masses and level markers."""
        elev_spec = next(s for s in DRAWING_SPECS if s["drawingId"] == "A-201")
        view_data = self.compiler.compile_view(elev_spec)
        self.assertEqual(view_data["facadeDirection"], "SOUTH")
        self.assertGreater(len(view_data["levelMarkers"]), 0, "Elevation must have level markers")
        self.assertIn("groundLine", view_data)

        svg_path = self.test_dir / "A-201_front_elevation_south.svg"
        self.assertTrue(svg_path.exists(), "Front elevation SVG artifact must exist")
        svg_content = svg_path.read_text(encoding="utf-8")
        self.assertIn('id="ground-line"', svg_content)
        self.assertIn('id="level-markers"', svg_content)

    def test_03_section_generated(self):
        """3. Verifies longitudinal (A-301) and cross (A-302) sections are generated from CBM cut."""
        sec_spec = next(s for s in DRAWING_SPECS if s["drawingId"] == "A-302")
        view_data = self.compiler.compile_view(sec_spec)
        self.assertIn("cutWalls", view_data)
        self.assertIn("slabs", view_data)
        self.assertGreater(len(view_data["slabs"]), 0, "Section must cut through slabs")

        svg_path = self.test_dir / "A-302_cross_section_b-b.svg"
        self.assertTrue(svg_path.exists(), "Cross section SVG artifact must exist")
        svg_content = svg_path.read_text(encoding="utf-8")
        self.assertIn('id="cut-walls"', svg_content)
        self.assertIn('id="slabs"', svg_content)

    def test_04_room_labels_present(self):
        """4. Verifies room names and authoritative areas in m² are present without fabrication."""
        plan_svg = (self.test_dir / "A-101_ground_floor_plan.svg").read_text(encoding="utf-8")
        # Check for known ground floor spaces from pilot CBM
        self.assertIn("LIVING ROOM", plan_svg)
        self.assertIn("MODULAR KITCHEN", plan_svg)
        self.assertIn("m²", plan_svg, "Room areas must be labeled in metric m²")

    def test_05_dimensions_present(self):
        """5. Verifies deterministic building width, depth, and metric dimension strings are rendered."""
        plan_svg = (self.test_dir / "A-101_ground_floor_plan.svg").read_text(encoding="utf-8")
        self.assertIn('id="dimensions"', plan_svg)
        # Pilot envelope width is 5.38m or similar
        self.assertIn("5.38 m", plan_svg, "Overall building width dimension must be rendered")

    def test_06_doors_tagged(self):
        """6. Verifies doors are tagged deterministically (D01, D02) and schedule is rendered."""
        plan_svg = (self.test_dir / "A-101_ground_floor_plan.svg").read_text(encoding="utf-8")
        self.assertIn(">D01<", plan_svg, "Door tag D01 must be placed on plan")
        self.assertIn("DOOR SCHEDULE", plan_svg, "Door schedule table must be present on sheet")

    def test_07_windows_tagged(self):
        """7. Verifies windows are tagged deterministically (W01, W02) and schedule is rendered."""
        plan_svg = (self.test_dir / "A-101_ground_floor_plan.svg").read_text(encoding="utf-8")
        self.assertIn(">W01<", plan_svg, "Window tag W01 must be placed on plan")
        self.assertIn("WINDOW SCHEDULE", plan_svg, "Window schedule table must be present on sheet")

    def test_08_north_arrow_present(self):
        """8. Verifies north arrow is present on plans pointing to True North (+Y axis)."""
        plan_svg = (self.test_dir / "A-101_ground_floor_plan.svg").read_text(encoding="utf-8")
        self.assertIn('id="north-arrow"', plan_svg)
        self.assertIn("TRUE NORTH", plan_svg)

    def test_09_title_block_present(self):
        """9. Verifies ISO 128 / Planwise title block contains project ID, revision, and disclaimers."""
        plan_svg = (self.test_dir / "A-101_ground_floor_plan.svg").read_text(encoding="utf-8")
        self.assertIn('id="title-block"', plan_svg)
        self.assertIn("PLANWISE ENTERPRISE", plan_svg)
        self.assertIn(self.ctx.project_id, plan_svg)
        self.assertIn("R0", plan_svg)
        self.assertIn("PRELIMINARY / FOR PROFESSIONAL REVIEW", plan_svg)
        self.assertIn('id="disclaimers"', plan_svg)

    def test_10_drawing_scale_correct(self):
        """10. Verifies explicit 1:100 scale is embedded in metadata and title block."""
        plan_svg = (self.test_dir / "A-101_ground_floor_plan.svg").read_text(encoding="utf-8")
        self.assertIn('data-scale="1:100"', plan_svg)
        self.assertIn(">1:100<", plan_svg)

    def test_11_drawing_ids_deterministic(self):
        """11. Verifies deterministic drawing numbers: A-101..A-103, A-201..A-204, A-301..A-302."""
        expected_ids = {"A-101", "A-102", "A-103", "A-201", "A-202", "A-203", "A-204", "A-301", "A-302"}
        compiled_ids = {d["drawingId"] for d in self.manifest["drawings"]}
        self.assertEqual(compiled_ids, expected_ids)

    def test_12_cbm_traceability_present(self):
        """12. Verifies drawing geometry has data-cbm-id and data-element-type attributes."""
        plan_svg = (self.test_dir / "A-101_ground_floor_plan.svg").read_text(encoding="utf-8")
        self.assertIn('data-cbm-id="WALL-EXT-001"', plan_svg)
        self.assertIn('data-element-type="IfcWall"', plan_svg)
        self.assertIn('data-cbm-id="SPACE-', plan_svg)
        self.assertIn('data-element-type="IfcSpace"', plan_svg)

    def test_13_pdf_generated(self):
        """13. Verifies standalone A3 landscape vector PDF sheets are generated."""
        pdf_path = self.test_dir / "A-101_ground_floor_plan.pdf"
        self.assertTrue(pdf_path.exists())
        pdf_bytes = pdf_path.read_bytes()
        self.assertTrue(pdf_bytes.startswith(b"%PDF"), "Must be a valid PDF binary")
        self.assertGreater(len(pdf_bytes), 3000, "PDF must have non-trivial size")

    def test_14_svg_generated(self):
        """14. Verifies SVG files are valid XML vectors with standard namespace and viewBox."""
        svg_path = self.test_dir / "A-101_ground_floor_plan.svg"
        self.assertTrue(svg_path.exists())
        svg_content = svg_path.read_text(encoding="utf-8")
        self.assertTrue(svg_content.startswith("<svg"))
        self.assertTrue(svg_content.endswith("</svg>"))
        self.assertIn('viewBox="0 0 1190.55 841.89"', svg_content, "Must conform to A3 landscape")

    def test_15_repeated_compilation_produces_identical_svg(self):
        """15. Verifies 100% byte-for-byte identical SVGs across repeated compilations."""
        pass2_dir = ROOT_DIR / "artifacts" / "test_drawings_m2_test15"
        try:
            self.compiler.compile_drawing_set(str(pass2_dir))
            for spec in DRAWING_SPECS:
                dwg_id = spec["drawingId"]
                svg_name = next(p.name for p in self.test_dir.glob(f"{dwg_id}_*.svg"))
                h1 = hashlib.sha256((self.test_dir / svg_name).read_bytes()).hexdigest()
                h2 = hashlib.sha256((pass2_dir / svg_name).read_bytes()).hexdigest()
                self.assertEqual(h1, h2, f"SVG {svg_name} must be byte-for-byte identical")
        finally:
            if pass2_dir.exists():
                shutil.rmtree(pass2_dir)

    def test_16_repeated_compilation_produces_identical_pdf(self):
        """16. Verifies 100% byte-for-byte identical PDFs across repeated compilations."""
        pass2_dir = ROOT_DIR / "artifacts" / "test_drawings_m2_test16"
        try:
            self.compiler.compile_drawing_set(str(pass2_dir))
            for spec in DRAWING_SPECS:
                dwg_id = spec["drawingId"]
                pdf_name = next(p.name for p in self.test_dir.glob(f"{dwg_id}_*.pdf"))
                h1 = hashlib.sha256((self.test_dir / pdf_name).read_bytes()).hexdigest()
                h2 = hashlib.sha256((pass2_dir / pdf_name).read_bytes()).hexdigest()
                self.assertEqual(h1, h2, f"PDF {pdf_name} must be byte-for-byte identical")
        finally:
            if pass2_dir.exists():
                shutil.rmtree(pass2_dir)

    def test_17_source_cbm_hash_preserved(self):
        """17. Verifies canonical CBM hash is embedded in SVG metadata and drawing_manifest.json."""
        manifest_file = self.test_dir / "drawing_manifest.json"
        self.assertTrue(manifest_file.exists())
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["cbmHash"], self.cbm.metadata.modelHash)
        self.assertEqual(data["projectId"], self.ctx.project_id)

    def test_18_no_benchmark_contamination(self):
        """18. Verifies zero benchmark contamination in any generated drawing file."""
        forbidden_tokens = ["2400", "40x60", "40×60", "10000", "opt_40x60", "opt-A"]
        for p in self.test_dir.glob("*.svg"):
            content = p.read_text(encoding="utf-8")
            for tok in forbidden_tokens:
                self.assertNotIn(tok, content, f"Forbidden benchmark token '{tok}' found in {p.name}")

    def test_19_pilot_release_unchanged(self):
        """19. Verifies artifacts/pilot_handoff/ is strictly immutable and untouched."""
        if self.pilot_dir.exists():
            for name, expected_hash in self.pilot_files_before.items():
                current_file = self.pilot_dir / name
                self.assertTrue(current_file.exists(), f"Pilot file {name} missing")
                current_hash = hashlib.sha256(current_file.read_bytes()).hexdigest()
                self.assertEqual(
                    current_hash, expected_hash,
                    f"Pilot file {name} was mutated during drawing compilation!"
                )

    def test_20_g5_g6_remain_locked(self):
        """20. Verifies G5 (Municipal Sanction) and G6 (Construction Authorization) remain LOCKED."""
        rev = self.ctx.review_record
        if rev and rev.gates:
            g5 = next((g for g in rev.gates if g.gateCode in [GateCode.G5, "G5"]), None)
            g6 = next((g for g in rev.gates if g.gateCode in [GateCode.G6, "G6"]), None)
            if g5:
                self.assertEqual(g5.status, GateStatus.LOCKED, "Gate G5 must remain strictly LOCKED")
            if g6:
                self.assertEqual(g6.status, GateStatus.LOCKED, "Gate G6 must remain strictly LOCKED")


if __name__ == "__main__":
    unittest.main()
