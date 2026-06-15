---
name: grill-with-docs
description: Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use when user wants to stress-test a plan against their project's language and documented decisions, or says "/grill-with-docs".
allowed-tools: AskUserQuestion, Read, Edit, Write, Grep, Glob, Bash, Agent
---

# Grill With Docs

Interview the user relentlessly about every aspect of the plan until reaching a shared understanding. Walk down each branch of the decision tree, resolving dependencies one at a time. For each question, provide your recommended answer.

**One question at a time via `AskUserQuestion`.** Wait for feedback before moving to the next node.

**If a question can be answered by exploring the codebase, explore the codebase instead.** For unfamiliar regions, spawn `🐶dog_explore` (`model: haiku`, `mode: auto`).

## Domain awareness

During exploration, locate existing documentation.

### File structure

Single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

Multiple contexts — `CONTEXT-MAP.md` at the root points to each:

```
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                  ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. No `CONTEXT.md` yet? Create it when the first term is resolved. No `docs/adr/`? Create it when the first ADR is needed.

## During the session

### Challenge against the glossary

If the user's term conflicts with `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

Vague or overloaded terms get a proposed canonical alternative. "You're saying 'account' — Customer or User? Those are different."

### Discuss concrete scenarios

Invent edge-case scenarios that force precision about boundaries between concepts.

### Cross-reference with code

If the user states how something works, check whether the code agrees. Surface contradictions: "Your code cancels entire Orders, but you said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

Resolve a term → update `CONTEXT.md` right there. Don't batch. Format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` is a glossary — totally devoid of implementation details. Not a spec, not a scratch pad.

### Offer ADRs sparingly

Only when **all three** are true:

1. **Hard to reverse** — changing your mind later is costly.
2. **Surprising without context** — a future reader will wonder "why this way?"
3. **The result of a real trade-off** — genuine alternatives existed, you picked one for specific reasons.

If any is missing, skip the ADR. Format in [ADR-FORMAT.md](./ADR-FORMAT.md).

## Output to user

Each question via `AskUserQuestion` with the recommended answer as the first option. End-of-session summary in compressed Thai. Decisions stored in `CONTEXT.md` / ADRs in English (matching project conventions).
