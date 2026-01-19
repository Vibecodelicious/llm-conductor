#!/usr/bin/env python3
"""
LLM Conductor - Main entry point.

Run the orchestration server or execute tasks from the command line.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents import AGENT_PRESETS, create_agent
from orchestration import CollaborativeConductor, FastCollaborativeConductor


def list_agents():
    """Print available agents."""
    print("\nAvailable Agent Presets:")
    print("-" * 50)
    for name, config in sorted(AGENT_PRESETS.items()):
        print(f"  {name:12} - {config.name} ({config.command})")
    print()


async def run_task(task: str, agent: str, fast: bool):
    """Run an orchestration task."""
    print(f"\n{'⚡' if fast else '🎭'} LLM Conductor")
    print(f"Agent: {agent}")
    print(f"Mode: {'Fast (parallel)' if fast else 'Detailed (sequential)'}")
    print(f"Task: {task}\n")

    if fast:
        conductor = FastCollaborativeConductor(agent_preset=agent)
    else:
        conductor = CollaborativeConductor(agent_preset=agent)

    result = await conductor.orchestrate(task)

    print("\n" + "=" * 50)
    print("Results:")
    print(f"  Success: {result['success']}")
    print(f"  Duration: {result['duration']:.1f}s")
    print(f"  Files created: {result['files_created']}")
    print(f"  Communications: {result['communications']}")
    print(f"  Project: {result['project_path']}")


def main():
    parser = argparse.ArgumentParser(
        description="LLM Conductor - Multi-Agent AI Orchestration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start the web server
  python run.py server

  # Run a task with default agent (Claude)
  python run.py task "Create a hello world Python script"

  # Run with a specific agent in fast mode
  python run.py task "Build a REST API" --agent kiro --fast

  # List available agents
  python run.py agents
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Server command
    server_parser = subparsers.add_parser("server", help="Start the web server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    server_parser.add_argument("--port", type=int, default=8200, help="Port to listen on")

    # Task command
    task_parser = subparsers.add_parser("task", help="Run an orchestration task")
    task_parser.add_argument("task", help="Task description")
    task_parser.add_argument("--agent", "-a", default="claude",
                            help=f"Agent to use ({', '.join(AGENT_PRESETS.keys())})")
    task_parser.add_argument("--fast", "-f", action="store_true",
                            help="Use fast parallel mode")
    task_parser.add_argument("--detailed", "-d", action="store_true",
                            help="Use detailed sequential mode (default)")

    # Agents command
    subparsers.add_parser("agents", help="List available agents")

    args = parser.parse_args()

    if args.command == "server":
        import os
        os.environ["HOST"] = args.host
        os.environ["PORT"] = str(args.port)
        from api.server import main as server_main
        server_main()

    elif args.command == "task":
        if args.agent not in AGENT_PRESETS:
            print(f"Error: Unknown agent '{args.agent}'")
            list_agents()
            sys.exit(1)

        fast = args.fast and not args.detailed
        asyncio.run(run_task(args.task, args.agent, fast))

    elif args.command == "agents":
        list_agents()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
