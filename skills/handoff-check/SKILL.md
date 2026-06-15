---
name: handoff-check
description: Rebuild context at the start of a session by reading the handoff file and git state. Use when user says "/handoff-check" or wants to catch up on previous session work.
allowed-tools: Read, Bash
---

# Handoff Check

Reconstruct context from the previous session and present a summary before continuing work.

## Steps

### 1. Read handoff file (if exists)

```bash
cat .claude/HANDOFF.md 2>/dev/null
```

Note whether the file exists. If it does not exist, proceed with git context only.

### 2. Read git context (always)

```bash
git log --oneline -10
git status --short
git diff --stat HEAD
```

If there are fewer than 15 changed files, also run:

```bash
git diff HEAD
```

If 15 or more changed files, read only the top-changed files by hunk count.

### 3. Synthesise and present summary

Produce a structured summary covering:

- **Goal** — what was being worked on (from handoff or inferred from git)
- **Completed** — commits or changes already done
- **In-flight** — uncommitted changes, their purpose
- **Next actions** — what the handoff or git state suggests doing next
- **Potential pitfalls** — anything that looks risky or incomplete

If no handoff file exists and git shows no branch divergence or uncommitted changes, say so clearly and ask the user what they want to work on.

### 4. Ask how to proceed

After presenting the summary, ask in Thai (compressed):

> "ต่องานเดิมเลยไหม หรือมีอะไรที่อยากเปลี่ยน?"

Wait for the user's answer before taking any action.

## Output style

- Summary in Thai (compressed per global rules)
- File paths, commands, and technical terms in English
- No tool call narration — state of the world only
