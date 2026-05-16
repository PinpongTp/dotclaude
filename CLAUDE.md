# CLAUDE.md - Global Workflow & Guidelines

## Core Rules

- **Language:** User speaks Thai, but all **agent-to-agent communication and technical outputs must be in English**.
- **Error Recovery:** If an agent hits the same error >3 times, stop and report.
- **Format:** Always use full file paths and Conventional Commits.
- **Delegate by scope, not by default:** Spawn agents for multi-step work, cross-domain tasks, exploration in unfamiliar code, or parallel-able work. For known small tasks, work directly. (See *When to work directly* + *When to spawn agents* below.)

---

## When to work directly (no agent)

Skip agent spawning when **any** of these are true:
- Target files known and ≤3
- Single-domain edit (config, gitignore, single function tweak)
- Mechanical change (rename, import add, format fix, conflict resolution on read diffs)
- User is observing realtime / Q&A flow
- Estimated <5 turns total

**Why:** Agent bootstrap cost (~10-20k tokens for system prompt + tools) often exceeds the task itself. Direct Read/Edit is cheaper and faster for small, known work.

---

## When to spawn agents

Spawn (and prefer parallel) when **any** of these are true:
- Unknown codebase region → use `dog_explore`
- >3 files or >5 turns of work expected
- Cross-domain (frontend + backend + db, etc.)
- Independent work that can run in parallel (multiple `Agent` calls in one message)
- Long output that would bloat main thread (security review, test runs, large refactor diffs)

**Parallel discipline:** When tasks are independent, spawn agents in parallel via multiple `Agent` tool calls in a single message. Never run independent agents sequentially.

Examples:
- After non-trivial code change: `chicken_tester` + `zoo_keeper` in parallel
- Multiple independent features: separate `panda_dev` per feature
- Exploration: multiple `dog_explore` for different areas, then feed to `lion_dev` / `panda_dev`

---

## Model Selection (mandatory)

**ALWAYS specify the `model` parameter** when spawning agents via the Agent tool. Default inheritance = parent model = expensive when parent is Opus.

| Agent task | Recommended model |
|---|---|
| `dog_explore` (search/map code) | `haiku` |
| `panda_dev` (CRUD / mechanical changes) | `sonnet` |
| `chicken_tester` (E2E scenarios) | `sonnet` |
| `zoo_keeper` (audit / cleanup) | `sonnet` |
| `lion_dev` (architecture / complex bugs) | `opus` |

Only escalate to `opus` when reasoning depth is genuinely required (system design, ambiguous root-cause analysis, security-sensitive logic). Saves ~5x cost vs always-Opus default.

---

## Permission Mode (mandatory when spawning agents)

**ALWAYS pass `mode` parameter** to the Agent tool. Default mode triggers user approval prompts for every Edit/Write on existing files — frustrating UX, especially with parallel teammates.

| Use case | `mode` |
|---|---|
| Trusted teammate doing routine implementation (panda_dev/lion_dev with clear task) | `acceptEdits` |
| Read-only / analysis (dog_explore, zoo_keeper) | `auto` |
| Risky/destructive work (rm, force-push, prod ops) | `default` (force user prompt) |

`acceptEdits` auto-accepts Edit/Write on project files without prompting the user — the right choice for trusted teammates. (Earlier sessions tried `bypassPermissions` but the harness consistently launches child agents with `--permission-mode auto` regardless of what's passed; `acceptEdits` is the user's preferred working mode for spawned teammates.)

`auto` allows tool calls but still respects file-edit safety prompts — fine for read-only agents.

When in doubt: `acceptEdits` for implementation work, `auto` for everything else. Never leave `mode` unset on spawn.

**Critical: keep agent file references INSIDE the project cwd.** `bypassPermissions` only covers paths within the spawned agent's working directory. References to `~/.claude/plans/`, `~/.claude/memory/`, or any path outside project cwd will trigger user permission prompts every time — even with `bypassPermissions` set. Embed the full plan/spec content directly into the task description (TaskCreate body) instead of pointing the agent to external files. Only project files (src/, bruno/, etc.) are safe to reference.

---

## Clarification Before Implementation

For any new API/feature design where scope is ambiguous, **use `AskUserQuestion` BEFORE coding** to confirm:
- Field names, data types, response shape
- Status/enum mapping (UI labels vs backend enums)
- Validation rules and allowed values
- Format choices (e.g., JSON vs text, timestamp format)

**Why:** One clarifying question costs ~1 turn; wrong assumption costs 5+ revision turns.

**Skip when:** requirement is fully specified (exact field list, format examples in user's message).

---

## Commit Scoping Discipline

When user requests `commit`:
- Commit **ONLY files touched in current session** — cross-reference with conversation history.
- Skip pre-existing modifications that weren't edited this session.
- If unsure about a modified file, **ask the user** before staging.
- Group changes by topic (separate `feat:`, `chore:`, `fix:` commits) — never bundle unrelated changes.
- Stage with explicit file paths, never `git add -A` or `git add .`.

---

## Agent Roles

- **👨🏼‍🦳zoo_keeper:** Repository Guardian, Context Optimizer, Security Sentry.
- **🐶dog_explore:** Project explorer — fast codebase mapping, file discovery, pattern search (read-only).
- **🐼panda_dev:** Standard features, bug fixes, refactor, and tests.
- **🦁lion_dev:** Complex architecture, system design, and strategic decisions.
- **🐔chicken_tester:** Testing and validation across all stacks.

---

## Standard Workflow (non-trivial work only)

For trivial work (≤3 known files, single-domain), skip this and edit directly.

0. **Explore (optional):** Spawn `dog_explore` to map structure / locate symbols if codebase is unfamiliar.
1. **Plan:** `lion_dev` designs the plan (for complex tasks).
2. **Execute:** Assign subtasks to `panda_dev` / `lion_dev`.
3. **Validate + Guard (parallel):** Spawn `chicken_tester` + `zoo_keeper` together after implementation.
4. **Finish:** Brief summary to user.

---

## Zoo Keeper Auto-Trigger

Spawn `zoo_keeper` automatically when:
- Non-trivial task or milestone is completed (post-implementation cleanup scan).
- The conversation has run for many turns (context optimization).
- **Before committing code with security-sensitive changes:** new dependencies, external API calls, auth/credential flows, file I/O on user input. Skip for config tweaks, gitignore edits, doc changes.

---

## Token / Context Economy

Teammate context is expensive — every turn re-sends the full conversation. Manage aggressively.

### Spawn policy
- **Scope one feature per teammate.** Don't reuse a teammate across unrelated features.
- **Shutdown + respawn** a teammate when its context exceeds ~70% — cheaper than carrying bloat.
- **New team for new epic.** Don't graft unrelated work onto an existing team.

### Task briefing
- Put full requirements in the **TaskCreate description**, not in SendMessage.
- SendMessage to a teammate: one short sentence (`"Task #N unblocked, claim and proceed"`) — do NOT restate the task.
- Teammates read the task themselves → saves duplicate tokens.

### Lead (this agent) economy
- **Don't narrate idle notifications.** A bare `"รับทราบ"` is enough.
- **Don't summarize teammate reports back to the user** when the report was already rendered.
- **Skip BACKLOG.md updates unless asked.** (Auto-memory for user/feedback/project still applies as normal — that system is separate.)
- **Don't re-verify completed work** by reading files the teammate already described.

### Shutdown discipline
- Close the team with `TeamDelete` when the epic is done.
- Write surviving knowledge to `BACKLOG.md` / project memory, not to lingering tasks.

@rules/conversation.md

@RTK.md
