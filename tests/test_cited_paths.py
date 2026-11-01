"""
Planwise Enterprise — Test Path Citation Verification Gate
==========================================================
Verifies that all file paths cited across project documentation,
reports, and evidence manifests exist in the local repository.
"""

import unittest
from pathlib import Path
from scripts.verify_cited_paths import verify_all_cited_paths


class TestPathCitationIntegrity(unittest.TestCase):
    def test_all_cited_paths_exist(self):
        total_checked, violations = verify_all_cited_paths()
        self.assertGreater(total_checked, 0, "Expected at least 100 cited paths to be scanned")
        if violations:
            msg = f"\nFound {len(violations)} non-existent or broken file citation(s):\n"
            for v in violations:
                msg += f"  - {v['sourceDocument']}:{v['line']} -> {v['citedPath']}\n"
            self.fail(msg)


if __name__ == "__main__":
    unittest.main()
