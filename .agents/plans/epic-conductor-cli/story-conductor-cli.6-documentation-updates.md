# Story: Documentation Updates

**Epic:** Conductor CLI Tool
**Size:** Medium
**Dependencies:** Story 5 (Loop Runner)

## Story Description

Update the existing subagent instruction docs to work with the CLI tool. The key changes:

1. **Judge**: Output a structured JSON verdict in addition to the markdown report. Stop self-committing the report — the CLI handles that.
2. **Reviewer**: Output report to stdout. Stop expecting to commit anything.
3. **Orchestrator**: Reference the CLI tool as the primary automation mechanism. Keep the manual orchestration instructions as a fallback for platforms without the tool.
4. **Developer**: Minor updates — the developer still commits code directly, but needs awareness that reports are handled externally.

## User Model

### User Gamut
- LLM agents reading these docs as operating instructions
- Users of the CLI tool who need the docs to match tool behavior
- Users NOT using the CLI tool who still follow docs manually (must not break this path)

### User-Needs Gamut
- Docs must work both with and without the CLI tool
- Clear indication of what's different when using the tool vs. manual orchestration
- Judge instructions must specify the exact JSON verdict format

### Design Implications
- Add "When using the conductor CLI" sections rather than replacing existing instructions
- The judge needs explicit instructions for the `--json-schema` structured output pattern
- Keep manual orchestration path functional for non-Claude-Code platforms

## Acceptance Criteria

- [ ] REVIEW_JUDGE_SUBAGENTS.md updated with structured verdict JSON output instructions
- [ ] REVIEW_JUDGE_SUBAGENTS.md: judge told NOT to commit report when invoked by the tool
- [ ] REVIEW_JUDGE_SUBAGENTS.md: judge told to write markdown report to a specified output path
- [ ] REVIEWER_SUBAGENTS.md updated: reviewer told to output report to stdout or specified path
- [ ] REVIEWER_SUBAGENTS.md: reviewer told NOT to commit when invoked by the tool
- [ ] ORCHESTRATOR_AGENT.md updated with "Using the conductor CLI" section
- [ ] DEVELOPER_SUBAGENTS.md: minor update noting reports are handled externally when using CLI
- [ ] All manual orchestration instructions still work (no breaking changes for non-tool users)
- [ ] README.md updated to mention the CLI tool and its commands

## Context References

### Relevant Codebase Files (must read)
- `REVIEW_JUDGE_SUBAGENTS.md` - Full judge instructions, especially lines 170-255 (report output)
- `REVIEWER_SUBAGENTS.md` - Full reviewer instructions, especially lines 262-334 (report format)
- `ORCHESTRATOR_AGENT.md` - Full orchestrator instructions
- `DEVELOPER_SUBAGENTS.md` - Developer instructions
- `README.md` - Getting started guide
- `conductor/schemas.py` - Verdict schema (the exact format the judge must output)

### Files to Modify
- `REVIEW_JUDGE_SUBAGENTS.md`
- `REVIEWER_SUBAGENTS.md`
- `ORCHESTRATOR_AGENT.md`
- `DEVELOPER_SUBAGENTS.md`
- `README.md`

## Implementation Plan

### Phase 1: Judge Updates
Add a section to REVIEW_JUDGE_SUBAGENTS.md:
- "When invoked by the conductor CLI" section explaining:
  - Write your markdown report to the file path specified in the prompt
  - Do NOT commit the report — the CLI handles git operations
  - Your final output must be a JSON verdict matching the schema:
- Update the Overall Verdict section: change `APPROVED AS-IS` → `APPROVED`, `NEEDS REVISION` → `NEEDS_REVISION`, `NEEDS DISCUSSION` → `NEEDS_DISCUSSION` (normalized enum values for machine parsing)
    ```json
    {
      "story_id": "X.Y",
      "iteration": N,
      "verdict": "APPROVED|NEEDS_REVISION|NEEDS_DISCUSSION",
      "approved_items": [{"id": "C1", "summary": "..."}],
      "rejected_items": [{"id": "M1", "summary": "...", "reason": "..."}]
    }
    ```
  - The verdict enum values and their meanings
- Keep existing manual instructions intact

### Phase 2: Reviewer Updates
Add a section to REVIEWER_SUBAGENTS.md:
- "When invoked by the conductor CLI" section explaining:
  - Write your review report to the file path specified in the prompt
  - Do NOT commit the report — the CLI handles git operations
  - Follow the same report format as before
- Keep existing manual instructions intact

### Phase 3: Developer Updates
Minor addition to DEVELOPER_SUBAGENTS.md:
- Note that when invoked by the conductor CLI, review reports and verdicts are handled externally
- Developer still commits code directly with `[Story X.Y]` format — no change there

### Phase 4: Orchestrator Updates
Add section to ORCHESTRATOR_AGENT.md:
- "Using the conductor CLI" section explaining:
  - How to use `conductor init` to set up a project
  - How to use `conductor validate-graph` to produce the dependency graph
  - How to use `conductor run --story X.Y` to automate the loop
  - How to use `conductor status` to check progress
  - When manual orchestration is still needed (NEEDS_DISCUSSION escalations, dependency ordering in v1)
- Keep all existing manual orchestration instructions

### Phase 5: README Updates
- Add "CLI Tool" section to README.md
- Document available commands
- Note that the CLI is optional — manual orchestration still works

## Step-by-Step Tasks

1. Add "When invoked by the conductor CLI" section to REVIEW_JUDGE_SUBAGENTS.md
2. Add verdict JSON schema example to judge instructions
3. Add "When invoked by the conductor CLI" section to REVIEWER_SUBAGENTS.md
4. Add brief CLI note to DEVELOPER_SUBAGENTS.md
5. Add "Using the conductor CLI" section to ORCHESTRATOR_AGENT.md
6. Update README.md with CLI tool documentation
7. Review all changes to ensure manual path still works
8. Test: read each doc as if you're an LLM agent — are instructions clear?

## Testing Strategy

- Read-through verification: each doc should be coherent for both CLI and manual use
- Verify verdict JSON schema in docs matches `conductor/schemas.py`
- Verify all CLI commands mentioned in docs actually exist

## Validation Commands

Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted.

- `grep -l "conductor CLI" *.md` (verify all docs updated)
- Diff review of each changed file

## Worktree Artifact Check

- Checked At: `2026-04-21`
- Planned Target Files: `REVIEW_JUDGE_SUBAGENTS.md`, `REVIEWER_SUBAGENTS.md`, `ORCHESTRATOR_AGENT.md`, `DEVELOPER_SUBAGENTS.md`, `README.md`
- Overlaps Found (path + class): `ORCHESTRATOR_AGENT.md -> tracked-dirty`
- Escalation Status: `pending`
- Decision Citation: `none`

### Escalation: ORCHESTRATOR_AGENT.md tracked-dirty overlap

- Target File: `ORCHESTRATOR_AGENT.md`
- Artifact Class: `tracked-dirty`
- Risk Summary: uncommitted modifications to this file exist in the working tree before this story begins. Editing now would conflate those prior changes with this story's "Using the conductor CLI" section additions, making review, revert, and attribution ambiguous.
- Recommended Default: commit or stash the pre-existing modifications (or explicitly discard) before this story's developer phase begins, restoring a clean working tree for `ORCHESTRATOR_AGENT.md`.
- User Decision Needed: confirm whether the pre-existing diff should be committed, stashed, or discarded, and by whom.

## Plan Approval and Commit Status

- Approval Status: `pending`
- Approval Citation: `none`
- Plan Commit Hash: `none`
- Ready-for-Orchestration: `no`

## Completion Checklist

- [ ] All acceptance criteria met
- [ ] Manual orchestration path still fully functional
- [ ] Verdict JSON format in docs matches code schema exactly
- [ ] README reflects current CLI capabilities
- [ ] Plan approved and committed before orchestration begins
- [ ] Worktree artifact overlaps resolved (approved direction or explicit deferral)
