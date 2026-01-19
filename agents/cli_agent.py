#!/usr/bin/env python3
"""
Generic CLI Agent implementation.

This module provides a concrete implementation of the BaseAgent that works
with any CLI-based AI tool by executing subprocess commands.
"""

import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import BaseAgent, AgentConfig, AgentResponse


class CLIAgent(BaseAgent):
    """
    Generic CLI agent that executes AI tools via subprocess.

    This implementation works with any CLI tool that accepts prompts as
    arguments and outputs responses to stdout.
    """

    def build_command(self, prompt: str, print_only: bool = False,
                      skip_permissions: bool = False,
                      extra_args: Optional[List[str]] = None) -> List[str]:
        """Build command line arguments for the CLI tool."""
        cmd = [self.command]

        # Add default args from config
        cmd.extend(self.config.args_template)

        # Add print flag if requested and available
        if print_only and self.config.print_flag:
            cmd.append(self.config.print_flag)

        # Add permission skip flag if requested and available
        if skip_permissions and self.config.permission_flag:
            cmd.append(self.config.permission_flag)

        # Add any extra arguments
        if extra_args:
            cmd.extend(extra_args)

        # Add the prompt as the final argument
        cmd.append(prompt)

        return cmd

    async def execute(self, prompt: str, working_dir: Optional[Path] = None,
                      print_only: bool = False, skip_permissions: bool = False,
                      timeout: Optional[int] = None) -> AgentResponse:
        """Execute the CLI agent asynchronously."""
        cmd = self.build_command(prompt, print_only, skip_permissions)
        effective_timeout = timeout or self.config.timeout
        cwd = str(working_dir) if working_dir else (
            str(self.config.working_dir) if self.config.working_dir else None
        )

        start_time = datetime.now()

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                cwd=cwd,
                env={**dict(__import__('os').environ), **self.config.env_vars}
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=effective_timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return AgentResponse(
                    success=False,
                    error=f"Command timed out after {effective_timeout} seconds",
                    exit_code=-1,
                    duration=effective_timeout,
                    command=' '.join(cmd[:3]) + '...',
                    agent_name=self.name
                )

            duration = (datetime.now() - start_time).total_seconds()

            return AgentResponse(
                success=process.returncode == 0,
                output=stdout.decode('utf-8') if stdout else "",
                error=stderr.decode('utf-8') if stderr else "",
                exit_code=process.returncode or 0,
                duration=duration,
                command=' '.join(cmd[:3]) + '...',
                agent_name=self.name
            )

        except FileNotFoundError:
            return AgentResponse(
                success=False,
                error=f"Command not found: {self.command}",
                exit_code=-1,
                duration=0.0,
                command=' '.join(cmd[:3]) + '...',
                agent_name=self.name
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return AgentResponse(
                success=False,
                error=str(e),
                exit_code=-1,
                duration=duration,
                command=' '.join(cmd[:3]) + '...',
                agent_name=self.name
            )

    def execute_sync(self, prompt: str, working_dir: Optional[Path] = None,
                     print_only: bool = False, skip_permissions: bool = False,
                     timeout: Optional[int] = None) -> AgentResponse:
        """Execute the CLI agent synchronously."""
        cmd = self.build_command(prompt, print_only, skip_permissions)
        effective_timeout = timeout or self.config.timeout
        cwd = str(working_dir) if working_dir else (
            str(self.config.working_dir) if self.config.working_dir else None
        )

        start_time = datetime.now()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=effective_timeout,
                env={**dict(__import__('os').environ), **self.config.env_vars}
            )

            duration = (datetime.now() - start_time).total_seconds()

            return AgentResponse(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode,
                duration=duration,
                command=' '.join(cmd[:3]) + '...',
                agent_name=self.name
            )

        except subprocess.TimeoutExpired:
            return AgentResponse(
                success=False,
                error=f"Command timed out after {effective_timeout} seconds",
                exit_code=-1,
                duration=effective_timeout,
                command=' '.join(cmd[:3]) + '...',
                agent_name=self.name
            )
        except FileNotFoundError:
            return AgentResponse(
                success=False,
                error=f"Command not found: {self.command}",
                exit_code=-1,
                duration=0.0,
                command=' '.join(cmd[:3]) + '...',
                agent_name=self.name
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return AgentResponse(
                success=False,
                error=str(e),
                exit_code=-1,
                duration=duration,
                command=' '.join(cmd[:3]) + '...',
                agent_name=self.name
            )
