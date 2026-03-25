/**
 * Unit tests for useDeliverables helpers.
 *
 * Covers acceptance criteria:
 * AC#1 – default filter includes 'completed'
 * AC#2 – search for 'Bundled v3.1' returns id bfcd519c-ec40-4783-aa66-2abae620f215
 * AC#3 – ready-only filter still works
 * AC#4 – category filter does NOT implicitly exclude any category
 */

import { buildDeliverableParams, DEFAULT_STATUSES, fetchDeliverables } from '../useDeliverables';
import type { Deliverable } from '../useDeliverables';

// ---------------------------------------------------------------------------
// AC#1 – default statuses include 'completed'
// ---------------------------------------------------------------------------
describe('DEFAULT_STATUSES', () => {
  it('includes completed', () => {
    expect(DEFAULT_STATUSES).toContain('completed');
  });

  it('includes ready', () => {
    expect(DEFAULT_STATUSES).toContain('ready');
  });
});

// ---------------------------------------------------------------------------
// buildDeliverableParams
// ---------------------------------------------------------------------------
describe('buildDeliverableParams', () => {
  // AC#1
  it('includes both ready and completed in default status param', () => {
    const params = buildDeliverableParams({ status: ['ready', 'completed'] });
    const statuses = params['status'].split(',');
    expect(statuses).toContain('ready');
    expect(statuses).toContain('completed');
  });

  // AC#3 – ready-only filter
  it('produces status=ready when only ready is requested', () => {
    const params = buildDeliverableParams({ status: 'ready' });
    expect(params['status']).toBe('ready');
  });

  // AC#2 – search param is forwarded
  it('includes search term in params', () => {
    const params = buildDeliverableParams({
      status: ['ready', 'completed'],
      search: 'Bundled v3.1',
    });
    expect(params['search']).toBe('Bundled v3.1');
  });

  // AC#4 – category is passed through without implicit exclusions
  it('passes category as-is without transformation', () => {
    const params = buildDeliverableParams({
      status: ['ready', 'completed'],
      category: 'Platform Diagnostics',
    });
    expect(params['category']).toBe('Platform Diagnostics');
  });

  it('passes Patent Disclosures category through', () => {
    const params = buildDeliverableParams({
      category: 'Patent Disclosures',
    });
    expect(params['category']).toBe('Patent Disclosures');
  });

  it('omits status param when "all" is requested', () => {
    const params = buildDeliverableParams({ status: 'all' });
    expect(params['status']).toBeUndefined();
  });

  it('omits status param when no status given', () => {
    const params = buildDeliverableParams({});
    expect(params['status']).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// AC#2 – fetchDeliverables search integration (mocked fetch)
// ---------------------------------------------------------------------------
describe('fetchDeliverables', () => {
  const MOCK_DELIVERABLE: Deliverable = {
    id: 'bfcd519c-ec40-4783-aa66-2abae620f215',
    title: 'Bundled v3.1',
    status: 'completed',
    category: 'Platform Diagnostics',
    created_at: new Date().toISOString(),
  };

  beforeEach(() => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ results: [MOCK_DELIVERABLE] }),
    } as unknown as Response);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('returns completed deliverable matching Bundled v3.1 search', async () => {
    const results = await fetchDeliverables('/api/deliverables/', {
      search: 'Bundled v3.1',
    });

    // Verify fetch was called with correct params (status includes completed)
    const calledUrl = (global.fetch as jest.Mock).mock.calls[0][0] as string;
    expect(calledUrl).toContain('search=Bundled+v3.1');
    expect(calledUrl).toContain('completed');

    // Result contains the expected deliverable
    expect(results).toHaveLength(1);
    expect(results[0].id).toBe('bfcd519c-ec40-4783-aa66-2abae620f215');
  });

  it('throws on non-ok response', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    } as unknown as Response);

    await expect(fetchDeliverables('/api/deliverables/')).rejects.toThrow(
      'Deliverables API error: 500'
    );
  });
});
