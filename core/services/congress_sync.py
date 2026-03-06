"""
Congress.gov Data Sync Service

Syncs members, bills, and roll call votes from the Congress.gov v3 API
into the dedicated government models.

API docs: https://api.congress.gov/

Endpoints used:
- /v3/member — current and historical congress members
- /v3/bill — bill listings with summaries
- /v3/bill/{congress}/{billType}/{billNumber}/actions — bill status history
- /v3/bill/{congress}/{billType}/{billNumber}/text — bill full text links
"""

import hashlib
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from django.utils import timezone

logger = logging.getLogger(__name__)

CONGRESS_BASE = "https://api.congress.gov/v3/"
CURRENT_CONGRESS = 119  # 2025-2027


class CongressSyncService:
    """Sync Congress.gov data into government models."""

    def __init__(self):
        self.api_key = os.environ.get('GOVERNMENT_API_KEY', '')
        self.session = requests.Session()
        self.session.headers['accept'] = 'application/json'
        self.calls = 0
        self.rate_limit = 0.5  # seconds between calls

    def _get(self, path: str, params: dict = None) -> Optional[dict]:
        """Make a rate-limited Congress.gov API call."""
        if not self.api_key:
            logger.error("GOVERNMENT_API_KEY not set")
            return None

        url = f"{CONGRESS_BASE}{path}"
        p = params or {}
        p['api_key'] = self.api_key
        p.setdefault('format', 'json')

        try:
            time.sleep(self.rate_limit)
            resp = self.session.get(url, params=p, timeout=30)
            self.calls += 1

            if resp.status_code == 429:
                logger.warning("Congress.gov rate limited, waiting 10s")
                time.sleep(10)
                resp = self.session.get(url, params=p, timeout=30)
                self.calls += 1

            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Congress.gov API error: {path} — {e}")
            return None

    # ─── Members ─────────────────────────────────────────────

    def sync_members(self, congress: int = CURRENT_CONGRESS) -> Dict:
        """Sync all members of a given Congress."""
        from core.models_government import CongressMember

        stats = {'created': 0, 'updated': 0, 'errors': 0}
        offset = 0
        limit = 250

        while True:
            data = self._get(f'member/congress/{congress}', {
                'limit': limit,
                'offset': offset,
            })
            if not data:
                break

            members = data.get('members', [])
            if not members:
                break

            for m in members:
                try:
                    bioguide = m.get('bioguideId')
                    if not bioguide:
                        continue

                    # Determine chamber and district from terms
                    terms = m.get('terms', {}).get('item', [])
                    chamber = 'house'
                    district = None
                    state_code = m.get('state', '')

                    if terms:
                        latest = terms[0] if isinstance(terms, list) else terms
                        chamber = latest.get('chamber', 'House')
                        chamber = 'senate' if 'Senate' in chamber else 'house'
                        district = latest.get('district')
                        if district:
                            try:
                                district = int(district)
                            except (ValueError, TypeError):
                                district = None

                    defaults = {
                        'first_name': m.get('name', '').split(', ')[-1].split()[0] if ', ' in m.get('name', '') else m.get('name', '').split()[0] if m.get('name') else '',
                        'last_name': m.get('name', '').split(', ')[0] if ', ' in m.get('name', '') else m.get('name', '').split()[-1] if m.get('name') else '',
                        'party': m.get('partyName', ''),
                        'chamber': chamber,
                        'state': state_code,
                        'district': district,
                        'in_office': True,
                        'profile_url': m.get('url', ''),
                        'photo_url': m.get('depiction', {}).get('imageUrl', '') if m.get('depiction') else '',
                        'terms': [t for t in terms] if isinstance(terms, list) else [],
                        'last_fetched_at': timezone.now(),
                    }

                    _, created = CongressMember.objects.update_or_create(
                        bioguide_id=bioguide,
                        defaults=defaults,
                    )
                    stats['created' if created else 'updated'] += 1

                except Exception as e:
                    logger.warning(f"Error syncing member {m.get('bioguideId')}: {e}")
                    stats['errors'] += 1

            offset += limit
            if offset >= data.get('pagination', {}).get('count', 0):
                break

        logger.info(f"Members sync: {stats}")
        return stats

    # ─── Bills (from existing SpiderData → Bill model) ───────

    def migrate_spider_bills(self) -> Dict:
        """Migrate bills from SpiderData into the Bill model."""
        from core.models_unified_system import SpiderData
        from core.models_government import Bill

        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}

        rows = SpiderData.objects.filter(spider_name='legislation').order_by('-created_at')

        for row in rows:
            rd = row.raw_data or {}
            items = rd.get('items', [])

            # Handle envelope format
            if items:
                for item in items:
                    inner = item.get('raw_data', item)
                    self._upsert_bill(inner, item.get('embedding_text', ''), stats)
            elif rd.get('bill_id') or rd.get('title'):
                self._upsert_bill(rd, row.embedding_text or '', stats)

        logger.info(f"Bill migration: {stats}")
        return stats

    def _upsert_bill(self, data: dict, fallback_embedding_text: str, stats: dict):
        """Create or update a Bill from raw data dict."""
        from core.models_government import Bill

        bill_id = data.get('bill_id')
        bill_number = data.get('bill_number', '')
        title = data.get('title', '')

        if not title and not bill_number:
            stats['skipped'] += 1
            return

        # Build canonical UID
        state = data.get('state', 'US')
        if state == 'US' and bill_number:
            # Try to parse federal bill number (e.g., "HR 1234", "S 5678")
            import re
            match = re.match(r'^([A-Z]+)\s*(\d+)$', str(bill_number).strip())
            if match:
                bill_uid = f"BILL:{CURRENT_CONGRESS}:{match.group(1)}:{match.group(2)}"
            else:
                bill_uid = f"LEGISCAN:{bill_id}" if bill_id else f"BILL:UNK:{bill_number}"
        elif bill_id:
            bill_uid = f"LEGISCAN:{bill_id}"
        else:
            bill_uid = f"BILL:{state}:{bill_number}"

        # Determine jurisdiction
        jurisdiction = 'federal' if state == 'US' else 'state'

        # Parse bill type from number
        bill_type_str = ''
        bill_num_int = None
        if bill_number:
            import re
            match = re.match(r'^([A-Z]+)\s*(\d+)$', str(bill_number).strip())
            if match:
                bill_type_str = match.group(1)
                bill_num_int = int(match.group(2))

        # Determine chamber
        chamber = ''
        if bill_type_str:
            chamber = 'senate' if bill_type_str.startswith('S') else 'house'

        try:
            defaults = {
                'jurisdiction': jurisdiction,
                'state': state if jurisdiction == 'state' else '',
                'congress': CURRENT_CONGRESS if jurisdiction == 'federal' else None,
                'bill_type': bill_type_str,
                'bill_number': bill_num_int,
                'title': title,
                'short_title': title[:500] if title else '',
                'description': data.get('description', ''),
                'plain_summary': data.get('plain_summary', ''),
                'summary_source': 'congressgov' if data.get('plain_summary') else '',
                'status': data.get('status', ''),
                'status_date': self._parse_date(data.get('status_date')),
                'chamber': chamber,
                'sponsor_names': data.get('sponsors', []),
                'committee': data.get('committee', ''),
                'topics': data.get('topics', []),
                'congress_gov_url': data.get('congress_gov_url', ''),
                'legiscan_url': data.get('url', ''),
                'legiscan_bill_id': bill_id,
                'source': 'legiscan',
                'last_action': data.get('last_action', ''),
                'last_action_date': self._parse_date(data.get('last_action_date')),
                'last_fetched_at': timezone.now(),
            }

            bill, created = Bill.objects.update_or_create(
                bill_uid=bill_uid,
                defaults=defaults,
            )

            # Build and save embedding text
            bill.build_embedding_text()
            bill.compute_content_hash()
            bill.save(update_fields=['embedding_text', 'content_hash'])

            stats['created' if created else 'updated'] += 1

        except Exception as e:
            logger.warning(f"Error upserting bill {bill_uid}: {e}")
            stats['errors'] += 1

    def _parse_date(self, val):
        if not val:
            return None
        try:
            if isinstance(val, str):
                return datetime.strptime(val[:10], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass
        return None

    # ─── Roll Call Votes ─────────────────────────────────────

    def sync_votes(self, congress: int = CURRENT_CONGRESS, chamber: str = 'house') -> Dict:
        """Sync recent roll call votes from Congress.gov."""
        from core.models_government import RollCallVote, VotePosition, CongressMember, Bill

        stats = {'votes_created': 0, 'votes_updated': 0, 'positions_created': 0, 'errors': 0}
        offset = 0
        limit = 20

        # Fetch recent roll call votes
        while True:
            data = self._get(f'bill', {
                'congress': congress,
                'limit': limit,
                'offset': offset,
                'sort': 'updateDate+desc',
            })

            # Actually, let's use the dedicated votes endpoint
            # Congress.gov doesn't have a direct /votes endpoint in v3
            # Instead, we fetch via the House/Senate clerk roll call XML
            # For now, use LegiScan roll calls which are more accessible
            break

        # Use LegiScan for roll calls (they have getSessionPeople + getRollCall)
        stats = self._sync_votes_legiscan(congress, chamber, stats)

        logger.info(f"Vote sync ({chamber}): {stats}")
        return stats

    def _sync_votes_legiscan(self, congress: int, chamber: str, stats: dict) -> dict:
        """Sync votes from LegiScan API."""
        legiscan_key = os.environ.get('LEGISCAN_API_KEY', '')
        if not legiscan_key:
            logger.error("LEGISCAN_API_KEY not set for vote sync")
            return stats

        from core.models_government import RollCallVote, VotePosition, CongressMember, Bill

        # Get master list of sessions
        try:
            resp = requests.get(
                "https://api.legiscan.com/",
                params={'key': legiscan_key, 'op': 'getSessionList', 'state': 'US'},
                timeout=30,
            )
            resp.raise_for_status()
            sessions_data = resp.json()
            sessions = sessions_data.get('sessions', {}).get('session', [])
            if not sessions:
                logger.warning("No LegiScan sessions found for US")
                return stats

            # Get most recent session
            latest = sessions[0] if isinstance(sessions, list) else sessions
            session_id = latest.get('session_id')
            logger.info(f"Using LegiScan session {session_id}: {latest.get('session_name')}")

        except Exception as e:
            logger.error(f"Error fetching LegiScan sessions: {e}")
            return stats

        # Get roll calls for bills in this session
        # LegiScan requires fetching roll calls per-bill, so we'll iterate
        # over bills that have roll_call_id in their data
        bills_with_votes = Bill.objects.filter(
            legiscan_bill_id__isnull=False,
            jurisdiction='federal',
        ).values_list('legiscan_bill_id', 'bill_uid')

        for legiscan_id, bill_uid in bills_with_votes[:50]:  # limit to 50 per run
            try:
                time.sleep(self.rate_limit)
                resp = requests.get(
                    "https://api.legiscan.com/",
                    params={
                        'key': legiscan_key,
                        'op': 'getBill',
                        'id': legiscan_id,
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                bill_data = resp.json().get('bill', {})

                votes = bill_data.get('votes', [])
                if not votes:
                    continue

                bill_obj = Bill.objects.filter(bill_uid=bill_uid).first()

                for vote in votes:
                    roll_call_id = vote.get('roll_call_id')
                    if not roll_call_id:
                        continue

                    # Fetch individual roll call
                    time.sleep(self.rate_limit)
                    rc_resp = requests.get(
                        "https://api.legiscan.com/",
                        params={
                            'key': legiscan_key,
                            'op': 'getRollCall',
                            'id': roll_call_id,
                        },
                        timeout=30,
                    )
                    rc_resp.raise_for_status()
                    rc_data = rc_resp.json().get('roll_call', {})

                    if not rc_data:
                        continue

                    vote_date = self._parse_date(rc_data.get('date'))
                    rc_chamber = 'senate' if 'Senate' in rc_data.get('chamber', '') else 'house'

                    rc_obj, created = RollCallVote.objects.update_or_create(
                        congress=congress,
                        chamber=rc_chamber,
                        roll_number=roll_call_id,
                        session=1,
                        defaults={
                            'date': vote_date or timezone.now().date(),
                            'question': rc_data.get('desc', ''),
                            'result': 'Passed' if rc_data.get('passed') else 'Failed',
                            'bill': bill_obj,
                            'yea_count': rc_data.get('yea', 0),
                            'nay_count': rc_data.get('nay', 0),
                            'not_voting_count': rc_data.get('nv', 0),
                            'present_count': rc_data.get('absent', 0),
                            'last_fetched_at': timezone.now(),
                        },
                    )
                    stats['votes_created' if created else 'votes_updated'] += 1

                    # Sync individual vote positions
                    for person_vote in rc_data.get('votes', []):
                        people_id = person_vote.get('people_id')
                        vote_text = person_vote.get('vote_text', '')

                        # Map LegiScan vote_text to our position
                        position_map = {
                            'Yea': 'Yea', 'Aye': 'Yea',
                            'Nay': 'Nay', 'No': 'Nay',
                            'NV': 'Not Voting', 'Not Voting': 'Not Voting',
                            'Absent': 'Not Voting',
                            'Present': 'Present',
                        }
                        position = position_map.get(vote_text, 'Not Voting')

                        # Try to match member by name (LegiScan uses people_id, not bioguide)
                        person_name = person_vote.get('name', '')
                        if not person_name:
                            continue

                        # Best-effort match to CongressMember
                        last_name = person_name.split()[-1] if person_name else ''
                        member = CongressMember.objects.filter(
                            last_name__iexact=last_name,
                            chamber=rc_chamber,
                        ).first()

                        if member:
                            VotePosition.objects.update_or_create(
                                roll_call=rc_obj,
                                member=member,
                                defaults={'position': position},
                            )
                            stats['positions_created'] += 1

            except Exception as e:
                logger.warning(f"Error syncing votes for bill {legiscan_id}: {e}")
                stats['errors'] += 1

        return stats

    # ─── Embeddings ──────────────────────────────────────────

    def embed_bills(self, batch_size: int = 50) -> Dict:
        """Generate embeddings for bills that need them."""
        from core.models_government import Bill

        stats = {'embedded': 0, 'skipped': 0, 'errors': 0}

        # Find bills needing embedding (no embedding or content changed)
        bills = Bill.objects.filter(embedding__isnull=True).exclude(embedding_text='')[:batch_size]

        if not bills.exists():
            # Also check for content hash changes
            for bill in Bill.objects.exclude(embedding_text='').exclude(embedding__isnull=True)[:batch_size]:
                old_hash = bill.content_hash
                bill.build_embedding_text()
                new_hash = hashlib.sha256(' '.join(bill.embedding_text.split()).encode()).hexdigest()
                if old_hash != new_hash:
                    bill.content_hash = new_hash
                    bill.embedding = None  # force re-embed
                    bill.save(update_fields=['embedding_text', 'content_hash', 'embedding'])
                    stats['skipped'] += 1  # will be picked up next run

            if stats['skipped'] == 0:
                logger.info("All bills already embedded and up to date")
            return stats

        # Batch embed
        texts = []
        bill_ids = []
        for bill in bills:
            if not bill.embedding_text:
                bill.build_embedding_text()
                bill.compute_content_hash()
                bill.save(update_fields=['embedding_text', 'content_hash'])

            texts.append(bill.embedding_text)
            bill_ids.append(bill.pk)

        if not texts:
            return stats

        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small",
            )

            for i, emb_data in enumerate(response.data):
                try:
                    Bill.objects.filter(pk=bill_ids[i]).update(
                        embedding=emb_data.embedding,
                    )
                    stats['embedded'] += 1
                except Exception as e:
                    logger.warning(f"Error saving embedding for bill {bill_ids[i]}: {e}")
                    stats['errors'] += 1

        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            stats['errors'] += len(texts)

        logger.info(f"Bill embeddings: {stats}")
        return stats

    # ─── Full Sync ───────────────────────────────────────────

    def full_sync(self) -> Dict:
        """Run complete sync: members → bills → votes → embeddings."""
        results = {}

        logger.info("Starting full Congress sync")

        # 1. Members
        results['members'] = self.sync_members()
        logger.info(f"Members: {results['members']}")

        # 2. Migrate existing bills from SpiderData
        results['bills'] = self.migrate_spider_bills()
        logger.info(f"Bills: {results['bills']}")

        # 3. Embed bills
        results['embeddings'] = self.embed_bills()
        logger.info(f"Embeddings: {results['embeddings']}")

        # 4. Votes (limited per run to avoid API exhaustion)
        results['votes_house'] = self.sync_votes(chamber='house')
        results['votes_senate'] = self.sync_votes(chamber='senate')

        results['api_calls'] = self.calls
        logger.info(f"Full Congress sync complete: {results}")
        return results
