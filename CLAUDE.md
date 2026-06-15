# CLAUDE.md - Global Workflow & Guidelines

## Core Rules

- **Language:** User speaks Thai; agent-to-agent and technical outputs must be in English.
- **Error Recovery:** Same error >3 times → stop and report.
- **Format:** Full file paths and Conventional Commits always.
- **Delegate by scope:** Spawn for multi-step/cross-domain/parallel work. Work directly for small known tasks.
- **Locate the layer first:** Confirm where behaviour lives before editing. Trace; don't assume.
- **Reuse before create:** Grep for existing file/function first. New file requires one-line justification.

---

## Clarification Before Implementation

For ambiguous scope, use `AskUserQuestion` BEFORE coding: field names, data types, status mapping, validation, format.

Skip when requirement is fully specified.

---

## Verify Before Concluding

Never claim "no change needed" from assumed contract. Hit the endpoint, read the actual response. Trust observed behaviour, not names.

---

## Commit Workflow

`/commit` — atomic conventional commits  
`/commit-ai` — same, with AI attribution footer

---

## Token / Context Economy

### Spawn policy
- One feature per teammate. Shutdown + respawn at ~70% context.
- New team for new epic.

### Task briefing
- Full requirements in TaskCreate description, not SendMessage.
- SendMessage: one short sentence — teammates read tasks themselves.

### Lead economy
- Don't narrate idle notifications.
- Don't summarize teammate reports already rendered.
- Skip BACKLOG.md updates unless asked.
- Don't re-verify completed work.

### Shutdown
- `TeamDelete` when epic done.

@RTK.md
