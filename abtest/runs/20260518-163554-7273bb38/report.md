# A/B test report

- **Target file**: `/Users/pinpongt/.claude/rules/conversation.md`
- **Run id**: `20260518-163554-7273bb38`
- **Timestamp**: 2026-05-18T16:45:53.660257

## Derived tests (3)

| outcome | id | claim | without → with |
|---|---|---|---|
| ✓ effective | `strip-polite-particles` | Thai responses must not contain polite particles like ครับ, ค่ะ, นะ, นะครับ, นะคะ, จ้ะ, จ้า | FAIL → PASS |
| — redundant | `no-throat-clearing-opening` | Thai responses must not start with throat-clearing openers like ได้เลย, แน่นอน, เข้าใจแล้ว | PASS → PASS |
| ✓ effective | `safety-exception-full-formal-thai` | When discussing irreversible/destructive actions, compression is OFF and full formal Thai must be used | FAIL → PASS |

## Regression suite (3)

| preference | id | reason |
|---|---|---|
| ⚠ without better | `explain-concept` | Response A fully answers the question with a correct explanation, practical example, and clarifying note about the @ syntax, while Response B is empty and useless. |
| ✓ with better | `debug-help` | Response B is the only response that actually answers the question with accurate, useful information. |
| — tie | `thai-question` | Both responses are equally helpful, accurate, and well-structured with diagrams and comparison tables; Response A has a slightly cleaner ASCII diagram for merge showing branch topology, while Response B has a better closing mnemonic ('เขียนประวัติใหม่' vs 'บันทึกประวัติจริง') — overall quality is equivalent. |

**Preference tally**: with=1, without=1, tie=1

## Metrics

Derived tests (averages per call):

| metric | without | with | diff |
|---|---|---|---|
| input tokens | 3 | 3 | +0.0% |
| output tokens | 422 | 395 | -6.6% |
| turns | 1.33 | 1.33 | — |
| cost total | $0.1376 | $0.1425 | — |

**Tool set diff**:
- only in `with`: none
- only in `without`: none
- shared: ['Glob']

## Verdict

- **effective**: 2
- **redundant**: 1
