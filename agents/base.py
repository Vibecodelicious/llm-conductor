#!/usr/bin/env python3
"""
Abstract base class for AI agent adapters.

This module defines the interface that all agent implementations must follow,
allowing the orchestrator to work with different AI CLI tools (Claude, Kiro,
Gemini CLI, etc.) through a unified interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str
    command: str  # The CLI command (e.g., 'claude', 'kiro', 'gemini')
    args_template: List[str] = field(default_factory=list)  # Default args
    print_flag: Optional[str] = None  # Flag to print output only (e.g., '--print')
    permission_flag: Optional[str] = None  # Flag to skip permissions
    timeout: int = 300  # Default timeout in seconds
    working_dir: Optional[Path] = None
    env_vars: Dict[str, str] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Standardized response from an agent."""
    success: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0
    duration: float = 0.0
    command: str = ""
    agent_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for AI agent implementations.

    All agent adapters (Claude, Kiro, Gemini CLI, etc.) should inherit from
    this class and implement the required methods.
    """

    def __init__(self, config: AgentConfig):
        """Initialize the agent with configuration."""
        self.config = config
        self.name = config.name
        self.command = config.command

    @abstractmethod
    def build_command(self, prompt: str, print_only: bool = False,
                      skip_permissions: bool = False,
                      extra_args: Optional[List[str]] = None) -> List[str]:
        """
        Build the command line arguments for the agent.

        Args:
            prompt: The prompt to send to the agent
            print_only: If True, agent should only print response (no file changes)
            skip_permissions: If True, skip permission prompts
            extra_args: Additional command line arguments

        Returns:
            List of command line arguments
        """
        pass

    @abstractmethod
    async def execute(self, prompt: str, working_dir: Optional[Path] = None,
                      print_only: bool = False, skip_permissions: bool = False,
                      timeout: Optional[int] = None) -> AgentResponse:
        """
        Execute the agent with the given prompt.

        Args:
            prompt: The prompt to send to the agent
            working_dir: Directory to run the agent in
            print_only: If True, agent should only print response
            skip_permissions: If True, skip permission prompts
            timeout: Timeout in seconds (overrides config)

        Returns:
            AgentResponse with the results
        """
        pass

    def execute_sync(self, prompt: str, working_dir: Optional[Path] = None,
                     print_only: bool = False, skip_permissions: bool = False,
                     timeout: Optional[int] = None) -> AgentResponse:
        """
        Synchronous execution of the agent.

        Args:
            prompt: The prompt to send to the agent
            working_dir: Directory to run the agent in
            print_only: If True, agent should only print response
            skip_permissions: If True, skip permission prompts
            timeout: Timeout in seconds (overrides config)

        Returns:
            AgentResponse with the results
        """
        # Default implementation - can be overridden
        import asyncio
        return asyncio.run(self.execute(prompt, working_dir, print_only,
                                        skip_permissions, timeout))

    def get_info(self) -> Dict[str, Any]:
        """Return information about this agent."""
        return {
            "name": self.name,
            "command": self.command,
            "config": {
                "timeout": self.config.timeout,
                "print_flag": self.config.print_flag,
                "permission_flag": self.config.permission_flag,
            }
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, command={self.command!r})"
