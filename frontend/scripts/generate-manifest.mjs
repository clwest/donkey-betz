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
const apiDependencies = extractRecord(manifestSrc, 'API_DEPENDENCIES');

const manifest = {
  build_sha: gitSha,
  build_timestamp: new Date().toISOString(),
  env: process.env.NODE_ENV || 'production',
  route_count: routes.length,
  routes,
  studios,
  capabilities,
  api_dependencies: apiDependencies,
};

// ── Write to dist ───────────────────────────────────────────────────────────

if (!existsSync(DIST)) {
  console.warn('[generate-manifest] dist/ not found — skipping manifest generation.');
  process.exit(0);
}

const outPath = resolve(DIST, '__manifest.json');
writeFileSync(outPath, JSON.stringify(manifest, null, 2));
console.log(`[generate-manifest] Wrote ${outPath} (${routes.length} routes, sha=${gitSha})`);

// ── Sync core/templates/index.html to current dist bundle hashes ────────────
// Django TEMPLATES DIRS puts core/templates/ before frontend/dist/, so the
// template's <script src=…> + <link href=…> must be updated on every build
// or the browser loads stale bundles. Ships automatically as part of build.
// (S2948 NEW-4 close: replaces manual sync surfaced in S2947 close.)

try {
  const distIndexPath = resolve(DIST, 'index.html');
  const templatePath = resolve(ROOT, '..', 'core', 'templates', 'index.html');

  if (existsSync(distIndexPath) && existsSync(templatePath)) {
    const distHtml = readFileSync(distIndexPath, 'utf-8');
    const templateHtml = readFileSync(templatePath, 'utf-8');

    const scriptRe = /<script[^>]*src="\/static\/assets\/index-[^"]+\.js"[^>]*><\/script>/;
    const linkRe = /<link[^>]*href="\/static\/assets\/index-[^"]+\.css"[^>]*>/;

    // Vite config already writes /static/assets/ paths in dist/index.html.
    const distScript = distHtml.match(scriptRe)?.[0];
    const distLink = distHtml.match(linkRe)?.[0];

    if (distScript && distLink && scriptRe.test(templateHtml) && linkRe.test(templateHtml)) {
      const updated = templateHtml.replace(scriptRe, distScript).replace(linkRe, distLink);
      if (updated !== templateHtml) {
        writeFileSync(templatePath, updated);
        console.log(`[generate-manifest] Synced ${templatePath} to current dist hashes.`);
      } else {
        console.log('[generate-manifest] core/templates/index.html already matches dist — no sync needed.');
      }
    } else {
      console.warn('[generate-manifest] Could not locate script/link tags in dist or template — skipping template sync.');
    }
  }
} catch (err) {
  console.warn(`[generate-manifest] Template sync failed (non-fatal): ${err.message}`);
}
