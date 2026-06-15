---
name: diagnose
description: Disciplined diagnosis loop for hard bugs and performance regressions — reproduce → minimise → hypothesise → instrument → fix → regression-test. Use when user says "diagnose this", "debug this", reports a bug, says something is broken/throwing/failing, or describes a performance regression.
allowed-tools: Bash, Read, Edit, Write, Grep, Glob, AskUserQuestion, Agent, LSP
---

# Diagnose

A discipline for hard bugs. Skip phases only when explicitly justified.

When exploring an unfamiliar area, spawn `🐶dog_explore` (`model: haiku`, `mode: auto`) to surface the domain glossary and any relevant ADRs before forming hypotheses.

## Phase 1 — Build a feedback loop

**This is the skill.** Everything else is mechanical. A fast, deterministic, agent-runnable pass/fail signal turns bisection, hypothesis-testing, and instrumentation into routine work. Without one, no amount of staring at code helps.

Be aggressive and creative. Try in roughly this order:

1. **Failing test** at the seam reaching the bug (unit, integration, e2e).
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** diffing stdout against a known-good snapshot.
4. **Headless browser** (Playwright / Puppeteer) asserting on DOM/console/network.
5. **Replay a captured trace** — saved payload / event log run through the code path in isolation.
6. **Throwaway harness** — minimal subset of the system that exercises the bug code path with one call.
7. **Property / fuzz loop** — 1000 random inputs, look for the failure mode.
8. **Bisection harness** — automate "boot at state X, check" for `git bisect run`.
9. **Differential loop** — same input through old vs new, diff outputs.
10. **HITL bash script** — last resort. Drive the human; capture their output back into the loop.

### Iterate on the loop itself

- Faster? (Cache setup, narrow scope.)
- Sharper signal? (Assert on the symptom, not "didn't crash".)
- More deterministic? (Pin time, seed RNG, freeze network.)

A 2-second deterministic loop is a debugging superpower. A 30-second flaky one is barely better than nothing.

### Non-deterministic bugs

Goal is a **higher reproduction rate**, not a clean repro. Loop 100×, parallelise, inject sleeps. A 50%-flake bug is debuggable; 1% is not.

### When you genuinely cannot build a loop

Stop and say so. List what you tried. Ask the user — via `AskUserQuestion` — for one of:

- Access to a reproducing environment
- A captured artifact (HAR, logs, core dump, timestamped screen recording)
- Permission for temporary production instrumentation

Do not proceed to hypothesise without a loop.

## Phase 2 — Reproduce

Run the loop. Confirm:

- The failure matches what the **user** described (wrong bug = wrong fix).
- It reproduces reliably (or at a high enough rate for non-determinism).
- The exact symptom is captured for later verification.

## Phase 3 — Hypothesise

Generate **3–5 ranked hypotheses** before testing any of them. Single-hypothesis generation anchors on the first plausible idea.

Each must be **falsifiable**:

> "If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse."

If you can't state the prediction, it's a vibe — discard or sharpen.

**Show the ranked list via `AskUserQuestion`** before instrumenting. The user often re-ranks instantly with domain knowledge. Don't block if they're AFK — proceed with your ranking.

## Phase 4 — Instrument

Each probe maps to one prediction. **Change one variable at a time.**

Tool preference:

1. **Debugger / REPL inspection** if the env allows. One breakpoint beats ten logs.
2. **Targeted logs** at boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag every debug log** with a unique prefix like `[DEBUG-a4f2]`. Cleanup at the end is one `grep -rn`.

**Perf branch**: for performance regressions, logs are usually wrong. Establish a baseline measurement (timing harness, `performance.now()`, profiler, query plan) and bisect. Measure first, fix second.

## Phase 5 — Fix + regression test

Write the regression test **before the fix**, but only if a **correct seam** exists — one where the test exercises the **real bug pattern** at the call site. A unit test that can't replicate the calling chain that triggered the bug gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it for Phase 6 — the architecture is preventing the bug from being locked down.

If a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 loop against the original scenario.

## Phase 6 — Cleanup + post-mortem

Required before declaring done:

- [ ] Original repro no longer reproduces (re-run Phase 1 loop).
- [ ] Regression test passes (or absence of seam is documented).
- [ ] All `[DEBUG-...]` instrumentation removed (`grep -rn '\[DEBUG-' .`).
- [ ] Throwaway prototypes deleted (or moved to a clearly-marked debug location).
- [ ] The hypothesis that turned out correct is stated in the commit / PR message — so the next debugger learns.

**Then ask: what would have prevented this bug?** If the answer is architectural (no good test seam, tangled callers, hidden coupling), hand off to `/improve-codebase-architecture` with the specifics. Recommend **after** the fix is in — you have more information than at the start.

For security-sensitive fixes, spawn `👨🏼‍🦳zoo_keeper` (`model: sonnet`, `mode: auto`) before committing.

## Output to user

Compressed Thai per phase transition. Hypothesis list and fix summary in clearer English when ambiguity would be dangerous (per global safety-exception rule).
