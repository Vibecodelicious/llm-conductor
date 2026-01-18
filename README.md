# LLM Conductor

A multi-agent development framework for managing complex software projects through coordinated LLM subagents.

## How It Works

The **Orchestrator Agent** coordinates development by launching specialized subagents:

- **Developer Subagents** - Implement stories following acceptance criteria
- **Reviewer Subagents** - Adversarially review implementations for issues
- **Judge Subagents** - Filter review feedback to prevent scope creep

Each story goes through a develop-review-judge loop (max 5 iterations) until complete or failed.

## Getting Started

1. **Prepare a project plan** - Even a simple task checklist works. The framework pushes through all available work systematically.

2. **Adapt your plan** - Ask an agent to read `ORCHESTRATOR_AGENT.md` and adapt your project plan to the epic/story format it expects. See `EPICS.example.md` for a template.

3. **Load the orchestrator** - Add `ORCHESTRATOR_AGENT.md` to your agent's context using whatever mechanism your harness provides:
   - **Claude Code**: Add to `CLAUDE.md` or reference in conversation
   - **Kiro**: `/context add ORCHESTRATOR_AGENT.md`
   - **Other harnesses**: Use your tool's persistent context or system prompt mechanism

4. **Start orchestrating** - Ask the agent if it needs anything else, then request work (e.g., "complete epics 1-3").

## Key Files

| File | Purpose |
|------|---------|
| `ORCHESTRATOR_AGENT.md` | Main orchestrator instructions |
| `DEVELOPER_SUBAGENTS.md` | Developer implementation guidelines |
| `REVIEWER_SUBAGENTS.md` | Adversarial review instructions |
| `REVIEW_JUDGE.md` | Review filtering and approval logic |
| `EPICS.example.md` | Example project structure template |

## Agent Harness Compatibility

This framework uses abstract `[LAUNCH SUBAGENT:]` markers that you map to your harness's subagent mechanism:

| Harness | Subagent Mechanism |
|---------|-------------------|
| Claude Code | `Task` tool with `subagent_type` |
| Kiro | `use_subagent` with `InvokeSubagents` |
| Generic | Any tool that spawns autonomous sub-tasks |

The orchestrator instructions are written to be harness-agnostic - adapt the subagent invocation to your specific tooling.

## Features

- Epic dependency management with parallel development paths
- Automatic merge conflict detection and resolution
- Story failure handling with escalation
- Progress tracking and completion reports
- Context window protection through delegation

## Attribution

The adversarial review methodology in `REVIEWER_SUBAGENTS.md` was derived from the BMAD-METHOD project's [adversarial review task](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/src/core/tasks/review-adversarial-general.xml).
