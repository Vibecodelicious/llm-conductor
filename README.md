# LLM Agent Harness

A multi-agent development framework for managing complex software projects through coordinated subagents and LLM-driven reviews. This lets an agent work on a dependency tree of tasks; it reviews its own work in a fresh context to produce more reliable output that requires less effort to review and approve or revise.

## Supported Platforms

This framework is designed to work with any LLM coding agent that supports:
- **Subagent/subprocess launching** (spawning isolated agent sessions)
- **File reading and writing**
- **Git operations**

Tested and compatible with:
- **Claude Code** (claude.ai/code)
- **Kiro** (AWS)
- **Codex** (OpenAI)
- **Gemini CLI** (Google)
- **AMP** (Sourcegraph)
- **Droids** (and similar agent frameworks)

## How It Works

The **Orchestrator Agent** coordinates development by launching specialized subagents:

- **Developer Subagents** - Implement stories following acceptance criteria
- **Reviewer Subagents** - Adversarially review implementations for issues
- **Judge Subagents** - Filter review feedback to prevent scope creep

Each story goes through a develop-review-judge loop (max 5 iterations) until complete or failed.

## Getting Started

### 1. Prepare Your Project Plan

You need some kind of project plan, even if it's just a checklist of tasks. The whole point of this framework is to push through all the work you have available systematically.

Ask an agent to read `ORCHESTRATOR_AGENT.md` and adapt your project plan to something that works with its structure. See `EPICS.example.md` for a template.

### 2. Load the Orchestrator Instructions

The method varies by platform:

**Claude Code:**
```bash
# Read the instructions directly in your prompt
cat ORCHESTRATOR_AGENT.md
# Or reference it in your initial prompt
```

**Kiro:**
```
/context add /path/to/ORCHESTRATOR_AGENT.md
```

**Codex / Other CLI tools:**
```bash
# Include in your system prompt or initial context
# Most tools support reading files as part of the conversation
```

**General approach:**
Ask the agent to read `ORCHESTRATOR_AGENT.md` as its operating instructions, then provide your project's epic/story definitions.

### 3. Start the Orchestration

Once the agent has the orchestrator instructions and your project plan, ask it to complete your tasks:

```
Complete epics 1-3
```

or

```
Work through all stories in the project plan
```

The orchestrator will launch subagents for development, review, and judgment, managing the entire workflow autonomously.

## Key Files

- `ORCHESTRATOR_AGENT.md` - Main orchestrator instructions
- `DEVELOPER_SUBAGENTS.md` - Developer implementation guidelines
- `REVIEWER_SUBAGENTS.md` - Adversarial review instructions
- `REVIEW_JUDGE.md` - Review filtering and approval logic
- `EPICS.example.md` - Example project structure template

## Platform-Specific Notes

### Subagent Invocation

Different platforms have different mechanisms for launching subagents:

| Platform | Subagent Mechanism |
|----------|-------------------|
| Claude Code | `Task` tool with subprocess |
| Kiro | `use_subagent` / `InvokeSubagents` |
| Codex | Agent spawning via API |
| Gemini CLI | Subprocess calls |
| AMP | Task delegation |

The orchestrator instructions use generic language that should adapt to your platform's subagent mechanism. If your platform has specific syntax, update the `ORCHESTRATOR_AGENT.md` file accordingly.

### Context Persistence

Some platforms support persistent context (instructions that survive session clears):
- **Kiro**: `/context add` for persistent instructions
- **Claude Code**: Project-level instructions
- **Others**: May require re-reading instructions each session

## Features

- Epic dependency management with parallel development paths
- Automatic merge conflict detection and resolution
- Story failure handling with escalation
- Progress tracking and completion reports
- Context window protection through delegation
- Adversarial review to catch issues before human review

## Customization

The instruction files use placeholder variables for project-specific paths:

```
[PROJECT_CODING_STANDARDS] - Your coding standards document
[PROJECT_EPICS] - Your epic/story definitions
[PROJECT_REQUIREMENTS] - Your requirements document
[PROJECT_ARCHITECTURE] - Your architecture document
```

Replace these placeholders with your actual file paths when setting up a project.

## Attribution

The adversarial review methodology in `REVIEWER_SUBAGENTS.md` was derived from the BMAD-METHOD project's [adversarial review task](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/src/core/tasks/review-adversarial-general.xml).
