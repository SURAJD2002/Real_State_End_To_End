"""
Planwise Enterprise — Real Plot Data End-to-End Test Suite
Delta Specification & Real Plot Data End-to-End Test

Comprehensive automated verification that a real customer can enter plot data
manually (WITHOUT image/OCR/image processing) and Planwise deterministically produces:
LAND DATA (PGV) → FEASIBILITY (M1) → BUILDABLE ENVELOPE → HOUSE OPTIONS (M2) →
2D/3D CBM MODEL → 12 VALIDATION CHECKS → QTO (M3) → BOQ (M3) → PRELIMINARY COST (M3) →
CHANGE PROPAGATION TEST (Step 9).

Strict Guarantees:
- Zero invented values.
- Strict USER_INPUT_REQUIRED on missing dimensions / under-constrained irregular polygons.
- Strict JURISDICTION_REQUIRED on missing / unconfigured statutory jurisdictions.
- Full traceability: BOQ -> Assembly -> Takeoff -> Measurement Rule -> CBM Element -> Geometry.
- Change propagation: DESIGN_CHANGED -> QTO_STALE -> BOQ_STALE -> COST_STALE.
"""

import unittest
import math
from typing import Dict, Any

from packages.schemas.real_plot_input import (
    RealPlotIntakePayload,
    SiteInput,
    CustomerRequirementsInput,
    PlotDimensions,
    ParcelGeometryVersion,
    SiteShape,
    RoadFacingSide,
    BuildingUse
)
from packages.schemas.customer_brief import CustomerBrief, ArchitecturalStyle
from packages.schemas.building_model import CanonicalBuildingModel
from packages.schemas.qto_model import TakeoffRecord
from packages.schemas.cost_model import CostEstimate, BOQLineItem
from workers.intake.real_plot_runner import RealPlotPipelineRunner
from workers.qto.change_propagation import GLOBAL_CHANGE_PROPAGATION, InvalidationTrigger


class TestRealPlotEndToEnd(unittest.TestCase):
    """Rigorous verification of the complete real plot intake and computational pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.runner = RealPlotPipelineRunner()

    # =========================================================================
    # 1. INPUT VALIDATION & STRICT REJECTION TESTS (NO INVENTED VALUES)
    # =========================================================================

    def test_01_missing_jurisdiction_returns_jurisdiction_required(self):
        """Must return JURISDICTION_REQUIRED when jurisdiction is missing. Never assume a regulation."""
        payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction=None,
                road_width_ft=40.0,
                shape=SiteShape.REGULAR,
                dimensions=PlotDimensions(front_width_ft=40.0, left_length_ft=60.0)
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=2,
                bathrooms=2
            )
        )
        res = self.runner.validate_intake(payload)
        self.assertEqual(res["status"], "JURISDICTION_REQUIRED")
        self.assertIn("MUMBAI-DCPR-2034-V1", res["available_jurisdictions"])

    def test_02_unknown_jurisdiction_returns_jurisdiction_required(self):
        """Must return JURISDICTION_REQUIRED for unregistered jurisdiction. Never guess regulations."""
        payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Random City",
                jurisdiction="UNKNOWN-JURISDICTION-2099",
                road_width_ft=30.0,
                shape=SiteShape.REGULAR,
                dimensions=PlotDimensions(front_width_ft=30.0, left_length_ft=50.0)
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=2,
                bathrooms=2
            )
        )
        res = self.runner.validate_intake(payload)
        self.assertEqual(res["status"], "JURISDICTION_REQUIRED")

    def test_03_underconstrained_irregular_plot_returns_user_input_required(self):
        """
        4 side lengths alone cannot close an irregular quadrilateral without guessing!
        Must return USER_INPUT_REQUIRED with 'site.dimensions.diagonal_ft'.
        """
        payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction="MUMBAI-DCPR-2034-V1",
                road_width_ft=16.0,
                shape=SiteShape.IRREGULAR,
                dimensions=PlotDimensions(
                    front_width_ft=28.0,
                    left_length_ft=44.0,
                    right_length_ft=40.0,
                    back_width_ft=28.0,
                    diagonal_ft=None
                )
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=2,
                bathrooms=2
            )
        )
        res = self.runner.validate_intake(payload)
        self.assertEqual(res["status"], "USER_INPUT_REQUIRED")
        self.assertIn("site.dimensions.diagonal_ft", res["missing_fields"])

    def test_04_missing_bedrooms_or_bathrooms_returns_user_input_required(self):
        """Must return USER_INPUT_REQUIRED if essential room brief requirements are missing."""
        payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction="MUMBAI-DCPR-2034-V1",
                road_width_ft=40.0,
                shape=SiteShape.REGULAR,
                dimensions=PlotDimensions(front_width_ft=40.0, left_length_ft=60.0)
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=None,
                bathrooms=None
            )
        )
        res = self.runner.validate_intake(payload)
        self.assertEqual(res["status"], "USER_INPUT_REQUIRED")
        self.assertIn("requirements.bedrooms", res["missing_fields"])
        self.assertIn("requirements.bathrooms", res["missing_fields"])

    # =========================================================================
    # 2. STEP 1: SITE INTAKE & PARCEL GEOMETRY VERSION (PGV)
    # =========================================================================

    def test_05_step1_parcel_geometry_version_creation(self):
        """Verifies Step 1 creates ParcelGeometryVersion with rigorous provenance and closed polygon."""
        site_in = SiteInput(
            location="Bandra West, Mumbai",
            jurisdiction="MUMBAI-DCPR-2034-V1",
            road_width_ft=40.0,
            shape=SiteShape.REGULAR,
            orientation="NORTH",
            dimensions=PlotDimensions(front_width_ft=40.0, left_length_ft=60.0)
        )
        pgv: ParcelGeometryVersion = self.runner.reconstruct_site_geometry(site_in, site_id="SITE-TEST-001")
        
        self.assertEqual(pgv.source, "USER_PROVIDED")
        self.assertEqual(pgv.confidence, "USER_CONFIRMED")
        self.assertEqual(pgv.units, "METRIC")
        self.assertAlmostEqual(pgv.areaSqft, 2400.0, delta=10.0)
        self.assertAlmostEqual(pgv.areaSqm, 222.97, delta=1.0)
        self.assertEqual(len(pgv.boundarySECS), 5)  # 4 vertices + closure
        self.assertEqual(pgv.boundarySECS[0], pgv.boundarySECS[-1])
        self.assertAlmostEqual(pgv.roadWidthM, 12.19, delta=0.05)

    # =========================================================================
    # 3. STEP 2: M1 FEASIBILITY & STATUTORY RULE ENGINE
    # =========================================================================

    def test_06_step2_m1_statutory_feasibility_pipeline(self):
        """Verifies Step 2 calculates setbacks, buildable footprint, permissible area, FAR/FSI, height, parking."""
        payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction="MUMBAI-DCPR-2034-V1",
                road_width_ft=40.0,
                shape=SiteShape.REGULAR,
                dimensions=PlotDimensions(front_width_ft=40.0, left_length_ft=60.0)
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=2,
                bathrooms=2,
                parking=1
            )
        )
        res = self.runner.run_e2e_pipeline(payload)
        self.assertEqual(res["status"], "SUCCESS")
        
        fb = res["feasibility"]
        self.assertGreater(fb.grossParcelAreaSqm, 0.0)
        self.assertGreater(fb.permissibleBUASqm, 0.0)
        self.assertGreater(fb.totalPermissibleFSI, 1.0)
        self.assertGreaterEqual(fb.parkingStallsRequired, 1)
        self.assertGreater(len(fb.traces), 6)  # Full RuleExecutionTrace

        # Verify buildable envelope bounding box
        env = res["envelope_dimensions"]
        self.assertGreater(env["width_m"], 5.0)
        self.assertGreater(env["length_m"], 5.0)
        self.assertGreater(env["area_sqm"], 50.0)

    # =========================================================================
    # 4. STEP 3: CUSTOMER BRIEF (HARD VS SOFT SEPARATION)
    # =========================================================================

    def test_07_step3_customer_brief_hard_vs_soft(self):
        """Verifies Step 3 separates Hard Constraints from Soft Preferences."""
        req = CustomerRequirementsInput(
            use=BuildingUse.RESIDENTIAL,
            floors=1,
            bedrooms=2,
            bathrooms=2,
            parking=1,
            balcony=True,
            terrace=True,
            preferred_style="modern",
            budget=8500000.0
        )
        brief: CustomerBrief = self.runner.convert_to_customer_brief(req)
        
        # Hard constraints
        self.assertTrue(brief.bedroomsConstraint.hardConstraint)
        self.assertEqual(brief.bedroomsConstraint.normalizedValue, 2)
        self.assertTrue(brief.bathroomsConstraint.hardConstraint)
        self.assertEqual(brief.bathroomsConstraint.normalizedValue, 2)
        self.assertTrue(brief.floorsConstraint.hardConstraint)
        self.assertEqual(brief.floorsConstraint.normalizedValue, 1)
        self.assertTrue(brief.parkingRequired)

        # Soft preferences
        self.assertFalse(brief.budgetConstraint.hardConstraint)
        self.assertEqual(brief.preferredStyle, ArchitecturalStyle.CONTEMPORARY)
        self.assertTrue(brief.balconyRequired)

    # =========================================================================
    # 5. STEP 4 & 5: M2 GENERATION, 12 VALIDATION CHECKS & CBM
    # =========================================================================

    def test_08_step4_and_5_m2_generation_and_cbm(self):
        """Verifies Step 4 generates multiple options, runs 12 validation checks, and compiles CBM."""
        payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction="MUMBAI-DCPR-2034-V1",
                road_width_ft=40.0,
                shape=SiteShape.REGULAR,
                dimensions=PlotDimensions(front_width_ft=40.0, left_length_ft=60.0)
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=2,
                bathrooms=2,
                parking=1
            )
        )
        res = self.runner.run_e2e_pipeline(payload)
        options = res["generated_options"]
        self.assertGreaterEqual(len(options), 1)

        opt = options[0]
        # Required returned metrics per prompt
        self.assertIn("totalGrossBUASqm", opt["layout"])
        self.assertIn("totalUsableAreaSqm", opt["layout"])
        self.assertIn("buildingEnvelope", opt["layout"])
        self.assertIn("rooms", opt["layout"])
        self.assertIn("overallScore", opt["scores"])
        self.assertIn("areaEfficiencyPercent", opt["scores"])
        self.assertIn("daylightProxy", opt["scores"])
        self.assertIn("ventilationProxy", opt["scores"])
        self.assertIn("constructabilityScore", opt["scores"])
        self.assertIn("customerFitScore", opt["scores"])
        self.assertEqual(opt["compliance"]["statutorySetbacks"], "PASS")

        # CBM Verification
        cbm: CanonicalBuildingModel = res["canonical_model"]
        self.assertGreater(len(cbm.spaces), 4)
        self.assertGreater(len(cbm.elements), 10)
        self.assertGreater(len(cbm.openings), 2)
        columns = [e for e in cbm.elements if e.elementType.value == "COLUMN"]
        self.assertGreater(len(columns), 4)
        self.assertGreater(len(cbm.structuralGrid.gridLinesX) + len(cbm.structuralGrid.gridLinesY), 2)

    # =========================================================================
    # 6. STEP 6, 7 & 8: M3 QTO, MODEL-LINKED BOQ & PRELIMINARY COST
    # =========================================================================

    def test_09_step6_7_8_qto_boq_and_cost(self):
        """Verifies Step 6 QTO, Step 7 BOQ, and Step 8 Cost Waterfall with full traceability."""
        payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction="MUMBAI-DCPR-2034-V1",
                road_width_ft=40.0,
                shape=SiteShape.REGULAR,
                dimensions=PlotDimensions(front_width_ft=40.0, left_length_ft=60.0)
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=2,
                bathrooms=2,
                parking=1
            )
        )
        res = self.runner.run_e2e_pipeline(payload)
        qto = res["qto"]
        self.assertGreater(len(qto), 8)

        # Every quantity references CBM Element ID + Measurement Rule + Geometry
        for rec in qto:
            self.assertTrue(len(rec.sourceElementIds) > 0, "TakeoffRecord must reference CBM Element IDs")
            self.assertTrue(len(rec.measurementRuleId) > 0, "TakeoffRecord must reference Measurement Rule")
            self.assertTrue(len(rec.geometryFingerprint) > 0, "TakeoffRecord must reference Geometry fingerprint")

        # BOQ & Cost Waterfall
        estimate: CostEstimate = res["cost_estimate"]
        self.assertGreater(len(estimate.boqLines), 8)
        self.assertEqual(estimate.status, "PRELIMINARY")
        self.assertIn("Preliminary Cost Estimate", estimate.disclaimer)

        wf = estimate.costWaterfall
        self.assertGreater(wf.directMaterialCost, 0.0)
        self.assertGreater(wf.directLabourCost, 0.0)
        self.assertGreater(wf.directEquipmentCost, 0.0)
        self.assertGreater(wf.materialWastageCost, 0.0)
        self.assertGreater(wf.overheadAndPrelims, 0.0)
        self.assertGreater(wf.contingency, 0.0)
        self.assertGreater(wf.totalConstructionCost, 0.0)
        self.assertGreater(wf.costPerSqFtBUA, 1000.0)
        self.assertGreater(wf.costPerCarpetSqFt, 1200.0)

    # =========================================================================
    # 7. STEP 9: CHANGE TEST (BEDROOMS 2 -> 3)
    # =========================================================================

    def test_10_step9_change_test_propagation(self):
        """Verifies Step 9: Mutating bedrooms 2 -> 3 marks QTO/BOQ/Cost stale and recalculates downstream."""
        initial_payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction="MUMBAI-DCPR-2034-V1",
                road_width_ft=40.0,
                shape=SiteShape.REGULAR,
                dimensions=PlotDimensions(front_width_ft=40.0, left_length_ft=60.0)
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=2,
                bathrooms=2,
                parking=1
            )
        )
        mutated_requirements = CustomerRequirementsInput(
            use=BuildingUse.RESIDENTIAL,
            floors=1,
            bedrooms=3,
            bathrooms=2,
            parking=1
        )
        change_res = self.runner.run_change_propagation_test(initial_payload, mutated_requirements)
        
        # Verify stale states
        self.assertTrue(change_res["stale_flags"]["qto_stale"])
        self.assertTrue(change_res["stale_flags"]["boq_stale"])
        self.assertTrue(change_res["stale_flags"]["cost_stale"])

        # Verify cost and area delta
        self.assertGreater(change_res["updated_bua_sqm"], change_res["initial_bua_sqm"])
        self.assertGreater(change_res["cost_delta_inr"], 0.0)
        self.assertNotEqual(change_res["initial_design_version"], change_res["updated_design_version"])

    # =========================================================================
    # 8. IRREGULAR PLOT WITH DIAGONAL TRIANGULATION E2E
    # =========================================================================

    def test_11_irregular_plot_with_diagonal_triangulation(self):
        """Verifies real irregular plot (28ft front × 44ft left × 40ft right × 28ft back × 50ft diag) runs E2E."""
        payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction="MUMBAI-DCPR-2034-V1",
                road_width_ft=16.0,
                shape=SiteShape.IRREGULAR,
                dimensions=PlotDimensions(
                    front_width_ft=28.0,
                    left_length_ft=44.0,
                    right_length_ft=40.0,
                    back_width_ft=28.0,
                    diagonal_ft=50.0
                )
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=2,
                bathrooms=2,
                parking=1
            )
        )
        res = self.runner.run_e2e_pipeline(payload)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertAlmostEqual(res["parcel_geometry"].areaSqm, 108.95, delta=1.0)
        self.assertGreaterEqual(len(res["generated_options"]), 1)
        self.assertGreater(res["cost_estimate"].costWaterfall.totalConstructionCost, 0.0)
    # =========================================================================
    # 9. REAL CUSTOMER DECLARED 1100 SQ FT PLOT INTAKE & MISMATCH TEST (§17)
    # =========================================================================

    def test_12_customer_declared_area_1100_sqft_authoritative_intake(self):
        """
        Customer declares 1100 sq ft as the authoritative plot area.
        System must preserve 1100 sq ft and not silently calculate a different area.
        """
        payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                city="Mumbai",
                state="Maharashtra",
                jurisdiction="MUMBAI-DCPR-2034-V1",
                declared_area_sqft=1100.0,
                road_width_ft=16.0,
                shape=SiteShape.REGULAR
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=2,
                bathrooms=2,
                parking=1
            )
        )
        res = self.runner.run_e2e_pipeline(payload)
        self.assertEqual(res["status"], "SUCCESS")
        pgv = res["parcel_geometry"]
        self.assertEqual(pgv.declaredAreaSqft, 1100.0)
        self.assertAlmostEqual(pgv.areaSqft, 1100.0, delta=1.0)
        self.assertGreater(res["feasibility"].permissibleBUASqm, 0.0)
        self.assertGreaterEqual(len(res["generated_options"]), 1)

    def test_13_geometry_area_mismatch_returns_error_and_does_not_overwrite(self):
        """
        If dimensions provided conflict with declared 1100 sq ft (e.g. 40ft x 60ft = 2400 sqft),
        system must return GEOMETRY_AREA_MISMATCH and ask user to verify, never silently overwrite.
        """
        payload = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction="MUMBAI-DCPR-2034-V1",
                declared_area_sqft=1100.0,
                road_width_ft=16.0,
                shape=SiteShape.REGULAR,
                dimensions=PlotDimensions(front_width_ft=40.0, left_length_ft=60.0)
            ),
            requirements=CustomerRequirementsInput(
                use=BuildingUse.RESIDENTIAL,
                floors=1,
                bedrooms=2,
                bathrooms=2,
                parking=1
            )
        )
        res = self.runner.validate_intake(payload)
        self.assertEqual(res["status"], "GEOMETRY_AREA_MISMATCH")
        self.assertEqual(res["declared_area_sqft"], 1100.0)
        self.assertEqual(res["calculated_area_sqft"], 2400.0)
        self.assertIn("dimensions and plot area don't match", res["message"])


if __name__ == "__main__":
    unittest.main()
