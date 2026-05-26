---
title: "Discord bot — narrative (batch K)"
status: draft (batch K of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/DISCORD_AUDIT.md
  - docs/DISCORD_INTEGRATION.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to DISCORD_AUDIT.md DOC-AUTOGEN output + DISCORD_INTEGRATION.md command list + per-cog session attributions visible in cog docstrings)
provenance_note: Discord is a large utility subsystem — 11,676 lines in one file, 25 Cogs, 96 commands. Each cog's session attribution is visible in its class docstring. Counts anchored to PLATFORM_INVENTORY 2026-05-25 (git HEAD d513cd7f) and DISCORD_AUDIT.md DOC-AUTOGEN. 144 → 96 correction in Session 1115 (regex was double-counting slash commands).
---

# Discord bot

> A second user-facing surface alongside the web UI.
> Notifications, quick lookups, voice features, mobile-
> friendly actions, content-creation triggers, account
> management. Single file (`core/services/discord_bot.py`,
> 11,676 lines), 25 Cog classes, 96 commands (48 slash + 48
> prefix). Built incrementally across ~30 sessions; each
> Cog's originating session is visible in its docstring.

---

## 1. What this is

The Discord bot is the platform's second user surface. It
covers what works well in Discord and doesn't try to replicate
what works better in the web Workspace. Per
`DISCORD_INTEGRATION.md`:

**What Discord IS for:**
- Notifications (system alerts, agent dreams, spider
  summaries, market / blockchain alerts).
- Quick lookups (`/status`, `/ask`, `/agents`, `/trending`,
  `/profile`).
- Voice features (TTS, speech-to-text, voice cloning, voice
  chat — Discord's strength).
- Mobile-friendly actions (`/bet`, `/apply`, `/digest`,
  `/consult`).
- Content creation triggers (`/create`, `/podcast-create`,
  `/create-content`).
- Account management (`/link`, `/unlink`, `/subscribe`,
  `/tier`).

**What Discord is NOT for:**
- Complex multi-step workflows (use web Workspace).
- Content review / approval pipelines (use web Blog Viewer).
- System configuration (use web Admin / Settings).
- Deep data exploration (use web).
- Dashboard views (anything requiring charts, tables, rich
  visualization).

The bot is one file because Discord.py's Cog pattern works well
as a single module — splitting Cogs across files adds
ergonomic friction without gain. 25 Cogs in 11,676 lines means
~470 lines per Cog on average; the largest three
(`AgentAccessCommands` 10 commands, `SpiderCommands` 10
commands, `ContentCommands` 9 commands) are the ones the
audit doc flags as "worth knowing if you want to split for
clarity."

The bot is also where Session 1115's audit framework caught
a long-running count claim — `CLAUDE.md` said 144 commands;
AST-parsed reality is 96. The 144 figure came from a regex
that double-counted slash commands. The audit doc is now
DOC-AUTOGEN.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **`core/services/discord_bot.py`** | The single-file bot. 11,676 lines. 25 Cog classes. Lives in `core/services/` because it consumes platform services (agents, spiders, PA) rather than being its own subsystem. |
| **Cog** | Discord.py organizational unit. Each Cog groups related commands. 25 Cogs in this bot, each with a class docstring naming its originating session. |
| **Slash command (`/foo`)** | Discord's modern command shape. Visible in Discord's command picker UI. The `description=` argument is what shows up in the picker. Defined with `@app_commands.command` decorator. 48 in this bot. |
| **Prefix command (`!foo`)** | The older interaction style. Triggered by typing `!command`. Defined with `@*.command` decorator (where * is the Cog class). 48 in this bot — same count as slash, but different commands. Total = 96 distinct commands. |
| **`build_discord_audit`** | The mgmt command that regenerates `docs/DISCORD_AUDIT.md` (DOC-AUTOGEN — do not hand-edit). AST-parses `discord_bot.py` in place; no import side-effects. The fix for the 144 → 96 count drift was running this. |
| **Notification channels** | 12 Discord channels the bot pushes to. Covered in `core/services/discord_notifications.py` (2,273 lines). Includes agent dreams, spider summaries, market alerts, blockchain alerts, system alerts. |
| **Voice subsystem** | `core/services/discord_voice.py` (871 lines). TTS, speech-to-text, voice cloning, voice chat. The "Discord's strength" use case. |
| **`AgentAccessCommands` Cog** | The largest Cog (10 commands). Phase 5 — direct access to all agents, advisors, and workflows. Commands: `/advisors`, `/agent-list`, `/agent-task`, `/audit-contract`, `/blockchain-status`, `/consult`, `/voice-ask`, `/voice-chat`, `/workflow-list`, `/workflow-run`. |
| **`SpiderCommands` Cog** | Spider/trending-data access. 10 commands. |
| **`ContentCommands` Cog** | 9 commands (Session 430). Content, profile, opportunities. |
| **Reaction feedback (`ReactionFeedbackCog`)** | Session 452. Automatic feedback from Discord reactions. Zero commands — purely event-driven. Picks up emoji reactions on bot messages as quality signals. |
| **`RoleManager` Cog** | Session 439. Subscription role management. Zero commands — event-driven. Promotes Discord roles when a user subscribes. |
| **Session attribution per Cog** | Most Cogs have their originating session in the class docstring. e.g., `ContentCommands` says "Session 430"; `AgentAccessCommands` says "Phase 5"; `HumanInterfaceCommands` says "Session 686". |
| **DOC-AUTOGEN audit doc** | `docs/DISCORD_AUDIT.md` is regenerated by `build_discord_audit`. Never hand-edit. Source: AST parse of `discord_bot.py`. |
| **`HumanInterfaceCommands` (Session 686)** | 6 commands. The bot's surface for the Human Interface Layer — bidirectional human↔platform interaction shaped for Discord. |
| **`ReviewCommands` (Session 556)** | 5 commands. Chief of Staff Review Document Commands. The Discord-side surface for the review pipeline. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Foundation — initial Discord bot** *(pre-Session 427, Inferred)* | Discord bot exists. Initial Cogs likely include `StatusCommands` (1 command, line 552), `AgentCommands` (2 commands, line 618), `SpiderCommands` (10 commands, line 792). The bot established as a second user surface alongside the web UI. | The platform needed a notification + quick-lookup surface that was mobile-friendly. Email is too slow; web is too desktop-heavy. Discord is where users (Chris) already spend time. | Bot in production; basic commands work; notification channels wired. | **Active** — these foundational Cogs are still in the bot. | `core/services/discord_bot.py:552-1000` (StatusCommands, AgentCommands, SpiderCommands) |
| **Sessions 427–432 — Discord matures (Interactive + Content + Server Setup + Client Management)** | `InteractiveCommands` (Session 427) — 7 commands for interacting with AI agents. `ContentCommands` (Session 430) — 9 commands for content, profile, opportunities. `ServerSetupCommands` (Session 431) — 1 command for Server Setup Wizard. `ClientCommands` (Session 432) — 4 commands for Client Management (Phase 3). | The bot grew from "status + queries" to "do things." Content workflows, server onboarding, client management — each had a natural fit in Discord. The "Phase N" framing on Cog docstrings reflects the platform's broader phase taxonomy of that era. | Bot becomes interactive — users can drive content creation, manage onboarding, and handle client workflows from Discord. | **Active.** | `core/services/discord_bot.py` — `InteractiveCommands` (line 1976), `ContentCommands` (line 2685), `ServerSetupCommands` (line 5909), `ClientCommands` (line 6114) |
| **Sessions 438–445 — Voice + RoleManager + AI Series** | `VoiceCommands` (Session 438, Phase 8) — 4 commands. TTS, speech-to-text, voice clone, voice chat. `RoleManager` (Session 439) — 0 commands; event-driven subscription role promotion. `ContentPipelineCommands` (Session 440) — 2 commands for the content pipeline. `SeriesCommands` (Session 445) — 4 commands for AI Series Creation. | Voice was Discord's natural strength — the platform leaned into it. Subscription role management closed the "user subscribes → Discord role updates" loop. Content pipeline commands gave Discord users access to deliberation-pipeline triggers (cross-ref narrative B). AI Series gave them multi-episode content creation. | The bot's audio + content surfaces are now first-class. Voice features become the highest-value Discord-specific capability. | **Active.** | Cogs at lines 3796, 4264, 4487, 4633 |
| **Sessions 452 + 466 + 480 — Reactions + Autonomous Studio + 19 Situations** | `ReactionFeedbackCog` (Session 452) — 0 commands; auto-feedback from Discord reactions on bot messages. The platform's first explicit feedback signal from Discord. `StudioCommands` (Session 466) — 7 commands for the Autonomous Content Studio. `SituationCommands` (Session 480) — 4 commands for all 19 Autonomous Situations. | The platform was building autonomy (agents acting without user prompts); Discord needed surfaces to monitor and trigger autonomous behavior. Reaction feedback closed the loop between bot output and user judgment without requiring explicit `/feedback` commands. | Bot becomes a window into autonomous platform behavior. Users can react to suggest quality; commands can trigger autonomous-system flows. | **Active.** | Cogs at lines 8305 (Reactions), 5098 (Studio), 9006 (Situations) |
| **Sessions 487–497 — Specialty cogs (Gumroad + Podcast + Resolve + ML + Legal + Developer + Help)** | `GumroadCommands` (Session 487) — 1 command for Gumroad Publishing. `PodcastCommands` (Session 496) — 4 commands for AI Podcast Studio. `LegalCommands` (Session 497) — 3 commands for Pro Se Legal Assistant. `MLScoringCommands` (Session 497) — 1 command for ML Scoring Status. `DeveloperCommands` (Session 497) — 2 commands for Code Generation and Review. `ResolveCommands` — 5 commands for DaVinci Resolve professional rendering. `HelpCommands` (likely earlier than 497) — 1 command for help. | Each Cog covered a vertical that justified a Discord surface. Gumroad for one-button publishing; Podcast for studio commands; Legal for the Pro Se assistant; ML scoring for status; Developer for code work. Pattern: small Cogs (1–5 commands) covering specific verticals. | The bot covers most platform verticals. The "small per-Cog command count" is intentional — verticals are surfaced but not deeply duplicated from web. | **Active.** | Cogs at lines 5772, 9776, 10143, 10573, 10381, 8470, 8047 |
| **Sessions 556 + 686 — Chief of Staff Review + Human Interface** | `ReviewCommands` (Session 556) — 5 commands for Chief of Staff Review Documents. `HumanInterfaceCommands` (Session 686) — 6 commands for the Human Interface Layer. | Two distinct human-in-the-loop surfaces: Chief of Staff Review for deliverable approval flow; Human Interface Layer for bidirectional human↔platform shaped for Discord. Both reflect the platform's maturing governance / decision layers (cross-ref narrative J). | The Discord side of governance + human-loop interaction is in place. Cross-refs to Decision Command and Human Interface narratives. | **Active.** | Cogs at lines 10678, 11026 |
| **Session 1115 — count correction (144 → 96) + audit DOC-AUTOGEN** | Long-standing claim `CLAUDE.md`: "144 total commands" was wrong. AST parsing of `discord_bot.py` produced 96 (48 slash + 48 prefix). The 144 figure came from a regex that double-counted slash commands (counting them once as `@app_commands.command` and again as `@*.command`). `build_discord_audit` mgmt command introduced; `docs/DISCORD_AUDIT.md` became DOC-AUTOGEN. Verifier guard added to flag drift between runtime count and doc claims. | The Discord audit doc was claiming an inflated count for months. The Session 1099 verifier framework caught it; Session 1115's audit sweep introduced the AST-parsing mgmt command that produces the authoritative count. | Count drift closed structurally — the audit doc is regenerated by running the command. Hand-edited claims are flagged by `verify_doc_claims --only-drift`. | **Active** — `docs/DISCORD_AUDIT.md` is DOC-AUTOGEN. Regenerate with `python manage.py build_discord_audit`. | `docs/DISCORD_AUDIT.md` (DOC-AUTOGEN header); `docs/handoffs/SESSION_1115_CONTEXT_KIT_DRIFT_CLEANUP.md`; `core/management/commands/build_discord_audit.py` |

---

## 4. What came of it

### Wins

- **Second user surface that fits its strengths.**
  Notifications + quick lookups + voice + mobile actions
  are Discord's good cases. The bot leans into them and
  explicitly doesn't try to be the web UI on Discord.
- **One file, AST-parseable.** 11,676 lines but the
  audit doc covers every command via AST parse — counts
  and per-command details are runtime-derivable. No "let
  me grep the file" needed.
- **DOC-AUTOGEN catches drift.** Session 1115's 144 → 96
  correction was a real bug in the docs; the AST-parse
  audit + verifier guard make recurrence structurally
  unlikely.
- **Voice is the strongest Discord-specific feature.**
  TTS, speech-to-text, voice clone, voice chat all
  exist. Discord's voice channel infrastructure is far
  better than web; the bot exploits it.
- **Reaction feedback (Session 452) closes a loop.**
  Users react with emojis; the bot picks up the signal
  as quality data without requiring explicit `/feedback`
  commands.
- **Session attribution in Cog docstrings.** Every Cog
  names its originating session. Tracing "when did this
  command get added?" is one grep away.
- **Discord-vs-web boundaries are explicit.**
  `DISCORD_INTEGRATION.md` says what the bot is for and
  isn't for. Operators don't have to guess.

### Tradeoffs

- **One 11,676-line file.** Audit findings flag the three
  largest Cogs (10, 10, 9 commands) as candidates for
  splitting. Not done yet; the file is unwieldy for
  newcomers.
- **Two command styles (slash + prefix).** 48 + 48 = 96.
  Some commands have only slash, some only prefix.
  Users have to know which mode each command supports.
- **Limited frontend reflection.** Discord users don't see
  what's happening in the web UI for the same workflow.
  No "you triggered this from Discord; check your web
  dashboard for the full result" link in most flows.
- **Notification volume.** 12 channels can produce a lot
  of traffic. Anti-spam rails (covered in narrative A
  milestone 7) apply to platform-side dispatch, but the
  Discord channels themselves don't have rate caps.
- **`AgentAccessCommands` includes `/consult` "Consult a
  legendary advisor"** — pre-Session 1142 framing leaked
  through. After the advisor rename (narrative I
  milestone 4), this command's description should say
  "Consult a domain specialist." Drift not yet caught.
- **Cog count drift between docs.** `CLAUDE.md` says 25
  Cogs; `DISCORD_INTEGRATION.md` says 25; both match.
  Command count: AUDIT 96, INTEGRATION says 144 in
  outdated text. Two-doc consistency requires a
  cross-doc pass.

### Follow-on systems enabled

- **Voice + advisor consultations.** `/consult` +
  `/voice-ask` + `/voice-chat` use the advisor layer
  (narrative I) and the agent system (A).
- **Reactions as feedback** feed into the agent-learning
  pipeline (H) — `record_interaction` style signals from
  Discord activity.
- **Governance surfaces (J)** have a Discord side via
  `ReviewCommands` (Session 556) and
  `HumanInterfaceCommands` (Session 686).
- **Content pipeline (B)** has Discord triggers via
  `ContentCommands` + `ContentPipelineCommands` +
  `StudioCommands`.

---

## 5. Current state snapshot

> Source for counts: `docs/DISCORD_AUDIT.md` (DOC-AUTOGEN)
> + `PLATFORM_INVENTORY.md` snapshot 2026-05-25. 11,676
> lines; 25 Cogs; 96 commands (48 slash + 48 prefix); 12
> notification channels; voice subsystem 871 lines;
> notifications subsystem 2,273 lines.

**Architecture.**
- `core/services/discord_bot.py` — 11,676 lines. 25 Cogs.
- `core/services/discord_notifications.py` — 2,273 lines.
  12 channels.
- `core/services/discord_voice.py` — 871 lines. TTS,
  STT, voice cloning, voice chat.

**Cogs by command count (top 5).**
- `AgentAccessCommands` (Phase 5) — 10 commands
- `SpiderCommands` — 10 commands
- `ContentCommands` (Session 430) — 9 commands
- `StudioCommands` (Session 466) — 7 commands
- `InteractiveCommands` (Session 427) — 7 commands

**Cogs with zero commands (event-driven only).**
- `ReactionFeedbackCog` (Session 452)
- `RoleManager` (Session 439)

**Command surface (high-level).**
- System & Status (6): `/status`, `/spiders`, `/agents`,
  `/agent`, `/trending`, `/help`.
- PA & AI Core (7): `/ask`, `/research`, `/clear`,
  `/sessions`, `/link`, `/unlink`, `/profile`.
- Agents & Advisors (4): `/consult`, `/agent-task`,
  `/agent-list`, `/workflow-list`.
- Voice (4): `/voice-ask`, `/voice-chat` + voice clone /
  TTS commands.
- Content (~13 across cogs): `/create`,
  `/podcast-create`, `/create-content`, `/series-*`, etc.
- Governance / Review (~11): `ReviewCommands` +
  `HumanInterfaceCommands` + `SituationCommands`.
- Specialty (~50+): Resolve, Gumroad, Legal, Developer,
  ML scoring, etc.

**Discord-vs-web boundary.** Per
`DISCORD_INTEGRATION.md`:
- Discord: notifications, quick lookups, voice, mobile
  actions, creation triggers, account management.
- Web: complex workflows, content review pipeline,
  system config, deep exploration, dashboards.

**Audit doc.** `docs/DISCORD_AUDIT.md` — DOC-AUTOGEN
(`build_discord_audit`). Per-Cog appendix with each
command's name, method, line, description.

**Where to look when something stops working.**
- New Discord command not appearing → bot didn't reload
  the Cog; restart Discord bot service.
- Slash command shows but errors → `app_commands` need
  to be synced to Discord's API; check the bot startup
  code's sync call. May need a Discord-side guild-level
  re-sync.
- Notification not arriving → check
  `discord_notifications.py` for the channel + the
  triggering signal; check notification rate limits at
  the platform-side dispatch.
- Voice command fails → check
  `core/services/discord_voice.py`; voice features
  require both Discord voice permissions AND backend TTS
  / STT services available.
- Discord-vs-web confusion → consult
  `DISCORD_INTEGRATION.md` "What Discord IS / IS NOT
  for" — most "should this be in Discord?" questions
  answer themselves from that section.
- Audit doc count drift → regenerate via
  `python manage.py build_discord_audit`; the doc is
  DOC-AUTOGEN. Hand-editing won't survive.
- `/consult legendary advisor` mentions named figures →
  pre-Session-1142 framing in command description; the
  command description string needs an update. The
  advisor names are correctly post-1142 in the registry
  (narrative I).

---

## 6. Open questions / unknown outcomes

- **Cog splitting.** *Known:* the audit doc flags
  `AgentAccessCommands` (10), `SpiderCommands` (10),
  `ContentCommands` (9) as worth splitting. *Unknown:*
  whether splitting is on any roadmap.
- **Notification channel rate limits.** *Known:* 12
  channels; can produce volume. *Unknown:* whether any
  per-channel rate caps exist. Anti-spam discipline
  exists at platform-dispatch side (narrative A
  milestone 7) but not on Discord channels themselves.
- **Slash command sync cadence.** *Known:* `app_commands`
  must be synced to Discord. *Unknown:* whether the bot
  re-syncs on every restart or only on first run / on
  command-set change. Affects "new command not showing
  up" debug.
- **`/consult` description post-1142 rename.** *Known:*
  description still says "legendary advisor". *Unknown:*
  whether the description is updated in the codebase or
  whether it's stale.
- **Discord audit DOC-AUTOGEN regen cadence.** *Known:*
  it's regenerable. *Unknown:* whether it runs on a
  schedule or only ad-hoc. The same question for
  ADVISOR_AUDIT etc. — covered in narrative I.
- **Voice features hit-rate.** *Known:* TTS, STT, voice
  clone, voice chat all exist. *Unknown:* what
  proportion of Discord usage is voice vs text. No
  telemetry surfaced.
- **Reaction-feedback signal strength.** *Known:*
  `ReactionFeedbackCog` exists. *Unknown:* whether the
  reaction signal is materially affecting agent learning
  or whether it's a "we capture this but don't act on
  it" path.
- **`HumanInterfaceCommands` scope.** *Known:* Session
  686, 6 commands, "Human Interface Layer". *Unknown:*
  the layer's full role — covered briefly in narrative
  J but not in depth here.

---

## 7. Source index

### Primary doc sources

- `docs/DISCORD_AUDIT.md` — DOC-AUTOGEN. AST-parsed
  command audit; per-cog appendix; the canonical count
  source.
- `docs/DISCORD_INTEGRATION.md` — Discord rules + command
  reference; the canonical "what Discord is for" doc.
- `docs/PLATFORM_INVENTORY.md` — inventory snapshot.

### Per-Cog session attributions

Most Cogs name their session in the class docstring.
Citations above use the docstring attribution. Full
attribution table:

- `AgentAccessCommands` — Phase 5
- `AgentCommands` — Inferred pre-Session 427
- `ClientCommands` — Session 432 (Phase 3)
- `ContentCommands` — Session 430
- `ContentPipelineCommands` — Session 440
- `DeveloperCommands` — Session 497
- `GumroadCommands` — Session 487
- `HelpCommands` — Inferred earlier
- `HumanInterfaceCommands` — Session 686
- `InteractiveCommands` — Session 427
- `LegalCommands` — Session 497
- `MLScoringCommands` — Session 497
- `OBSCommands` — Unknown (not session-attributed in
  docstring)
- `PodcastCommands` — Session 496
- `ReactionFeedbackCog` — Session 452
- `ResolveCommands` — Unknown (DaVinci Resolve)
- `ReviewCommands` — Session 556
- `RoleManager` — Session 439
- `SeriesCommands` — Session 445
- `ServerSetupCommands` — Session 431
- `SituationCommands` — Session 480
- `SpiderCommands` — Inferred pre-Session 427
- `StatusCommands` — Inferred pre-Session 427
- `StudioCommands` — Session 466
- `VoiceCommands` — Session 438 (Phase 8)

### Code anchors

- `core/services/discord_bot.py` — single-file bot.
- `core/services/discord_notifications.py` — 12 channels.
- `core/services/discord_voice.py` — voice subsystem.
- `core/management/commands/build_discord_audit.py` —
  DOC-AUTOGEN regenerator (Session 1115).

### Verification commands

- `python manage.py build_discord_audit` — regenerate
  `docs/DISCORD_AUDIT.md`.
- `python manage.py verify_doc_claims --only-drift` —
  flag drift on Discord counts.
- `python manage.py generate_platform_inventory` —
  inventory snapshot.
