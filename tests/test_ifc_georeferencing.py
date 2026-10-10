"""
Planwise Enterprise — Milestone 1: BIM / IFC Professionalization Automated Test Suite
=====================================================================================
Tests buildingSMART IFC4 Georeferencing, Deterministic UUIDv5 GUIDs, Standard Property Sets,
Uniclass 2015 Classification References, and Pilot Release Immutability.
"""

import os
import json
import re
import hashlib
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

from workers.generation.model_compiler import compile_canonical_building_model
from workers.release.manifest_engine import generate_ifc4_model
from workers.release.ifc_guid import (
    generate_deterministic_ifc_guid,
    compress_guid,
    expand_guid,
    IFC_BASE64_ALPHABET
)
from workers.release.ifc_georeference import (
    resolve_projected_crs,
    latlon_to_utm_coordinates,
    ProjectedCRSMetadata
)


class TestIFCGeoreferencingAndProfessionalization(unittest.TestCase):
    """Test suite covering Milestone 1 acceptance criteria A through O."""

    @classmethod
    def setUpClass(cls):
        cls.authoritative_release_id = "rel-pilot-20261002-aedf9830"
        cls.authoritative_project_id = "proj-mumbai-real-1100"
        cls.authoritative_design_version_id = "DV-OPT-B-9be0a983"
        cls.authoritative_fingerprint = "876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4"
        cls.authoritative_plot_area = 1100.0

        # Isolated test directory - MUST NOT touch artifacts/pilot_handoff/
        cls.test_output_dir = ROOT_DIR / "artifacts" / "test_ifc_m1"
        cls.test_output_dir.mkdir(parents=True, exist_ok=True)
        cls.pilot_handoff_dir = ROOT_DIR / "artifacts" / "pilot_handoff"

        # Compile authoritative Option B Canonical Building Model
        cls.cbm = compile_canonical_building_model(
            archetype="compact_2bhk",
            design_version_id=cls.authoritative_design_version_id
        )

        # Baseline pilot site data
        cls.site_data = {
            "declaredPlotAreaSqFt": 1100.0,
            "declaredPlotAreaSqm": 102.193,
            "referenceFrame": {
                "originLatitude": 19.0596,
                "originLongitude": 72.8295,
                "originElevationM": 12.0,
                "trueNorthBearingDeg": 0.0,
                "coordinateSystem": "SECS_ENU"
            }
        }

        # Generate test IFC output
        cls.ifc_content = generate_ifc4_model(
            cls.cbm,
            release_id=cls.authoritative_release_id,
            site_data=cls.site_data
        )

        cls.test_ifc_path = cls.test_output_dir / f"{cls.authoritative_release_id}.ifc"
        cls.test_ifc_path.write_text(cls.ifc_content, encoding="utf-8")

    # A. IFC file exists and is non-empty
    def test_a_ifc_file_exists_and_non_empty(self):
        self.assertTrue(self.test_ifc_path.exists())
        self.assertGreater(self.test_ifc_path.stat().st_size, 1000)

    # B. ISO-10303-21 header exists
    def test_b_iso_10303_21_step_syntax(self):
        self.assertTrue(self.ifc_content.startswith("ISO-10303-21;"))
        self.assertIn("HEADER;", self.ifc_content)
        self.assertIn("DATA;", self.ifc_content)
        self.assertIn("ENDSEC;", self.ifc_content)
        self.assertTrue(self.ifc_content.rstrip().endswith("END-ISO-10303-21;"))

    # C. IFC4 schema declaration exists
    def test_c_ifc4_schema_declaration(self):
        self.assertIn("FILE_SCHEMA(('IFC4'));", self.ifc_content)

    # D. IfcProjectedCRS exists with correct EPSG metadata
    def test_d_ifc_projected_crs_present(self):
        self.assertIn("IFCPROJECTEDCRS", self.ifc_content)
        self.assertIn("EPSG:32643", self.ifc_content)
        self.assertIn("WGS 84 / UTM zone 43N", self.ifc_content)
        self.assertIn("UTM", self.ifc_content)
        self.assertIn("43N", self.ifc_content)

    # E. IfcMapConversion exists with accurate SECS values
    def test_e_ifc_map_conversion_present(self):
        self.assertIn("IFCMAPCONVERSION", self.ifc_content)
        # Check Easting, Northing, Orthogonal Height
        self.assertIn("271593.2917", self.ifc_content)
        self.assertIn("2108835.3168", self.ifc_content)
        self.assertIn("12.0000", self.ifc_content)

    # F. Geometric representation context references georeferencing
    def test_f_geometric_context_linking(self):
        # Match MapConversion linking to #3 (Context) and ProjectedCRS
        match = re.search(r"#\d+=IFCMAPCONVERSION\(#3,#(\d+),", self.ifc_content)
        self.assertIsNotNone(match, "IFCMAPCONVERSION must reference #3 (Context)")
        crs_id = match.group(1)
        # Ensure that crs_id is an IFCPROJECTEDCRS
        self.assertIn(f"#{crs_id}=IFCPROJECTEDCRS", self.ifc_content)

    # G. Deterministic GUID generation
    def test_g_deterministic_guid_generation(self):
        g1 = generate_deterministic_ifc_guid(self.authoritative_release_id, "WALL-EXT-001")
        g2 = generate_deterministic_ifc_guid(self.authoritative_release_id, "WALL-EXT-001")
        g3 = generate_deterministic_ifc_guid(self.authoritative_release_id, "WALL-EXT-002")

        self.assertEqual(g1, g2, "Same release and element must produce identical GUID")
        self.assertNotEqual(g1, g3, "Different elements must produce distinct GUIDs")

    # H. All IfcRoot GUIDs have exact length 22 and valid characters
    def test_h_all_root_guids_valid(self):
        ROOT_ENTITIES = [
            "IFCPROJECT", "IFCSITE", "IFCBUILDING", "IFCBUILDINGSTOREY",
            "IFCSPACE", "IFCWALL", "IFCCOLUMN", "IFCSLAB", "IFCDOOR", "IFCWINDOW",
            "IFCPROPERTYSET", "IFCRELDEFINESBYPROPERTIES", "IFCRELASSOCIATESCLASSIFICATION"
        ]
        pattern = re.compile(r"#\d+=(IFC[A-Z0-9_]+)\('([^']+)'")
        root_count = 0

        for match in pattern.finditer(self.ifc_content):
            ent_type, guid = match.group(1), match.group(2)
            if ent_type in ROOT_ENTITIES:
                root_count += 1
                self.assertEqual(len(guid), 22, f"Entity {ent_type} has invalid GUID length: {guid}")
                for char in guid:
                    self.assertIn(char, IFC_BASE64_ALPHABET, f"Invalid char {char} in GUID {guid}")

        self.assertGreater(root_count, 50, "Expected at least 50 IfcRoot entities with standard GUIDs")

    # I. Repeated export gives identical SHA-256 (Byte-for-byte determinism)
    def test_i_repeated_export_byte_for_byte_determinism(self):
        export_1 = generate_ifc4_model(self.cbm, release_id=self.authoritative_release_id, site_data=self.site_data)
        export_2 = generate_ifc4_model(self.cbm, release_id=self.authoritative_release_id, site_data=self.site_data)

        hash_1 = hashlib.sha256(export_1.encode("utf-8")).hexdigest()
        hash_2 = hashlib.sha256(export_2.encode("utf-8")).hexdigest()

        self.assertEqual(hash_1, hash_2, "Repeated IFC export must be 100% byte-for-byte identical")

    # J. Pset_WallCommon exists where applicable
    def test_j_pset_wall_common_present(self):
        self.assertIn("Pset_WallCommon", self.ifc_content)
        self.assertIn("LoadBearing", self.ifc_content)
        self.assertIn("IsExternal", self.ifc_content)
        self.assertIn("NominalThickness", self.ifc_content)
        self.assertIn("IFCRELDEFINESBYPROPERTIES", self.ifc_content)

    # K. Pset_ConcreteElementGeneral exists where applicable
    def test_k_pset_concrete_element_general_present(self):
        self.assertIn("Pset_ConcreteElementGeneral", self.ifc_content)
        self.assertIn("StrengthClass", self.ifc_content)
        self.assertIn("ConstructionType", self.ifc_content)
        self.assertIn("M25", self.ifc_content)

    # L. Uniclass 2015 classification references are deterministic
    def test_l_uniclass_classification_present(self):
        self.assertIn("IFCCLASSIFICATION", self.ifc_content)
        self.assertIn("Uniclass 2015", self.ifc_content)
        self.assertIn("IFCCLASSIFICATIONREFERENCE", self.ifc_content)
        self.assertIn("Pr_20_85_12_02", self.ifc_content)  # AAC Block units
        self.assertIn("Pr_20_85_16_40", self.ifc_content)  # In situ concrete
        self.assertIn("IFCRELASSOCIATESCLASSIFICATION", self.ifc_content)

    # M. Pilot project/release/design lineage is preserved
    def test_m_pilot_lineage_preserved(self):
        self.assertIn(self.authoritative_release_id, self.ifc_content)
        self.assertIn(self.cbm.name, self.ifc_content)

    # N. No benchmark contamination
    def test_n_no_benchmark_contamination(self):
        # Must not contain legacy benchmark tokens in IFC strings
        for bad_token in ["2400sqft", "40x60", "GOLDEN-10000", "CTS-DEMO-101"]:
            self.assertNotIn(bad_token, self.ifc_content)

    # O. Immutability of authoritative pilot release
    def test_o_authoritative_pilot_release_untouched(self):
        authoritative_manifest_path = self.pilot_handoff_dir / "pilot_release_manifest.json"
        self.assertTrue(authoritative_manifest_path.exists())

        manifest_data = json.loads(authoritative_manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest_data["releaseFingerprint"],
            self.authoritative_fingerprint,
            "Authoritative release fingerprint must remain untouched"
        )
        self.assertEqual(
            manifest_data["releaseId"],
            self.authoritative_release_id
        )

        # Assert test file was written to isolated directory, not pilot_handoff
        self.assertTrue(str(self.test_ifc_path).startswith(str(self.test_output_dir)))
        self.assertFalse(str(self.test_ifc_path).startswith(str(self.pilot_handoff_dir)))

    # P. Graceful fallback when reference frame is not available
    def test_p_graceful_fallback_without_crs(self):
        plain_model = compile_canonical_building_model(archetype="compact_2bhk", design_version_id="DV-PLAIN-001")
        plain_ifc = generate_ifc4_model(plain_model, release_id="rel-plain-001")
        self.assertIn("ISO-10303-21;", plain_ifc)
        self.assertIn("IFCPROJECT", plain_ifc)
        self.assertIn("END-ISO-10303-21;", plain_ifc)


if __name__ == "__main__":
    unittest.main()
