# 24/7 Global AI — Spokesperson Corpus

The knowledge base the public-facing spokesperson reads from. Each chunk is a small,
embedding-friendly markdown file with structured facts and pre-written voice prose.
The spokesperson is **not** in this directory — only what it knows about.

## Source-of-truth pointers

| Anchor | What lives there |
|---|---|
| Public taxonomy | `/Users/donkeyking/development/24-7-ai-global/src/lib/products.ts` |
| Marketing site (live) | `https://247globalai.com` |
| Engine narrative anchor | `../PLATFORM_WHAT_IT_IS.md` |
| Engine runtime inventory | `../PLATFORM_INVENTORY.md` |
| Pivot context | `../handoffs/SESSION_1116_GLOBAL_AI_PIVOT_AND_LIVE_INTEL.md` + Part 2 |
| Pattern this corpus follows | `../docs-pattern/spokesperson-corpus/` |

When any anchor shifts, re-run the recipe in `../docs-pattern/spokesperson-corpus/RECIPE.md`
and re-ingest into the downstream spokesperson system (Character OS).

## Audience tier

Every chunk in this corpus is `audience: public-everyone` unless explicitly flagged otherwise.
That means: no internal session numbers, no stack jargon, no unshipped roadmap, no internal
codenames except where they're part of the public taxonomy (Rigby, The Council, The Network
are public names on `247globalai.com` and are fine to use).

The engine itself (the platform powering the public Suite) is **never** named publicly.
References to it use **"the engine"**, **"the studio's engine"**, or **"the platform behind
the works"**. The previous brand name ("Donkey Betz") appears **only** in the origin chunk,
framed in past tense.

## Voice anchor

`01_voice.md` is the authoritative voice rules for this project. It supersedes the
pattern's default `VOICE_GUIDE.md` where they conflict.

## Chunk index

| File | Section | Status |
|---|---|---|
| `00_overview.md` | Overview | shipped |
| `01_voice.md` | Voice | reference |
| `02_pillars.md` | Pillars | reference |
| `10_mentorforge.md` | Suite | shipped |
| `30_the_network.md` | Lab / Engine | in-development (powering /now) |
| `40_operator_edge.md` | Channel | shipped |
| `60_origin_pivot.md` | Story | story |
| `70_faq.md` | FAQ | reference |
| `90_facts.md` | Facts | reference |

This is the **vertical slice** — one chunk per section type so the voice can be vetted
before the remaining ~15 product chunks (the other three Suite products, three Verticals,
nine other Lab entries, four other Channels) are filled in.

## How the spokesperson uses this

1. Each markdown chunk is embedded (one chunk = one vector). The chunk's frontmatter
   becomes filterable metadata.
2. At inference time, the spokesperson retrieves the K most relevant chunks for the
   user's question.
3. The spokesperson is system-prompted to:
   - Quote **How to talk about it** prose verbatim when answering
   - Defend specific claims from **Quick facts** or **90_facts.md** only
   - Refuse to claim anything that falls under any chunk's **Off-limits** section
   - Decline gracefully when a question isn't covered ("Let me have the proprietor
     reach out — that's worth a real answer")

## Refresh cadence

Re-run the recipe on:

- New product launches → new chunk added
- Pricing changes → product chunk's Quick facts updated
- Engine inventory shifts that affect cited counts → `90_facts.md` updated, dependent
  chunks re-verified
- Brand voice doc changes → `01_voice.md` updated, every chunk re-reviewed

After any refresh, re-ingest into Character OS.
