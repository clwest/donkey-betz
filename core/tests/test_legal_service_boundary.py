"""Service-boundary invariant tests for legal services (S2802 Phase 2.1).

Enforces the IDOR contract from Phase 1 (PR #3218): after the refactor,
`LegalResponseWriter.generate_response` + `LegalFilingPackager.create_filing_package`
take pre-scoped model instances, not raw IDs. Their docstrings say:

    `doc` MUST be scoped to the requesting user by the caller — this
    service performs no authorization check. Pass a raw ID lookup and
    you have an IDOR vector.

These tests assert the invariant that MISUSE — passing a raw UUID or None —
fails fast (attribute error), rather than silently doing the wrong thing.
The failure mode is documented current behavior: services dereference
instance attributes (`.case_profile`, `.id`, `.full_document`, etc.),
which will not silently coerce a UUID or None into a model.

This is a defense-in-depth regression guard for the Phase 1 refactor.
If a future edit accidentally reintroduces an internal `.objects.get(id=X)`
lookup, one of these tests will fail (either by not raising, or by
raising a different exception type that indicates the service did an
unscoped DB fetch).

Follow-up committed per Rigby Phase 2 SIGN Fold 2.

Run: python manage.py test core.tests.test_legal_service_boundary -v2
"""

import uuid

from django.test import SimpleTestCase

from core.services.litigation_brain import (
    LegalFilingPackager,
    LegalResponseWriter,
)


class LegalResponseWriterServiceBoundaryTests(SimpleTestCase):
    """LegalResponseWriter.generate_response takes a LitigationDocument
    instance. Passing anything else must fail fast — the service must
    not perform its own DB lookup and must not silently succeed with
    unscoped data."""

    def test_raw_uuid_fails_fast(self):
        writer = LegalResponseWriter()
        with self.assertRaises(AttributeError):
            writer.generate_response(uuid.uuid4())

    def test_none_fails_fast(self):
        writer = LegalResponseWriter()
        with self.assertRaises(AttributeError):
            writer.generate_response(None)


class LegalFilingPackagerServiceBoundaryTests(SimpleTestCase):
    """LegalFilingPackager.create_filing_package takes a GeneratedResponse
    instance. Same invariant as above."""

    def test_raw_uuid_fails_fast(self):
        packager = LegalFilingPackager()
        with self.assertRaises(AttributeError):
            packager.create_filing_package(uuid.uuid4())

    def test_none_fails_fast(self):
        packager = LegalFilingPackager()
        with self.assertRaises(AttributeError):
            packager.create_filing_package(None)
