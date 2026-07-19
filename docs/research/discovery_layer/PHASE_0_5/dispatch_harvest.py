"""Phase-0.5 harvest dispatch — S2825.

Dispatches each query in PHASE_0_5/corpus.json via `pa_chat.py` wrapper
(Rigby PA → kb_tool.semantic_search handler → flag-on router path per
S2824). The celery pa worker's router singleton auto-mints an active
measurement window on first classify; all dispatches in this batch will
share that window_id. Filter JSONL SoT by that window_id post-hoc.

Per Rigby S2825 Q4 SIGN AGREE — dispatch via handler surface (router
fires); Q5 SIGN AGREE — measurement_window_id segregation via post-hoc
filter (single-user pre-prod env — no pollution from concurrent real
work).

Correlation to corpus.json rows via query_text (verbatim, all 20 unique
within Phase-0.5).

Usage:
    python docs/research/discovery_layer/PHASE_0_5/dispatch_harvest.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
CORPUS_PATH = HERE / "corpus.json"
RESULTS_PATH = HERE / "harvest_dispatch_results.json"
REPO_ROOT = Path(__file__).parents[4]
PA_LOCAL = REPO_ROOT / "tools" / "pa_local.sh"
ROUTER_JSONL = REPO_ROOT / "logs" / "phase_0_5_router.jsonl"


def dispatch_via_rigby(query: str, timeout_sec: int = 90) -> dict:
    """Dispatch via pa_chat.py wrapper. Returns raw stdout tail for post-hoc parse."""
    escaped = query.replace('"', '\\"')
    prompt = (
        f'Run kb_tool.semantic_search with query="{escaped}" and limit=3. '
        f'Return ONLY the raw envelope JSON — no prose, no commentary.'
    )
    proc = subprocess.run(
        ["bash", str(PA_LOCAL), prompt],
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )
    return {
        "returncode": proc.returncode,
        "raw_stdout_tail": proc.stdout[-3000:],
        "raw_stderr_tail": proc.stderr[-500:],
    }


def read_jsonl_tail(path: Path, n: int = 100) -> list:
    if not path.exists():
        return []
    lines = path.read_text().strip().splitlines()
    return [json.loads(line) for line in lines[-n:] if line.strip()]


def main() -> int:
    corpus = json.loads(CORPUS_PATH.read_text())
    rows = corpus["rows"]

    # Capture JSONL row count baseline BEFORE dispatch
    baseline_count = len(read_jsonl_tail(ROUTER_JSONL, n=10000))
    print(f"[baseline] JSONL row count before dispatch: {baseline_count}")

    results = []
    for i, row in enumerate(rows, start=1):
        query = row["query_text"]
        qid = row["query_id"]
        print(f"[{i:2d}/{len(rows)}] {qid} :: {query[:60]}{'...' if len(query)>60 else ''}", flush=True)
        try:
            resp = dispatch_via_rigby(query)
            results.append({
                "query_id": qid,
                "query_text": query,
                "returncode": resp["returncode"],
                "raw_stdout_tail": resp["raw_stdout_tail"],
                "raw_stderr_tail": resp["raw_stderr_tail"],
            })
        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] {qid}")
            results.append({"query_id": qid, "query_text": query, "error": "TIMEOUT"})
        time.sleep(1)

    # Post-dispatch JSONL delta
    all_rows = read_jsonl_tail(ROUTER_JSONL, n=10000)
    delta_rows = all_rows[baseline_count:]
    windows_seen = sorted({r.get("measurement_window_id") for r in delta_rows if r.get("measurement_window_id")})
    print(f"[delta] JSONL grew by {len(delta_rows)} rows across windows: {windows_seen}")

    output = {
        "n_dispatched": len(results),
        "n_errors": sum(1 for r in results if r.get("error") or r.get("returncode") != 0),
        "baseline_jsonl_row_count": baseline_count,
        "post_dispatch_jsonl_row_count": len(all_rows),
        "delta_rows": len(delta_rows),
        "windows_observed": windows_seen,
        "results": results,
    }
    RESULTS_PATH.write_text(json.dumps(output, indent=2, default=str))
    print(f"[OK] Wrote dispatch results to {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
