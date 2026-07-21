"""Session 2863 slate #1 — HuggingFaceSpider sort param fix (Rigby Tool Gap Ledger #13).

Locks in the S2863 fix:
  - HF Hub API endpoints /api/models, /api/datasets, /api/spaces reject
    `sort=trending` with HTTP 400 (verified live 2026-07-21).
  - The spider now passes `sort=downloads` at all three sites
    (huggingface_spider.py:87, :144, :200), which returns HTTP 200 with
    populated items and enables the live path instead of the curated fallback.

Three test classes:
  1. SortParamRegressionTests — mock cached_get and assert each _fetch_*
     method passes `sort=downloads` (not `trending`).
  2. SourceCodeGuardTests — grep the spider source: no `sort=trending`
     assignment inside a params dict remains.
  3. LiveHubAPIContractTests — network-required. Hits the real HF Hub API
     for /models, /datasets, /spaces with `sort=downloads`; asserts HTTP 200
     + non-empty JSON list. Skipped if the network is unavailable.
"""

import re
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import TestCase

import ai_core.spiders.specialized.huggingface_spider as hf_mod
from ai_core.spiders.specialized.huggingface_spider import HuggingFaceSpider


def _stub_response(payload):
    resp = MagicMock()
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    return resp


class SortParamRegressionTests(TestCase):
    """Each _fetch_* method must pass `sort=downloads` to cached_get."""

    def _captured_params(self, method_name, sample_payload):
        spider = HuggingFaceSpider()
        with patch.object(hf_mod, "cached_get", return_value=_stub_response(sample_payload)) as m:
            getattr(spider, method_name)(limit=3)
        self.assertEqual(m.call_count, 1, f"{method_name} should call cached_get exactly once")
        _, kwargs = m.call_args
        return kwargs.get("params") or {}

    def test_fetch_models_uses_sort_downloads(self):
        params = self._captured_params("_fetch_models", [])
        self.assertEqual(params.get("sort"), "downloads")
        self.assertNotEqual(params.get("sort"), "trending")
        self.assertEqual(params.get("direction"), -1)

    def test_fetch_datasets_uses_sort_downloads(self):
        params = self._captured_params("_fetch_datasets", [])
        self.assertEqual(params.get("sort"), "downloads")
        self.assertNotEqual(params.get("sort"), "trending")
        self.assertEqual(params.get("direction"), -1)

    def test_fetch_spaces_uses_sort_downloads(self):
        params = self._captured_params("_fetch_spaces", [])
        self.assertEqual(params.get("sort"), "downloads")
        self.assertNotEqual(params.get("sort"), "trending")
        self.assertEqual(params.get("direction"), -1)


class SourceCodeGuardTests(TestCase):
    """Grep the spider file for a `sort: 'trending'` assignment inside a params dict."""

    def test_no_sort_trending_assignment_remains(self):
        source = Path(hf_mod.__file__).read_text()
        # Match `'sort': 'trending'` or `"sort": "trending"` — quoted-key form
        # used in params dicts, not the word "trending" in comments/docstrings.
        pattern = re.compile(r"""["']sort["']\s*:\s*["']trending["']""")
        matches = pattern.findall(source)
        self.assertEqual(
            matches, [],
            "sort=trending assignment must not appear in HuggingFaceSpider "
            "(HF Hub API rejects it with HTTP 400)",
        )


class LiveHubAPIContractTests(unittest.TestCase):
    """Hit the real HF Hub API. Skip if network is unavailable."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            import requests
            cls._requests = requests
            probe = requests.get(
                "https://huggingface.co/api/models",
                params={"sort": "downloads", "direction": -1, "limit": 1},
                timeout=10,
            )
            if probe.status_code != 200:
                raise unittest.SkipTest(
                    f"HF Hub API probe returned HTTP {probe.status_code}; skipping live tests"
                )
        except Exception as exc:  # noqa: BLE001 — network probe skip is intentional
            raise unittest.SkipTest(f"HF Hub API unreachable ({exc!r}); skipping live tests")

    def _probe(self, endpoint):
        return self._requests.get(
            f"https://huggingface.co/api/{endpoint}",
            params={"sort": "downloads", "direction": -1, "limit": 3},
            timeout=15,
        )

    def test_models_sort_downloads_returns_200(self):
        resp = self._probe("models")
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertIsInstance(payload, list)
        self.assertGreater(len(payload), 0)
        top = payload[0]
        self.assertTrue(top.get("modelId") or top.get("id"))

    def test_datasets_sort_downloads_returns_200(self):
        resp = self._probe("datasets")
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertIsInstance(payload, list)
        self.assertGreater(len(payload), 0)
        self.assertTrue(payload[0].get("id"))

    def test_spaces_sort_downloads_returns_200(self):
        resp = self._probe("spaces")
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertIsInstance(payload, list)
        self.assertGreater(len(payload), 0)
        self.assertTrue(payload[0].get("id"))
