#!/usr/bin/env npx tsx
/**
 * API Contract Test Suite
 *
 * Validates that all mobile API endpoints return data matching the expected
 * zod schemas. Run against Railway prod:
 *
 *   API_BASE=https://donkey-betz-platform-production.up.railway.app/api \
 *   API_USER=Donkeyking API_PASS=<password> \
 *   npx tsx scripts/contract-test.ts
 *
 * Or with an existing token:
 *   API_BASE=... API_TOKEN=<token> npx tsx scripts/contract-test.ts
 */

import { z } from 'zod';

// ── Config ──────────────────────────────────────────────────────────────────

const API_BASE = process.env.API_BASE ?? 'https://donkey-betz-platform-production.up.railway.app/api';
const API_TOKEN = process.env.API_TOKEN ?? '';
const API_USER = process.env.API_USER ?? '';
const API_PASS = process.env.API_PASS ?? '';

// ── Schemas (minimal expected shape for each endpoint) ──────────────────────

const schemas: Record<string, { method: 'GET' | 'POST'; path: string; schema: z.ZodType; body?: Record<string, unknown> }> = {
  // Dashboard
  'body/summary': {
    method: 'GET',
    path: '/body/summary/',
    schema: z.object({
      overall_health: z.string(),
      health_score: z.number(),
      healthy_systems: z.number(),
      total_systems: z.number(),
      systems: z.record(z.string(), z.unknown()),
    }).passthrough(),
  },
  'human/attention/stats': {
    method: 'GET',
    path: '/human/attention/stats/',
    schema: z.object({
      success: z.boolean(),
      stats: z.object({
        total_items: z.number(),
        pending_count: z.number(),
        by_urgency: z.object({
          critical: z.number(),
          high: z.number(),
          medium: z.number(),
          low: z.number(),
        }).passthrough(),
      }).passthrough(),
    }).passthrough(),
  },
  'boardroom/governance-stats': {
    method: 'GET',
    path: '/boardroom/governance-stats/',
    schema: z.object({
      success: z.boolean(),
      stats: z.object({}).passthrough(),
    }).passthrough(),
  },
  'initiatives/list': {
    method: 'GET',
    path: '/initiatives/?limit=5',
    schema: z.object({
      initiatives: z.array(z.object({ id: z.string() }).passthrough()),
    }).passthrough(),
  },
  'recent-activity': {
    method: 'GET',
    path: '/recent-activity/',
    schema: z.object({
      activities: z.array(z.unknown()),
    }).passthrough(),
  },
  'dashboard/stats': {
    method: 'GET',
    path: '/dashboard/stats/',
    schema: z.object({
      active_agents: z.number(),
    }).passthrough(),
  },

  // Boardroom
  'human/attention/list': {
    method: 'GET',
    path: '/human/attention/',
    schema: z.object({
      items: z.array(z.unknown()),
    }).passthrough(),
  },
  'boardroom/decisions': {
    method: 'GET',
    path: '/boardroom/decisions/',
    schema: z.object({
      decisions: z.array(z.unknown()),
    }).passthrough(),
  },

  // Governance
  'artifacts/needs-classification': {
    method: 'GET',
    path: '/artifacts/needs-classification/',
    schema: z.object({
      artifacts: z.array(z.unknown()),
    }).passthrough(),
  },
  'pilot-gates': {
    method: 'GET',
    path: '/pilot-gates/',
    schema: z.object({
      gates: z.array(z.unknown()),
    }).passthrough(),
  },

  // Workspace
  'workspaces': {
    method: 'GET',
    path: '/workspaces/',
    schema: z.object({}).passthrough(),
  },
  'workspace-operations': {
    method: 'GET',
    path: '/workspace-operations/',
    schema: z.object({}).passthrough(),
  },

  // Deliberation
  'deliberation/failure-stats': {
    method: 'GET',
    path: '/deliberation/failure-stats/',
    schema: z.object({
      total_sessions: z.number(),
      total_failed: z.number(),
      failure_rate: z.number(),
    }).passthrough(),
  },
  'deliberation/sessions': {
    method: 'GET',
    path: '/deliberation/sessions/',
    schema: z.object({
      sessions: z.array(z.unknown()),
    }).passthrough(),
  },

  // Agents
  'agents/list': {
    method: 'GET',
    path: '/agents/',
    schema: z.union([
      z.object({ agents: z.array(z.unknown()) }).passthrough(),
      z.array(z.unknown()),
    ]),
  },
  'agents/stats': {
    method: 'GET',
    path: '/agents/stats/',
    schema: z.object({}).passthrough(),
  },

  // Media
  'images/history': {
    method: 'GET',
    path: '/images/history/',
    schema: z.object({}).passthrough(),
  },

  // Manifest
  'app/manifest': {
    method: 'GET',
    path: '/app/manifest/',
    schema: z.object({
      routes: z.array(z.object({ path: z.string() }).passthrough()),
      user_role: z.string(),
    }).passthrough(),
  },

  // Auth
  'auth/validate-token': {
    method: 'POST',
    path: '/v1/auth/validate-token/',
    schema: z.object({
      valid: z.boolean(),
      user: z.object({
        id: z.string(),
        username: z.string(),
        platform_role: z.string(),
      }).passthrough(),
    }),
    body: {}, // token filled dynamically
  },
};

// ── Runner ──────────────────────────────────────────────────────────────────

interface TestResult {
  name: string;
  status: 'pass' | 'fail' | 'error';
  httpStatus?: number;
  issues?: string[];
  receivedKeys?: string[];
}

async function getToken(): Promise<string> {
  if (API_TOKEN) return API_TOKEN;

  if (!API_USER || !API_PASS) {
    console.error('Set API_TOKEN or (API_USER + API_PASS) environment variables');
    process.exit(1);
  }

  const res = await fetch(`${API_BASE}/v1/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: API_USER, password: API_PASS }),
  });

  if (!res.ok) {
    console.error(`Login failed: ${res.status} ${res.statusText}`);
    process.exit(1);
  }

  const data = await res.json();
  return data.token;
}

async function testEndpoint(
  name: string,
  config: typeof schemas[string],
  token: string,
): Promise<TestResult> {
  const url = `${API_BASE}${config.path}`;
  const headers: Record<string, string> = {
    Authorization: `Token ${token}`,
    'Content-Type': 'application/json',
  };

  try {
    let body: string | undefined;
    if (config.method === 'POST') {
      const payload = { ...config.body };
      if (name === 'auth/validate-token') {
        payload.token = token;
      }
      body = JSON.stringify(payload);
    }

    const res = await fetch(url, { method: config.method, headers, body });

    if (!res.ok) {
      return { name, status: 'fail', httpStatus: res.status, issues: [`HTTP ${res.status}`] };
    }

    const data = await res.json();
    const result = config.schema.safeParse(data);

    if (result.success) {
      return { name, status: 'pass', httpStatus: res.status };
    }

    const issues = result.error.issues.map(
      (i) => `${i.path.join('.') || '<root>'}: ${i.message}`,
    );
    const receivedKeys = typeof data === 'object' && data !== null ? Object.keys(data) : [];

    return { name, status: 'fail', httpStatus: res.status, issues, receivedKeys };
  } catch (err: any) {
    return { name, status: 'error', issues: [err.message ?? String(err)] };
  }
}

async function main() {
  console.log(`\n  API Contract Test Suite`);
  console.log(`  Target: ${API_BASE}\n`);

  const token = await getToken();
  console.log(`  Auth: Token ${token.slice(0, 8)}...`);
  console.log(`  Endpoints: ${Object.keys(schemas).length}\n`);

  const results: TestResult[] = [];
  const entries = Object.entries(schemas);

  for (const [name, config] of entries) {
    const result = await testEndpoint(name, config, token);
    results.push(result);

    const icon = result.status === 'pass' ? 'PASS' : result.status === 'fail' ? 'FAIL' : 'ERR ';
    const suffix = result.httpStatus ? ` (${result.httpStatus})` : '';
    console.log(`  [${icon}] ${name}${suffix}`);

    if (result.issues?.length) {
      for (const issue of result.issues.slice(0, 5)) {
        console.log(`         ${issue}`);
      }
      if (result.receivedKeys?.length) {
        console.log(`         keys: ${result.receivedKeys.join(', ')}`);
      }
    }
  }

  // Summary
  const passed = results.filter((r) => r.status === 'pass').length;
  const failed = results.filter((r) => r.status === 'fail').length;
  const errored = results.filter((r) => r.status === 'error').length;

  console.log(`\n  Results: ${passed} passed, ${failed} failed, ${errored} errors`);
  console.log(`  Total: ${results.length} endpoints\n`);

  if (failed > 0 || errored > 0) {
    process.exit(1);
  }
}

main();
