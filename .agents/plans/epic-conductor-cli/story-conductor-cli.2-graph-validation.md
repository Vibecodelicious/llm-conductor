# Story: Graph Validation

**Epic:** Conductor CLI Tool
**Size:** Small
**Dependencies:** Story 1 (Foundation)

## Story Description

Implement `conductor validate-graph [path]` which validates the dependency graph JSON that an LLM produces from a freeform project plan. Defaults to `.conductor/graph.json` if no path given. This is the bridge between human-readable epics and machine-executable orchestration.

## User Model

### User Gamut
- LLM agents that just produced a graph and need validation feedback
- Users manually editing a graph file and checking their work
- The loop runner (Story 5) which needs to know story execution order

### User-Needs Gamut
- Clear error messages that help the LLM or user fix the graph
- Topological sort output so the runner knows what order to execute
- Fast feedback — this runs often during graph authoring

### Design Implications
- Error messages should be specific enough for an LLM to self-correct
- The command should output the execution order on success (topological sort)
- Exit codes: 0 for valid, 1 for invalid

## Acceptance Criteria

- [ ] `conductor validate-graph [path]` validates a graph JSON file (defaults to `.conductor/graph.json`)
- [ ] Validates struct fields via `Graph.Validate()`
- [ ] Detects circular dependencies and reports the cycle
- [ ] Detects dangling dependency references (depends_on story that doesn't exist)
- [ ] Verifies all story IDs are unique (enforced by map keys, but check for empty IDs)
- [ ] Verifies context_path files exist on disk
- [ ] On success, prints topological execution order
- [ ] On failure, prints all errors found (not just the first one)
- [ ] Exit code 0 on success, 1 on failure
- [ ] `--json` flag for machine-readable output
- [ ] Graph logic importable from `internal/graph` package

## Context References

### Relevant Codebase Files (must read)
- `internal/types/graph.go` - Graph struct (from Story 1)
- `EPICS.example.md` - The freeform format the graph represents
- `ORCHESTRATOR_AGENT.md:51-98` - Dependency graph concepts and parallel paths

### New Files to Create
- `internal/graph/validate.go` - Graph validation and cycle detection
- `internal/graph/topo.go` - Topological sort with wave grouping
- `internal/graph/validate_test.go` - Tests

## Implementation Plan

### Phase 1: Core Validation
- Load and unmarshal graph JSON
- Run `Graph.Validate()` for structural checks
- Check all `depends_on` entries reference existing story IDs
- Check `context_path` files exist relative to working directory

### Phase 2: Cycle Detection
- Implement cycle detection via DFS (Kahn's algorithm or tarjan)
- Report the specific cycle found (e.g., "cycle: 1.1 → 1.2 → 1.1")

### Phase 3: Topological Sort
- Produce execution order respecting dependencies
- Group stories by "wave" (stories with all deps met at each level) for future parallel support
- Return `[][]string` — each inner slice is a wave of parallelizable stories

### Phase 4: CLI Integration
- Wire into subcommand dispatch
- Default path: `.conductor/graph.json`
- `--json` flag outputs `{"valid": bool, "errors": [], "execution_order": [[]]}`
- Human-readable: errors as bullet list, success as ordered story list with wave grouping

## Step-by-Step Tasks

1. Create `internal/graph/validate.go` with `ValidateGraph(graph Graph, basePath string) ([][]string, []error)`
2. Implement dependency reference checking
3. Implement cycle detection with cycle path reporting
4. Implement topological sort with wave grouping in `topo.go`
5. Implement context_path existence checking
6. Wire `validate-graph` subcommand
7. Add `--json` flag
8. Create `validate_test.go` with tests for: valid graph, circular graph, missing deps, missing files
9. Test with the EPICS.example.md structure converted to a graph JSON

## Testing Strategy

- Test cycle detection with known cyclic graphs
- Test topological sort produces correct order for EPICS.example.md structure
- Test error accumulation (multiple errors reported at once)
- Test wave grouping for parallel paths

## Validation Commands

Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted.

- `go build ./cmd/conductor && ./conductor validate-graph`
- `go test ./internal/graph/...`

## Worktree Artifact Check

- Checked At: `2026-04-21`
- Planned Target Files: `internal/graph/validate.go`, `internal/graph/topo.go`, `internal/graph/validate_test.go`
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
- [ ] Cycle detection works on complex graphs
- [ ] Topological sort produces correct execution order
- [ ] Error messages are clear enough for LLM self-correction
- [ ] Plan approved and committed before orchestration begins
- [ ] Worktree artifact overlaps resolved (approved direction or explicit deferral)
