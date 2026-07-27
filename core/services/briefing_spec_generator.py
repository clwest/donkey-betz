"""
Briefing spec generator — S2989 Phase A.

Converts a canonical-briefing bullet + citations into an execution-ready
spec-shape markdown body. The resulting Deliverable is what Claude picks
up and executes against; the S2988 raw-bullet compose shape was a
bookmark, not a spec.

Spec-shape schema (SPEC_V1):
- goal: 1 sentence, imperative
- context: 2-3 sentences of grounded background
- open_question: 1 sentence or "None"
- files_implicated: list of {path, source: "citation"|"inferred"}
    - "citation" paths MUST appear in the incoming citations payload
    - "inferred" paths are flagged so downstream can distrust them
- acceptance_criteria: 3-5 short imperative bullets
- warnings: list of strings — truncation / degrade notes

Fail-open: LLM failure or schema violation emits the same section
layout with placeholders and a warning banner, so downstream consumers
(the Deliverable body renderer, future filters/exports) never see a
shape mismatch.

Rigby SIGN cycle 1 (S2989) folds applied inline:
- F-A1: strict schema + validation + repair; fallback preserves layout
- F-A2: files_implicated locked to citation-path allowlist + source tag
- F-A3: per-field length caps + warnings[] surface for truncation
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from core.services.llm_call_wrapper import llm_call_span
from core.services.openai_client_factory import get_openai_client

logger = logging.getLogger(__name__)

SPEC_PROMPT_VERSION = "v1"
DEFAULT_SPEC_MODEL = "gpt-5-mini"
DEFAULT_SPEC_MAX_COMPLETION_TOKENS = 3000

# Per-field caps (F-A3). Enforced post-LLM; truncation logged to warnings[].
CAP_GOAL_CHARS = 300
CAP_CONTEXT_CHARS = 800
CAP_OPEN_QUESTION_CHARS = 300
CAP_FILE_PATH_CHARS = 200
CAP_ACCEPTANCE_CHARS = 200
MAX_FILES_IMPLICATED = 8
MIN_ACCEPTANCE_CRITERIA = 1
MAX_ACCEPTANCE_CRITERIA = 8

FILE_SOURCE_CITATION = "citation"
FILE_SOURCE_INFERRED = "inferred"

# S2993 item #3: prompt-shape axis. Mirrors DocResearchFinding.finding_type
# but the generator only cares about "which prompt do I run?" so we keep a
# generator-local vocabulary rather than importing the model.
PROMPT_SHAPE_ENGINEERING = "engineering"
PROMPT_SHAPE_EVIDENCE = "evidence_capture"
_FINDING_TYPE_TO_PROMPT_SHAPE = {
    "decision_evidence": PROMPT_SHAPE_EVIDENCE,
    "executable": PROMPT_SHAPE_ENGINEERING,
    "unknown": PROMPT_SHAPE_ENGINEERING,
}


@dataclass
class FileEntry:
    path: str
    source: str  # citation | inferred

    def to_dict(self) -> Dict[str, str]:
        return {"path": self.path, "source": self.source}


@dataclass
class BriefingSpec:
    goal: str
    context: str
    open_question: str
    files_implicated: List[FileEntry]
    acceptance_criteria: List[str]
    warnings: List[str] = field(default_factory=list)
    schema_version: str = "SPEC_V1"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "goal": self.goal,
            "context": self.context,
            "open_question": self.open_question,
            "files_implicated": [f.to_dict() for f in self.files_implicated],
            "acceptance_criteria": list(self.acceptance_criteria),
            "warnings": list(self.warnings),
        }


def _cap(text: str, limit: int) -> Tuple[str, bool]:
    """Return (text_maybe_truncated, was_truncated)."""
    if len(text) <= limit:
        return text, False
    return text[: limit - 1].rstrip() + "\u2026", True


def _format_citation_blocks(citations: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Return (citations_text, known_paths_bullets) for prompt injection."""
    citation_paths = sorted(
        {(c.get("path") or "").strip() for c in citations if isinstance(c, dict) and c.get("path")}
    )
    citation_blocks: List[str] = []
    for i, c in enumerate(citations or [], start=1):
        path = c.get("path") or "?"
        snippet = (c.get("snippet") or "").replace("\r", " ").strip()
        if len(snippet) > 800:
            snippet = snippet[:799] + "\u2026"
        citation_blocks.append(f"[{i}] path={path}\n{snippet}")
    citations_text = "\n\n".join(citation_blocks) or "(no citations attached)"
    known_paths = "\n".join(f"- {p}" for p in citation_paths) or "(none)"
    return citations_text, known_paths


def _build_spec_prompt_engineering(
    bullet_text: str,
    section_title: str,
    anchor_path: str,
    citations: List[Dict[str, Any]],
) -> Tuple[str, str]:
    citations_text, known_paths = _format_citation_blocks(citations)
    system = (
        "You convert one bullet from a canonical documentation audit into a "
        "spec that a code-writing AI agent will pick up and implement. The "
        "reader has no arc context.\n\n"
        "Output MUST be JSON with keys: goal, context, open_question, "
        "files_implicated, acceptance_criteria.\n\n"
        "Rules:\n"
        "- goal: ONE sentence, imperative form. What to accomplish.\n"
        "- context: 2-3 sentences grounded in the citations. Plain English.\n"
        "- open_question: ONE sentence — what a human should decide — "
        "OR the exact string \"None\" if unambiguous.\n"
        "- files_implicated: array of objects {path, source}. "
        f"source MUST be one of \"{FILE_SOURCE_CITATION}\" (path taken verbatim "
        "from the citations list — copy the path exactly) or "
        f"\"{FILE_SOURCE_INFERRED}\" (path a human should verify). "
        "Prefer citation-sourced paths. If you cannot find any real file path "
        "in the citations, return an empty array — DO NOT invent code paths.\n"
        "- acceptance_criteria: array of 3-5 short imperative bullets. Each ≤ 20 "
        "words, testable, concrete.\n"
        "- Do NOT invent facts. Every claim must be grounded in the citation "
        "snippets or the bullet text.\n"
        "- Return ONLY the JSON object. No prose, no code fences."
    )
    user = (
        f"Source canonical summary: {anchor_path}\n"
        f"Source section: {section_title}\n"
        f"Bullet text:\n{bullet_text}\n\n"
        f"Retrieved citations:\n{citations_text}\n\n"
        f"Paths present in citations (allowlist for source=\"{FILE_SOURCE_CITATION}\"):\n"
        f"{known_paths}\n\n"
        "Return the spec JSON now."
    )
    return system, user


def _build_spec_prompt_evidence(
    bullet_text: str,
    section_title: str,
    anchor_path: str,
    citations: List[Dict[str, Any]],
) -> Tuple[str, str]:
    """S2993 item #3: prompt shape for decision_evidence findings.

    Reframes the same JSON schema — goal/context/open_question/files_implicated/
    acceptance_criteria — to CAPTURE the boundary/verdict rather than propose
    engineering work. acceptance_criteria become verification/re-audit steps.
    """
    citations_text, known_paths = _format_citation_blocks(citations)
    system = (
        "You convert one bullet from a canonical documentation audit into a "
        "decision-evidence record. The bullet documents a boundary, verdict, "
        "or contract — not a task to implement. The reader has no arc context.\n\n"
        "Output MUST be JSON with keys: goal, context, open_question, "
        "files_implicated, acceptance_criteria.\n\n"
        "Rules:\n"
        "- goal: ONE sentence stating the boundary/verdict the finding records. "
        "Do NOT propose an implementation. Example shapes: "
        "\"Record that <X> is the enforced boundary between <A> and <B>.\" / "
        "\"Capture that <system> deliberately does not <behavior> and why.\"\n"
        "- context: 2-3 sentences grounded in the citations that explain what "
        "the boundary is and why it holds. Plain English.\n"
        "- open_question: ONE sentence naming what a future audit should check "
        "to falsify or renew this evidence — OR the exact string \"None\" if "
        "the record is self-contained.\n"
        "- files_implicated: array of objects {path, source}. These point at "
        "code/docs where the evidence LIVES (not where work would happen). "
        f"source MUST be one of \"{FILE_SOURCE_CITATION}\" (path taken verbatim "
        "from the citations list — copy the path exactly) or "
        f"\"{FILE_SOURCE_INFERRED}\" (path a human should verify). "
        "Prefer citation-sourced paths. If no real file path is present in the "
        "citations, return an empty array — DO NOT invent code paths.\n"
        "- acceptance_criteria: array of 3-5 short imperative VERIFICATION "
        "steps that would let a future auditor confirm the boundary/verdict "
        "still holds. Each ≤ 20 words, testable, concrete. Example shapes: "
        "\"Re-read <cited section> at HEAD confirms <boundary> still enforced.\" / "
        "\"Grep <symbol> in <path> returns only the expected callers.\" "
        "Do NOT phrase these as \"implement X\" or \"add Y\".\n"
        "- Do NOT invent facts. Every claim must be grounded in the citation "
        "snippets or the bullet text.\n"
        "- Return ONLY the JSON object. No prose, no code fences."
    )
    user = (
        f"Source canonical summary: {anchor_path}\n"
        f"Source section: {section_title}\n"
        f"Bullet text:\n{bullet_text}\n\n"
        f"Retrieved citations:\n{citations_text}\n\n"
        f"Paths present in citations (allowlist for source=\"{FILE_SOURCE_CITATION}\"):\n"
        f"{known_paths}\n\n"
        "Return the decision-evidence spec JSON now."
    )
    return system, user


def _resolve_prompt_shape(finding_type: Optional[str]) -> str:
    """Map finding_type → prompt shape. Unknown values fall through to engineering."""
    if not finding_type:
        return PROMPT_SHAPE_ENGINEERING
    return _FINDING_TYPE_TO_PROMPT_SHAPE.get(finding_type.strip().lower(), PROMPT_SHAPE_ENGINEERING)


def _build_spec_prompt(
    bullet_text: str,
    section_title: str,
    anchor_path: str,
    citations: List[Dict[str, Any]],
    prompt_shape: str = PROMPT_SHAPE_ENGINEERING,
) -> Tuple[str, str]:
    """Route to the prompt builder for the given shape.

    Kept as the single public callsite so callers stay stable; internal
    branch selects engineering vs evidence-capture per S2993 item #3.
    """
    if prompt_shape == PROMPT_SHAPE_EVIDENCE:
        return _build_spec_prompt_evidence(bullet_text, section_title, anchor_path, citations)
    return _build_spec_prompt_engineering(bullet_text, section_title, anchor_path, citations)


def _call_spec_llm(system_prompt: str, user_prompt: str, model: str) -> str:
    client = get_openai_client()
    with llm_call_span(
        provider="openai",
        model=model,
        agent_name="briefing_spec_generator",
    ) as span:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_completion_tokens=DEFAULT_SPEC_MAX_COMPLETION_TOKENS,
            response_format={"type": "json_object"},
        )
        try:
            span.attach_response(response)
        except Exception:  # noqa: BLE001 - telemetry attach must never mask body
            logger.debug("briefing_spec: attach_response failed", exc_info=True)
    return response.choices[0].message.content or ""


def _validate_and_repair(
    raw_json: str,
    citation_paths: set[str],
) -> BriefingSpec:
    """Parse LLM JSON into BriefingSpec with strict validation.

    Raises ValueError on unrecoverable schema violation so caller
    falls open to placeholder shape.
    """
    payload = json.loads(raw_json)
    warnings: List[str] = []

    goal_raw = str(payload.get("goal") or "").strip()
    if not goal_raw:
        raise ValueError("goal missing")
    goal, truncated = _cap(goal_raw, CAP_GOAL_CHARS)
    if truncated:
        warnings.append("goal_truncated")

    context_raw = str(payload.get("context") or "").strip()
    context, truncated = _cap(context_raw, CAP_CONTEXT_CHARS)
    if truncated:
        warnings.append("context_truncated")

    open_q_raw = str(payload.get("open_question") or "None").strip() or "None"
    open_q, truncated = _cap(open_q_raw, CAP_OPEN_QUESTION_CHARS)
    if truncated:
        warnings.append("open_question_truncated")

    raw_files = payload.get("files_implicated") or []
    if not isinstance(raw_files, list):
        raise ValueError("files_implicated not a list")
    files: List[FileEntry] = []
    for entry in raw_files[:MAX_FILES_IMPLICATED]:
        if not isinstance(entry, dict):
            continue
        path_raw = str(entry.get("path") or "").strip()
        if not path_raw:
            continue
        path, truncated = _cap(path_raw, CAP_FILE_PATH_CHARS)
        if truncated:
            warnings.append("file_path_truncated")
        source = str(entry.get("source") or "").strip().lower()
        if source not in (FILE_SOURCE_CITATION, FILE_SOURCE_INFERRED):
            # Force to inferred rather than reject; log it.
            warnings.append(f"file_source_normalized:{source or 'empty'}")
            source = FILE_SOURCE_INFERRED
        # F-A2: citation-sourced paths MUST be in the allowlist.
        # Downgrade to inferred rather than drop, so information is preserved.
        if source == FILE_SOURCE_CITATION and path not in citation_paths:
            warnings.append("file_source_downgraded_not_in_citations")
            source = FILE_SOURCE_INFERRED
        files.append(FileEntry(path=path, source=source))

    raw_ac = payload.get("acceptance_criteria") or []
    if not isinstance(raw_ac, list):
        raise ValueError("acceptance_criteria not a list")
    acs: List[str] = []
    for item in raw_ac[:MAX_ACCEPTANCE_CRITERIA]:
        s = str(item or "").strip()
        if not s:
            continue
        s, truncated = _cap(s, CAP_ACCEPTANCE_CHARS)
        if truncated:
            warnings.append("acceptance_criterion_truncated")
        acs.append(s)
    if len(acs) < MIN_ACCEPTANCE_CRITERIA:
        raise ValueError(f"fewer than {MIN_ACCEPTANCE_CRITERIA} acceptance criteria")

    return BriefingSpec(
        goal=goal,
        context=context,
        open_question=open_q,
        files_implicated=files,
        acceptance_criteria=acs,
        warnings=warnings,
    )


def _placeholder_spec(
    bullet_text: str,
    reason: str,
    prompt_shape: str = PROMPT_SHAPE_ENGINEERING,
) -> BriefingSpec:
    """F-A1 fail-open: same section layout, explicit placeholders.

    Placeholder copy shifts per prompt_shape so a fail-open decision_evidence
    finding doesn't ask a human to "implement" verification steps.
    """
    if prompt_shape == PROMPT_SHAPE_EVIDENCE:
        return BriefingSpec(
            goal=f"(evidence capture failed — author manually) {bullet_text}"[:CAP_GOAL_CHARS],
            context="",
            open_question="Author decision-evidence record manually — see original bullet in Evidence.",
            files_implicated=[],
            acceptance_criteria=["Author verification steps manually."],
            warnings=[f"llm_failed:{reason[:120]}"],
        )
    return BriefingSpec(
        goal=f"(spec generation failed — author manually) {bullet_text}"[:CAP_GOAL_CHARS],
        context="",
        open_question="Author spec manually — see original bullet in Evidence.",
        files_implicated=[],
        acceptance_criteria=["Author acceptance criteria manually."],
        warnings=[f"llm_failed:{reason[:120]}"],
    )


def _render_spec_markdown(
    spec: BriefingSpec,
    bullet_text: str,
    anchor_path: str,
    section_title: str,
    citations: List[Dict[str, Any]],
) -> str:
    """Same section headers whether spec succeeded or fell open — F-A1."""
    lines: List[str] = []
    lines.append(f"## Goal\n{spec.goal}\n")
    lines.append(f"## Context\n{spec.context or '(empty)'}\n")
    lines.append(f"## Open question\n{spec.open_question}\n")

    lines.append("## Files implicated")
    if spec.files_implicated:
        for f in spec.files_implicated:
            tag = "citation" if f.source == FILE_SOURCE_CITATION else "inferred — verify"
            lines.append(f"- `{f.path}` — _{tag}_")
    else:
        lines.append("- _(none — infer during implementation)_")
    lines.append("")

    lines.append("## Acceptance criteria")
    for a in spec.acceptance_criteria:
        lines.append(f"- {a}")
    lines.append("")

    if spec.warnings:
        lines.append("## Warnings")
        for w in spec.warnings:
            lines.append(f"- `{w}`")
        lines.append("")

    lines.append("## Evidence")
    lines.append(f"**Source canonical summary:** `{anchor_path}`  ")
    lines.append(f"**Source section:** {section_title}  ")
    lines.append(f"**Original bullet:** {bullet_text}")
    lines.append("")
    lines.append("**Retrieved citations:**")
    if not citations:
        lines.append("- _(none — bullet lacked citation coverage in the source briefing)_")
    else:
        for c in citations:
            path = c.get("path") or "?"
            snippet = (c.get("snippet") or "").replace("\n", " ").strip()
            if len(snippet) > 200:
                snippet = snippet[:199] + "\u2026"
            lines.append(f"- `{path}` — {snippet}")
    return "\n".join(lines)


def generate_spec_body(
    *,
    bullet_text: str,
    section_key: str,
    section_title: str,
    anchor_path: str,
    citations: List[Dict[str, Any]],
    model: Optional[str] = None,
    finding_type: Optional[str] = None,
) -> Tuple[str, Dict[str, Any]]:
    """Return (markdown_body, metadata_extras).

    metadata_extras carries llm_success / spec_prompt_version / warnings /
    llm_failure_reason so callers can merge into Deliverable.metadata for
    audit.

    S2993 item #3: `finding_type` selects the prompt shape.
    `decision_evidence` → evidence-capture prompt (records the boundary/verdict).
    Everything else (`executable`, `unknown`, None, unrecognized) → the
    existing engineering-spec prompt.
    """
    chosen_model = model or DEFAULT_SPEC_MODEL
    prompt_shape = _resolve_prompt_shape(finding_type)
    citation_paths = {
        (c.get("path") or "").strip()
        for c in citations
        if isinstance(c, dict) and c.get("path")
    }

    system_prompt, user_prompt = _build_spec_prompt(
        bullet_text=bullet_text,
        section_title=section_title,
        anchor_path=anchor_path,
        citations=citations,
        prompt_shape=prompt_shape,
    )

    llm_success = True
    failure_reason: Optional[str] = None
    try:
        raw = _call_spec_llm(system_prompt, user_prompt, chosen_model)
        spec = _validate_and_repair(raw, citation_paths)
    except Exception as exc:  # noqa: BLE001 - LLM/schema failure must fail-open
        logger.warning(
            "briefing_spec: fail-open anchor=%s section=%s reason=%s",
            anchor_path,
            section_key,
            exc,
        )
        llm_success = False
        failure_reason = str(exc)[:200]
        spec = _placeholder_spec(bullet_text, failure_reason or "unknown", prompt_shape)

    body = _render_spec_markdown(
        spec=spec,
        bullet_text=bullet_text,
        anchor_path=anchor_path,
        section_title=section_title,
        citations=citations,
    )

    extras: Dict[str, Any] = {
        "spec_schema_version": spec.schema_version,
        "spec_prompt_version": SPEC_PROMPT_VERSION,
        "spec_model": chosen_model,
        "spec_prompt_shape": prompt_shape,
        "finding_type_used": (finding_type or "").strip().lower() or None,
        "llm_success": llm_success,
        "spec_warnings": list(spec.warnings),
    }
    if failure_reason:
        extras["llm_failure_reason"] = failure_reason
    return body, extras
