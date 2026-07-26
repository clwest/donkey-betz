"""Tests for S2970 PR-B — RSS-first fixes for reddit + sports_injuries.

Covers:
- ``SPIDER_TARGET_URLS`` config shape (reddit ``.rss`` endpoints, no legacy
  ``.json``; sports_injuries per-sport rotowire feeds, no ``injuries.xml``).
- ``parse_rss_feed`` on reddit Atom + rotowire RSS fixtures (extension
  of what S2969 covered so future feed-format drift is caught).
- ``filter_injury_items`` positive + negative cases (Rigby T1 guardrail:
  proves the filter does not degrade into a roster-news firehose).
- ``derive_empty_reason`` precedence: ``fetch_failed`` > ``no_items`` >
  ``all_deduped`` (Rigby T1 guardrail).
- ``build_empty_run_diagnostic`` fetch-failure branch carries
  ``urls_attempted`` + ``failed_urls``.
- ``collect_spider_data`` populates ``fetch_stats`` (attempts, successes,
  failed_urls) and applies the injury filter for sports_injuries only.
- Runner integration: ``_impl_run_spider_network`` reads ``fetch_stats``
  and persists a diagnostic row with ``empty_reason='fetch_failed'``
  when all URL fetches fail.
"""

import asyncio
import os
from types import SimpleNamespace
from unittest.mock import patch

import aiohttp
from django.test import SimpleTestCase


# ---------------------------------------------------------------------------
# Fixtures (kept inline to avoid a fixtures/ dir; small enough to read).
# ---------------------------------------------------------------------------

REDDIT_ATOM_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>Test reddit feed</title>
<id>test:reddit</id>
<updated>2026-07-25T00:00:00+00:00</updated>
<entry>
<title>Monthly Getting Started / Web Dev Career Thread</title>
<link href="https://www.reddit.com/r/webdev/comments/1ukjn5j/monthly_getting_started_web_dev_career_thread/"/>
<updated>2026-07-01T12:00:15+00:00</updated>
<id>https://www.reddit.com/r/webdev/comments/1ukjn5j/monthly_getting_started_web_dev_career_thread/</id>
<content type="html">Sample summary</content>
</entry>
<entry>
<title>I made this Mario-themed OTP input</title>
<link href="https://www.reddit.com/r/webdev/comments/1v67w5v/i_made_this_mariothemed_otp_input/"/>
<updated>2026-07-25T13:05:08+00:00</updated>
<id>https://www.reddit.com/r/webdev/comments/1v67w5v/i_made_this_mariothemed_otp_input/</id>
<content type="html">Sample summary</content>
</entry>
<entry>
<title>It has a Lock api?! I love you MDN</title>
<link href="https://www.reddit.com/r/webdev/comments/1v6jakg/it_has_a_lock_api_i_love_you_mdn/"/>
<updated>2026-07-25T20:38:56+00:00</updated>
<id>https://www.reddit.com/r/webdev/comments/1v6jakg/it_has_a_lock_api_i_love_you_mdn/</id>
<content type="html">Sample summary</content>
</entry>
<entry>
<title>I made open source MIT licensed visual CMS</title>
<link href="https://www.reddit.com/r/webdev/comments/1v6i4aw/i_made_open_source_mit_licensed_visual_cms/"/>
<updated>2026-07-25T19:52:19+00:00</updated>
<id>https://www.reddit.com/r/webdev/comments/1v6i4aw/i_made_open_source_mit_licensed_visual_cms/</id>
<content type="html">Sample summary</content>
</entry>
<entry>
<title>Stolen Buttons</title>
<link href="https://www.reddit.com/r/webdev/comments/1v6ehnf/stolen_buttons/"/>
<updated>2026-07-25T17:32:37+00:00</updated>
<id>https://www.reddit.com/r/webdev/comments/1v6ehnf/stolen_buttons/</id>
<content type="html">Sample summary</content>
</entry>
</feed>
"""


ROTOWIRE_RSS_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>RotoWire.com Latest Sports News</title>
<link>https://www.rotowire.com/</link>
<description>Latest news</description>
<item>
<title>Brandon Aiyuk: Remains on left squad list</title>
<link>https://www.rotowire.com/football/news/brandon-aiyuk-remains-1</link>
<pubDate>Fri, 25 Jul 2026 22:00:00 -0500</pubDate>
<description>Aiyuk remains on the squad list.</description>
</item>
<item>
<title>George Kittle: Starting training camp on PUP</title>
<link>https://www.rotowire.com/football/news/george-kittle-pup-2</link>
<pubDate>Fri, 25 Jul 2026 21:30:00 -0500</pubDate>
<description>Kittle placed on physically unable to perform list.</description>
</item>
<item>
<title>James Garner: Undergoes successful groin surgery</title>
<link>https://www.rotowire.com/soccer/news/james-garner-surgery-3</link>
<pubDate>Fri, 25 Jul 2026 20:00:00 -0500</pubDate>
<description>Garner had surgery on his groin.</description>
</item>
<item>
<title>LeBron James: Heading to Philadelphia</title>
<link>https://www.rotowire.com/basketball/news/lebron-philadelphia-4</link>
<pubDate>Fri, 25 Jul 2026 19:00:00 -0500</pubDate>
<description>James signs with the Sixers.</description>
</item>
<item>
<title>Player X: Ruled out for tonight with hamstring strain</title>
<link>https://www.rotowire.com/football/news/player-x-hamstring-5</link>
<pubDate>Fri, 25 Jul 2026 18:00:00 -0500</pubDate>
<description>Sidelined with hamstring injury.</description>
</item>
</channel>
</rss>
"""


# ---------------------------------------------------------------------------
# SPIDER_TARGET_URLS configuration
# ---------------------------------------------------------------------------

class SpiderTargetUrlsConfigTests(SimpleTestCase):
    """Guard the URL swap so future refactors can't silently regress
    back to the JSON API (reddit) or the 404 rotowire feeds
    (sports_injuries) without a failing test."""

    def test_reddit_urls_all_atom_rss_endpoints(self):
        from ai_core.spiders.real_data_collector import SPIDER_TARGET_URLS
        urls = SPIDER_TARGET_URLS['reddit']
        self.assertGreaterEqual(len(urls), 3, 'expected at least 3 subreddit feeds')
        for url in urls:
            self.assertTrue(
                url.endswith('/.rss'),
                f'{url} — reddit URLs must be .rss endpoints (Atom), not JSON',
            )
            self.assertNotIn('hot.json', url)
            self.assertNotIn('.json?', url)

    def test_sports_injuries_urls_removed_dead_feeds(self):
        from ai_core.spiders.real_data_collector import SPIDER_TARGET_URLS
        urls = SPIDER_TARGET_URLS['sports_injuries']
        self.assertGreaterEqual(len(urls), 3)
        joined = '|'.join(urls)
        # All three previous URLs returned HTTP 404 in S2970 probe.
        self.assertNotIn('rss/injuries.xml', joined)
        self.assertNotIn('cbssports.com/rss/headlines/injuries', joined)
        self.assertNotIn('rotogrinders.com/feeds/injury-report.xml', joined)

    def test_sports_injuries_urls_are_rotowire_per_sport_feeds(self):
        from ai_core.spiders.real_data_collector import SPIDER_TARGET_URLS
        urls = SPIDER_TARGET_URLS['sports_injuries']
        for url in urls:
            self.assertIn('rotowire.com/rss/news.php', url)
            self.assertIn('sport=', url)


# ---------------------------------------------------------------------------
# parse_rss_feed on fixtures
# ---------------------------------------------------------------------------

class ParseRssFeedFixtureTests(SimpleTestCase):
    """Verify the shared RSS parser produces stable URL/title/timestamp
    for the two feed formats we now depend on (reddit Atom + rotowire
    RSS 2.0). Guards against feed-format drift."""

    def test_parse_reddit_atom_fixture_yields_five_items(self):
        from ai_core.spiders.real_data_collector import parse_rss_feed
        items = parse_rss_feed(REDDIT_ATOM_FIXTURE, 'reddit')
        self.assertGreaterEqual(len(items), 5)
        for item in items:
            self.assertTrue(item['title'])
            self.assertTrue(item['link'].startswith('https://www.reddit.com/'))
            self.assertTrue(item['published'])
            self.assertEqual(item['source'], 'reddit')

    def test_parse_rotowire_rss_fixture_yields_five_items(self):
        from ai_core.spiders.real_data_collector import parse_rss_feed
        items = parse_rss_feed(ROTOWIRE_RSS_FIXTURE, 'sports_injuries')
        self.assertGreaterEqual(len(items), 5)
        for item in items:
            self.assertTrue(item['title'])
            self.assertTrue(item['link'].startswith('https://www.rotowire.com/'))


# ---------------------------------------------------------------------------
# filter_injury_items — Rigby T1 guardrail: negative case explicit
# ---------------------------------------------------------------------------

class FilterInjuryItemsTests(SimpleTestCase):
    """Rigby T1 guardrail: the injury filter is what keeps sports_injuries
    from becoming a roster-news firehose after we swap in per-sport feeds.
    These tests pin the positive and (crucially) the negative behavior."""

    def test_empty_input_returns_empty(self):
        from ai_core.spiders.real_data_collector import filter_injury_items
        self.assertEqual(filter_injury_items([]), [])

    def test_keeps_items_with_injury_keywords(self):
        from ai_core.spiders.real_data_collector import filter_injury_items
        items = [
            {'title': 'Player X: Ruled out for tonight', 'description': ''},
            {'title': 'Player Y: Undergoes successful groin surgery', 'description': ''},
            {'title': 'Player Z: Placed on IR', 'description': 'Torn ACL'},
            {'title': 'Player Q: Questionable', 'description': ''},
            {'title': 'Player R: PUP list to start camp', 'description': ''},
            {'title': 'Player S: Concussion protocol update', 'description': ''},
            {'title': 'Player T: Hamstring strain sidelines him', 'description': ''},
        ]
        kept = filter_injury_items(items)
        self.assertEqual(len(kept), len(items))

    def test_drops_roster_news_without_injury_keywords(self):
        """Negative case (Rigby T1 pushback): 'Remains on left squad list'
        is roster news, not injury news — must be dropped."""
        from ai_core.spiders.real_data_collector import filter_injury_items
        items = [
            {'title': 'Brandon Aiyuk: Remains on left squad list', 'description': ''},
            {'title': 'LeBron James: Heading to Philadelphia', 'description': 'Signs with Sixers'},
            {'title': 'Ty Simpson: Agrees to rookie contract', 'description': ''},
            {'title': 'Akira Schmid: Inks two-year deal', 'description': ''},
        ]
        kept = filter_injury_items(items)
        self.assertEqual(
            kept,
            [],
            f'expected all roster-news items dropped, kept {[k["title"] for k in kept]}',
        )

    def test_mixed_batch_keeps_only_injury_items(self):
        from ai_core.spiders.real_data_collector import filter_injury_items
        items = [
            {'title': 'Player A: Trade rumors heat up', 'description': ''},           # drop
            {'title': 'Player B: Out with knee sprain', 'description': ''},           # keep
            {'title': 'Player C: Signs multi-year extension', 'description': ''},      # drop
            {'title': 'Player D: Doubtful for Sunday', 'description': ''},             # keep
            {'title': 'Player E: Named team captain', 'description': ''},              # drop
        ]
        kept = filter_injury_items(items)
        titles = [k['title'] for k in kept]
        self.assertEqual(len(kept), 2)
        self.assertIn('Player B: Out with knee sprain', titles)
        self.assertIn('Player D: Doubtful for Sunday', titles)


# ---------------------------------------------------------------------------
# derive_empty_reason precedence (Rigby T1 guardrail)
# ---------------------------------------------------------------------------

class DeriveEmptyReasonTests(SimpleTestCase):
    """Precedence baked into a matrix: fetch_failed > no_items > all_deduped."""

    def test_fetch_failed_when_all_urls_failed(self):
        from core.services.spider_diagnostic import (
            EMPTY_REASON_FETCH_FAILED,
            derive_empty_reason,
        )
        # Even if items_before_dedup > 0 the fetch_stats verdict wins.
        reason = derive_empty_reason(
            items_before_dedup=0,
            unique_after_dedup=0,
            fetch_stats={'attempts': 3, 'successes': 0, 'failed_urls': ['a', 'b', 'c']},
        )
        self.assertEqual(reason, EMPTY_REASON_FETCH_FAILED)

    def test_no_items_when_fetches_succeeded_but_feed_empty(self):
        from core.services.spider_diagnostic import (
            EMPTY_REASON_NO_ITEMS,
            derive_empty_reason,
        )
        reason = derive_empty_reason(
            items_before_dedup=0,
            unique_after_dedup=0,
            fetch_stats={'attempts': 3, 'successes': 3, 'failed_urls': []},
        )
        self.assertEqual(reason, EMPTY_REASON_NO_ITEMS)

    def test_all_deduped_when_items_existed_but_dedup_dropped_them(self):
        from core.services.spider_diagnostic import (
            EMPTY_REASON_ALL_DEDUPED,
            derive_empty_reason,
        )
        reason = derive_empty_reason(
            items_before_dedup=10,
            unique_after_dedup=0,
            fetch_stats={'attempts': 3, 'successes': 3, 'failed_urls': []},
        )
        self.assertEqual(reason, EMPTY_REASON_ALL_DEDUPED)

    def test_all_deduped_requires_items_before_dedup_positive(self):
        """Rigby T1 guardrail: all_deduped only wins with items_before_dedup>0."""
        from core.services.spider_diagnostic import (
            EMPTY_REASON_NO_ITEMS,
            derive_empty_reason,
        )
        reason = derive_empty_reason(
            items_before_dedup=0,
            unique_after_dedup=0,
            fetch_stats=None,
        )
        self.assertEqual(reason, EMPTY_REASON_NO_ITEMS)

    def test_no_fetch_stats_falls_back_to_items_based_reason(self):
        from core.services.spider_diagnostic import (
            EMPTY_REASON_ALL_DEDUPED,
            EMPTY_REASON_NO_ITEMS,
            derive_empty_reason,
        )
        self.assertEqual(
            derive_empty_reason(items_before_dedup=0, unique_after_dedup=0),
            EMPTY_REASON_NO_ITEMS,
        )
        self.assertEqual(
            derive_empty_reason(items_before_dedup=5, unique_after_dedup=0),
            EMPTY_REASON_ALL_DEDUPED,
        )


# ---------------------------------------------------------------------------
# build_empty_run_diagnostic fetch-failure branch
# ---------------------------------------------------------------------------

class BuildEmptyRunDiagnosticFetchFailureTests(SimpleTestCase):
    """When fetch_stats says every URL failed, the diagnostic must carry
    urls_attempted + failed_urls so operators can debug without another
    trip to the code."""

    def test_fetch_failure_diagnostic_shape(self):
        from core.services.spider_diagnostic import (
            EMPTY_REASON_FETCH_FAILED,
            STATUS_SUCCESS_EMPTY,
            build_empty_run_diagnostic,
        )
        diag = build_empty_run_diagnostic(
            items_before_dedup=0,
            unique_after_dedup=0,
            duplicates=0,
            execution_log_id='exec-99',
            ephemeral=True,
            fetch_stats={
                'attempts': 3,
                'successes': 0,
                'urls_attempted': ['a', 'b', 'c'],
                'failed_urls': ['a', 'b', 'c'],
            },
        )
        self.assertEqual(diag['status'], STATUS_SUCCESS_EMPTY)
        self.assertEqual(diag['empty_reason'], EMPTY_REASON_FETCH_FAILED)
        self.assertEqual(diag['urls_attempted'], ['a', 'b', 'c'])
        self.assertEqual(diag['failed_urls'], ['a', 'b', 'c'])
        self.assertTrue(diag['ephemeral_empty_run'])
        self.assertEqual(diag['execution_log_id'], 'exec-99')

    def test_success_reason_diagnostic_does_not_carry_url_lists(self):
        """Only the fetch_failed branch carries URL lists; no_items /
        all_deduped stay lean."""
        from core.services.spider_diagnostic import build_empty_run_diagnostic
        diag = build_empty_run_diagnostic(
            items_before_dedup=5,
            unique_after_dedup=0,
            duplicates=5,
            fetch_stats={'attempts': 1, 'successes': 1, 'failed_urls': []},
        )
        self.assertEqual(diag['empty_reason'], 'all_deduped')
        self.assertNotIn('urls_attempted', diag)
        self.assertNotIn('failed_urls', diag)


# ---------------------------------------------------------------------------
# collect_spider_data fetch_stats + injury filter integration
# ---------------------------------------------------------------------------

class CollectSpiderDataFetchStatsTests(SimpleTestCase):
    """Verify the collector reports fetch_stats and applies the injury
    filter (sports_injuries only, post-parse pre-dedup)."""

    def test_fetch_stats_populated_on_all_failure(self):
        from ai_core.spiders import real_data_collector

        async def _fake_fetch(_session, _url, timeout=30):
            return None  # every URL fails

        with patch.object(real_data_collector, 'fetch_url', side_effect=_fake_fetch):
            data = asyncio.run(real_data_collector.collect_spider_data('reddit'))
        stats = data['fetch_stats']
        self.assertEqual(stats['attempts'], len(data['urls_scraped']))
        self.assertEqual(stats['successes'], 0)
        self.assertEqual(stats['failed_urls'], list(data['urls_scraped']))
        self.assertEqual(data['items'], [])

    def test_fetch_stats_populated_on_partial_success(self):
        from ai_core.spiders import real_data_collector

        call_counter = {'n': 0}

        async def _fake_fetch(_session, url, timeout=30):
            call_counter['n'] += 1
            if call_counter['n'] == 1:
                # First URL succeeds — returns feedparser-parseable Atom
                return {'type': 'rss', 'data': REDDIT_ATOM_FIXTURE, 'url': url}
            return None

        with patch.object(real_data_collector, 'fetch_url', side_effect=_fake_fetch):
            data = asyncio.run(real_data_collector.collect_spider_data('reddit'))
        stats = data['fetch_stats']
        self.assertEqual(stats['attempts'], len(data['urls_scraped']))
        self.assertEqual(stats['successes'], 1)
        self.assertGreaterEqual(len(data['items']), 5)

    def test_sports_injuries_applies_injury_filter(self):
        """Feed with mixed injury + roster items — collector drops roster
        items before returning."""
        from ai_core.spiders import real_data_collector

        mixed_rss = """<?xml version="1.0"?><rss version="2.0"><channel>
        <title>t</title><link>x</link><description>d</description>
        <item><title>Player: Concussion protocol</title><link>https://x/a</link><description>d</description></item>
        <item><title>Player: Signs new deal</title><link>https://x/b</link><description>d</description></item>
        <item><title>Player: Ruled out with hamstring</title><link>https://x/c</link><description>d</description></item>
        <item><title>Player: Traded to Rangers</title><link>https://x/d</link><description>d</description></item>
        </channel></rss>"""

        async def _fake_fetch(_session, url, timeout=30):
            return {'type': 'rss', 'data': mixed_rss, 'url': url}

        with patch.object(real_data_collector, 'fetch_url', side_effect=_fake_fetch):
            data = asyncio.run(real_data_collector.collect_spider_data('sports_injuries'))
        titles = [i['title'] for i in data['items']]
        # 5 rotowire URLs × 3 injury items = 15 (parser + filter identical per URL);
        # roster-news items dropped even though feedparser produced them.
        self.assertGreater(len(titles), 0)
        self.assertTrue(all('Signs new deal' not in t and 'Traded' not in t for t in titles),
                        f'roster items should have been filtered: {titles}')
        self.assertTrue(any('Concussion' in t or 'hamstring' in t.lower() for t in titles))

    def test_non_sports_injuries_spider_not_filtered(self):
        """Injury filter is spider-scoped — reddit items must pass through."""
        from ai_core.spiders import real_data_collector

        async def _fake_fetch(_session, url, timeout=30):
            return {'type': 'rss', 'data': REDDIT_ATOM_FIXTURE, 'url': url}

        with patch.object(real_data_collector, 'fetch_url', side_effect=_fake_fetch):
            data = asyncio.run(real_data_collector.collect_spider_data('reddit'))
        titles = [i['title'] for i in data['items']]
        # Reddit fixture titles are all non-injury; must survive.
        self.assertTrue(any('OTP input' in t for t in titles))
        self.assertTrue(any('Stolen Buttons' in t for t in titles))


# ---------------------------------------------------------------------------
# Dedup stability across two runs on the same RSS links
# ---------------------------------------------------------------------------

class DedupStabilityRssTests(SimpleTestCase):
    """First run: N unique items. Second run with same permalinks: 0
    unique, N duplicates. Uses in-memory hash tracking mock — proves
    the dedup key is stable across runs given RSS canonical URLs."""

    def test_two_runs_second_all_duplicates(self):
        from core.services.spider_deduplication import SpiderDeduplicationService

        # Mock SpiderItemHash to hold state in memory across the two runs.
        seen = set()

        class _MockHashQS:
            def __init__(self):
                self._items = list(seen)

            def filter(self, **kwargs):
                return self

            def values_list(self, field, flat=False):
                return list(self._items)

        class _MockHashManager:
            def filter(self, **kwargs):
                return _MockHashQS()

            def bulk_create(self, hashes, ignore_conflicts=True):
                for h in hashes:
                    seen.add(h.content_hash)

        class _MockHash:
            objects = _MockHashManager()

            def __init__(self, spider_name, content_hash, item_title, data_type):
                self.spider_name = spider_name
                self.content_hash = content_hash
                self.item_title = item_title
                self.data_type = data_type

        with patch('core.models_unified_system.SpiderItemHash', _MockHash):
            svc = SpiderDeduplicationService()
            items = [
                {'title': 'A', 'link': 'https://www.reddit.com/r/webdev/comments/1'},
                {'title': 'B', 'link': 'https://www.reddit.com/r/webdev/comments/2'},
                {'title': 'C', 'link': 'https://www.reddit.com/r/webdev/comments/3'},
            ]
            unique1, stats1 = svc.deduplicate_items('reddit', items, 'community')
            self.assertEqual(len(unique1), 3)
            self.assertEqual(stats1['duplicates'], 0)

            # Second run with identical items
            unique2, stats2 = svc.deduplicate_items('reddit', items, 'community')
            self.assertEqual(len(unique2), 0)
            self.assertEqual(stats2['duplicates'], 3)


# ---------------------------------------------------------------------------
# ThreadedResolver flag (PR-B.1 fold)
# ---------------------------------------------------------------------------

class ThreadedDnsResolverFlagTests(SimpleTestCase):
    """PR-B.1: aiodns 3.5.0 fails on macOS + some Linux configs where the
    system DNS is mediated by a stub the pycares backend does not read;
    swap to :class:`aiohttp.ThreadedResolver` (sync ``getaddrinfo`` on a
    thread pool) by default so ``collect_spider_data`` actually reaches
    the network. Flag-gated so environments with a known-good aiodns
    can flip it off."""

    def test_flag_default_true(self):
        from ai_core.spiders.real_data_collector import _use_threaded_dns_resolver
        with patch.dict('os.environ', {}, clear=False):
            os.environ.pop('SPIDER_USE_THREADED_DNS_RESOLVER', None)
            self.assertTrue(_use_threaded_dns_resolver())

    def test_flag_false_when_set_false(self):
        from ai_core.spiders.real_data_collector import _use_threaded_dns_resolver
        with patch.dict('os.environ', {'SPIDER_USE_THREADED_DNS_RESOLVER': 'false'}):
            self.assertFalse(_use_threaded_dns_resolver())

    def test_flag_true_when_set_true(self):
        from ai_core.spiders.real_data_collector import _use_threaded_dns_resolver
        with patch.dict('os.environ', {'SPIDER_USE_THREADED_DNS_RESOLVER': 'true'}):
            self.assertTrue(_use_threaded_dns_resolver())

    def test_client_session_kwargs_threaded_resolver_when_flag_on(self):
        """Must be constructed inside a running loop — ThreadedResolver
        binds the loop at ``__init__``."""
        from ai_core.spiders.real_data_collector import _build_client_session_kwargs

        async def _construct_and_check():
            with patch.dict('os.environ', {'SPIDER_USE_THREADED_DNS_RESOLVER': 'true'}):
                kwargs = _build_client_session_kwargs()
            self.assertIn('connector', kwargs)
            connector = kwargs['connector']
            self.assertIsInstance(connector, aiohttp.TCPConnector)
            self.assertIsInstance(connector._resolver, aiohttp.ThreadedResolver)
            await connector.close()

        asyncio.run(_construct_and_check())

    def test_client_session_kwargs_empty_when_flag_off(self):
        from ai_core.spiders.real_data_collector import _build_client_session_kwargs
        with patch.dict('os.environ', {'SPIDER_USE_THREADED_DNS_RESOLVER': 'false'}):
            kwargs = _build_client_session_kwargs()
        self.assertEqual(kwargs, {})

    def test_collect_spider_data_wires_threaded_resolver_when_flag_on(self):
        """End-to-end: with flag on, ``collect_spider_data`` constructs
        the aiohttp ClientSession with a TCPConnector whose resolver is
        a ThreadedResolver. Verifies the wiring, not the network."""
        from ai_core.spiders import real_data_collector

        seen_connector_resolvers = []

        original_client_session = aiohttp.ClientSession

        def _spying_session(*args, **kwargs):
            connector = kwargs.get('connector')
            if connector is not None:
                seen_connector_resolvers.append(type(connector._resolver))
            return original_client_session(*args, **kwargs)

        async def _fake_fetch(_session, _url, timeout=30):
            return None

        with patch.dict('os.environ', {'SPIDER_USE_THREADED_DNS_RESOLVER': 'true'}), \
             patch.object(real_data_collector, 'aiohttp', new=SimpleNamespace(
                 ClientSession=_spying_session,
                 TCPConnector=aiohttp.TCPConnector,
                 ThreadedResolver=aiohttp.ThreadedResolver,
                 ClientTimeout=aiohttp.ClientTimeout,
             )), \
             patch.object(real_data_collector, 'fetch_url', side_effect=_fake_fetch):
            asyncio.run(real_data_collector.collect_spider_data('reddit'))
        self.assertEqual(seen_connector_resolvers, [aiohttp.ThreadedResolver])


# ---------------------------------------------------------------------------
# Runner integration: fetch-failure diagnostic row + reported empty_reason
# ---------------------------------------------------------------------------

def _make_runner_env(spider_configs):
    """Trimmed variant of the S2969 runner-mock scaffolding."""
    fake_registry = SimpleNamespace()
    fake_registry.list_spiders = lambda: spider_configs
    fake_registry.get_spider_class = lambda name: object()
    fake_governance = SimpleNamespace(
        objects=SimpleNamespace(
            filter=lambda *a, **kw: SimpleNamespace(
                first=lambda: SimpleNamespace(effective_mode='normal')
            )
        )
    )
    return fake_registry, fake_governance


class RunnerFetchFailureIntegrationTests(SimpleTestCase):
    """When collect_spider_data reports every URL failed, the runner
    must persist a diagnostic row whose empty_reason is 'fetch_failed'
    AND surface that reason in the per-spider result payload."""

    def test_runner_persists_fetch_failed_diagnostic_and_reports_reason(self):
        from core.tasks_spiders import _impl_run_spider_network

        fake_registry, fake_governance = _make_runner_env(
            {'reddit': {'config': {'category': 'community'}, 'category': 'community'}}
        )

        fake_return = {
            'item_count': 0,
            'items': [],
            'source': 'reddit',
            'urls_scraped': ['u1', 'u2', 'u3'],
            'fetch_stats': {
                'attempts': 3,
                'successes': 0,
                'urls_attempted': ['u1', 'u2', 'u3'],
                'failed_urls': ['u1', 'u2', 'u3'],
            },
        }

        diag_rows = []
        real_rows = []

        with patch.dict('os.environ', {
            'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'diagnostic_7d',
        }), \
             patch('core.models_governance.GovernanceState', fake_governance), \
             patch('ai_core.spiders.spider_registry.SpiderRegistry', return_value=fake_registry), \
             patch('ai_core.spiders.real_data_collector.collect_spider_data_sync', return_value=fake_return), \
             patch('core.services.spider_deduplication.deduplicate_spider_items', return_value=([], {'duplicates': 0, 'total': 0})), \
             patch('core.models_unified_system.SpiderExecutionLog') as mock_exec_log, \
             patch('core.models_unified_system.LegacySpiderData') as mock_spider_data:

            mock_exec_log.start_execution.return_value = SimpleNamespace(
                id='exec-ff',
                source_urls_attempted=[],
                complete_success=lambda *a, **k: None,
                complete_error=lambda *a, **k: None,
            )

            def _create(**kwargs):
                row = SimpleNamespace(id=f'row-{len(diag_rows) + len(real_rows)}', **kwargs)
                if 'diagnostic' in kwargs.get('raw_data', {}):
                    diag_rows.append(kwargs)
                else:
                    real_rows.append(kwargs)
                return row

            mock_spider_data.objects.create.side_effect = _create

            result = _impl_run_spider_network(SimpleNamespace(request=SimpleNamespace(id='t-ff')))

        self.assertEqual(len(diag_rows), 1)
        diag = diag_rows[0]['raw_data']['diagnostic']
        self.assertEqual(diag['status'], 'success_empty')
        self.assertEqual(diag['empty_reason'], 'fetch_failed')
        self.assertEqual(diag['urls_attempted'], ['u1', 'u2', 'u3'])
        self.assertEqual(diag['failed_urls'], ['u1', 'u2', 'u3'])

        spider_result = result['spider_results'][0]
        self.assertEqual(spider_result['empty_reason'], 'fetch_failed')
        self.assertTrue(spider_result['persisted_row'])
        self.assertEqual(real_rows, [], 'no real LegacySpiderData row should be created')

    def test_runner_reports_no_items_when_fetch_succeeded_but_feed_empty(self):
        from core.tasks_spiders import _impl_run_spider_network

        fake_registry, fake_governance = _make_runner_env(
            {'reddit': {'config': {'category': 'community'}, 'category': 'community'}}
        )
        fake_return = {
            'item_count': 0,
            'items': [],
            'source': 'reddit',
            'urls_scraped': ['u1'],
            'fetch_stats': {
                'attempts': 1,
                'successes': 1,
                'urls_attempted': ['u1'],
                'failed_urls': [],
            },
        }

        diag_rows = []

        with patch.dict('os.environ', {
            'SPIDER_EMPTY_RUN_PERSISTENCE_MODE': 'diagnostic_7d',
        }), \
             patch('core.models_governance.GovernanceState', fake_governance), \
             patch('ai_core.spiders.spider_registry.SpiderRegistry', return_value=fake_registry), \
             patch('ai_core.spiders.real_data_collector.collect_spider_data_sync', return_value=fake_return), \
             patch('core.services.spider_deduplication.deduplicate_spider_items', return_value=([], {'duplicates': 0, 'total': 0})), \
             patch('core.models_unified_system.SpiderExecutionLog') as mock_exec_log, \
             patch('core.models_unified_system.LegacySpiderData') as mock_spider_data:

            mock_exec_log.start_execution.return_value = SimpleNamespace(
                id='exec-ni',
                source_urls_attempted=[],
                complete_success=lambda *a, **k: None,
                complete_error=lambda *a, **k: None,
            )

            def _create(**kwargs):
                row = SimpleNamespace(id='row-0', **kwargs)
                if 'diagnostic' in kwargs.get('raw_data', {}):
                    diag_rows.append(kwargs)
                return row

            mock_spider_data.objects.create.side_effect = _create

            result = _impl_run_spider_network(SimpleNamespace(request=SimpleNamespace(id='t-ni')))

        self.assertEqual(len(diag_rows), 1)
        diag = diag_rows[0]['raw_data']['diagnostic']
        self.assertEqual(diag['empty_reason'], 'no_items')
        self.assertNotIn('urls_attempted', diag)
        self.assertEqual(result['spider_results'][0]['empty_reason'], 'no_items')
