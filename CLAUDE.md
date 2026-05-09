# CLAUDE.md - Global Workflow & Guidelines

## Core Rules

- **Language:** User speaks Thai, but all **agent-to-agent communication and technical outputs must be in English**.
- **Error Recovery:** If an agent hits the same error >3 times, stop and report.
- **Format:** Always use full file paths and Conventional Commits.
- **Agent First:** Always prefer delegating work to subagents instead of executing directly. For multi-step or cross-domain tasks, **orchestrate an agent team** (spawn multiple specialized agents in parallel via `TeamCreate` or coordinated `Agent` calls) rather than working solo. The main thread should act as an orchestrator — plan, delegate, and synthesize.
- **Skip-explore exception:** When target file(s) are known and ≤3, just Read them. Use `dog_explore` only for: unknown regions, cross-cutting edits (rename / signature / schema), or bugs in unfamiliar code.

---

## Agent Roles

- **👨🏼‍🦳zoo_keeper:** Repository Guardian, Context Optimizer, Security Sentry.
- **🐶dog_explore:** Project explorer — fast codebase mapping, file discovery, pattern search (read-only).
- **🐼panda_dev:** Standard features, bug fixes, refactor, and tests.
- **🦁lion_dev:** Complex architecture, system design, and strategic decisions.
- **🐔chicken_tester:** Testing and validation across all stacks.

---

## Parallel Spawning Rules (MUST follow)

- When tasks are independent, you **MUST** spawn agents in parallel using multiple Agent tool calls in a single message.
- Examples of parallel spawning:
  - After code is written: spawn `chicken_tester` (validate) + `zoo_keeper` (security scan) in parallel.
  - Multiple independent features: spawn separate `panda_dev` agents for each.
  - Planning + cleanup: spawn `lion_dev` (design) + `zoo_keeper` (repo cleanup) in parallel.
  - Exploration + planning: spawn multiple `dog_explore` agents for different areas of the codebase, then feed findings to `lion_dev` / `panda_dev`.
- **Never** run agents sequentially if they have no dependency on each other.

---

## Standard Workflow

0. **Explore (optional):** Spawn `dog_explore` to map structure / locate symbols before planning, when working in an unfamiliar codebase.
1. **Plan:** `lion_dev` designs the plan (for complex tasks). Skip for simple tasks.
2. **Execute:** Assign subtasks to `panda_dev` / `lion_dev`.
3. **Validate + Guard (parallel):** Spawn `chicken_tester` AND `zoo_keeper` together after implementation.
4. **Finish:** Provide a brief summary of work to the user.

---

## Zoo Keeper Auto-Trigger

Spawn `zoo_keeper` automatically when:

- A task or milestone is completed (post-implementation security + cleanup scan).
- The conversation has run for many turns (context optimization).
- Before committing code (secret detection scan).

@RTK.md
