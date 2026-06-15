# Agent Rules

## Roles

- **🐶dog_explore** — fast codebase mapping, file discovery, pattern search (read-only)
- **🐼panda_dev** — standard features, bug fixes, refactor, tests
- **🦁lion_dev** — complex architecture, system design, strategic decisions
- **🐔chicken_tester** — testing and validation across all stacks
- **👨🏼‍🦳zoo_keeper** — repository guardian, context optimizer, security sentry

> `subagent_type` MUST use emoji prefix — `🐶dog_explore` not `dog_explore`.

## Model Selection

Always specify `model` when spawning.

| Agent | Model |
|-------|-------|
| `dog_explore` | `haiku` |
| `panda_dev` | `sonnet` |
| `chicken_tester` | `sonnet` |
| `zoo_keeper` | `sonnet` |
| `lion_dev` | `opus` |

Escalate to `opus` only for: system design, ambiguous root-cause, security-sensitive logic.

## Permission Mode

Always pass `mode` when spawning.

| Use case | `mode` |
|----------|--------|
| Implementation (panda_dev / lion_dev) | `acceptEdits` |
| Read-only / analysis (dog_explore / zoo_keeper) | `auto` |
| Risky / destructive (rm, force-push, prod ops) | `default` |

Embed plan content in TaskCreate body — never reference `~/.claude/` paths from inside agents.

## When to Work Directly (no agent)

Skip spawning when any are true:
- Target files known and ≤3
- Single-domain edit (config, gitignore, single function)
- Mechanical change (rename, import add, format fix)
- User observing realtime / Q&A
- Estimated <5 turns

## When to Spawn Agents

Spawn (prefer parallel) when any are true:
- Unknown codebase region → `dog_explore`
- >3 files or >5 turns expected
- Cross-domain (frontend + backend + db)
- Independent work → multiple Agent calls in one message
- Long output that would bloat main thread

**Parallel discipline:** Independent agents always in parallel. Never sequential.

## Standard Workflow

Trivial work (≤3 known files, single-domain) → edit directly.

0. **Explore** (optional): `dog_explore` if unfamiliar codebase
1. **Plan**: `lion_dev` for complex tasks
2. **Execute**: `panda_dev` / `lion_dev`
3. **Validate + Guard** (parallel): `chicken_tester` + `zoo_keeper`
4. **Finish**: brief summary

## Zoo Keeper Auto-Trigger

Spawn `zoo_keeper` when:
- Non-trivial milestone completed
- Conversation has run many turns
- Before committing: new deps, external API calls, auth flows, file I/O on user input
