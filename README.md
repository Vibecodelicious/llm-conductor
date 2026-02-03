# LLM Agent Harness

A multi-agent development framework for managing complex software projects through coordinated subagents and LLM-driven reviews. This lets an agent work on a dependency tree of tasks; it reviews its own work in a fresh context to produce more reliable output that requires less effort to review and approve or revise.

## Supported Platforms

This framework is designed to work with any LLM coding agent that supports:
- **Subagent/subprocess launching** (spawning isolated agent sessions)
- **File reading and writing**
- **Git operations**

Tested and compatible with:
- **Claude Code** (Anthropic)
- **Kiro** (AWS)
- **Codex** (OpenAI)
- **Gemini CLI** (Google)
- **AMP** (Sourcegraph)
- **Droids** (Factory AI)
- **OpenCode** (open-source terminal AI)

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

**Claude Code** ([docs](https://docs.anthropic.com/en/docs/claude-code/memory)):
```markdown
# Add to your CLAUDE.md file (recommended for persistence):
@ORCHESTRATOR_AGENT.md

# Or ask Claude to read it in conversation:
"Please read ORCHESTRATOR_AGENT.md as your operating instructions"
```

**Kiro** ([docs](https://kiro.dev/docs/steering/)):
```bash
# Temporary (per-session):
/context add ORCHESTRATOR_AGENT.md

# Persistent: Copy to .kiro/steering/ directory
cp ORCHESTRATOR_AGENT.md .kiro/steering/
```

**Codex** ([docs](https://developers.openai.com/codex/guides/agents-md/)):
```markdown
# Create AGENTS.md in project root with:
@ORCHESTRATOR_AGENT.md
```

**Gemini CLI** ([docs](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html)):
```markdown
# Add to GEMINI.md file:
@ORCHESTRATOR_AGENT.md
```

**AMP** ([docs](https://ampcode.com/manual)):
```markdown
# Add to AGENT.md in project root, or create a skill in .agents/skills/
```

**Droids** ([docs](https://docs.factory.ai/cli/configuration/custom-droids)):
```yaml
# Create .factory/droids/orchestrator.md with YAML frontmatter:
---
name: orchestrator
tools: all
---

(paste ORCHESTRATOR_AGENT.md content here)
```

**OpenCode** ([docs](https://opencode.ai/docs/agents/)):
```yaml
# Create .opencode/agents/orchestrator.md with YAML frontmatter:
---
description: Multi-agent orchestrator for epic/story development
mode: primary
---

(paste ORCHESTRATOR_AGENT.md content here)
```
Then switch to it with Tab or invoke by name.

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
- `REVIEW_JUDGE_SUBAGENTS.md` - Review filtering and approval logic
- `EPICS.example.md` - Example project structure template

## Platform Reference

### Instruction File Locations

| Platform | Instruction File | Persistent Location | Documentation |
|----------|-----------------|---------------------|---------------|
| Claude Code | `CLAUDE.md` | `./CLAUDE.md`, `~/.claude/CLAUDE.md` | [docs.anthropic.com](https://docs.anthropic.com/en/docs/claude-code/memory) |
| Kiro | Steering files | `.kiro/steering/` | [kiro.dev/docs](https://kiro.dev/docs/steering/) |
| Codex | `AGENTS.md` | `./AGENTS.md`, `~/.codex/AGENTS.md` | [developers.openai.com](https://developers.openai.com/codex/guides/agents-md/) |
| Gemini CLI | `GEMINI.md` | `./GEMINI.md`, `~/.gemini/GEMINI.md` | [google-gemini.github.io](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html) |
| AMP | `AGENT.md` | `./AGENT.md`, `.agents/skills/` | [ampcode.com](https://ampcode.com/manual) |
| Droids | Custom `.md` | `.factory/droids/`, `~/.factory/droids/` | [docs.factory.ai](https://docs.factory.ai/cli/configuration/custom-droids) |
| OpenCode | Agent `.md` files | `.opencode/agents/`, `~/.config/opencode/agents/` | [opencode.ai](https://opencode.ai/docs/agents/) |

### Subagent Mechanisms

Different platforms have different mechanisms for launching subagents:

| Platform | Subagent Mechanism |
|----------|-------------------|
| Claude Code | `Task` tool with subprocess |
| Kiro | `use_subagent` / `InvokeSubagents` |
| Codex | Agent spawning via API |
| Gemini CLI | Subprocess calls |
| AMP | Task delegation |
| Droids | Droid invocation |
| OpenCode | Subagents (`mode: subagent`) |

The orchestrator instructions use generic language that should adapt to your platform's subagent mechanism. If your platform has specific syntax, update the `ORCHESTRATOR_AGENT.md` file accordingly.

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
