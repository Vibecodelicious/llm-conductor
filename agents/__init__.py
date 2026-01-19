"""
Agents module - AI agent implementations and registry.

This module provides a harness-agnostic interface for working with different
AI CLI tools like Claude, Kiro, Gemini CLI, and others.

Usage:
    from agents import create_agent, AgentConfig

    # Create an agent from a preset
    agent = create_agent("claude")

    # Execute a prompt
    response = await agent.execute("Write a hello world program")

    # Or create a custom agent
    from agents import CLIAgent, AgentConfig

    config = AgentConfig(
        name="MyTool",
        command="mytool",
        print_flag="--print",
        permission_flag="--yes",
    )
    agent = CLIAgent(config)
"""

from .base import BaseAgent, AgentConfig, AgentResponse
from .cli_agent import CLIAgent
from .registry import (
    AgentRegistry,
    AGENT_PRESETS,
    get_registry,
    create_agent,
)

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentConfig",
    "AgentResponse",
    # Implementations
    "CLIAgent",
    # Registry
    "AgentRegistry",
    "AGENT_PRESETS",
    "get_registry",
    "create_agent",
]
