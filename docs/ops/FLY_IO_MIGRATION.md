---
title: "Fly.io Migration Plan — u-d-b backend (Session 1116)"
date: 2026-05-20
status: draft
audience: Jessica (deployment owner)
companion_config: fly.toml
---

# Fly.io Migration Plan — u-d-b backend

> **For Jessica.** Step-by-step runbook to migrate the unified-donkey-betz
> backend from Railway → Fly.io. Nothing in this doc has been executed —
> it's a pre-built plan. Run each step in order, verify before proceeding
> to the next. The companion `fly.toml` at the repo root is the locked
> starting config.

---

## 1. Pre-flight checklist

- [ ] `flyctl` installed: `brew install flyctl` (macOS) or `curl -L https://fly.io/install.sh | sh`
- [ ] Fly.io account created with payment method on file (free allowance applies, but Fly requires a card)
- [ ] `flyctl auth login` — opens browser, completes auth
- [ ] GitHub already connected to Fly.io (you did this — auto-deploy will be available later)
- [ ] Railway dashboard open in another tab — you'll need it for env var copy-paste + DB dump
- [ ] Decide on app name (suggestion: `udb-backend` or `donkey-betz-backend`). Used in `fly.toml` and all subsequent commands.

**Budget expectation:** ~$30-40/mo total at the sizes in `fly.toml`, before Fly's monthly free allowance (~$5 credit). Real net cost: ~$25-35/mo. See § 8 for line-item breakdown.

---

## 2. Create the app shell (no deploy yet)

From the repo root with `fly.toml` present:

```bash
# Pick a name when prompted; the `fly.toml` in repo will be copied as the starting config.
flyctl launch --copy-config --no-deploy --name udb-backend

# Confirm:
flyctl status -a udb-backend
```

This creates the Fly.io app but does NOT build/deploy yet. Don't deploy until secrets + Postgres + Redis are wired (next two sections).

---

## 3. Provision managed Postgres + Redis

### 3.1 Postgres

```bash
flyctl postgres create \
  --name udb-db \
  --region ord \
  --vm-size shared-cpu-1x \
  --initial-cluster-size 1 \
  --volume-size 10
```

When prompted for plan, choose **"Development"** (1 node, 256MB VM). Upgrade later if/when load demands.

**Attach to the app:**

```bash
flyctl postgres attach udb-db -a udb-backend
```

This auto-sets `DATABASE_URL` as a secret on the app. Verify:

```bash
flyctl secrets list -a udb-backend | grep DATABASE_URL
```

### 3.2 pgvector extension

u-d-b depends on `pgvector` (570+ models, embedding-backed RAG, signal aggregation). Fly Postgres ships with the extension available but not enabled. Enable it:

```bash
flyctl postgres connect -a udb-db
# In the psql prompt:
\c udb_backend       # or the db name shown when attach completed
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

Confirm by reconnecting and running `\dx vector`.

### 3.3 Redis

Two paths — pick one:

**Option A: Fly Redis (Upstash-backed, easiest)**

```bash
flyctl redis create \
  --name udb-redis \
  --region ord \
  --no-replicas \
  --plan free
```

Free plan: 100MB, 10k commands/day. **Probably insufficient for u-d-b's beat schedule** (258 enabled PeriodicTask rows firing constantly). Upgrade to "Pay-as-you-go" ($10 minimum) if you hit the command cap.

Set the URL:

```bash
flyctl redis status udb-redis  # copy the private connection URL
flyctl secrets set REDIS_URL='<the url>' -a udb-backend
```

**Option B: External Redis (Upstash direct, Render, or self-hosted)**

If Fly Redis's pricing isn't right, sign up at Upstash.com directly, create a free 256MB instance, and:

```bash
flyctl secrets set REDIS_URL='<external url>' -a udb-backend
```

u-d-b uses Redis for 3 things: Celery broker, Channels layer, cache. All can share one instance — `core/settings.py` reads `REDIS_URL` and partitions to 3 DB indices.

---

## 4. Set secrets

The full list u-d-b expects, with where to get each. Copy from your Railway dashboard (Variables tab) and paste into the `flyctl secrets set` command.

### 4.1 Required for the app to boot

```bash
flyctl secrets set \
  SECRET_KEY='<copy from Railway>' \
  ALLOWED_HOSTS='udb-backend.fly.dev,donkey-betz-platform-production.up.railway.app' \
  DEBUG='False' \
  -a udb-backend
```

> **Note:** Keep the Railway hostname in `ALLOWED_HOSTS` during the cutover window so traffic can flow either direction.

### 4.2 Public intelligence + changelog endpoints (Session 1116)

```bash
flyctl secrets set \
  PUBLIC_INTEL_TOKEN='<generate fresh: openssl rand -hex 16>' \
  -a udb-backend
```

> After setting, **share this token with the 24-7-ai-global Vercel env** (`UDB_PUBLIC_INTEL_TOKEN`) so `/now` and `/shipped` keep working. You can use the existing Railway token value if you want zero token rotation.

### 4.3 LLM provider keys (copy from Railway, paste as a single `secrets set` call)

```bash
flyctl secrets set \
  OPENAI_API_KEY='<copy from Railway>' \
  ANTHROPIC_API_KEY='<copy from Railway>' \
  TOGETHER_API_KEY='<copy from Railway>' \
  DEEPSEEK_API_KEY='<copy from Railway>' \
  GEMINI_API_KEY='<copy from Railway>' \
  -a udb-backend
```

### 4.4 Media + integrations

```bash
flyctl secrets set \
  CLOUDINARY_URL='<copy from Railway>' \
  ELEVENLABS_API_KEY='<copy from Railway>' \
  STABILITY_API_KEY='<copy from Railway>' \
  RUNWAY_API_KEY='<copy from Railway>' \
  REPLICATE_API_TOKEN='<copy from Railway>' \
  DISCORD_BOT_TOKEN='<copy from Railway>' \
  -a udb-backend
```

### 4.5 Anything else Railway uses

Run this on Railway to see what's there:

```bash
railway variables --json | jq 'keys'
```

Anything in that list NOT already set above should be added. Common candidates: `STRIPE_*`, `SENTRY_DSN`, `RESOLVE_NODE_URL`, `RENDER_NODE_TOKEN`.

**Verify:**

```bash
flyctl secrets list -a udb-backend
```

---

## 5. Migrate the database (Railway PG → Fly PG)

### 5.1 Dump from Railway

```bash
# Get Railway DB URL
railway variables --json | jq -r '.DATABASE_URL'

# Or via the dashboard → Postgres → Connect → "Postgres Connection URL"

# Dump (writes to local file)
pg_dump '<railway-db-url>' \
  --no-owner --no-acl --clean --if-exists \
  -Fc -f udb-railway-backup.dump
```

`.dump` will be ~50-500MB depending on data volume. **Inspect** before restoring:

```bash
ls -lh udb-railway-backup.dump
```

### 5.2 Restore to Fly Postgres

```bash
# Open a proxy to Fly Postgres on localhost
flyctl proxy 5433:5432 -a udb-db &
PROXY_PID=$!

# Find the Fly PG password
flyctl secrets list -a udb-db   # not always accessible
# OR: flyctl postgres connect -a udb-db, then `\du` and copy connection params

# Restore (replace <password> + <dbname>)
pg_restore \
  --no-owner --no-acl --clean --if-exists \
  --host=localhost --port=5433 \
  --username=postgres \
  --dbname='<dbname from attach output>' \
  udb-railway-backup.dump

kill $PROXY_PID
```

### 5.3 Verify row counts

```bash
flyctl postgres connect -a udb-db
\c <dbname>
SELECT 'core_signalcluster', count(*) FROM core_signalcluster
UNION ALL SELECT 'core_deliverables', count(*) FROM core_deliverables
UNION ALL SELECT 'core_workspace', count(*) FROM core_workspace
UNION ALL SELECT 'auth_user', count(*) FROM auth_user;
```

Compare against Railway counts (run the same query against `railway run psql`).

---

## 6. First deploy

```bash
# Build the production image (multi-stage Dockerfile — must target 'production')
flyctl deploy --build-target production --remote-only -a udb-backend
```

`--remote-only` builds on Fly's builder (faster than local Docker on M1 macs). First build is ~10-15 min because dependencies install fresh.

### 6.1 Watch the deploy

```bash
# In another terminal
flyctl logs -a udb-backend
```

Watch for:
- `release_command` running migrations cleanly
- All 9 process groups starting their VMs
- Web responding to `https://udb-backend.fly.dev/api/health/` (if that endpoint exists; otherwise hit `/`)
- Celery workers logging `celery@... ready.`
- Beat logging `Scheduler: Sending due task`

### 6.2 First-deploy verification

```bash
# 1. Web is up
curl -i https://udb-backend.fly.dev/

# 2. Token-gated endpoint rejects without token
curl -i https://udb-backend.fly.dev/api/public/intelligence/now/
# Expect: 401

# 3. Token-gated endpoint works with token
curl -i -H "X-Intel-Token: <PUBLIC_INTEL_TOKEN>" \
  https://udb-backend.fly.dev/api/public/intelligence/now/
# Expect: 200 + JSON

# 4. Beat is scheduling
flyctl logs -a udb-backend --instance beat -n 100 | grep "Scheduler"

# 5. Workers are accepting tasks
flyctl ssh console -a udb-backend --process-group worker
# In container:
celery -A core inspect active
# Expect: a list of active workers, no errors
exit
```

---

## 7. Scale + cutover

### 7.1 Match Railway's worker count

The Procfile runs **2 instances** of `celery-long-running`. Fly's default is 1 per process group — scale:

```bash
flyctl scale count long_running=2 -a udb-backend
```

Verify: `flyctl status -a udb-backend` should show 2 `long_running` machines.

### 7.2 Update 24-7-ai-global Vercel env

Once Fly.io's `/api/public/intelligence/now/` works (step 6.2 #3), point Vercel at it:

In Vercel dashboard, project 24-7-ai-global, Settings → Environment Variables:
- `UDB_API_URL` → change from `https://donkey-betz-platform-production.up.railway.app` to `https://udb-backend.fly.dev`
- `UDB_PUBLIC_INTEL_TOKEN` → keep the same value (matches Fly's `PUBLIC_INTEL_TOKEN`)

Redeploy 24-7-ai-global. Visit `/now` and `/shipped` — they should now pull from Fly.

### 7.3 DNS cutover (optional, do later)

If you have a custom domain pointing at Railway:

```bash
flyctl certs add api.247globalai.com -a udb-backend
# Follow the CNAME / A record instructions Fly prints
```

Wait for DNS to propagate (10 min to 24h). Then turn off Railway services.

### 7.4 Auto-deploy from GitHub

You already connected GitHub to Fly. Inside the Fly dashboard for `udb-backend`:
- Settings → GitHub → enable auto-deploy from `main`
- Recommended: enable only AFTER the first manual deploy has succeeded so a broken deploy doesn't lock you out of the dashboard.

---

## 8. Cost estimate (rough, recheck against Fly's calculator before launch)

| Resource | Size | Approx monthly |
|---|---|---|
| `web` machine | shared-cpu-1x, 1024MB | ~$5.70 |
| `worker` machine | shared-cpu-1x, 512MB | ~$3.89 |
| `pa` machine | shared-cpu-1x, 512MB | ~$3.89 |
| `content` machine | shared-cpu-1x, 512MB | ~$3.89 |
| `long_running` machines × 2 | shared-cpu-1x, 512MB | ~$7.78 |
| `broadcast` machine | shared-cpu-1x, 512MB | ~$3.89 |
| `beat` machine | shared-cpu-1x, 256MB | ~$1.94 |
| `code_worker` machine | shared-cpu-2x, 1024MB | ~$15 |
| `resolve` machine | shared-cpu-1x, 256MB | ~$1.94 |
| Fly Postgres (Development) | shared-cpu-1x, 10GB volume | ~$1.94 + storage |
| Fly Redis (free → pay-as-you-go) | 100MB free OR ~$10/mo | $0-10 |
| **Subtotal** | | **~$50-65/mo gross** |
| Fly monthly free allowance | | **-$5** |
| **Net estimated** | | **~$45-60/mo** |

This is **higher than my $30-40 earlier estimate** because `code_worker` is a shared-cpu-2x and we're running long_running × 2. If budget is tight:

- Drop `code_worker` to 512MB and use `--max-tasks-per-child=1` (already the case) — save $10/mo
- Run `long_running` at count=1 instead of 2 — save $4/mo
- Drop `broadcast` and merge into `worker` (single threaded process) — save $4/mo

Best-case lean config: ~$25-30/mo. Probably the right target for survival mode.

---

## 9. Rollback plan

If anything goes wrong post-cutover and you need to revert to Railway:

1. **DNS first:** revert the CNAME on `api.247globalai.com` back to Railway's `donkey-betz-platform-production.up.railway.app`.
2. **Vercel env:** revert `UDB_API_URL` to Railway URL, redeploy.
3. **Don't touch the data:** Fly Postgres still holds the migrated data; Railway Postgres still has the pre-cutover state. If you decide to stay on Railway, run any new migrations there, not on Fly.
4. **Leave the Fly app suspended** rather than deleted: `flyctl scale count <process>=0 -a udb-backend` for every process group. Stops billing, keeps the config + DB.

Rollback time: **<10 minutes** if DNS TTL is low (300s).

---

## 10. What this plan does NOT do

- **No data migration from Railway Redis to Fly Redis.** Redis is mostly transient state (Celery broker queue + cache); a clean cutover during low traffic is preferred.
- **No Cloudinary changes.** Media stays where it is. Both Railway and Fly point at the same Cloudinary account.
- **No Resolve Node hardware migration.** It runs in `MOCK_MODE=true` on Fly — full Resolve rendering still needs a real machine.
- **No deletion of the Railway environment.** Leave Railway running until Fly has been stable for at least 7 days. Switching back is much harder if Railway's been torn down.
- **No DNS automation.** Cutover is manual to give you the kill-switch.

---

## 11. Checklist (printable)

Pre-flight:
- [ ] flyctl installed + authed
- [ ] Payment method on Fly
- [ ] App name decided
- [ ] Railway DB URL accessible (for dump)
- [ ] PUBLIC_INTEL_TOKEN value handy (existing or fresh)

Provisioning:
- [ ] `flyctl launch --copy-config --no-deploy` succeeded
- [ ] Fly Postgres created + attached
- [ ] `CREATE EXTENSION vector` succeeded
- [ ] Fly Redis OR external Redis URL set as secret

Secrets:
- [ ] DATABASE_URL auto-set by postgres attach
- [ ] REDIS_URL set
- [ ] SECRET_KEY + DEBUG + ALLOWED_HOSTS set
- [ ] PUBLIC_INTEL_TOKEN set
- [ ] All 5 LLM keys set
- [ ] Cloudinary + media keys set
- [ ] Anything else from Railway variables

Migration:
- [ ] DB dumped from Railway
- [ ] DB restored to Fly
- [ ] Row counts verified

First deploy:
- [ ] `flyctl deploy --build-target production` succeeded
- [ ] All 9 process groups have machines running
- [ ] curl probe of `/api/public/intelligence/now/` returns 401 without token, 200 with
- [ ] Beat is scheduling tasks
- [ ] Workers are accepting tasks

Scale + cutover:
- [ ] `long_running` scaled to count=2
- [ ] Vercel `UDB_API_URL` updated
- [ ] 247globalai.com `/now` and `/shipped` working against Fly
- [ ] (Optional) DNS cutover for custom domain

Post-deploy:
- [ ] 24h observation window with both Railway + Fly running
- [ ] Auto-deploy from GitHub enabled (after first manual success)
- [ ] After 7 days stable: tear down Railway services

---

## 12. References

- `fly.toml` at repo root — the locked starting config
- `Procfile` — the source of truth for process commands
- `Dockerfile` — multi-stage, must target `production`
- `docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md` — context for the PUBLIC_INTEL_TOKEN env var
- `docs/handoffs/SESSION_1116_GLOBAL_AI_PIVOT_AND_LIVE_INTEL.md` — what landed before this migration
- Fly.io docs: https://fly.io/docs/apps/processes/
- Fly.io pricing: https://fly.io/docs/about/pricing/

---

**End of plan.** Ping me on any step that's surprising — the `fly.toml` numbers (memory sizes, counts) are educated guesses based on the Procfile annotations, not measurements on Fly's actual machines. Some tuning post-first-deploy is expected.
