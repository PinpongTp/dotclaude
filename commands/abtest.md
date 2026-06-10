---
description: A/B test a Claude config file by running auto-generated tests with and without the file loaded.
---

Run the A/B test runner on the file path provided in arguments.

Execute this command, passing through any arguments the user gave:

```bash
python3 /Users/pinpongt/.claude/abtest/runner.py $ARGUMENTS
```

The runner:
1. Auto-generates testcases from the target file's claims
2. Runs each test under two variants (file present / file renamed away)
3. Judges responses with regex + LLM
4. Prints a 4-quadrant report to stdout (effective / redundant / ineffective / harmful) plus token & regression-preference metrics

Display the runner's stdout output to the user verbatim. Do NOT summarize or paraphrase the report — the table format is the deliverable. If the runner exits non-zero, show the error from stderr.

If `$ARGUMENTS` is empty or starts with `--help`, print the usage:

```
/abtest <path-to-config-file.md> [--n-tests=N] [--model=sonnet|opus|haiku] [--no-regression] [--parallel=N]

Example: /abtest ~/.claude/rules/conversation.md
```
