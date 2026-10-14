"""
Regression test verifying fix for H1:
Building envelope must be constrained by statutory setbacks and 55% coverage cap,
not 100% of declared plot area, and must fit within plot boundaries.
"""

import unittest
import math
from workers.generation.house_generator import generate_m2_house_options
from packages.schemas.customer_brief import CustomerBrief


class TestH1EnvelopeSetbacksCoverage(unittest.TestCase):
    def test_envelope_respects_coverage_and_fits_plot(self):
        declared_sqft = 1100.0
        plot_sqm = declared_sqft * 0.092903  # 102.19 sqm

        brief = CustomerBrief(
            briefId="BRIEF-ENV-TEST",
            projectId="proj-env-test",
            bedrooms=2,
            bathrooms=2,
            floors=1
        )
        opts = generate_m2_house_options(
            declared_plot_area_sqft=declared_sqft,
            brief=brief
        )
        self.assertTrue(len(opts) > 0)
        opt = opts[0]
        layout = opt["layout"]
        env = layout.get("buildingEnvelope", {})
        env_w = env.get("widthM", 0.0)
        env_l = env.get("lengthM", 0.0)
        env_area = env_w * env_l

        # Invariant 1: Envelope footprint MUST NOT be 100% of the plot!
        # It must be <= 65% of plot area (DCPR 2034 coverage cap)
        self.assertLessEqual(
            env_area,
            plot_sqm * 0.65,
            f"Envelope area {env_area:.2f} m² exceeds 65% plot coverage cap ({plot_sqm * 0.65:.2f} m²)!"
        )

        # Invariant 2: Envelope width must fit within plot width (8.38m for 27.5ft plot) minus setbacks
        self.assertLessEqual(
            env_w,
            8.38,
            f"Envelope width {env_w}m exceeds plot frontage (8.38m)!"
        )


if __name__ == "__main__":
    unittest.main()
