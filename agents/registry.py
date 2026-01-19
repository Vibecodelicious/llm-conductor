#!/usr/bin/env python3
"""
Agent Registry and Factory.

This module provides pre-configured agent configurations for popular AI CLI
tools and a registry system for managing agents.
"""

from typing import Dict, Optional, Type
from pathlib import Path

from .base import BaseAgent, AgentConfig
from .cli_agent import CLIAgent


# Pre-defined configurations for popular AI CLI tools
AGENT_PRESETS: Dict[str, AgentConfig] = {
    # Claude Code CLI (Anthropic)
    "claude": AgentConfig(
        name="Claude",
        command="claude",
        print_flag="--print",
        permission_flag="--dangerously-skip-permissions",
        timeout=300,
    ),

    # Kiro (Amazon/AWS)
    "kiro": AgentConfig(
        name="Kiro",
        command="kiro",
        print_flag="--print",
        permission_flag="--yes",
        timeout=300,
    ),

    # Gemini CLI (Google)
    "gemini": AgentConfig(
        name="Gemini",
        command="gemini",
        print_flag="--no-interactive",
        permission_flag="--auto-approve",
        timeout=300,
    ),

    # Cline CLI
    "cline": AgentConfig(
        name="Cline",
        command="cline",
        print_flag="--print",
        permission_flag="--yes",
        timeout=300,
    ),

    # Aider
    "aider": AgentConfig(
        name="Aider",
        command="aider",
        args_template=["--yes-always", "--no-git"],
        print_flag=None,  # Aider doesn't have a print-only flag
        permission_flag=None,
        timeout=300,
    ),

    # Codex CLI (OpenAI)
    "codex": AgentConfig(
        name="Codex",
        command="codex",
        print_flag="--quiet",
        permission_flag="--approve-all",
        timeout=300,
    ),

    # Cursor CLI
    "cursor": AgentConfig(
        name="Cursor",
        command="cursor",
        print_flag="--print",
        permission_flag="--yes",
        timeout=300,
    ),

    # OpenCode
    "opencode": AgentConfig(
        name="OpenCode",
        command="opencode",
        print_flag="--output-only",
        permission_flag="--non-interactive",
        timeout=300,
    ),

    # Roo Code
    "roo": AgentConfig(
        name="Roo",
        command="roo",
        print_flag="--print",
        permission_flag="--auto",
        timeout=300,
    ),

    # Amp
    "amp": AgentConfig(
        name="Amp",
        command="amp",
        print_flag="--quiet",
        permission_flag="--yes",
        timeout=300,
    ),

    # GitHub Copilot CLI
    "copilot": AgentConfig(
        name="Copilot",
        command="gh",
        args_template=["copilot", "suggest"],
        print_flag=None,
        permission_flag=None,
        timeout=120,
    ),
}


class AgentRegistry:
    """
    Registry for managing agent instances.

    Provides factory methods to create agents from presets or custom configs.
    """

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._configs: Dict[str, AgentConfig] = dict(AGENT_PRESETS)

    def register_config(self, name: str, config: AgentConfig) -> None:
        """Register a custom agent configuration."""
        self._configs[name] = config

    def create_agent(self, preset_name: str,
                     agent_class: Type[BaseAgent] = CLIAgent,
                     override_config: Optional[Dict] = None) -> BaseAgent:
        """
        Create an agent from a preset configuration.

        Args:
            preset_name: Name of the preset (e.g., 'claude', 'kiro')
            agent_class: Agent implementation class to use
            override_config: Optional dict to override config values

        Returns:
            Configured agent instance
        """
        if preset_name not in self._configs:
            raise ValueError(f"Unknown agent preset: {preset_name}. "
                             f"Available: {list(self._configs.keys())}")

        config = self._configs[preset_name]

        # Apply overrides if provided
        if override_config:
            config_dict = {
                'name': config.name,
                'command': config.command,
                'args_template': config.args_template.copy(),
                'print_flag': config.print_flag,
                'permission_flag': config.permission_flag,
                'timeout': config.timeout,
                'working_dir': config.working_dir,
                'env_vars': config.env_vars.copy(),
            }
            config_dict.update(override_config)
            config = AgentConfig(**config_dict)

        agent = agent_class(config)
        self._agents[preset_name] = agent
        return agent

    def create_custom_agent(self, name: str, command: str,
                            print_flag: Optional[str] = None,
                            permission_flag: Optional[str] = None,
                            timeout: int = 300,
                            agent_class: Type[BaseAgent] = CLIAgent) -> BaseAgent:
        """
        Create an agent with custom configuration.

        Args:
            name: Display name for the agent
            command: CLI command to execute
            print_flag: Flag for print-only mode
            permission_flag: Flag to skip permission prompts
            timeout: Command timeout in seconds
            agent_class: Agent implementation class to use

        Returns:
            Configured agent instance
        """
        config = AgentConfig(
            name=name,
            command=command,
            print_flag=print_flag,
            permission_flag=permission_flag,
            timeout=timeout,
        )
        return agent_class(config)

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get a previously created agent by name."""
        return self._agents.get(name)

    def list_presets(self) -> Dict[str, AgentConfig]:
        """List all available agent presets."""
        return dict(self._configs)

    def list_agents(self) -> Dict[str, BaseAgent]:
        """List all created agent instances."""
        return dict(self._agents)


# Global registry instance
_default_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get the global agent registry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = AgentRegistry()
    return _default_registry


def create_agent(preset_name: str, **kwargs) -> BaseAgent:
    """Convenience function to create an agent from the global registry."""
    return get_registry().create_agent(preset_name, **kwargs)
