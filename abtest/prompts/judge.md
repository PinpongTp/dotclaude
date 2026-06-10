You are judging whether two Claude responses follow a specific rule.

## Testcase

```json
{TESTCASE_JSON}
```

## Response A (variant: "without" — rule file removed)

```
{OUTPUT_WITHOUT}
```

## Response B (variant: "with" — rule file present)

```
{OUTPUT_WITH}
```

## Instructions

Evaluate each response independently against the testcase's `pass_criteria`.

If `pass_criteria.judge_question` is set, answer it (yes = pass, no = fail) for each response. If only regex criteria exist (`must_contain` / `must_not_contain`), they are already evaluated mechanically — but you may still flag if a response is technically passing but obviously gaming the rule (e.g., extremely terse output that avoids matching forbidden patterns by saying almost nothing).

Output STRICTLY as JSON. No prose, no markdown fences.

Schema:

```json
{
  "without": {"pass": true|false, "reasoning": "one sentence"},
  "with": {"pass": true|false, "reasoning": "one sentence"},
  "preference": "without" | "with" | "tie",
  "preference_reason": "one sentence on which response better serves the user, ignoring the rule"
}
```

The `preference` field is the head-to-head judgment: which response would a user prefer for the original prompt, judged ONLY on quality/usefulness (correctness, completeness, clarity) — NOT on rule adherence. This catches cases where the rule helps OR hurts general quality.

Output the JSON now.
