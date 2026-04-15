
import os, json, time, signal, sys
import logging
logger = logging.getLogger(__name__)

print('[repo-review] starting', flush=True)
from pathlib import Path
from typing import Dict, Any, List
import requests

# -------- settings / env ----------
REPO_ROOT = Path.cwd()
REVIEW_DIR = Path("review")
REVIEW_DIR.mkdir(exist_ok=True)
CHECKPOINT = REVIEW_DIR / "progress.json"
REPORT_MD  = REVIEW_DIR / "REPO_REVIEW.md"

OLLAMA_BASE = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
CHAT_URL    = OLLAMA_BASE.rstrip("/") + "/v1/chat/completions"
EMB_URL     = OLLAMA_BASE.rstrip("/") + "/v1/embeddings"
MODEL       = os.environ.get("OLLAMA_CHAT_MODEL", "qwen2.5:14b-instruct")
EMB_MODEL   = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")
HTTP_TIMEOUT= int(os.environ.get("OLLAMA_HTTP_TIMEOUT","600"))

# -------- persistence -------------
def load_progress() -> Dict[str, Any]:
    if CHECKPOINT.exists():
        try:
            return json.loads(CHECKPOINT.read_text())
        except Exception as _e:
            logger.warning(
                "repo_review_with_ollama.load_progress: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )
    return {"completed": {}, "failed": {}, "started_at": time.time()}

def save_progress(state: Dict[str, Any]) -> None:
    CHECKPOINT.write_text(json.dumps(state, indent=2))

# -------- http helpers ------------
def post_ollama(url: str, payload: dict, timeout_s: int = None, max_retries: int = 3, backoff: float = 2.0):
    if timeout_s is None:
        timeout_s = HTTP_TIMEOUT
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            return requests.post(url, json=payload, timeout=timeout_s)
        except (requests.Timeout, requests.ConnectionError) as e:
            last_exc = e
            print(f"[repo-review] retry {attempt}/{max_retries} for {url} …", flush=True)
            time.sleep(backoff * attempt)
    if last_exc:
        raise last_exc

def ollama_chat(messages: List[Dict[str,str]], max_tokens: int = 800, temperature: float = 0.2) -> str:
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        # pass low-level options via extra_body for compatibility with Ollama’s OpenAI shim
        "extra_body": {"options": {"num_ctx": 16384, "num_keep": 64, "parallel": 1,"num_batch": 256 }}
    }
    print("[repo-review] calling chat …", flush=True)
    r = post_ollama(CHAT_URL, payload)
    r.raise_for_status()
    data = r.json()
    # OpenAI-compatible response
    content = data.get("choices", [{}])[0].get("message", {}).get("content")
    return content or ""

def check_connectivity() -> None:
    # chat ping
    pong = ollama_chat([{"role":"user","content":"Reply with OK"}], max_tokens=5, temperature=0)
    print(f"[repo-review] chat ping: {pong!r}", flush=True)
    # embeddings ping
    emb_payload = {"model": EMB_MODEL, "input": "hello"}
    print("[repo-review] calling embeddings …", flush=True)
    er = post_ollama(EMB_URL, emb_payload)
    er.raise_for_status()
    ed = er.json()
    dim = len(ed.get("data", [{}])[0].get("embedding", []) or [])
    print(f"[repo-review] embeddings dim: {dim}", flush=True)

# -------- analysis helpers --------
def sample_text(file: Path, limit_bytes: int = 4000) -> str:
    try:
        txt = file.read_text(errors="ignore")
        return txt[:limit_bytes]
    except Exception as _e:
        logger.warning(
            "repo_review_with_ollama.sample_text: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return ""

def build_repo_outline(root: Path, max_files_per_dir: int = 50) -> str:
    keep_dirs = [
        "ai_core", "core", "intelligence", "sports", "content",
        "scripts", "setup", "testing", "review", "docs"
    ]
    lines = []
    for dname in keep_dirs:
        d = root / dname
        if not d.exists():
            continue
        lines.append(f"### /{dname}")
        count = 0
        for path in sorted(d.rglob("*")):
            if path.is_dir(): 
                continue
            rel = path.relative_to(root)
            lines.append(f"- {rel}")
            count += 1
            if count >= max_files_per_dir:
                lines.append(f"- … (+ more)")
                break
        lines.append("")
    return "\n".join(lines)

def build_prompt(outline: str, samples: List[Dict[str,str]]) -> List[Dict[str,str]]:
    sys_msg = {"role":"system","content":"You are a pragmatic senior engineer. Give concise, actionable repo review with concrete steps and code block snippets where useful."}
    user_parts = [
        "Repo outline:\n",
        outline,
        "\n---\nSample file excerpts (truncated):\n"
    ]
    for s in samples:
        user_parts.append(f"\n# {s['path']}\n```\n{s['text']}\n```")
    user_parts.append("\nProvide:\n1) Top risks / broken links\n2) Quick wins (<= 10 bullet points)\n3) Ollama integration checks\n4) Next actions for 75%→90% integration\n")
    user_msg = {"role":"user","content":"".join(user_parts)}
    return [sys_msg, user_msg]

# -------- main --------------------
def main() -> int:
    print("[repo-review] entering main()", flush=True)
    state = load_progress()

    # 1) connectivity
    try:
        check_connectivity()
    except Exception as e:
        print(f"[repo-review] connectivity failed: {e}", flush=True)
        return 2

    # 2) repo outline + small samples
    outline = build_repo_outline(REPO_ROOT)
    sample_paths = [
        Path("scripts/review/repo_review_with_ollama.py"),
        Path("README.md"),
        Path("docs/QUICK_FIX_GUIDE.md"),
        Path("ai_core/agents/universal_agent_loader.py"),
        Path("ai_core/spiders/spider_registry.py"),
    ]
    samples: List[Dict[str,str]] = []
    for p in sample_paths:
        if p.exists():
            samples.append({"path": str(p), "text": sample_text(p)})

    # 3) ask the model once (fast path)
    messages = build_prompt(outline, samples)
    try:
        review_text = ollama_chat(messages, max_tokens=1200, temperature=0.1)
    except Exception as e:
        state["failed"]["repo_review"] = {"error": str(e), "ts": time.time()}
        save_progress(state)
        print(f"[repo-review] chat error: {e}", flush=True)
        return 3

    # 4) write report
    REPORT_MD.write_text(f"# Repo Review (local Ollama: {MODEL})\n\n{review_text}\n")
    state["completed"]["repo_review"] = {"report": str(REPORT_MD), "ts": time.time()}
    save_progress(state)
    print(f"[repo-review] wrote {REPORT_MD}", flush=True)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("[repo-review] aborted by user", flush=True)
        sys.exit(130)
