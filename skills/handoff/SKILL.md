---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up. Use when user says "/handoff" or asks to prepare a handoff for a fresh session.
argument-hint: "What will the next session be used for?"
allowed-tools: Write, Read, Bash, Grep, Glob
---

# Handoff

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

## Where to write

Save to the OS temp directory — **not** the project workspace. Resolve via `${TMPDIR:-/tmp}` on macOS/Linux. Filename: `handoff-<YYYYMMDD-HHMMSS>.md`. Print the absolute path at the end.

## What to include

1. **Goal** — one paragraph: what the user is ultimately trying to achieve.
2. **Status** — done / in-progress / blocked, with file paths or PR/branch links.
3. **Key decisions made** — with the *why*, not just the *what*. Decisions made silently are decisions lost.
4. **Open questions** — anything the next session will need to resolve.
5. **Next steps** — concrete first actions, ordered.
6. **Suggested skills** — which skills the next agent should invoke (e.g. `/tdd`, `/diagnose`, `/grill-with-docs`).
7. **Suggested agents** — when delegation is obvious, name the agent (`🐶dog_explore` for unfamiliar regions, `🐼panda_dev` for mechanical work, `🦁lion_dev` for architecture, `🐔chicken_tester` for validation, `👨🏼‍🦳zoo_keeper` for cleanup/security).

## What to leave out

- **Do not duplicate** content already in PRDs, plans, ADRs, issues, commits, or diffs. Reference them by path/URL.
- **Redact secrets** — API keys, passwords, tokens, PII. If any appeared in the conversation, omit them.
- **No narration** of every tool call. Summarise the *state of the world*, not the transcript.

## Argument handling

If the user passed an argument after `/handoff`, treat it as the focus of the next session and tailor the doc accordingly (e.g. `/handoff continue auth refactor` → bias toward auth files, decisions, and next steps).

## Output to user

Confirm in Thai (compressed): path + one-line summary of what's in it.
