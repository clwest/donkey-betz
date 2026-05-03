from __future__ import annotations

import unittest

from scripts.verify_repo_guardrails import classify_platform_inventory_freshness


class PlatformInventoryFreshnessTests(unittest.TestCase):
    def test_passes_when_recorded_head_matches_current_head(self) -> None:
        ok, message = classify_platform_inventory_freshness(
            recorded_head="abc1234",
            current_head="abc1234",
            current_commit_files=["docs/PLATFORM_INVENTORY.md"],
            parent_head="deadbeef",
        )

        self.assertTrue(ok)
        self.assertIn("matches repo head abc1234", message)

    def test_passes_for_inventory_only_commit_against_parent_head(self) -> None:
        ok, message = classify_platform_inventory_freshness(
            recorded_head="deadbeef",
            current_head="abc1234",
            current_commit_files=["docs/PLATFORM_INVENTORY.md"],
            parent_head="deadbeef",
        )

        self.assertTrue(ok)
        self.assertIn("inventory reflects parent HEAD", message)
        self.assertIn("inventory-only", message)

    def test_fails_for_real_stale_inventory(self) -> None:
        ok, message = classify_platform_inventory_freshness(
            recorded_head="deadbeef",
            current_head="abc1234",
            current_commit_files=["README.md"],
            parent_head="deadbeef",
        )

        self.assertFalse(ok)
        self.assertEqual(message, "inventory head deadbeef != repo head abc1234")


if __name__ == "__main__":
    unittest.main()
