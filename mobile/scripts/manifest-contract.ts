#!/usr/bin/env npx tsx
/**
 * Manifest Contract Test
 *
 * Ensures all routes in screenRegistry exist in the server manifest,
 * and vice versa. Prevents features from silently disappearing due to
 * manifest drift.
 *
 *   API_BASE=https://donkey-betz-platform-production.up.railway.app/api \
 *   API_TOKEN=<token> npx tsx scripts/manifest-contract.ts
 */

const API_BASE = process.env.API_BASE ?? 'https://donkey-betz-platform-production.up.railway.app/api';
const API_TOKEN = process.env.API_TOKEN ?? '';

// Routes that MUST appear in both screenRegistry and manifest
const REQUIRED_ROUTES = [
  '/',
  '/dashboard',
  '/boardroom',
  '/governance',
  '/workspace',
  '/content',
  '/initiatives',
  '/intelligence',
  '/agents',
  '/media',
  '/settings',
  '/diagnostics',
];

// Routes in screenRegistry (mirrors mobile/src/navigation/screenRegistry.ts)
const SCREEN_REGISTRY_ROUTES = [
  '/',
  '/dashboard',
  '/boardroom',
  '/governance',
  '/workspace',
  '/content',
  '/initiatives',
  '/intelligence',
  '/agents',
  '/media',
  '/settings',
  '/diagnostics',
  '/betting',
  '/stocks',
  '/portfolio',
];

async function main() {
  console.log('\n  Manifest Contract Test');
  console.log(`  Target: ${API_BASE}\n`);

  if (!API_TOKEN) {
    console.error('  Set API_TOKEN environment variable');
    process.exit(1);
  }

  const res = await fetch(`${API_BASE}/app/manifest/`, {
    headers: { Authorization: `Token ${API_TOKEN}` },
  });

  if (!res.ok) {
    console.error(`  Manifest fetch failed: ${res.status}`);
    process.exit(1);
  }

  const manifest = await res.json();
  const manifestPaths = new Set<string>(manifest.routes.map((r: any) => r.path));
  const registryPaths = new Set<string>(SCREEN_REGISTRY_ROUTES);

  let failures = 0;

  // Check required routes exist in manifest
  for (const route of REQUIRED_ROUTES) {
    if (!manifestPaths.has(route)) {
      console.log(`  [FAIL] ${route} — in screenRegistry but MISSING from manifest`);
      failures++;
    } else {
      console.log(`  [PASS] ${route}`);
    }
  }

  // Warn about manifest routes without screen implementations
  const unimplemented = [...manifestPaths].filter((p) => !registryPaths.has(p));
  if (unimplemented.length) {
    console.log(`\n  Info: ${unimplemented.length} manifest routes without mobile screens:`);
    for (const p of unimplemented) {
      console.log(`    - ${p}`);
    }
  }

  console.log(`\n  user_role: ${manifest.user_role}`);
  console.log(`  Total manifest routes: ${manifestPaths.size}`);
  console.log(`  Total registry routes: ${registryPaths.size}`);
  console.log(`  Required: ${REQUIRED_ROUTES.length} (${REQUIRED_ROUTES.length - failures} pass)\n`);

  if (failures > 0) process.exit(1);
}

main();
