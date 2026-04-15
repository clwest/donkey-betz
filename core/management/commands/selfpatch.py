# core/management/commands/selfpatch.py
import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from django.core.management.base import BaseCommand, CommandError

# Optional LLM (for propose mode)
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_API_KEY  = os.getenv("LLM_API_KEY")
LLM_MODEL    = os.getenv("LLM_MODEL", "qwen2.5:14b-instruct")

REPO_ROOT = Path(__file__).resolve().parents[3]  # project root

PROMPT_HEADER = """You are a careful code-modifying assistant.
You will write a minimal, correct patch for a Django project.

RULES:
- Prefer a unified diff patch that applies cleanly with 'git apply'.
- If changing multiple files, include them all in one diff.
- Keep changes surgical and include context lines.
- No unrelated refactors.
- Use 4-space indentation for Python.
- If adding imports, keep them sorted and minimal.
- Ensure code runs on Python 3.11.

PROJECT HINTS:
- Django project; management commands live under core/management/commands/.
- We use a Makefile with 'make start/stop/restart'.
- RAG command: core/management/commands/ragtest.py (uses OpenAI-compatible client).
"""

PROPOSE_USER_FMT = """Task:
{desc}

Target files (edit only these unless absolutely necessary):
{files_block}

Output format:
Return ONLY a unified diff starting with lines like:
***BEGIN PATCH***
diff --git a/RELATIVE/PATH b/RELATIVE/PATH
...
***END PATCH***

If a unified diff is impractical, return:
***BEGIN JSON***
[{{"path":"relative/path.py","content":"<full file content>"}} , ...]
***END JSON***
"""

def run(cmd: List[str], cwd: Optional[Path] = None, check=True, capture=False):
    proc = subprocess.run(
        cmd, cwd=str(cwd or REPO_ROOT),
        check=check, text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    return proc

def ensure_git_clean():
    out = run(["git", "status", "--porcelain"], capture=True)
    if out.stdout.strip():
        raise CommandError("Git working tree not clean. Commit or stash first.")

def create_backup_branch(prefix="selfpatch"):
    # create a backup branch with timestamp
    import time
    branch = f"{prefix}/{int(time.time())}"
    run(["git", "checkout", "-b", branch])
    return branch

def switch_back_to_prev(prev_branch: str):
    run(["git", "checkout", prev_branch])

def guess_prev_branch() -> str:
    out = run(["git", "branch", "--show-current"], capture=True)
    return out.stdout.strip()

def write_temp(content: str, suffix=""):
    f = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=suffix, dir=str(REPO_ROOT))
    f.write(content)
    f.close()
    return Path(f.name)

def detect_block(marked_text: str):
    if "***BEGIN PATCH***" in marked_text and "***END PATCH***" in marked_text:
        return "patch", marked_text.split("***BEGIN PATCH***",1)[1].split("***END PATCH***",1)[0].strip()
    if "***BEGIN JSON***" in marked_text and "***END JSON***" in marked_text:
        return "json", marked_text.split("***BEGIN JSON***",1)[1].split("***END JSON***",1)[0].strip()
    # fallbacks: try to detect a diff header
    if marked_text.strip().startswith("diff --git "):
        return "patch", marked_text.strip()
    # or a json array
    if marked_text.strip().startswith("["):
        return "json", marked_text.strip()
    return None, None

def apply_unified_diff(diff_text: str, dry_run: bool):
    patch_file = write_temp(diff_text, suffix=".patch")
    try:
        # check first
        run(["git", "apply", "--index", "--check", str(patch_file)])
        if dry_run:
            print("Dry-run OK: patch applies cleanly.")
            return
        # apply and stage
        run(["git", "apply", "--index", str(patch_file)])
        print("Patch applied and staged.")
    finally:
        patch_file.unlink(missing_ok=True)

def apply_json_patchset(json_text: str, dry_run: bool):
    try:
        patchset = json.loads(json_text)
        assert isinstance(patchset, list)
    except Exception as e:
        raise CommandError(f"Invalid JSON patchset: {e}")

    touched = []
    for item in patchset:
        path = REPO_ROOT / item["path"]
        content = item["content"]
        if dry_run:
            print(f"Dry-run: would write {path} ({len(content)} bytes)")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            run(["git", "add", str(path)])
            touched.append(str(path.relative_to(REPO_ROOT)))
    if not dry_run:
        print(f"Wrote {len(touched)} files and staged them.")
    return touched

def sanity_checks(paths_maybe: Optional[List[str]] = None, run_manage_check=True, run_pycompile=True, run_pytest=False):
    changed = paths_maybe or []
    # 1) py_compile
    if run_pycompile and changed:
        py_files = [p for p in changed if p.endswith(".py")]
        if py_files:
            for p in py_files:
                run([sys.executable, "-m", "py_compile", p])
            print("Python syntax check passed.")

    # 2) manage.py check
    if run_manage_check:
        run([sys.executable, "manage.py", "check"])
        print("Django manage.py check passed.")

    # 3) pytest (optional)
    if run_pytest and (REPO_ROOT / "pytest.ini").exists():
        run(["pytest", "-q"])
        print("pytest passed.")

class Command(BaseCommand):
    help = "Self-patching helper: propose patches with LLM, or apply patches/diffs safely."

    def add_arguments(self, parser):
        sub = parser.add_subparsers(dest="mode")

        p_prop = sub.add_parser("propose", help="Ask the model to propose a patch")
        p_prop.add_argument("--desc", required=True, help="What you want changed")
        p_prop.add_argument("--paths", nargs="+", required=True, help="Limit edits to these files")
        p_prop.add_argument("--k", type=int, default=6, help="(reserved) ")
        p_prop.add_argument("--temperature", type=float, default=0.2)
        p_prop.add_argument("--max_tokens", type=int, default=3000)
        p_prop.add_argument("--raw", action="store_true", help="Print raw model output")

        p_apply = sub.add_parser("apply", help="Apply a patch/diff")
        p_apply.add_argument("--from-file", help="Path to a .patch or .json patchset")
        p_apply.add_argument("--stdin", action="store_true", help="Read patch from stdin")
        p_apply.add_argument("--dry-run", action="store_true", help="Do not write, just check")
        p_apply.add_argument("--no-manage-check", action="store_true", help="Skip manage.py check")
        p_apply.add_argument("--no-pycompile", action="store_true", help="Skip py_compile")
        p_apply.add_argument("--pytest", action="store_true", help="Run pytest after apply")
        p_apply.add_argument("--commit", action="store_true", help="Commit with a default message")
        p_apply.add_argument("--commit-msg", default="chore(selfpatch): apply model-proposed patch")

    def handle(self, *args, **opts):
        mode = opts.get("mode")
        if mode == "propose":
            self.propose(opts)
        elif mode == "apply":
            self.apply(opts)
        else:
            raise CommandError("Specify mode: propose | apply")

    # -------- propose --------
    def propose(self, opts):
        desc = opts["desc"]
        paths = [str(Path(p)) for p in opts["paths"]]

        if not (LLM_BASE_URL and LLM_API_KEY):
            raise CommandError("LLM_BASE_URL and LLM_API_KEY must be set in env for propose mode.")

        files_block = "\n".join(f"- {p}" for p in paths)
        user_prompt = PROPOSE_USER_FMT.format(desc=desc, files_block=files_block)

        # Build context with file contents (short)
        context_parts = []
        for p in paths:
            path = REPO_ROOT / p
            if not path.exists():
                raise CommandError(f"Target file not found: {p}")
            text = path.read_text()
            # Truncate long files to keep prompt sane (model can still propose precise diffs).
            if len(text) > 8000:
                text = text[:8000] + "\n# ... (truncated)"
            context_parts.append(f"--- FILE: {p} ---\n{text}")

        system = PROMPT_HEADER
        user = user_prompt + "\n\nREFERENCE FILES:\n" + "\n\n".join(context_parts)

        # OpenAI-compatible client
        from core.services.openai_client_factory import get_openai_client
        client = get_openai_client(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            temperature=float(opts["temperature"]),
            max_tokens=int(opts["max_tokens"]),
            messages=[
                {"role":"system","content":system},
                {"role":"user","content":user},
            ],
        )
        out = resp.choices[0].message.content
        if opts["raw"]:
            print(out)
            return

        kind, body = detect_block(out or "")
        if not kind:
            print(out)
            raise CommandError("Model did not return a recognized block. Use --raw to inspect.")

        print(f"Detected {kind.upper()} block.")
        print("\n=== BEGIN ===")
        print(body)
        print("=== END ===")
        print("\nTip: save and apply, e.g.:")
        if kind == "patch":
            print("  python manage.py selfpatch apply --from-file proposed.patch")
        else:
            print("  python manage.py selfpatch apply --from-file proposed.json")

    # -------- apply --------
    def apply(self, opts):
        src = None
        if opts["from_file"]:
            src = Path(opts["from_file"]).read_text()
        elif opts["stdin"]:
            src = sys.stdin.read()
        else:
            raise CommandError("Provide --from-file or --stdin")

        kind, body = detect_block(src)
        if not kind:
            # try to sniff if raw src is already a diff or json
            if src.strip().startswith("diff --git"):
                kind, body = "patch", src
            elif src.strip().startswith("["):
                kind, body = "json", src
            else:
                raise CommandError("Could not detect patch kind (patch/json).")

        # Ensure clean tree
        prev_branch = guess_prev_branch()
        # We don't force clean tree to allow iterative development, but strong recommend:
        # ensure_git_clean()

        # Create a backup branch
        backup_branch = create_backup_branch(prefix="selfpatch-backup")
        print(f"Created backup branch: {backup_branch}")

        # Switch back to previous to apply there
        switch_back_to_prev(prev_branch)

        dry = bool(opts["dry_run"])
        touched = None
        if kind == "patch":
            apply_unified_diff(body, dry_run=dry)
        elif kind == "json":
            touched = apply_json_patchset(body, dry_run=dry)

        # Verify if not dry-run
        if not dry:
            # get list of staged files for py_compile
            if touched is None:
                # get staged changes
                staged = run(["git", "diff", "--cached", "--name-only"], capture=True).stdout.splitlines()
                touched = [s for s in staged if s]
            sanity_checks(
                paths_maybe=touched,
                run_manage_check=not opts["no_manage_check"],
                run_pycompile=not opts["no_pycompile"],
                run_pytest=bool(opts["pytest"]),
            )
            if opts["commit"]:
                run(["git", "commit", "-m", opts["commit_msg"]])
                print("Committed.")

        print("Done.")