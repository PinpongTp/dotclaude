---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up. Use when user says "/handoff" or asks to prepare a handoff for a fresh session.
argument-hint: "What will the next session focus on?"
allowed-tools: Write, Read, Bash
---

# Handoff

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

## Where to write

Save to `.claude/HANDOFF.md` in the **current project directory** (overwrite if exists — only the latest matters).

After writing, ensure `HANDOFF.md` is listed in `.claude/.gitignore`. If `.claude/.gitignore` does not exist, create it. If `HANDOFF.md` is not already in it, append the entry.

```bash
# Check/create .claude/.gitignore
grep -q "^HANDOFF.md$" .claude/.gitignore 2>/dev/null || echo "HANDOFF.md" >> .claude/.gitignore
```

## What to include (≤30 lines total)

1. **Goal** — one sentence: what the user is ultimately trying to achieve.
2. **Status** — done / in-progress / blocked, with file paths or commit refs.
3. **Key decisions** — with the *why*. Decisions made silently are decisions lost.
4. **Open questions** — anything the next session needs to resolve.
5. **Next steps** — concrete first actions, ordered.
6. **Suggested skills** — e.g. `/tdd`, `/diagnose`, `/handoff-check`.
7. **Suggested agents** — `🐶dog_explore`, `🐼panda_dev`, `🦁lion_dev`, `🐔chicken_tester`, `👨🏼‍🦳zoo_keeper`.

## What to leave out

- Don't duplicate content in commits, diffs, or existing docs — reference by path.
- Redact secrets — API keys, passwords, tokens, PII.
- No narration of tool calls. State of the world only.

## Argument handling

If the user passed an argument, treat it as the focus of the next session and tailor accordingly (e.g. `/handoff continue auth refactor` → bias toward auth context).

## Output to user

Confirm in Thai (compressed): path written + one-line summary of content.
