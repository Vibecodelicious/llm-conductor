# Story: Foundation — Module Structure, Types, and Init

**Epic:** Conductor CLI Tool
**Size:** Medium
**Dependencies:** None

## Story Description

Set up the Go module structure for the `conductor` CLI tool, define typed structs for all structured data formats (dependency graph, verdict, state, config), and implement the `conductor init` command that configures a project to use the tool.

Compiles to a single static binary with no runtime dependencies.

## User Model

### User Gamut
- Developers setting up the conductor tool for the first time in an existing project
- Users who already have a project plan and want to start orchestrating
- Users who may not know which placeholder paths their project needs

### User-Needs Gamut
- Quick setup — `conductor init` should get them running with minimal friction
- Clear error messages when config is incomplete
- Types that are strict enough to catch errors but flexible enough for real use

### Design Implications
- `conductor init` should accept flags for non-interactive use (CI)
- `conductor init` with no flags creates a template config with TODO placeholders
- Config file should be human-readable and editable JSON

## Acceptance Criteria

- [ ] Go module at repo root with `go.mod` and `cmd/conductor/main.go` entry point
- [ ] `go build ./cmd/conductor` produces a `conductor` binary
- [ ] `conductor --help` shows available subcommands
- [ ] `conductor init` creates `.conductor/config.json` with placeholder mappings
- [ ] `conductor init` creates `.conductor/` directory structure (reports/)
- [ ] `conductor init --project-epics path --coding-standards path ...` works non-interactively
- [ ] `conductor init` with no flags creates a template config with TODO placeholders and instructions to edit
- [ ] Config struct defined and validated on load
- [ ] Graph struct defined with JSON tags (used by Story 2)
- [ ] Verdict struct defined with JSON tags (used by Story 3)
- [ ] State struct defined with JSON tags (used by Story 4)
- [ ] All types in `internal/types/` package
- [ ] Config validation produces clear error messages for missing required fields
- [ ] `go test ./...` passes

## Context References

### Relevant Codebase Files (must read)
- `ORCHESTRATOR_AGENT.md:66-89` - All placeholder variables that need config mappings
- `EPICS.example.md` - The freeform format that the graph schema must represent
- `REVIEW_JUDGE_SUBAGENTS.md:170-255` - Judge verdict format the verdict schema must capture

### New Files to Create
- `go.mod` - Go module definition
- `cmd/conductor/main.go` - Entry point
- `internal/types/graph.go` - Graph struct + validation
- `internal/types/verdict.go` - Verdict struct + validation
- `internal/types/state.go` - State struct + validation
- `internal/types/config.go` - Config struct + validation
- `internal/config/config.go` - Config loading and init logic
- `internal/cli/root.go` - Root command and subcommand registration

## Implementation Plan

### Phase 1: Module Structure
- Init Go module: `go mod init github.com/basil/llm-conductor`
- Create `cmd/conductor/main.go` with subcommand dispatch
- Use stdlib `flag` or a lightweight approach for subcommands (no heavy framework needed — just `os.Args` dispatch to subcommand handlers)
- Register subcommands: init, validate-graph, commit-review, commit-verdict, status, run
- Placeholder implementations that print "not implemented"

### Phase 2: Type Definitions
- Define Go structs with JSON tags in `internal/types/`
- Graph types:
  ```go
  type Graph struct {
      Version int                 `json:"version"`
      Stories map[string]Story    `json:"stories"`
  }
  type Story struct {
      Name         string   `json:"name"`
      Epic         string   `json:"epic"`
      DependsOn    []string `json:"depends_on"`
      ContextPath  string   `json:"context_path"`
      ResearchPath string   `json:"research_path,omitempty"`
  }
  ```
- Verdict types:
  ```go
  type Verdict struct {
      StoryID        string         `json:"story_id"`
      Iteration      int            `json:"iteration"`
      Decision       VerdictDecision `json:"verdict"`
      ApprovedItems  []VerdictItem  `json:"approved_items"`
      RejectedItems  []RejectItem   `json:"rejected_items"`
      ReportMarkdown string         `json:"report_markdown,omitempty"`
  }
  type VerdictDecision string
  const (
      VerdictApproved        VerdictDecision = "APPROVED"
      VerdictNeedsRevision   VerdictDecision = "NEEDS_REVISION"
      VerdictNeedsDiscussion VerdictDecision = "NEEDS_DISCUSSION"
  )
  type VerdictItem struct {
      ID      string `json:"id"`
      Summary string `json:"summary"`
  }
  type RejectItem struct {
      ID      string `json:"id"`
      Summary string `json:"summary"`
      Reason  string `json:"reason"`
  }
  ```
  Note: verdict enum values are normalized from existing docs ("APPROVED AS-IS" → "APPROVED",
  "NEEDS REVISION" → "NEEDS_REVISION", "NEEDS DISCUSSION" → "NEEDS_DISCUSSION"). Story 6 updates docs to match.
- State types:
  ```go
  type State struct {
      Version int                    `json:"version"`
      Stories map[string]StoryState  `json:"stories"`
  }
  type StoryState struct {
      Status           string      `json:"status"`
      Iteration        int         `json:"iteration"`
      Phase            string      `json:"phase"`
      PrePhaseHead     string      `json:"pre_phase_head,omitempty"`
      Commits          []string    `json:"commits"`
      ReportPaths      ReportPaths `json:"report_paths"`
      FailureReason    string      `json:"failure_reason,omitempty"`
      EscalationReason string      `json:"escalation_reason,omitempty"`
  }
  type ReportPaths struct {
      Reviews    []string `json:"reviews"`
      Judgements []string `json:"judgements"`
      Verdicts   []string `json:"verdicts"`
  }
  ```
- Config types:
  ```go
  type Config struct {
      Version       int          `json:"version"`
      ConductorPath string       `json:"conductor_path"`
      Placeholders  Placeholders `json:"placeholders"`
      AgentCommand  string       `json:"agent_command"`
      AgentFlags    []string     `json:"agent_flags"`
      Model         string       `json:"model,omitempty"`
      MaxIterations int          `json:"max_iterations"`
  }
  type Placeholders struct {
      ProjectCodingStandardsPath string `json:"PROJECT_CODING_STANDARDS_PATH"`
      ProjectEpicsPath           string `json:"PROJECT_EPICS_PATH"`
      ProjectRequirementsPath    string `json:"PROJECT_REQUIREMENTS_PATH"`
      ProjectArchitecturePath    string `json:"PROJECT_ARCHITECTURE_PATH"`
      ProjectRoadmapPath         string `json:"PROJECT_ROADMAP_PATH,omitempty"`
      ProjectFutureFeaturesPath  string `json:"PROJECT_FUTURE_FEATURES_PATH,omitempty"`
      ProjectResearchNotesPath   string `json:"PROJECT_RESEARCH_NOTES_PATH,omitempty"`
  }
  ```
  Note: orchestration instruction paths (DEVELOPER_SUBAGENTS_INSTRUCTIONS_PATH, etc.) are derived
  from `ConductorPath` using well-known filenames, not stored in config.
- Each type gets a `Validate() []error` method that checks required fields, valid enum values, etc.

### Phase 3: Init Command
- `conductor init` with no flags → creates template config with TODO placeholders
- `conductor init --project-epics path --coding-standards path ...` → fills in values
- Creates `.conductor/` directory
- Creates `.conductor/config.json` with validated content
- Creates `.conductor/reports/` directory
- Prints summary of what was created
- Defaults: `agent_command: "claude"`, `agent_flags: ["-p", "--dangerously-skip-permissions"]`, `max_iterations: 5`

### Phase 4: Testing
- Unit tests for each type's Validate() method
- Test init command creates expected directory structure
- Test config loading from existing file
- Test JSON round-trip for all types

## Step-by-Step Tasks

1. `go mod init` at repo root
2. Create `cmd/conductor/main.go` with subcommand dispatch
3. Create `internal/cli/root.go` with subcommand registration
4. Create `internal/types/graph.go` with Graph/Story structs + Validate()
5. Create `internal/types/verdict.go` with Verdict/VerdictDecision types + Validate()
6. Create `internal/types/state.go` with State/StoryState types + Validate()
7. Create `internal/types/config.go` with Config/Placeholders types + Validate()
8. Create `internal/config/config.go` with Load() and Init() functions
9. Implement `conductor init` subcommand
10. Add `.conductor/` to `.gitignore`
11. Test: `go build ./cmd/conductor && ./conductor --help`
12. Test: `go test ./...` passes
13. Test: init creates expected directory structure and valid config

## Testing Strategy

- `go test` for type validation (valid/invalid data, missing fields, wrong enum values)
- `go test` for config init logic
- Manual testing of CLI binary

## Validation Commands

Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted.

- `go build ./cmd/conductor`
- `./conductor --help`
- `./conductor init --help`
- `go test ./...`

## Worktree Artifact Check

- Checked At: `2026-04-21`
- Planned Target Files: `go.mod`, `cmd/conductor/main.go`, `internal/types/graph.go`, `internal/types/verdict.go`, `internal/types/state.go`, `internal/types/config.go`, `internal/config/config.go`, `internal/cli/root.go`, `.gitignore`
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
- [ ] Validation commands pass
- [ ] Types cover all fields from existing orchestrator docs
- [ ] Config maps all placeholder variables from ORCHESTRATOR_AGENT.md
- [ ] Plan approved and committed before orchestration begins
- [ ] Worktree artifact overlaps resolved (approved direction or explicit deferral)
