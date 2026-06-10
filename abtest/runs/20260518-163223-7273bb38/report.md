# A/B test report

- **Target file**: `/Users/pinpongt/.claude/rules/conversation.md`
- **Run id**: `20260518-163223-7273bb38`
- **Timestamp**: 2026-05-18T16:33:28.918729

## Derived tests (1)

| outcome | id | claim | without → with |
|---|---|---|---|
| ✓ effective | `strip-polite-particles` | Thai responses must not contain polite particles like ครับ, ค่ะ, นะ, นะครับ, นะคะ, จ้ะ, จ้า | FAIL → PASS |

## Metrics

Derived tests (averages per call):

| metric | without | with | diff |
|---|---|---|---|
| input tokens | 4 | 5 | +25.0% |
| output tokens | 324 | 421 | +29.9% |
| turns | 2.00 | 3.00 | — |
| cost total | $0.0493 | $0.0821 | — |

**Tool set diff**:
- only in `with`: none
- only in `without`: none
- shared: ['Glob']

## Verdict

- **effective**: 1
