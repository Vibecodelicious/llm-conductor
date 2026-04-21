# Story: Loop Runner

**Epic:** Conductor CLI Tool
**Size:** Large
**Dependencies:** Story 1 (Foundation), Story 2 (Graph Validation), Story 3 (Report Management), Story 4 (State Management)

## Story Description

Implement `conductor run --story X.Y` — the core automation command. This assembles prompts for each subagent phase, invokes them via `claude -p`, collects outputs, commits reports, parses verdicts, and drives the develop→review→judge loop until the story is approved, failed, or escalated.

This is the keystone story — it integrates all previous components into the main automation loop.

## User Model

### User Gamut
- Users running orchestration from the command line
- Users who started a run, had it interrupted, and want to resume
- Users monitoring a long-running orchestration
- Future: a `conductor run --all` command that calls this per-story

### User-Needs Gamut
- Fire-and-forget execution for a single story
- Clear progress output during the run
- Graceful handling of subagent failures (timeouts, crashes, rate limits)
- Ability to Ctrl+C and resume later without losing progress
- Dry-run mode to preview prompts without executing

### Design Implications
- The runner must be resumable — check state before each phase
- Prompt assembly must be self-contained (subagent gets everything it needs)
- SIGINT handler should save state cleanly before exiting
- V1 assumes all work happens on the current branch (no branch-per-story)

## Acceptance Criteria

- [ ] `conductor run --story X.Y` executes the full develop→review→judge loop
- [ ] Assembles developer subagent prompt with: instructions path, story context, coding standards, revision context (if iteration > 1)
- [ ] Assembles reviewer subagent prompt with: instructions path, story context, commit list, project standards, output report path
- [ ] Assembles judge subagent prompt with: instructions path, story context, review report path, previous judgements, iteration count, project spec paths, output report path
- [ ] Invokes subagents via `claude -p` with appropriate flags
- [ ] Uses `--json-schema` for judge invocation to get structured verdict
- [ ] Uses `--output-format json` to capture structured output from judge
- [ ] Collects developer commit hashes from git after developer phase
- [ ] Commits review report via `internal/reports`
- [ ] Commits verdict + judge report via `internal/reports`
- [ ] Updates state after each phase transition
- [ ] Loops on NEEDS_REVISION (up to max_iterations from config)
- [ ] Stops on APPROVED, marking story complete
- [ ] Stops on NEEDS_DISCUSSION, marking story escalated
- [ ] Stops on max iterations, marking story failed
- [ ] Resumes from last saved state if re-run after interruption
- [ ] `--dry-run` prints assembled prompts without executing
- [ ] Progress output shows current phase and iteration
- [ ] Verifies clean git state (no uncommitted changes) before starting developer phase
- [ ] Verifies no unrelated staged changes before committing reports
- [ ] Handles subagent timeout/crash gracefully (report error, save state, exit)

## Context References

### Relevant Codebase Files (must read)
- `ORCHESTRATOR_AGENT.md:138-326` - The development loop and subagent prompt templates
- `ORCHESTRATOR_AGENT.md:219-326` - Exact prompt templates for developer, reviewer, judge
- `internal/config/config.go` - Config loading (Story 1)
- `internal/graph/validate.go` - Graph loading and validation (Story 2)
- `internal/reports/reports.go` - Report committing (Story 3)
- `internal/state/state.go` - State management (Story 4)
- `internal/types/` - All type definitions (Story 1)

### New Files to Create
- `internal/runner/runner.go` - StoryRunner with the loop logic
- `internal/runner/prompts.go` - Prompt assembly templates
- `internal/agent/agent.go` - Subagent invocation wrapper (claude -p)
- `internal/runner/runner_test.go` - Tests

## Implementation Plan

### Phase 1: Agent Invocation Layer
- `internal/agent/agent.go`: wrapper around `claude -p` subprocess via `os/exec`
- Function: `InvokeAgent(opts InvokeOpts) (*AgentResult, error)`
- `InvokeOpts`: prompt, jsonSchema (optional), model, timeout, allowedTools, outputFile
- `AgentResult`: stdout, structuredOutput (if jsonSchema), exitCode, duration
- Handle timeouts via `context.WithTimeout`
- Handle crashes, non-zero exit codes
- Pass through model, agent flags from config
- When `outputFile` is specified, verify the file was written after the subagent exits

### Phase 2: Prompt Assembly
- `internal/runner/prompts.go`: functions that build subagent prompts from templates
- `BuildDeveloperPrompt(story, config, graph, revisionContext) string`
- `BuildReviewerPrompt(story, config, graph, commits, outputReportPath) string`
- `BuildJudgePrompt(story, config, graph, reviewReportPath, prevJudgements, iteration, outputReportPath) string`
- Templates mirror ORCHESTRATOR_AGENT.md prompt structures
- Instruction paths derived from config: `{config.ConductorPath}/DEVELOPER_SUBAGENTS.md`, etc.
- **Report output mechanism:** each prompt includes "Write your report to: {outputReportPath}" — the CLI creates a temp file path and includes it in the prompt text. After the subagent exits, the CLI reads from that path.
- All placeholder substitution uses resolved paths from config, not raw placeholders

### Phase 3: Commit Collection
- Before launching developer, save `git rev-parse HEAD` to state as `PrePhaseHead`
- After developer phase, collect new commits:
  ```
  git log --oneline <PrePhaseHead>..HEAD --grep="[Story X.Y]" --format="%H %s"
  ```
- V1 assumes all work happens on the current branch (no branch-per-story)
- Store commit hashes in state

### Phase 4: Loop Logic
- `internal/runner/runner.go`: `type StoryRunner struct`
- `Run(storyID string) error` method:
  ```
  load config, graph, state
  validate story exists in graph
  check resume point from state

  while iteration <= maxIterations:
      if phase is pending or developing:
          verify clean git state
          save PrePhaseHead
          run developer (initial or revision)
          collect commits
          update state → phase: reviewing

      if phase is reviewing:
          create temp path for review report
          run reviewer with outputReportPath in prompt
          verify report file was written
          commit review report
          update state → phase: judging

      if phase is judging:
          create temp path for judge report
          run judge with --json-schema, outputReportPath in prompt
          parse structured verdict from output
          if judge report file exists, use it; else extract from verdict.ReportMarkdown fallback
          commit verdict + judge report

          if verdict == APPROVED:
              update state → status: complete
              return
          elif verdict == NEEDS_DISCUSSION:
              update state → status: escalated
              return
          elif verdict == NEEDS_REVISION:
              build revision context from verdict approved items
              update state → phase: developing, iteration++
              continue

  // max iterations reached
  update state → status: failed
  ```

### Phase 5: CLI Integration
- Wire `run` subcommand
- Required: `--story X.Y`
- Optional: `--dry-run`, `--verbose`
- Progress output: `[Story 1.2] Iteration 1/5 — Phase: Developer`
- Final output: `[Story 1.2] APPROVED after 2 iterations` (or FAILED/ESCALATED)

### Phase 6: Resilience
- SIGINT handler via `signal.Notify`: save current state before exiting
- Pre-developer git state check (`git.IsClean()`)
- Post-developer git verification (new commits exist)
- Subagent timeout handling (configurable via config, default 10 minutes per phase)

## Step-by-Step Tasks

1. Create `internal/agent/agent.go` with `InvokeAgent()` function
2. Create `internal/runner/prompts.go` with three prompt builder functions
3. Implement prompt templates mirroring ORCHESTRATOR_AGENT.md
4. Create `internal/runner/runner.go` with `StoryRunner`
5. Implement the main loop in `Run()`
6. Implement commit collection after developer phase
7. Implement review report collection and commit
8. Implement judge invocation with `--json-schema` and `--output-format json`
9. Implement verdict parsing and decision logic
10. Implement resume logic (check state, skip completed phases)
11. Wire `run` subcommand
12. Implement `--dry-run` mode
13. Implement SIGINT handler for clean shutdown
14. Implement git state verification between phases
15. Write tests for prompt assembly, verdict parsing, resume logic
16. End-to-end manual test with a real story

## Testing Strategy

- Unit test prompt assembly (verify templates produce expected output)
- Unit test verdict parsing and decision logic
- Unit test resume logic for each state
- Test SIGINT handler saves state
- Manual end-to-end test with a real story

## Validation Commands

Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted.

- `go build ./cmd/conductor`
- `./conductor run --help`
- `./conductor run --story 1.1 --dry-run`
- `go test ./internal/runner/... ./internal/agent/...`

## Worktree Artifact Check

- Checked At: `2026-04-21`
- Planned Target Files: `internal/runner/runner.go`, `internal/runner/prompts.go`, `internal/agent/agent.go`, `internal/runner/runner_test.go`
- Overlaps Found (path + class): `none`
- Escalation Status: `none`
- Decision Citation: `none`

## Plan Approval and Commit Status

- Approval Status: `pending`
- Approval Citation: `none`
- Plan Commit Hash: `none`
- Ready-for-Orchestration: `no`

## Completion Checklist

- [ ] All acceptance criteria met
- [ ] Loop correctly handles all three verdict types
- [ ] Resume works after interruption
- [ ] Dry-run shows complete prompts
- [ ] Subagent failures don't corrupt state
- [ ] Git state is verified between phases
- [ ] Plan approved and committed before orchestration begins
- [ ] Worktree artifact overlaps resolved (approved direction or explicit deferral)
