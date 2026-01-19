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

## Conductor Server

In addition to the orchestrator agent framework, this repo includes a **Conductor** - a web-based orchestration server that coordinates AI CLI tools to work collaboratively on tasks.

### Quick Start (Conductor)

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
python run.py server

# Open browser to http://localhost:8200
```

### Supported AI CLI Tools

The conductor supports multiple AI CLI tools through a harness-agnostic interface:

| Tool | Command | Status |
|------|---------|--------|
| Claude Code | `claude` | ✅ Tested |
| Kiro | `kiro` | ✅ Supported |
| Gemini CLI | `gemini` | ✅ Supported |
| Cline | `cline` | ✅ Supported |
| Aider | `aider` | ✅ Supported |
| Cursor CLI | `cursor` | ✅ Supported |
| OpenCode | `opencode` | ✅ Supported |
| Roo Code | `roo` | ✅ Supported |
| Amp | `amp` | ✅ Supported |
| GitHub Copilot | `gh copilot` | ✅ Supported |

### Orchestration Modes

- **Fast Mode** (⚡): Parallel agent execution for quick results
- **Detailed Mode** (🎭): Sequential 5-phase collaboration with reviews

### Command Line Usage

```bash
# Run a task with default agent (Claude)
python run.py task "Create a hello world Python script"

# Use a specific agent
python run.py task "Build a REST API" --agent kiro --fast

# List available agents
python run.py agents
```

### Architecture

```
llm-conductor/
├── agents/                 # Agent interface and implementations
│   ├── base.py            # Abstract agent interface
│   ├── cli_agent.py       # Generic CLI agent implementation
│   └── registry.py        # Agent presets and factory
├── orchestration/         # Orchestration conductors
│   ├── base_conductor.py  # Base conductor class
│   ├── collaborative_conductor.py  # Detailed 5-phase workflow
│   └── fast_conductor.py  # Parallel execution workflow
├── api/                   # Web server
│   └── server.py          # FastAPI server with WebSocket support
├── projects_master/       # Generated project outputs
└── run.py                 # CLI entry point
```

## Attribution

The adversarial review methodology in `REVIEWER_SUBAGENTS.md` was derived from the BMAD-METHOD project's [adversarial review task](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/src/core/tasks/review-adversarial-general.xml).

The conductor components were adapted from the [Multi-LLM-Conductor](https://github.com/Clark-Wallace/Multi-LLM-Conductor) project and genericized to support multiple AI CLI tools.
