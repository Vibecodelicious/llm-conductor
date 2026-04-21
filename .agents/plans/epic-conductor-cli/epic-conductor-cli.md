# Epic: Conductor CLI Tool

**Goal:** Replace the LLM orchestrator's coordination bookkeeping with a deterministic CLI tool that automates the develop-review-judge loop, manages state, and commits reports in standardized formats.

**Depends on:** None
**Parallel with:** None
**Complexity:** High

## Context

The llm-conductor framework currently relies on an LLM orchestrator agent to coordinate the develop→review→judge loop. This burns expensive context window tokens on deterministic bookkeeping: state tracking, prompt assembly, iteration counting, report filing, and verdict parsing. A CLI tool can do all of this reliably while the LLM focuses on what it's good at — the actual subagent work (development, review, judgment).

The tool also enforces structure: reports go to predictable paths, verdicts are machine-parseable JSON, commits have standardized messages, and state persists across crashes.

### Design Decisions

**Go (single static binary):** No runtime dependency — compiles to a single binary users can drop into PATH. Strong JSON handling via struct tags + `encoding/json`, clean subprocess management via `os/exec`, good file operations. Source lives at repo root as a Go module. Cross-compile for Linux/macOS/Windows. Releases can be pre-built binaries.

**CLI owns report commits:** Subagent docs currently instruct agents to commit their own reports. We're changing this — the CLI commits reports deterministically. This prevents path/naming drift and gives the tool full control over the git timeline. Subagent docs will be updated to write reports to a CLI-specified file path (passed in the prompt text), not to commit them.

**Developer subagents still commit code directly.** Only reports/verdicts are committed by the CLI. Developer code commits stay with the developer subagent since that's core to their workflow and the commit messages carry implementation context.

**Subagent output delivery via prompt-injected file paths.** The CLI creates temp file paths and includes them in the subagent prompt: "Write your report to: {path}". After the subagent exits, the CLI reads from that path. This is the most reliable mechanism since the LLM always sees the prompt. Both reviewer and judge follow this pattern.

**`claude -p --json-schema` for structured verdicts:** The judge subagent writes its markdown report to the CLI-specified file path during execution (via tool use), then returns the structured verdict JSON as its final output via `--json-schema`. As a fallback in case `--json-schema` prevents tool use, the verdict schema includes an optional `report_markdown` field so the judge can embed the report content directly in the JSON.

**Verdict enum normalization:** The existing docs use `APPROVED AS-IS`, `NEEDS REVISION`, `NEEDS DISCUSSION` (with spaces). The CLI normalizes these to `APPROVED`, `NEEDS_REVISION`, `NEEDS_DISCUSSION` (no spaces, underscores, drop "AS-IS"). The docs will be updated in Story 6 to match.

**State in `.conductor/state.json`:** Atomic writes (write-then-rename), schema-versioned, referential (stores paths to reports, not report content). Includes `pre_phase_head` field to track git HEAD before each phase for commit collection.

**Graph in `.conductor/graph.json`:** The dependency graph lives at a well-known path by convention. `validate-graph` defaults to this path (with override via argument). `conductor run` reads from it. The graph is created externally (by an LLM or manually) and validated by the tool.

**Reports in `.conductor/reports/story-{id}/`:** Git-committed, organized by story, predictable naming.

**Config in `.conductor/config.json`:** Maps placeholder variables to actual project paths. Created by `conductor init`. Orchestration instruction file paths (DEVELOPER_SUBAGENTS_INSTRUCTIONS_PATH, etc.) are derived from the `conductor_path` config value using well-known filenames, not stored separately.

**Git state checks:** Before committing reports, verify no unrelated files are staged. Before launching developer subagent, verify clean working directory (no uncommitted changes). The developer check is stricter because the developer subagent modifies arbitrary files.

**Story 7 is human-assisted.** The skill-creation workflow (skill-creator) is iterative and requires human evaluation. Story 7 does not go through the automated conductor loop — it's done collaboratively.

## User Model

### User Gamut
- Solo developers using Claude Code to manage medium-to-large projects
- Teams where one person runs the orchestrator and reviews results
- Power users of other LLM agents (Kiro, Codex, Gemini CLI) who may adapt the tool
- Developers who are comfortable with CLI tools but may not know the llm-conductor framework deeply
- People running orchestration in CI/CD or unattended contexts

### User-Needs Gamut
- Reliable automation that doesn't lose state when things crash
- Auditable git history with predictable report locations
- Cost control — don't waste tokens on bookkeeping
- Ability to intervene when NEEDS_DISCUSSION escalations occur
- Clear visibility into what the orchestrator is doing and where each story stands
- Easy setup — minimal config to get started with an existing project plan

### Ambiguities From User Model
- **Agent portability:** V1 targets `claude -p`. Users of other agents will need adapter work. Acceptable for v1; note in docs.
- **Parallel story execution:** The framework supports it, but git worktrees add complexity. V1 runs stories sequentially. Document this limitation.
- **Prompt size growth:** By iteration 3-4, accumulated review/judge context in prompts gets large. V1 includes all prior context; may need summarization strategy later.

## Stories

### Story 1: Foundation — Package Structure, Schemas, and Init
**Size:** Medium
**Description:** Set up the Python package, define JSON schemas for all structured data formats, and implement `conductor init` for project configuration.
**Implementation Plan:** `.agents/plans/epic-conductor-cli/story-conductor-cli.1-foundation.md`

### Story 2: Graph Validation
**Size:** Small
**Description:** Implement `conductor validate-graph` to validate LLM-produced dependency graphs — checking structure, circular dependencies, and reference integrity.
**Implementation Plan:** `.agents/plans/epic-conductor-cli/story-conductor-cli.2-graph-validation.md`

### Story 3: Report Management
**Size:** Small
**Description:** Implement `conductor commit-review` and `conductor commit-verdict` to commit reviewer reports and judge verdicts to standardized locations.
**Implementation Plan:** `.agents/plans/epic-conductor-cli/story-conductor-cli.3-report-management.md`

### Story 4: State Management and Status
**Size:** Medium
**Description:** Implement the state tracking system with atomic writes, resume/recovery support, and `conductor status` command.
**Implementation Plan:** `.agents/plans/epic-conductor-cli/story-conductor-cli.4-state-management.md`

### Story 5: Loop Runner
**Size:** Large
**Description:** Implement `conductor run --story X.Y` — the core automation that assembles prompts, invokes subagents via `claude -p`, and drives the develop→review→judge loop.
**Implementation Plan:** `.agents/plans/epic-conductor-cli/story-conductor-cli.5-loop-runner.md`

### Story 6: Documentation Updates
**Size:** Medium
**Description:** Update subagent instruction docs to work with the CLI tool — structured verdict output, report-to-stdout patterns, and orchestrator references to the tool.
**Implementation Plan:** `.agents/plans/epic-conductor-cli/story-conductor-cli.6-documentation-updates.md`

### Story 7: Skill Creation
**Size:** Medium
**Description:** Create the llm-conductor skill with SKILL.md router and bundled references. The skill tells agents how to set up and use the framework + CLI tool.
**Implementation Plan:** `.agents/plans/epic-conductor-cli/story-conductor-cli.7-skill-creation.md`

## Dependency Graph

```
Story 1: Foundation
    ├── Story 2: Graph Validation ──────────┐
    ├── Story 3: Report Management ─────────┼── Can run in parallel
    └── Story 4: State Management ──────────┘
                    │
                    ▼
         Story 5: Loop Runner
                    │
              ┌─────┴─────┐
              ▼            ▼
    Story 6: Docs    Story 7: Skill ── (depends on 6 too)
```

## Dependencies and Integration

- **Prerequisites:** None — this is greenfield tooling within an existing docs-only repo
- **Enables:** Fully automated orchestration runs, future `conductor run --all` with graph walking, CI/CD integration
- **Integration points:** Subagent instruction docs (updated in Story 6), skill ecosystem (Story 7), `claude -p` CLI

## Validation Loop Results

### Iteration 1: Missing Details Check
Resolved 9 gaps identified by validation sub-agent:
1. **Verdict enum mismatch** → normalized to `APPROVED`/`NEEDS_REVISION`/`NEEDS_DISCUSSION` (underscores, no "AS-IS"). Documented in epic design decisions, Story 1 schemas, and Story 6 update scope.
2. **Orchestration instruction paths missing from config** → derived from `conductor_path` config value using well-known filenames. Documented in Story 1 config schema and Story 5 prompt assembly.
3. **Graph file location unspecified** → `.conductor/graph.json` by convention. Documented in epic design decisions.
4. **Report handoff mechanism unspecified** → prompt-injected file path. Documented in epic design decisions and Story 5 prompt assembly.
5. **Developer commit collection** → save `git rev-parse HEAD` before launch, filter by story tag after. Added `pre_phase_head` to state schema (Story 1, 4). Documented in Story 5.
6. **`--json-schema` + tool use risk** → added optional `report_markdown` field to verdict schema as fallback. Documented in Story 1 schema.
7. **`STORY_RESEARCH_PATH` missing** → added optional `research_path` field to graph story schema (Story 1).
8. **Story 7 skill-creator invocation** → marked as human-assisted, not automated.
9. **Runtime dependency** → switched from Python to Go for zero runtime dependencies. Single static binary.

### Iteration 1: Ambiguity Check
Resolved 10 ambiguities identified by validation sub-agent:
1. Subagent output delivery → prompt-injected file path (matches gap #4)
2. Graph location → `.conductor/graph.json` by convention (matches gap #3)
3. Commit collection → HEAD pre-launch + grep (matches gap #5)
4. Verdict enum format → underscores, drop AS-IS (matches gap #1)
5. Reviewer output → file-based, consistent with judge pattern
6. Git state checks → staged-check for reports, full-clean for developer
7. StateManager graph dependency → pass graph as parameter to methods
8. Interactive init → dropped; flags + template config only
9. Package location → `conductor/` at repo root
10. **Skill directory structure → UNRESOLVED. Needs user input.** Options: (A) `skill/` subdirectory with adapted copies, or (B) repo root IS the skill (SKILL.md at root, no duplication).

### Iteration count: 1 (no blocking gaps or high-impact ambiguity remaining, except skill directory question deferred to Story 7)
