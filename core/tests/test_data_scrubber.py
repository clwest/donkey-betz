"""
Session 1190 Step 1: data_scrubber tests covering the UUID false-positive
fix on the credit-card regex + regression coverage on every other pattern.

Background: Session 1189 workspace consolidation recon found that
`workspace_tool action=list` returned the Agent-Testing workspace_id as
`"59af4248-70b9-4472-[REDACTED_CC]"`. The cause was the credit-card
regex matching the digit-only tail of a UUID. Without this fix the
workspace was un-addressable for migration (no usable UUID).

The fix tightens the CC regex with lookbehind/lookahead so UUIDs no
longer collide.

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_data_scrubber -v2 --keepdb
"""

from django.test import SimpleTestCase

from core.services.data_scrubber import scrub, scrub_dict


class CreditCardUuidFalsePositiveTests(SimpleTestCase):
    """Session 1190 Step 1: the bug we're fixing."""

    def test_workspace_uuid_with_digit_heavy_tail_is_not_redacted(self):
        # The exact pattern that broke during Session 1189 recon.
        uuid_str = '59af4248-70b9-4472-1234-567890123456'
        self.assertEqual(scrub(uuid_str), uuid_str)

    def test_uuid_inside_json_payload_is_not_redacted(self):
        payload = '{"id":"59af4248-70b9-4472-1234-567890123456"}'
        self.assertEqual(scrub(payload), payload)

    def test_scrub_dict_preserves_uuid_values(self):
        # The actual call path that produced the bug — workspace_tool
        # response gets piped through scrub_dict before serialization.
        data = {
            'id': '59af4248-70b9-4472-1234-567890123456',
            'name': 'Agent-Testing',
        }
        result = scrub_dict(data)
        self.assertEqual(result['id'], '59af4248-70b9-4472-1234-567890123456')
        self.assertEqual(result['name'], 'Agent-Testing')

    def test_various_uuid_shapes_all_pass_through(self):
        # Sample of digit-heavy UUIDs that would have tripped the old regex.
        uuids = [
            '11111111-2222-3333-4444-555566667777',  # all-digit
            '00000000-0000-0000-0000-000000000000',  # nil uuid
            'aaaaaaaa-bbbb-cccc-1234-567890123456',  # digit tail
            '12345678-90ab-cdef-1234-567890123456',  # mixed
        ]
        for u in uuids:
            self.assertEqual(scrub(u), u, f"UUID '{u}' should not be redacted")


class CreditCardStillRedactedTests(SimpleTestCase):
    """Regression: real credit-card-shaped strings must STILL get redacted."""

    def test_dashed_cc(self):
        self.assertIn('[REDACTED_CC]', scrub('Card: 1234-5678-9012-3456'))

    def test_spaced_cc(self):
        self.assertIn('[REDACTED_CC]', scrub('Card: 1234 5678 9012 3456'))

    def test_no_separator_cc(self):
        self.assertIn('[REDACTED_CC]', scrub('Card: 1234567890123456'))

    def test_cc_inside_sentence(self):
        result = scrub('My card 1234-5678-9012-3456 is fine.')
        self.assertIn('[REDACTED_CC]', result)
        self.assertNotIn('1234-5678-9012-3456', result)

    def test_long_digit_sequence_not_treated_as_cc(self):
        # 20-digit sequence — fails new lookbehind because preceded by digit.
        self.assertEqual(scrub('12345678901234567890'), '12345678901234567890')


class OtherPatternsRegressionTests(SimpleTestCase):
    """Ensure tightening the CC regex didn't break any of the other rules."""

    def test_openai_api_key(self):
        self.assertIn('[REDACTED_API_KEY]', scrub('Key: sk-abc123def456ghi789jkl012'))

    def test_github_token(self):
        token = 'ghp_' + 'A' * 36
        self.assertIn('[REDACTED_GITHUB_TOKEN]', scrub(f'token={token}'))

    def test_aws_key(self):
        self.assertIn('[REDACTED_AWS_KEY]', scrub('AKIAIOSFODNN7EXAMPLE'))

    def test_bearer_token(self):
        self.assertIn('[REDACTED_TOKEN]', scrub('Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.abc'))

    def test_email(self):
        self.assertIn('[REDACTED_EMAIL]', scrub('Contact: user@example.com'))

    def test_phone(self):
        self.assertIn('[REDACTED_PHONE]', scrub('Call: 555-123-4567'))

    def test_ssn(self):
        self.assertIn('[REDACTED_SSN]', scrub('SSN: 123-45-6789'))

    def test_postgres_url(self):
        self.assertIn('[REDACTED_DB_URL]', scrub('DB: postgresql://user:pass@host:5432/db'))

    def test_redis_url(self):
        self.assertIn('[REDACTED_REDIS_URL]', scrub('Cache: redis://localhost:6379/0'))
