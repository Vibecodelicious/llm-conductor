#!/usr/bin/env python3
"""Tests for the agents module."""

import pytest
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import (
    BaseAgent,
    AgentConfig,
    AgentResponse,
    CLIAgent,
    AgentRegistry,
    AGENT_PRESETS,
    create_agent,
    get_registry,
)


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_basic_config(self):
        """Test creating a basic config."""
        config = AgentConfig(
            name="TestAgent",
            command="test-cli",
        )
        assert config.name == "TestAgent"
        assert config.command == "test-cli"
        assert config.timeout == 300  # default

    def test_full_config(self):
        """Test creating a config with all options."""
        config = AgentConfig(
            name="TestAgent",
            command="test-cli",
            args_template=["--verbose"],
            print_flag="--print",
            permission_flag="--yes",
            timeout=600,
        )
        assert config.print_flag == "--print"
        assert config.permission_flag == "--yes"
        assert config.timeout == 600


class TestAgentPresets:
    """Tests for pre-defined agent presets."""

    def test_claude_preset_exists(self):
        """Test that Claude preset is defined."""
        assert "claude" in AGENT_PRESETS
        config = AGENT_PRESETS["claude"]
        assert config.name == "Claude"
        assert config.command == "claude"
        assert config.print_flag == "--print"

    def test_kiro_preset_exists(self):
        """Test that Kiro preset is defined."""
        assert "kiro" in AGENT_PRESETS
        config = AGENT_PRESETS["kiro"]
        assert config.name == "Kiro"

    def test_all_presets_have_required_fields(self):
        """Test that all presets have required fields."""
        for name, config in AGENT_PRESETS.items():
            assert config.name, f"{name} missing name"
            assert config.command, f"{name} missing command"
            assert config.timeout > 0, f"{name} has invalid timeout"


class TestCLIAgent:
    """Tests for CLIAgent implementation."""

    def test_build_command_basic(self):
        """Test building a basic command."""
        config = AgentConfig(
            name="Test",
            command="test-cli",
        )
        agent = CLIAgent(config)
        cmd = agent.build_command("hello")
        assert cmd == ["test-cli", "hello"]

    def test_build_command_with_flags(self):
        """Test building a command with flags."""
        config = AgentConfig(
            name="Test",
            command="test-cli",
            print_flag="--print",
            permission_flag="--yes",
        )
        agent = CLIAgent(config)
        cmd = agent.build_command("hello", print_only=True, skip_permissions=True)
        assert "--print" in cmd
        assert "--yes" in cmd
        assert "hello" in cmd

    def test_build_command_with_template_args(self):
        """Test building a command with template args."""
        config = AgentConfig(
            name="Test",
            command="test-cli",
            args_template=["--verbose", "--output=json"],
        )
        agent = CLIAgent(config)
        cmd = agent.build_command("hello")
        assert cmd == ["test-cli", "--verbose", "--output=json", "hello"]


class TestAgentRegistry:
    """Tests for AgentRegistry."""

    def test_create_from_preset(self):
        """Test creating an agent from a preset."""
        registry = AgentRegistry()
        agent = registry.create_agent("claude")
        assert agent.name == "Claude"
        assert agent.command == "claude"

    def test_create_unknown_preset_raises(self):
        """Test that unknown preset raises error."""
        registry = AgentRegistry()
        with pytest.raises(ValueError, match="Unknown agent preset"):
            registry.create_agent("unknown-agent")

    def test_create_with_override(self):
        """Test creating with config override."""
        registry = AgentRegistry()
        agent = registry.create_agent("claude", override_config={"timeout": 600})
        assert agent.config.timeout == 600

    def test_create_custom_agent(self):
        """Test creating a custom agent."""
        registry = AgentRegistry()
        agent = registry.create_custom_agent(
            name="Custom",
            command="custom-cli",
            print_flag="--output",
        )
        assert agent.name == "Custom"
        assert agent.command == "custom-cli"

    def test_list_presets(self):
        """Test listing presets."""
        registry = AgentRegistry()
        presets = registry.list_presets()
        assert "claude" in presets
        assert "kiro" in presets


class TestGlobalRegistry:
    """Tests for global registry functions."""

    def test_get_registry(self):
        """Test getting the global registry."""
        registry = get_registry()
        assert isinstance(registry, AgentRegistry)

    def test_create_agent_convenience(self):
        """Test the create_agent convenience function."""
        agent = create_agent("claude")
        assert agent.name == "Claude"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
