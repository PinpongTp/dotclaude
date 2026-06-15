---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me" or "/grill-me".
allowed-tools: AskUserQuestion, Read, Grep, Glob, Bash, Agent
---

# Grill Me

Interview the user relentlessly about every aspect of the plan until reaching a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one at a time.

## Rules

1. **One question at a time.** Use `AskUserQuestion` so the user picks from concrete options rather than typing prose. Each question = one decision node in the tree.
2. **Always provide your recommended answer** as the first option, marked `(Recommended)`. State the trade-off so the user can override.
3. **If a question can be answered by reading the codebase, read the codebase instead.** For unfamiliar areas spawn `🐶dog_explore` (`model: haiku`, `mode: auto`) — don't grill the user on facts the code already knows.
4. **Resolve dependencies in order.** Don't ask about leaf decisions before the parent decision is settled. If choosing the storage engine flips half the API design questions, ask storage first.
5. **Stop when the tree is resolved** — every load-bearing decision has an explicit answer and the user agrees the plan is grillable no further.

## Output

User-facing summary in Thai (compressed style, per global rules). Internal reasoning and any agent dispatches in English.

## Hand-offs

- If decisions start touching domain terminology or documented decisions, suggest switching to `/grill-with-docs` instead.
- If grilling reveals the plan needs a written implementation strategy, suggest spawning `🦁lion_dev` (`model: opus`) to produce it.
