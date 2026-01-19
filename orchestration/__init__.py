"""
Orchestration module - Conductor implementations for AI agent coordination.

This module provides conductors that orchestrate AI agents to work together
on software development tasks.

Usage:
    from orchestration import CollaborativeConductor, FastCollaborativeConductor

    # Use detailed 5-phase collaboration (slower, more thorough)
    conductor = CollaborativeConductor(agent_preset="claude")
    result = await conductor.orchestrate("Create a web app")

    # Use fast parallel collaboration (faster, streamlined)
    fast_conductor = FastCollaborativeConductor(agent_preset="kiro")
    result = await fast_conductor.orchestrate("Create a CLI tool")
"""

from .base_conductor import BaseConductor
from .collaborative_conductor import CollaborativeConductor
from .fast_conductor import FastCollaborativeConductor

__all__ = [
    "BaseConductor",
    "CollaborativeConductor",
    "FastCollaborativeConductor",
]
