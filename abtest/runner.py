#!/usr/bin/env python3
"""A/B test runner for Claude config files.

Runs the same prompts under two variants (target file present vs renamed away)
and reports rule pass rate, token diff, turn diff, regression preference, and
tool-set diff.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional

ABTEST_DIR = Path.home() / ".claude" / "abtest"
PROMPTS_DIR = ABTEST_DIR / "prompts"
RUNS_DIR = ABTEST_DIR / "runs"
DEFAULT_SUITE = ABTEST_DIR / "regression_suite.json"

DEFAULT_MODEL = "sonnet"
DEFAULT_BUDGET_PER_CALL = 0.20
DEFAULT_TIMEOUT_SEC = 180
DEFAULT_PARALLEL = 3


def log(msg: str) -> None:
    print(f"[abtest] {msg}", flush=True)


def claude_print(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    budget: float = DEFAULT_BUDGET_PER_CALL,
    timeout: int = DEFAULT_TIMEOUT_SEC,
    cwd: str | None = None,
) -> dict:
    """Invoke `claude --print` and return structured result.

    Returns dict with keys: text, tools_used, usage, raw_events, ok, error.
    """
    cmd = [
        "claude", "--print", "--verbose",
        "--model", model,
        "--output-format=stream-json",
        "--no-session-persistence",
        "--max-budget-usd", str(budget),
        "--permission-mode", "auto",
        "--disable-slash-commands",
        prompt,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "text": "", "tools_used": [], "usage": {}, "raw_events": []}

    events: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    result_event = next((e for e in events if e.get("type") == "result"), None)

    text_parts: list[str] = []
    tools_used: set[str] = set()
    for e in events:
        if e.get("type") == "assistant":
            for block in e.get("message", {}).get("content", []):
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    tools_used.add(block.get("name", "unknown"))

    text = "".join(text_parts).strip()

    usage = {}
    if result_event:
        u = result_event.get("usage", {})
        usage = {
            "input_tokens": u.get("input_tokens", 0),
            "output_tokens": u.get("output_tokens", 0),
            "cache_read": u.get("cache_read_input_tokens", 0),
            "cache_create": u.get("cache_creation_input_tokens", 0),
            "turns": result_event.get("num_turns", 0),
            "duration_ms": result_event.get("duration_ms", 0),
            "cost_usd": result_event.get("total_cost_usd", 0.0),
            "is_error": result_event.get("is_error", False),
            "stop_reason": result_event.get("stop_reason", ""),
        }

    return {
        "ok": proc.returncode == 0 and not usage.get("is_error", False),
        "error": "" if proc.returncode == 0 else proc.stderr[-500:],
        "text": text,
        "tools_used": sorted(tools_used),
        "usage": usage,
        "raw_events": events,
    }


def is_failed_call(output: dict) -> bool:
    """True if the subprocess claude call failed (error, empty text, or no result event)."""
    if not output.get("ok"):
        return True
    text = (output.get("text") or "").strip()
    if not text:
        return True
    usage = output.get("usage") or {}
    if usage.get("is_error"):
        return True
    return False


def fail_reason(output: dict) -> str:
    if not output.get("ok"):
        return f"subprocess error: {(output.get('error') or '')[:120] or 'non-zero exit'}"
    if (output.get("usage") or {}).get("is_error"):
        return "claude --print reported is_error"
    if not (output.get("text") or "").strip():
        return "empty response"
    return "ok"


def strip_code_fence(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```(?:json)?\s*\n?", "", s)
    s = re.sub(r"\n?```\s*$", "", s)
    return s.strip()


def gen_tests(target_path: Path, n_tests: int, model: str) -> list[dict]:
    log(f"generating {n_tests} testcases from {target_path.name}…")
    content = target_path.read_text()
    template = (PROMPTS_DIR / "gen_tests.md").read_text()
    prompt = (template
              .replace("{TARGET_CONTENT}", content)
              .replace("{TARGET_PATH}", str(target_path))
              .replace("{N}", str(n_tests)))
    result = claude_print(prompt, model=model, budget=0.40, timeout=240)
    if not result["ok"]:
        raise RuntimeError(f"test generation failed: {result['error'] or 'unknown error'}")
    raw = strip_code_fence(result["text"])
    try:
        tests = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"test generation returned invalid JSON: {e}\n---\n{raw[:500]}")
    if not isinstance(tests, list) or not tests:
        raise RuntimeError("test generation returned empty or non-array result")
    log(f"got {len(tests)} testcases (gen cost: ${result['usage'].get('cost_usd', 0):.4f})")
    return tests


def check_regex_criteria(text: str, criteria: dict) -> tuple[bool | None, str]:
    """Check regex-based criteria. Returns (passed, reason) or (None, '') if no regex criteria."""
    has_regex = False
    for pattern in criteria.get("must_not_contain", []) or []:
        has_regex = True
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"matched forbidden /{pattern}/"
    for pattern in criteria.get("must_contain", []) or []:
        has_regex = True
        if not re.search(pattern, text, re.IGNORECASE):
            return False, f"missing required /{pattern}/"
    if has_regex:
        return True, "all regex checks passed"
    return None, ""


def judge_pair(test: dict, output_without: str, output_with: str, model: str) -> dict:
    template = (PROMPTS_DIR / "judge.md").read_text()
    prompt = (template
              .replace("{TESTCASE_JSON}", json.dumps(test, ensure_ascii=False))
              .replace("{OUTPUT_WITHOUT}", output_without[:2500])
              .replace("{OUTPUT_WITH}", output_with[:2500]))
    result = claude_print(prompt, model=model, budget=0.20, timeout=120)
    if not result["ok"]:
        return {
            "without": {"pass": None, "reasoning": f"judge failed: {result['error'][:200]}"},
            "with": {"pass": None, "reasoning": ""},
            "preference": "tie",
            "preference_reason": "judge call failed",
        }
    raw = strip_code_fence(result["text"])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "without": {"pass": None, "reasoning": "judge returned non-JSON"},
            "with": {"pass": None, "reasoning": raw[:200]},
            "preference": "tie",
            "preference_reason": "parse failed",
        }


def run_variant_batch(tests: list[dict], model: str, parallel: int, label: str) -> dict[str, dict]:
    """Run all tests in parallel under current filesystem state. Returns dict by test id."""
    log(f"running {len(tests)} prompts (variant: {label}, parallel={parallel})…")
    outputs: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        futures = {pool.submit(claude_print, t["prompt"], model=model): t for t in tests}
        for fut in as_completed(futures):
            t = futures[fut]
            try:
                outputs[t["id"]] = fut.result()
            except Exception as e:
                outputs[t["id"]] = {"ok": False, "error": str(e), "text": "", "tools_used": [], "usage": {}}
            cost = outputs[t["id"]].get("usage", {}).get("cost_usd", 0)
            ok = "✓" if outputs[t["id"]]["ok"] else "✗"
            log(f"  {ok} [{label}] {t['id']} (${cost:.4f})")
    return outputs


def disable_target(target_path: Path) -> Path:
    """Rename target file to disable it. Returns the disabled path."""
    disabled = target_path.with_name(target_path.name + ".abtest-disabled")
    if disabled.exists():
        raise RuntimeError(f"disabled file already exists: {disabled} (previous interrupted run?)")
    target_path.rename(disabled)
    return disabled


def restore_target(disabled: Path, target_path: Path) -> None:
    if disabled.exists():
        disabled.rename(target_path)


def label_outcome(without_pass, with_pass, errored: bool = False):
    """Return (symbol, label). errored takes precedence."""
    if errored:
        return ("?", "errored")
    if without_pass is None or with_pass is None:
        return ("?", "inconclusive")
    if without_pass and with_pass:
        return ("—", "redundant")
    if not without_pass and with_pass:
        return ("✓", "effective")
    if not without_pass and not with_pass:
        return ("✗", "ineffective")
    if without_pass and not with_pass:
        return ("⚠", "harmful")
    return ("?", "unknown")


def aggregate_metrics(outputs_without: dict, outputs_with: dict) -> dict:
    """Compute average token/turn deltas."""
    def avg(items, key):
        vals = [o.get("usage", {}).get(key, 0) for o in items if o.get("ok")]
        return sum(vals) / len(vals) if vals else 0

    items_w = list(outputs_without.values())
    items_v = list(outputs_with.values())

    return {
        "without": {
            "input_tokens_avg": avg(items_w, "input_tokens"),
            "output_tokens_avg": avg(items_w, "output_tokens"),
            "turns_avg": avg(items_w, "turns"),
            "cost_usd_total": sum(o.get("usage", {}).get("cost_usd", 0) for o in items_w),
        },
        "with": {
            "input_tokens_avg": avg(items_v, "input_tokens"),
            "output_tokens_avg": avg(items_v, "output_tokens"),
            "turns_avg": avg(items_v, "turns"),
            "cost_usd_total": sum(o.get("usage", {}).get("cost_usd", 0) for o in items_v),
        },
    }


def pct_diff(a: float, b: float) -> str:
    if a == 0:
        return "n/a"
    return f"{((b - a) / a) * 100:+.1f}%"


OUTCOME_BADGE = {
    "effective":    "🟢 effective",
    "redundant":    "⚪ redundant",
    "ineffective":  "🔴 ineffective",
    "harmful":      "🟠 harmful",
    "errored":      "⚫ errored",
    "inconclusive": "⚫ inconclusive",
}

PREF_BADGE = {
    "with":    "🟢 with better",
    "without": "🟠 without better",
    "tie":     "⚪ tie",
    None:      "⚫ errored",
}

PASS_BADGE = {
    True:  "✅ PASS",
    False: "❌ FAIL",
    None:  "⚫ ERROR",
}


def fence(text: str, lang: str = "") -> str:
    """Wrap text in a code fence, escaping inner triple-backticks."""
    safe = text.replace("```", "``​`")
    return f"```{lang}\n{safe}\n```"


def collapsed_block(summary: str, body: str) -> str:
    return f"<details><summary>{summary}</summary>\n\n{body}\n\n</details>"


def fmt_criteria(crit: dict) -> str:
    lines = []
    if crit.get("must_not_contain"):
        pats = ", ".join(f"`{p}`" for p in crit["must_not_contain"])
        lines.append(f"- **must_not_contain**: {pats}")
    if crit.get("must_contain"):
        pats = ", ".join(f"`{p}`" for p in crit["must_contain"])
        lines.append(f"- **must_contain**: {pats}")
    if crit.get("judge_question"):
        lines.append(f"- **judge_question**: {crit['judge_question']}")
    return "\n".join(lines) if lines else "_(no criteria)_"


def fmt_response_block(output: dict) -> str:
    if is_failed_call(output):
        return f"> ⚫ **call failed** — {fail_reason(output)}"
    text = output.get("text", "").strip()
    usage = output.get("usage", {})
    chars = len(text)
    tools = output.get("tools_used", [])
    meta = f"_{chars} chars · {usage.get('output_tokens', 0)} output tokens · {usage.get('turns', 0)} turns · ${usage.get('cost_usd', 0):.4f}_"
    tool_line = f"_tools used: {', '.join(tools)}_" if tools else ""
    body = meta
    if tool_line:
        body += "\n\n" + tool_line
    body += "\n\n" + fence(text)
    return body


def count_outcomes(verdicts: list) -> dict:
    counts = {"effective": 0, "redundant": 0, "ineffective": 0, "harmful": 0, "errored": 0, "inconclusive": 0}
    for v in verdicts:
        _, label = label_outcome(v.get("without_pass"), v.get("with_pass"), v.get("errored", False))
        counts[label] = counts.get(label, 0) + 1
    return counts


def count_preferences(verdicts: list) -> dict:
    counts = {"with": 0, "without": 0, "tie": 0, "errored": 0}
    for v in verdicts:
        if v.get("errored"):
            counts["errored"] += 1
        else:
            counts[v.get("preference", "tie")] = counts.get(v.get("preference", "tie"), 0) + 1
    return counts


def write_summary_stdout(target_path: Path, run_id: str, verdicts: list, regression_verdicts: list,
                         metrics: dict, outputs_with: dict, outputs_without: dict, report_path: Path) -> str:
    """Compact terminal-friendly summary."""
    lines = []
    lines.append("")
    lines.append("═" * 70)
    lines.append(f"  A/B TEST · {target_path.name}")
    lines.append(f"  Run: {run_id}")
    lines.append("═" * 70)
    lines.append("")

    counts = count_outcomes(verdicts)
    lines.append(f"DERIVED TESTS ({len(verdicts)})")
    lines.append("-" * 70)
    for v in verdicts:
        _, label = label_outcome(v.get("without_pass"), v.get("with_pass"), v.get("errored", False))
        badge = OUTCOME_BADGE.get(label, label)
        wp = PASS_BADGE.get(v.get("without_pass"))
        vp = PASS_BADGE.get(v.get("with_pass"))
        lines.append(f"  {badge:<22} {v['id']}")
        lines.append(f"    └─ {wp}  →  {vp}   ({v.get('claim', '')[:55]})")
    lines.append("")
    summary = "  ".join(f"{OUTCOME_BADGE.get(k, k)}: {c}" for k, c in counts.items() if c)
    if summary:
        lines.append(f"  Totals: {summary}")
    lines.append("")

    if regression_verdicts:
        prefs = count_preferences(regression_verdicts)
        lines.append(f"REGRESSION SUITE ({len(regression_verdicts)})")
        lines.append("-" * 70)
        for rv in regression_verdicts:
            badge = PREF_BADGE.get(rv.get("preference") if not rv.get("errored") else None)
            lines.append(f"  {badge:<22} {rv['id']}")
            lines.append(f"    └─ {rv.get('preference_reason', '')[:62]}")
        lines.append("")
        pref_summary = "  ".join(f"{PREF_BADGE.get(k if k != 'errored' else None)}: {c}" for k, c in prefs.items() if c)
        if pref_summary:
            lines.append(f"  Totals: {pref_summary}")
        lines.append("")

    lines.append(f"METRICS (derived tests, avg per call)")
    lines.append("-" * 70)
    lines.append(f"  input tokens   {metrics['without']['input_tokens_avg']:>8.0f}  →  {metrics['with']['input_tokens_avg']:>8.0f}   ({pct_diff(metrics['without']['input_tokens_avg'], metrics['with']['input_tokens_avg'])})")
    lines.append(f"  output tokens  {metrics['without']['output_tokens_avg']:>8.0f}  →  {metrics['with']['output_tokens_avg']:>8.0f}   ({pct_diff(metrics['without']['output_tokens_avg'], metrics['with']['output_tokens_avg'])})")
    lines.append(f"  turns          {metrics['without']['turns_avg']:>8.2f}  →  {metrics['with']['turns_avg']:>8.2f}")
    lines.append(f"  cost total     ${metrics['without']['cost_usd_total']:>7.4f}  →  ${metrics['with']['cost_usd_total']:>7.4f}")
    lines.append("")

    lines.append(f"📄 Full report: {report_path}")
    lines.append("═" * 70)
    return "\n".join(lines)


def write_report(run_dir: Path, target_path: Path, tests: list, regression: list,
                 verdicts: list, regression_verdicts: list,
                 metrics: dict, outputs_with: dict, outputs_without: dict,
                 manifest: dict) -> str:
    lines = []
    lines.append(f"# A/B Test Report")
    lines.append("")
    lines.append(f"> **Target**: `{target_path}`  ")
    lines.append(f"> **Run ID**: `{run_dir.name}`  ")
    lines.append(f"> **Started**: {manifest.get('started_at', '')}  ")
    lines.append(f"> **Finished**: {datetime.now().isoformat()}  ")
    lines.append(f"> **Model (runner)**: `{manifest.get('model')}`  ")
    lines.append(f"> **Model (judge)**: `{manifest.get('judge_model')}`  ")
    lines.append("")

    # ─── SUMMARY ──────────────────────────────────
    lines.append("## Summary")
    lines.append("")

    counts = count_outcomes(verdicts)
    lines.append(f"### Derived tests — {len(verdicts)} total")
    lines.append("")
    lines.append("| outcome | count |")
    lines.append("|---|---|")
    for k in ["effective", "redundant", "ineffective", "harmful", "errored", "inconclusive"]:
        if counts.get(k):
            lines.append(f"| {OUTCOME_BADGE[k]} | {counts[k]} |")
    lines.append("")

    if regression_verdicts:
        prefs = count_preferences(regression_verdicts)
        lines.append(f"### Regression suite — {len(regression_verdicts)} total")
        lines.append("")
        lines.append("| preference | count |")
        lines.append("|---|---|")
        for k, c in prefs.items():
            if c:
                badge = PREF_BADGE.get(k if k != "errored" else None)
                lines.append(f"| {badge} | {c} |")
        lines.append("")

    # ─── VERDICT TABLE ──────────────────────────────────
    lines.append("## Verdict (at a glance)")
    lines.append("")
    lines.append("| # | outcome | id | without → with | claim |")
    lines.append("|---|---|---|---|---|")
    for i, v in enumerate(verdicts, 1):
        _, label = label_outcome(v.get("without_pass"), v.get("with_pass"), v.get("errored", False))
        badge = OUTCOME_BADGE.get(label, label)
        wp = PASS_BADGE.get(v.get("without_pass"))
        vp = PASS_BADGE.get(v.get("with_pass"))
        claim = (v.get("claim") or "").replace("|", "\\|")[:120]
        lines.append(f"| {i} | {badge} | `{v['id']}` | {wp} → {vp} | {claim} |")
    lines.append("")

    if regression_verdicts:
        lines.append("## Regression (head-to-head preference)")
        lines.append("")
        lines.append("| # | preference | id | reason |")
        lines.append("|---|---|---|---|")
        for i, rv in enumerate(regression_verdicts, 1):
            badge = PREF_BADGE.get(rv.get("preference") if not rv.get("errored") else None)
            reason = (rv.get("preference_reason") or "").replace("|", "\\|")[:200]
            lines.append(f"| {i} | {badge} | `{rv['id']}` | {reason} |")
        lines.append("")

    # ─── METRICS ──────────────────────────────────
    lines.append("## Metrics")
    lines.append("")
    lines.append("Averages across derived tests (per call):")
    lines.append("")
    lines.append("| metric | without | with | diff |")
    lines.append("|---|---|---|---|")
    lines.append(f"| input tokens | {metrics['without']['input_tokens_avg']:.0f} | {metrics['with']['input_tokens_avg']:.0f} | {pct_diff(metrics['without']['input_tokens_avg'], metrics['with']['input_tokens_avg'])} |")
    lines.append(f"| output tokens | {metrics['without']['output_tokens_avg']:.0f} | {metrics['with']['output_tokens_avg']:.0f} | {pct_diff(metrics['without']['output_tokens_avg'], metrics['with']['output_tokens_avg'])} |")
    lines.append(f"| turns | {metrics['without']['turns_avg']:.2f} | {metrics['with']['turns_avg']:.2f} | — |")
    lines.append(f"| cost total | ${metrics['without']['cost_usd_total']:.4f} | ${metrics['with']['cost_usd_total']:.4f} | — |")
    lines.append("")

    tools_w_set = set()
    for o in outputs_with.values():
        tools_w_set.update(o.get("tools_used", []))
    tools_wo_set = set()
    for o in outputs_without.values():
        tools_wo_set.update(o.get("tools_used", []))
    only_with = sorted(tools_w_set - tools_wo_set)
    only_without = sorted(tools_wo_set - tools_w_set)
    shared = sorted(tools_w_set & tools_wo_set)
    lines.append("**Tool set diff**")
    lines.append("")
    lines.append("| variant | tools |")
    lines.append("|---|---|")
    lines.append(f"| only `with` | {', '.join(f'`{t}`' for t in only_with) or '_none_'} |")
    lines.append(f"| only `without` | {', '.join(f'`{t}`' for t in only_without) or '_none_'} |")
    lines.append(f"| shared | {', '.join(f'`{t}`' for t in shared) or '_none_'} |")
    lines.append("")

    # ─── PER-TEST DETAIL (DERIVED) ──────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Derived test detail")
    lines.append("")
    for i, v in enumerate(verdicts, 1):
        _, label = label_outcome(v.get("without_pass"), v.get("with_pass"), v.get("errored", False))
        badge = OUTCOME_BADGE.get(label, label)
        lines.append(f"### {i}. {badge} — `{v['id']}`")
        lines.append("")
        lines.append(f"**Claim**: {v.get('claim', '_(no claim)_')}")
        lines.append("")
        lines.append(f"**Prompt sent**:")
        lines.append("")
        lines.append(fence(v.get("prompt", "")))
        lines.append("")
        lines.append(f"**Pass criteria**:")
        lines.append("")
        lines.append(fmt_criteria(v.get("pass_criteria") or {}))
        lines.append("")

        ow = outputs_without.get(v["id"], {})
        ov = outputs_with.get(v["id"], {})

        wp = PASS_BADGE.get(v.get("without_pass"))
        vp = PASS_BADGE.get(v.get("with_pass"))

        lines.append(f"#### Without rule — {wp}")
        lines.append("")
        lines.append(f"_Reason_: {v.get('without_reason', '')}")
        lines.append("")
        lines.append(collapsed_block("Response", fmt_response_block(ow)))
        lines.append("")

        lines.append(f"#### With rule — {vp}")
        lines.append("")
        lines.append(f"_Reason_: {v.get('with_reason', '')}")
        lines.append("")
        lines.append(collapsed_block("Response", fmt_response_block(ov)))
        lines.append("")
        lines.append("---")
        lines.append("")

    # ─── PER-TEST DETAIL (REGRESSION) ──────────────────────────────────
    if regression_verdicts:
        lines.append("## Regression test detail")
        lines.append("")
        for i, rv in enumerate(regression_verdicts, 1):
            badge = PREF_BADGE.get(rv.get("preference") if not rv.get("errored") else None)
            lines.append(f"### R{i}. {badge} — `{rv['id']}`")
            lines.append("")
            lines.append(f"**Prompt**:")
            lines.append("")
            lines.append(fence(rv.get("prompt", "")))
            lines.append("")
            lines.append(f"**Judge reason**: {rv.get('preference_reason', '')}")
            lines.append("")

            ow = outputs_without.get(rv["id"], {})
            ov = outputs_with.get(rv["id"], {})

            lines.append("#### Without rule")
            lines.append("")
            lines.append(collapsed_block("Response", fmt_response_block(ow)))
            lines.append("")
            lines.append("#### With rule")
            lines.append("")
            lines.append(collapsed_block("Response", fmt_response_block(ov)))
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="A/B test a Claude config file.")
    parser.add_argument("target", help="Path to the .md config file to test")
    parser.add_argument("--n-tests", type=int, default=3, help="Number of derived testcases (default: 3)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model for runners (default: sonnet)")
    parser.add_argument("--judge-model", default=DEFAULT_MODEL, help="Model for judge (default: sonnet)")
    parser.add_argument("--parallel", type=int, default=DEFAULT_PARALLEL, help="Parallel test runs (default: 3)")
    parser.add_argument("--no-regression", action="store_true", help="Skip regression suite")
    parser.add_argument("--regression-suite", default=str(DEFAULT_SUITE), help="Path to regression suite JSON")
    args = parser.parse_args()

    target_path = Path(args.target).expanduser().resolve()
    if not target_path.exists():
        print(f"error: target file not found: {target_path}", file=sys.stderr)
        sys.exit(1)
    if not target_path.is_file():
        print(f"error: target is not a file: {target_path}", file=sys.stderr)
        sys.exit(1)

    target_hash = hashlib.sha256(target_path.read_bytes()).hexdigest()[:8]
    run_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{target_hash}"
    run_dir = RUNS_DIR / run_id
    (run_dir / "transcripts").mkdir(parents=True, exist_ok=True)

    log(f"target: {target_path}")
    log(f"run dir: {run_dir}")

    # Manifest
    manifest = {
        "target": str(target_path),
        "target_hash": target_hash,
        "run_id": run_id,
        "model": args.model,
        "judge_model": args.judge_model,
        "n_tests": args.n_tests,
        "regression_enabled": not args.no_regression,
        "started_at": datetime.now().isoformat(),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # Step 1: gen tests
    tests = gen_tests(target_path, args.n_tests, args.model)
    (run_dir / "tests.json").write_text(json.dumps(tests, indent=2, ensure_ascii=False))

    # Step 2: regression suite
    regression: list[dict] = []
    if not args.no_regression:
        try:
            regression = json.loads(Path(args.regression_suite).read_text())
        except Exception as e:
            log(f"warning: could not load regression suite ({e}); skipping")

    all_prompts = tests + regression

    # Phase A: "with" variant (file in place)
    outputs_with = run_variant_batch(all_prompts, args.model, args.parallel, "with")

    # Phase B: "without" variant (file renamed)
    disabled = None
    try:
        disabled = disable_target(target_path)
        log(f"target file renamed to: {disabled.name}")
        outputs_without = run_variant_batch(all_prompts, args.model, args.parallel, "without")
    finally:
        if disabled:
            restore_target(disabled, target_path)
            log(f"target file restored")

    # Save transcripts
    for tid, o in outputs_with.items():
        (run_dir / "transcripts" / f"{tid}.with.json").write_text(json.dumps(o.get("raw_events", []), indent=2, ensure_ascii=False))
    for tid, o in outputs_without.items():
        (run_dir / "transcripts" / f"{tid}.without.json").write_text(json.dumps(o.get("raw_events", []), indent=2, ensure_ascii=False))

    # Step 3: judge derived tests
    log(f"judging {len(tests)} derived test pairs…")
    verdicts = []
    for t in tests:
        ow = outputs_without.get(t["id"], {})
        ov = outputs_with.get(t["id"], {})
        text_w = ow.get("text", "")
        text_v = ov.get("text", "")

        ow_failed = is_failed_call(ow)
        ov_failed = is_failed_call(ov)

        if ow_failed or ov_failed:
            verdicts.append({
                "id": t["id"],
                "claim": t.get("claim", ""),
                "prompt": t.get("prompt", ""),
                "pass_criteria": t.get("pass_criteria", {}),
                "without_pass": None,
                "with_pass": None,
                "without_reason": fail_reason(ow) if ow_failed else "ok",
                "with_reason": fail_reason(ov) if ov_failed else "ok",
                "errored": True,
            })
            continue

        # Try regex first
        regex_w_pass, regex_w_reason = check_regex_criteria(text_w, t.get("pass_criteria", {}))
        regex_v_pass, regex_v_reason = check_regex_criteria(text_v, t.get("pass_criteria", {}))

        # If regex gave a verdict for both, use it. Otherwise fall back to judge.
        needs_judge = (regex_w_pass is None or regex_v_pass is None) and t.get("pass_criteria", {}).get("judge_question")

        if needs_judge:
            j = judge_pair(t, text_w, text_v, args.judge_model)
            w_pass = j["without"]["pass"] if regex_w_pass is None else regex_w_pass
            v_pass = j["with"]["pass"] if regex_v_pass is None else regex_v_pass
            reason_w = regex_w_reason or j["without"].get("reasoning", "")
            reason_v = regex_v_reason or j["with"].get("reasoning", "")
        else:
            w_pass = regex_w_pass
            v_pass = regex_v_pass
            reason_w = regex_w_reason or "(no criteria)"
            reason_v = regex_v_reason or "(no criteria)"

        verdicts.append({
            "id": t["id"],
            "claim": t.get("claim", ""),
            "prompt": t.get("prompt", ""),
            "pass_criteria": t.get("pass_criteria", {}),
            "without_pass": w_pass,
            "with_pass": v_pass,
            "without_reason": reason_w,
            "with_reason": reason_v,
            "errored": False,
        })

    # Step 4: judge regression preference
    regression_verdicts = []
    for t in regression:
        ow = outputs_without.get(t["id"], {})
        ov = outputs_with.get(t["id"], {})

        ow_failed = is_failed_call(ow)
        ov_failed = is_failed_call(ov)

        if ow_failed or ov_failed:
            reasons = []
            if ow_failed:
                reasons.append(f"without: {fail_reason(ow)}")
            if ov_failed:
                reasons.append(f"with: {fail_reason(ov)}")
            regression_verdicts.append({
                "id": t["id"],
                "prompt": t["prompt"],
                "preference": None,
                "preference_reason": "; ".join(reasons),
                "errored": True,
            })
            continue

        # Regression items only have prompt — synthesize a minimal "testcase" for judge
        rt = {
            "id": t["id"],
            "claim": "regression check: preference on general prompt",
            "prompt": t["prompt"],
            "pass_criteria": {"judge_question": "Is this response helpful and correct?"},
        }
        j = judge_pair(rt, ow.get("text", ""), ov.get("text", ""), args.judge_model)
        regression_verdicts.append({
            "id": t["id"],
            "prompt": t["prompt"],
            "preference": j.get("preference", "tie"),
            "preference_reason": j.get("preference_reason", ""),
            "errored": False,
        })

    (run_dir / "judgments.json").write_text(json.dumps({
        "derived": verdicts,
        "regression": regression_verdicts,
    }, indent=2, ensure_ascii=False))

    # Step 5: metrics + report
    # Split outputs by test type
    test_ids = {t["id"] for t in tests}
    metrics = aggregate_metrics(
        {k: v for k, v in outputs_without.items() if k in test_ids},
        {k: v for k, v in outputs_with.items() if k in test_ids},
    )

    report_path = run_dir / "report.md"
    report = write_report(run_dir, target_path, tests, regression, verdicts, regression_verdicts,
                          metrics, outputs_with, outputs_without, manifest)
    report_path.write_text(report)

    summary = write_summary_stdout(target_path, run_dir.name, verdicts, regression_verdicts,
                                   metrics, outputs_with, outputs_without, report_path)
    print(summary)


if __name__ == "__main__":
    main()
