# Story: Skill Creation

**Epic:** Conductor CLI Tool
**Size:** Medium
**Dependencies:** Story 5 (Loop Runner), Story 6 (Documentation Updates)

## Story Description

Create the llm-conductor skill for the agent skills ecosystem. The skill serves as the entry point for agents discovering and using the framework — it routes them to the right docs and tools based on what they need.

This story uses the skill-creator workflow: draft the SKILL.md, create test cases, evaluate, iterate. **This is a human-assisted story** — the skill-creator process is iterative and requires human evaluation of outputs. It does not go through the automated conductor loop.

**Open question:** Should the skill directory be at `skill/` (separate from framework docs, references are adapted copies) or should the repo root itself be the skill (SKILL.md at root, no duplication)? The latter avoids maintaining two copies of docs but constrains repo structure. This needs to be resolved before implementation.

## User Model

### User Gamut
- Developers who say "orchestrate my project" or "run my stories"
- Developers who have a project plan and want to automate development
- Developers who hear about llm-conductor and want to set it up
- Users who want help planning a project using the epic/story structure
- Users debugging a failed orchestration run

### User-Needs Gamut
- Quick setup guidance — "how do I get started?"
- Orchestration kickoff — "run my project plan through the develop-review-judge loop"
- Planning help — "break this feature request into stories"
- Status/debugging — "what went wrong with story 2.3?"
- Understanding — "how does the review judge work?"

### Design Implications
- SKILL.md must be a router, not a dump of all content
- Description must trigger on orchestration, multi-agent development, story management, and review loop keywords
- References should be loaded on demand, not all at once
- The skill must work for both CLI users and manual orchestration users

## Acceptance Criteria

- [ ] SKILL.md with frontmatter (name, description) exists at skill root
- [ ] SKILL.md under 500 lines (progressive disclosure via references)
- [ ] Description triggers on relevant user intents (orchestrate, stories, epics, review loop, etc.)
- [ ] SKILL.md routes to correct reference based on user need
- [ ] References bundled for: orchestrator, developer, reviewer, judge, planning, CLI tool usage
- [ ] Skill installable via `npx skills add` (proper directory structure)
- [ ] Works for Claude Code users (primary target)
- [ ] Doesn't break for non-Claude-Code users (graceful fallback to manual orchestration)

## Context References

### Relevant Codebase Files (must read)
- All `.md` files in repo root — these become references
- `~/.agents/skills/skill-creator/SKILL.md` - Skill-creator instructions for authoring
- `conductor/` - CLI tool (from previous stories)

### New Files to Create
- `skill/SKILL.md` - Main skill file
- `skill/references/orchestrator.md` - Orchestrator reference
- `skill/references/developer.md` - Developer subagent reference
- `skill/references/reviewer.md` - Reviewer subagent reference
- `skill/references/judge.md` - Judge subagent reference
- `skill/references/planning.md` - Planning guidance reference
- `skill/references/cli-tool.md` - CLI tool usage reference
- `skill/references/epics-template.md` - Epic/story template reference

## Implementation Plan

### Phase 1: Draft SKILL.md
Write the main skill file that:
- Describes what llm-conductor is and when to use it
- Detects user intent:
  - "Set up orchestration" → guide through init + graph creation
  - "Run my stories/epics" → guide through CLI tool or manual orchestration
  - "Plan a feature" → route to planning guidance
  - "Debug orchestration" → check status, read reports, diagnose
  - "How does X work?" → route to relevant reference doc
- Points to the right reference for each path
- Keeps under 500 lines

### Phase 2: Create References
- Copy/adapt the framework docs into reference files
- Each reference should be self-contained enough to be useful when loaded
- Add table of contents to references over 300 lines
- CLI tool reference is new content (how to use the conductor commands)

### Phase 3: Test Cases (using skill-creator workflow)
Create 2-3 test prompts:
1. "I have a project plan, help me orchestrate the development"
2. "Set up llm-conductor in my project"
3. "Story 2.1 failed after 5 iterations, what do I do?"

### Phase 4: Evaluate and Iterate
- Run test cases with skill loaded
- Review outputs
- Refine SKILL.md based on results

### Phase 5: Description Optimization
- Use skill-creator's description optimization loop
- Generate trigger eval queries (should-trigger and should-not-trigger)
- Optimize description for accurate triggering

## Step-by-Step Tasks

1. Read skill-creator SKILL.md for authoring best practices
2. Draft SKILL.md with routing logic and intent detection
3. Create reference files from existing docs
4. Create CLI tool reference (new content)
5. Write test prompts in evals/evals.json
6. Run test cases via skill-creator workflow
7. Evaluate results and gather feedback
8. Iterate on SKILL.md based on feedback
9. Run description optimization
10. Package final skill

## Testing Strategy

- Skill-creator evaluation workflow (test prompts + human review)
- Verify all references are reachable from SKILL.md
- Verify skill triggers on expected intents
- Verify skill doesn't trigger on unrelated prompts

## Validation Commands

Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted.

- Verify SKILL.md is under 500 lines: `wc -l skill/SKILL.md`
- Verify all referenced files exist
- Run skill-creator test workflow

## Worktree Artifact Check

- Checked At: `2026-04-21`
- Planned Target Files: `skill/SKILL.md`, `skill/references/orchestrator.md`, `skill/references/developer.md`, `skill/references/reviewer.md`, `skill/references/judge.md`, `skill/references/planning.md`, `skill/references/cli-tool.md`, `skill/references/epics-template.md`
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
- [ ] SKILL.md under 500 lines
- [ ] Description optimized for triggering accuracy
- [ ] All references accessible and self-contained
- [ ] Skill installable via npx skills add
- [ ] Plan approved and committed before orchestration begins
- [ ] Worktree artifact overlaps resolved (approved direction or explicit deferral)
