#!/usr/bin/env node
/**
 * Postbuild script: reads appManifest.ts exports (via compiled JS) and
 * writes frontend/dist/__manifest.json with build metadata.
 *
 * Run automatically via `npm run build` (postbuild hook).
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');
const DIST = resolve(ROOT, 'dist');

// ── Parse manifest data from the TS source directly ─────────────────────────
// We read the TS file and extract the exported arrays/objects via regex
// rather than importing compiled JS, to avoid ESM/CJS headaches.

const manifestSrc = readFileSync(resolve(ROOT, 'src/appManifest.ts'), 'utf-8');

function extractArray(src, varName) {
  const re = new RegExp(`export const ${varName}[^=]*=\\s*(\\[)`, 's');
  const match = re.exec(src);
  if (!match) return [];
  const start = match.index + match[0].length - 1;
  let depth = 0;
  let i = start;
  for (; i < src.length; i++) {
    if (src[i] === '[') depth++;
    else if (src[i] === ']') { depth--; if (depth === 0) break; }
  }
  const raw = src.slice(start, i + 1);
  // Sanitise TS for JSON eval: strip type annotations, trailing commas, single-line comments
  const cleaned = raw
    .replace(/\/\/.*$/gm, '')                       // strip comments
    .replace(/(\w+)\s*:/g, '"$1":')                 // unquoted keys → quoted
    .replace(/'/g, '"')                              // single → double quotes
    .replace(/,\s*([\]}])/g, '$1')                   // trailing commas
    .replace(/"(category|studioType|roles)":\s*"([^"]+)"/g, '"$1":"$2"')  // keep as-is
    .replace(/as const/g, '');                        // strip TS

  try { return JSON.parse(cleaned); } catch { return []; }
}

function extractRecord(src, varName) {
  const re = new RegExp(`export const ${varName}[^=]*=\\s*(\\{)`, 's');
  const match = re.exec(src);
  if (!match) return {};
  const start = match.index + match[0].length - 1;
  let depth = 0;
  let i = start;
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) break; }
  }
  const raw = src.slice(start, i + 1);
  const cleaned = raw
    .replace(/\/\/.*$/gm, '')
    .replace(/(\w+)\s*:/g, '"$1":')
    .replace(/'/g, '"')
    .replace(/,\s*([\]}])/g, '$1')
    .replace(/as const/g, '');

  try { return JSON.parse(cleaned); } catch { return {}; }
}

// ── Build metadata ──────────────────────────────────────────────────────────

let gitSha = 'unknown';
try {
  gitSha = execSync('git rev-parse --short HEAD', { encoding: 'utf-8' }).trim();
} catch { /* not a git repo */ }

const routes = extractArray(manifestSrc, 'APP_ROUTES');
const studios = extractRecord(manifestSrc, 'STUDIO_CONFIG');
const capabilities = extractRecord(manifestSrc, 'APP_CAPABILITIES');

const manifest = {
  build_sha: gitSha,
  build_timestamp: new Date().toISOString(),
  env: process.env.NODE_ENV || 'production',
  route_count: routes.length,
  routes,
  studios,
  capabilities,
};

// ── Write to dist ───────────────────────────────────────────────────────────

if (!existsSync(DIST)) {
  console.warn('[generate-manifest] dist/ not found — skipping manifest generation.');
  process.exit(0);
}

const outPath = resolve(DIST, '__manifest.json');
writeFileSync(outPath, JSON.stringify(manifest, null, 2));
console.log(`[generate-manifest] Wrote ${outPath} (${routes.length} routes, sha=${gitSha})`);
