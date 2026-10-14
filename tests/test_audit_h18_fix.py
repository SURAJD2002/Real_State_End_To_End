"""
Unit test verifying fix for H18:
Fallback archetypes must never claim false statutory compliance PASS.
"""

import unittest
from workers.generation.house_generator import generate_m2_house_options
from packages.schemas.customer_brief import CustomerBrief

class TestH18ComplianceBypass(unittest.TestCase):
    def test_fallback_does_not_claim_pass_compliance(self):
        # Providing a 2m x 2m envelope forces CP-SAT infeasibility -> fallback
        brief = CustomerBrief(
            briefId="BRIEF-FAIL-TEST",
            projectId="proj-fail-test",
            bedrooms=3,
            bathrooms=2,
            floors=1
        )
        opts = generate_m2_house_options(site_width_m=2.0, site_length_m=2.0, brief=brief)
        self.assertTrue(len(opts) > 0)
        for opt in opts:
            self.assertTrue(opt.get("isFallback"))
            self.assertEqual(opt.get("fallbackReason"), "CP_SAT_INFEASIBLE_OR_TIMEOUT")
            compliance = opt.get("compliance", {})
            self.assertNotEqual(compliance.get("statutorySetbacks"), "PASS")
            self.assertNotEqual(compliance.get("nbcRoomMinimums"), "PASS")
            self.assertEqual(compliance.get("statutorySetbacks"), "WARNING_UNVERIFIED_FALLBACK")

if __name__ == "__main__":
    unittest.main()
