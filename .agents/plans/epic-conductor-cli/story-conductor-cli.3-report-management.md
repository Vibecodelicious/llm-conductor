# Story: Report Management

**Epic:** Conductor CLI Tool
**Size:** Small
**Dependencies:** Story 1 (Foundation)

## Story Description

Implement `conductor commit-review` and `conductor commit-verdict` commands that write reviewer reports and judge verdicts/reports to standardized locations and commit them to git with predictable messages.

The CLI owns report commits — subagents output their reports, and the tool handles filesystem placement and git operations.

## User Model

### User Gamut
- The loop runner (Story 5) calling these as library functions
- Users manually committing a report after running a subagent outside the tool
- LLM agents that need to know where reports will be stored

### User-Needs Gamut
- Predictable report locations for easy reference
- Standardized commit messages for git log filtering
- Ability to find all reports for a story in one place

### Design Implications
- Report paths must be deterministic from (story_id, iteration, type)
- Commands should work standalone (not just as loop-runner internals)
- Verdict JSON is validated before commit

## Acceptance Criteria

- [ ] `conductor commit-review --story X.Y --iteration N --report <path>` commits the review report
- [ ] `conductor commit-verdict --story X.Y --iteration N --report <path> --verdict <path>` commits verdict + report
- [ ] Review report written to `.conductor/reports/story-{id}/review.iteration-{n}.md`
- [ ] Judge report written to `.conductor/reports/story-{id}/judgement.iteration-{n}.md`
- [ ] Verdict JSON written to `.conductor/reports/story-{id}/verdict.iteration-{n}.json`
- [ ] Verdict JSON validated against Verdict struct before commit
- [ ] Review commit message: subject + body (body includes issue count summary)
- [ ] Verdict commit message: subject + body (body includes verdict value)
- [ ] Commands fail cleanly if report file doesn't exist
- [ ] Commands check no unrelated files are staged before committing
- [ ] `--dry-run` flag shows what would be committed
- [ ] Report logic importable from `internal/reports` package

## Context References

### Relevant Codebase Files (must read)
- `internal/types/verdict.go` - Verdict struct (from Story 1)
- `REVIEW_JUDGE_SUBAGENTS.md:170-172` - Current judge report commit behavior (being replaced)
- `REVIEWER_SUBAGENTS.md:262-334` - Review report format

### New Files to Create
- `internal/reports/reports.go` - Report path resolution, file copy, git commit
- `internal/reports/reports_test.go` - Tests
- `internal/git/git.go` - Git operation helpers (commit, status check, rev-parse)

## Implementation Plan

### Phase 1: Git Helpers
- `internal/git/git.go`: thin wrappers around `git` subprocess
- `CommitFiles(files []string, subject, body string) (string, error)` — returns commit hash
- `HasStagedChanges() bool` — check for unrelated staged files
- `IsClean() bool` — check for clean working directory
- `RevParseHead() (string, error)` — get current HEAD hash

### Phase 2: Report Path Resolution
- `ReportPath(storyID string, iteration int, reportType string) string`
- Creates parent directories as needed
- Report types: "review", "judgement", "verdict"

### Phase 3: commit-review Command
- Read report file from `--report` path
- Copy to standardized location
- Stage and commit with subject: `[Story X.Y] Review report for iteration N`
- Body: summary extracted from report (issue counts if parseable, otherwise generic)
- Return commit hash

### Phase 4: commit-verdict Command
- Read report from `--report` and verdict from `--verdict`
- Unmarshal and validate verdict JSON
- Copy both to standardized locations
- Stage and commit with subject: `[Story X.Y] Judge verdict for iteration N`
- Body: includes verdict decision value
- Return commit hash

### Phase 5: CLI Integration
- Wire both subcommands
- Add `--dry-run` flag

## Step-by-Step Tasks

1. Create `internal/git/git.go` with git operation helpers
2. Create `internal/reports/reports.go` with path resolution
3. Implement `CommitReview()` function
4. Implement `CommitVerdict()` function with struct validation
5. Wire `commit-review` subcommand
6. Wire `commit-verdict` subcommand
7. Add `--dry-run` flag
8. Create test files and test the full flow
9. Test error cases: missing files, invalid verdict, dirty git state

## Testing Strategy

- Test report path resolution matches expected patterns
- Test verdict validation catches invalid JSON
- Test dry-run doesn't modify filesystem or git
- Test git helpers in a temp repo

## Validation Commands

Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted.

- `go build ./cmd/conductor`
- `./conductor commit-review --help`
- `./conductor commit-verdict --help`
- `go test ./internal/reports/... ./internal/git/...`

## Worktree Artifact Check

- Checked At: `2026-04-21`
- Planned Target Files: `internal/reports/reports.go`, `internal/reports/reports_test.go`, `internal/git/git.go`
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
- [ ] Report paths are deterministic and predictable
- [ ] Commit messages include bodies
- [ ] Verdict validation catches struct violations before commit
- [ ] Plan approved and committed before orchestration begins
- [ ] Worktree artifact overlaps resolved (approved direction or explicit deferral)
