---
name: handoff-del
description: Delete the current project's handoff file. Use when user says "/handoff-del" or wants to clear the handoff.
allowed-tools: Bash
---

# Handoff Delete

Delete `.claude/HANDOFF.md` in the current project directory.

## Steps

1. Check if the file exists:

```bash
ls .claude/HANDOFF.md 2>/dev/null
```

2. If it exists, delete it:

```bash
rm .claude/HANDOFF.md
```

3. Confirm to user in Thai (compressed): file deleted, or that no handoff file was found.

## Notes

- Does not remove `HANDOFF.md` from `.claude/.gitignore` — keep the entry so future handoffs are still ignored.
- Does not affect git history.
