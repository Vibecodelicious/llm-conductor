# Story: State Management and Status

**Epic:** Conductor CLI Tool
**Size:** Medium
**Dependencies:** Story 1 (Foundation)

## Story Description

Implement the persistent state tracking system and `conductor status` command. The state file tracks where each story is in the develop-review-judge loop, enabling resume after crashes and visibility into progress.

## User Model

### User Gamut
- The loop runner (Story 5) reading/writing state continuously
- Users checking progress mid-run
- Users resuming after a crash or interruption
- CI/CD systems polling for completion

### User-Needs Gamut
- State survives crashes (atomic writes)
- Clear status output showing where everything stands
- Ability to resume exactly where things left off

### Design Implications
- Atomic writes via write-to-temp-then-rename
- State includes enough context to resume any phase
- Status output is both human-readable and machine-parseable (`--json`)

## Acceptance Criteria

- [ ] State file at `.conductor/state.json` tracks all story statuses
- [ ] State writes are atomic (temp file + os.Rename)
- [ ] State schema includes version field
- [ ] `conductor status` shows human-readable status table
- [ ] `conductor status --json` outputs machine-readable state
- [ ] `conductor status --story X.Y` shows one story's detail
- [ ] State tracks: status, iteration, phase, pre_phase_head, commits, report paths, failure/escalation reasons
- [ ] State can be initialized from a validated graph (all stories start as "pending")
- [ ] Granular story updates (update one story without manual full-state manipulation)
- [ ] Resume support: given a state file, determine next action for any story
- [ ] State management importable from `internal/state` package

## Context References

### Relevant Codebase Files (must read)
- `internal/types/state.go` - State struct (from Story 1)
- `internal/types/graph.go` - Graph struct (state initialized from graph)
- `ORCHESTRATOR_AGENT.md:100-134` - Current markdown-based state tracking format

### New Files to Create
- `internal/state/state.go` - StateManager with atomic read/write/update
- `internal/state/state_test.go` - Tests

## Implementation Plan

### Phase 1: StateManager Core
- `type StateManager struct` with conductor dir path
- `Load() (*State, error)` — read and unmarshal state file
- `Save(state *State) error` — atomic write (write to temp, os.Rename)
- `InitFromGraph(graph *Graph) *State` — create initial state, all stories "pending"

### Phase 2: Story State Operations
- `UpdateStory(state *State, storyID string, updates func(*StoryState))` — update specific story
- `GetStory(state *State, storyID string) *StoryState`
- `GetReadyStories(state *State, graph *Graph) []string` — stories whose deps are all "complete"
- `GetNextAction(story *StoryState) string` — what phase to resume from
- `SetPrePhaseHead(state *State, storyID, headHash string)`

### Phase 3: Status Command
- Table format:
  ```
  Story   | Epic              | Status     | Iteration | Phase
  --------|-------------------|------------|-----------|----------
  1.1     | Foundation        | complete   | 1         | -
  1.2     | Foundation        | reviewing  | 2         | reviewer
  2.1     | Backend API       | pending    | 0         | -
  ```
- Summary line: "3/12 complete, 1 in progress, 0 failed, 8 pending"
- `--json` outputs the raw state
- `--story X.Y` filters to one story with full detail

### Phase 4: Resume Logic
- `GetNextAction()` examines story state and returns:
  - "pending" → start developer phase
  - "developing" → developer may have crashed; check git for commits, restart developer
  - "reviewing" → launch reviewer
  - "judging" → launch judge
  - "complete"/"failed"/"escalated" → no action

## Step-by-Step Tasks

1. Create `internal/state/state.go` with StateManager
2. Implement atomic Load/Save with temp file + rename
3. Implement `InitFromGraph()`
4. Implement `UpdateStory()`, `GetStory()`, `GetReadyStories()`
5. Implement `GetNextAction()` resume logic
6. Implement `SetPrePhaseHead()`
7. Implement status table formatting
8. Wire `status` subcommand
9. Add `--json` and `--story` flags
10. Create `state_test.go` with tests
11. Test atomic write safety
12. Test resume logic for each story status
13. Test InitFromGraph with EPICS.example structure

## Testing Strategy

- Test atomic write (write then verify content matches)
- Test InitFromGraph produces all-pending state
- Test GetReadyStories with various completion patterns
- Test GetNextAction for each status value
- Test status table output

## Validation Commands

Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted.

- `go build ./cmd/conductor && ./conductor status --help`
- `go test ./internal/state/...`

## Worktree Artifact Check

- Checked At: `2026-04-21`
- Planned Target Files: `internal/state/state.go`, `internal/state/state_test.go`
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
- [ ] Atomic writes prevent corruption
- [ ] Resume logic handles all story states
- [ ] Status output is clear and useful
- [ ] Plan approved and committed before orchestration begins
- [ ] Worktree artifact overlaps resolved (approved direction or explicit deferral)
