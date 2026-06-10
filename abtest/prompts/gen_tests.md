You are generating A/B testcases for a Claude Code config file.

The user has authored a config rule file that claims to change Claude's behavior. Your job: extract testable claims from the file and emit observable testcases that verify whether the rule is being followed.

## Instructions

For each testcase emit:
- `id`: short kebab-case identifier
- `claim`: one-line description of the rule being tested
- `prompt`: a realistic user prompt that should trigger the rule. Phrase it as a normal user request — do NOT mention the rule itself or hint at expected behavior.
- `pass_criteria`: how to verify the response follows the rule. Combine:
  - `must_not_contain`: array of regex patterns (case-insensitive) that, if matched, mean the rule was violated
  - `must_contain`: array of regex patterns that must appear for the rule to be satisfied
  - `judge_question`: a single yes/no question for an LLM judge to evaluate (use only when regex is insufficient — subjective tone, format, reasoning quality)
- `type`: always `"derived"`

## Rules for good testcases

1. **Observable**: pass/fail must be checkable from the response text alone.
2. **Triggering**: the prompt should naturally invoke the rule, not test it artificially.
3. **Prefer regex over LLM judge**: if the rule says "strip particle X", use `must_not_contain: ["X"]`. Only use `judge_question` for things like "is the tone concise" where regex won't work.
4. **Cover edge cases**: include a counterexample if the rule has exceptions (e.g., a safety scenario where the rule should NOT apply).
5. **No meta-tests**: don't test whether Claude can recite the rule. Test whether Claude FOLLOWS the rule on natural prompts.

## Output format

Strictly a JSON array. No prose, no markdown code fences, no explanation. Start with `[` and end with `]`.

## Target file

Path: {TARGET_PATH}

Content:

{TARGET_CONTENT}

## Task

Generate {N} testcases as a JSON array. Output ONLY the JSON array.
