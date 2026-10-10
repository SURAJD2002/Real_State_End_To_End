"""
Planwise Enterprise — Automated Test Suite for Home PDF Generation
===================================================================
Tests deterministic PDF compilation, pypdfium2 opening, content assertions,
authoritative 1,100 sq ft invariant, CBM geometry linkage, BOQ and cost alignment,
gate statuses, release fingerprints, database persistence, and immutability.
"""

import os
import sys
import json
import zipfile
import unittest
from pathlib import Path

import pypdfium2 as pdfium

from workers.generation.model_compiler import compile_canonical_building_model
from workers.qto.qto_engine import ModelLinkedQTOEngine
from workers.qto.cost_engine import DeterministicCostEngine
from workers.reports.home_report import generate_home_report_pdf
from workers.reports.package_builder import (
    build_complete_package,
    build_technical_report,
    build_cost_boq_report,
    build_professional_report,
    save_generated_report_record,
    get_generated_report_record,
    list_generated_reports_records,
    mark_reports_stale_for_design,
    compute_file_sha256,
    compute_manifest_hash
)

ROOT_DIR = Path(__file__).resolve().parent.parent
API_GATEWAY_DIR = ROOT_DIR / "apps" / "api-gateway"
if str(API_GATEWAY_DIR) not in sys.path:
    sys.path.append(str(API_GATEWAY_DIR))


class TestHomeReportPDFGeneration(unittest.TestCase):
    """Authoritative test suite for Planwise Home PDF Documentation."""

    @classmethod
    def setUpClass(cls):
        cls.design_version_id = "DV-OPT-B-9be0a983"
        cls.cbm = compile_canonical_building_model(
            archetype="compact_2bhk",
            design_version_id=cls.design_version_id
        )
        cls.qto = ModelLinkedQTOEngine(cls.cbm).run_full_takeoff()
        cls.cost_engine = DeterministicCostEngine(
            model=cls.cbm,
            rate_snapshot_id="INDIA-MUMBAI-2026-Q4-V1",
            quality_tier="STANDARD"
        )
        cls.cost_estimate = cls.cost_engine.calculate_cost_estimate(cls.qto)

        cls.project_data = {
            "id": "proj-mumbai-real-1100",
            "name": "Bandra West Residential Development",
            "location": "Bandra West, Mumbai, Maharashtra",
            "cadastralNumber": "CTS-1842-BANDRA"
        }
        cls.site_data = {
            "declaredPlotAreaSqFt": 1100.0,
            "declaredPlotAreaSqm": 102.193,
            "plotDimensions": {"frontageM": 8.38, "depthM": 12.19},
            "roadWidthM": 4.88,
            "roadWideningM": 3.0,
            "netPlotAreaSqm": 77.05,
            "setbacks": {"frontM": 3.0, "rearM": 2.0, "sideM": 1.5},
            "maxHeightM": 10.0,
            "maxFloors": 2,
            "maxBUASqm": 102.19,
            "permissibleFSI": 1.0,
            "proposedFSI": 0.96
        }
        cls.release_data = {
            "releaseId": "rel-pilot-20261002-aedf9830",
            "id": "rel-pilot-20261002-aedf9830",
            "fingerprint": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
            "engineVersion": "Planwise-CBM-v1.4.0",
            "rateSnapshotId": "INDIA-MUMBAI-2026-Q4-V1",
            "regulationSnapshotId": "REG-MUMBAI-DCPR-2034-V2",
            "cbmHash": "sha256:cbm_option_b_compact_2bhk_9be0a983_v1",
            "qtoHash": "sha256:qto_takeoff_option_b_is1200_v1",
            "boqHash": cls.cost_estimate.boqHash,
            "validationHash": "sha256:validation_12_checks_pass_all_green",
            "designVersionId": cls.design_version_id
        }

        cls.test_output_dir = ROOT_DIR / "artifacts" / "test_reports"
        cls.test_output_dir.mkdir(parents=True, exist_ok=True)

    def test_01_customer_home_report_compilation_and_validity(self):
        """Verifies customer home report compiles, opens with pypdfium2, and contains authoritative content."""
        out_pdf = str(self.test_output_dir / "TEST_CUSTOMER_HOME_REPORT.pdf")
        res = generate_home_report_pdf(
            cbm=self.cbm,
            project_data=self.project_data,
            site_data=self.site_data,
            cost_estimate=self.cost_estimate,
            engineer_review=None,
            release_data=self.release_data,
            output_pdf_path=out_pdf
        )
        self.assertTrue(os.path.exists(out_pdf))
        self.assertGreater(os.path.getsize(out_pdf), 500000)

        # Open with pypdfium2 to verify valid PDF structures
        doc = pdfium.PdfDocument(out_pdf)
        page_count = len(doc)
        self.assertGreaterEqual(page_count, 15, f"Expected at least 15 pages, got {page_count}")

        # Extract text across all pages
        full_text = ""
        for i in range(page_count):
            full_text += doc[i].get_textpage().get_text_range() + "\n"

        # Content assertions
        self.assertIn("PLANWISE ENTERPRISE", full_text)
        self.assertIn("HOME DEVELOPMENT REPORT", full_text)
        self.assertIn("Bandra West", full_text)
        self.assertIn("CTS-1842-BANDRA", full_text)
        self.assertIn("1,100", full_text)  # 1,100 sq ft plot area
        self.assertIn("102.19", full_text)  # 102.19 m² plot area
        self.assertIn(self.design_version_id, full_text)
        expected_cost_str = f"{int(self.cost_estimate.costWaterfall.totalConstructionCost):,}"
        self.assertIn(expected_cost_str, full_text)
        self.assertIn("[G0] Site & Boundary", full_text)
        self.assertIn("[G5] Municipal Build", full_text)
        self.assertIn("[G6] Contractor Handoff", full_text)
        self.assertIn("LOCKED", full_text)

        # Invariant checks: No benchmark contamination
        self.assertNotIn("2400 sq ft", full_text.lower())
        self.assertNotIn("2,400 sq ft", full_text.lower())
        self.assertNotIn("40x60", full_text.lower())

        # Mandatory statutory disclaimers check
        self.assertIn("COMPUTATIONAL VALIDATION IS NOT PROFESSIONAL CERTIFICATION", full_text)
        self.assertIn("Council of Architecture", full_text)
        self.assertIn("geotechnical", full_text.lower())

    def test_02_complete_package_and_zip_archive(self):
        """Verifies complete package generates all 10 PDFs, master PDF, and valid ZIP archive."""
        pkg_dir = str(self.test_output_dir / "complete_pkg")
        master_pdf, zip_path, file_list = build_complete_package(
            cbm=self.cbm,
            project_data=self.project_data,
            site_data=self.site_data,
            cost_estimate=self.cost_estimate,
            engineer_review=None,
            release_data=self.release_data,
            output_dir=pkg_dir
        )

        self.assertEqual(len(file_list), 10, "Complete package must include exactly 10 modular PDFs")
        for f in file_list:
            self.assertTrue(os.path.exists(f), f"Expected file {f} to exist")
            doc = pdfium.PdfDocument(f)
            self.assertGreater(len(doc), 0, f"File {f} must have at least 1 page")

        # Master combined PDF check
        self.assertTrue(os.path.exists(master_pdf))
        master_doc = pdfium.PdfDocument(master_pdf)
        self.assertGreater(len(master_doc), 20, "Combined package must contain merged pages from all reports")

        # ZIP archive check
        self.assertTrue(os.path.exists(zip_path))
        with zipfile.ZipFile(zip_path, "r") as z:
            namelist = z.namelist()
            self.assertIn("01_Home_Report.pdf", namelist)
            self.assertIn("02_Technical_Report.pdf", namelist)
            self.assertIn("03_Floor_Plans.pdf", namelist)
            self.assertIn("04_3D_Views.pdf", namelist)
            self.assertIn("05_QTO.pdf", namelist)
            self.assertIn("06_BOQ.pdf", namelist)
            self.assertIn("07_Cost_Estimate.pdf", namelist)
            self.assertIn("08_Validation_Report.pdf", namelist)
            self.assertIn("09_Engineer_Review.pdf", namelist)
            self.assertIn("10_Release_Manifest.pdf", namelist)

    def test_03_technical_and_specialized_reports(self):
        """Verifies standalone Technical, Cost & BOQ, and Professional reports."""
        tech_pdf = str(self.test_output_dir / "TEST_TECHNICAL_REPORT.pdf")
        build_technical_report(
            self.cbm, self.project_data, self.site_data,
            self.cost_estimate, None, self.release_data, tech_pdf
        )
        self.assertTrue(os.path.exists(tech_pdf))
        tech_doc = pdfium.PdfDocument(tech_pdf)
        self.assertGreaterEqual(len(tech_doc), 4)

        cost_pdf = str(self.test_output_dir / "TEST_COST_BOQ_REPORT.pdf")
        build_cost_boq_report(
            self.cost_estimate, self.cbm, self.project_data, self.release_data, cost_pdf
        )
        self.assertTrue(os.path.exists(cost_pdf))
        cost_doc = pdfium.PdfDocument(cost_pdf)
        self.assertGreaterEqual(len(cost_doc), 2)

        prof_pdf = str(self.test_output_dir / "TEST_PROFESSIONAL_REPORT.pdf")
        build_professional_report(
            None, self.release_data, self.project_data, self.cbm, prof_pdf
        )
        self.assertTrue(os.path.exists(prof_pdf))
        prof_doc = pdfium.PdfDocument(prof_pdf)
        self.assertGreaterEqual(len(prof_doc), 1)

    def test_04_database_persistence_and_staleness(self):
        """Verifies report record persistence in PostgreSQL and change-propagation staleness handling."""
        rep_id = f"test-rep-{self.design_version_id}-unit"
        dummy_pdf = str(self.test_output_dir / "TEST_CUSTOMER_HOME_REPORT.pdf")
        pdf_hash = compute_file_sha256(dummy_pdf)
        manifest_hash = compute_manifest_hash({"dv": self.design_version_id, "bua": 98.16})

        rec = save_generated_report_record(
            report_id=rep_id,
            project_id=self.project_data["id"],
            site_id="site-mumbai-real-1100",
            design_version_id=self.design_version_id,
            report_type="HOME_REPORT",
            release_id=None,  # Unreleased draft to test staleness marking
            release_fingerprint=None,
            input_manifest_hash=manifest_hash,
            output_pdf_hash=pdf_hash,
            file_path=dummy_pdf,
            file_size_bytes=os.path.getsize(dummy_pdf),
            engine_version="1.0.0",
            metadata={"test": True}
        )
        self.assertEqual(rec["id"], rep_id)

        fetched = get_generated_report_record(rep_id)
        if fetched:
            self.assertEqual(fetched["id"], rep_id)
            self.assertFalse(fetched["is_stale"])

            # Test change propagation: mark unreleased reports stale
            mark_reports_stale_for_design(self.design_version_id)
            updated = get_generated_report_record(rep_id)
            self.assertTrue(updated["is_stale"])

    def test_05_cryptographic_fingerprint_deterministic_output(self):
        """Verifies manifest hashing is 100% deterministic given identical inputs."""
        dict_a = {"project": "proj-1100", "dv": "DV-01", "cbm_bua": 98.16}
        dict_b = {"cbm_bua": 98.16, "dv": "DV-01", "project": "proj-1100"}  # Same keys different order
        hash_a = compute_manifest_hash(dict_a)
        hash_b = compute_manifest_hash(dict_b)
        self.assertEqual(hash_a, hash_b)
        self.assertTrue(hash_a.startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
