#!/usr/bin/env python3
"""
Fast Collaborative Conductor - Parallel execution orchestration.

This conductor implements a streamlined 3-phase workflow with parallel
execution for faster task completion.
"""

import asyncio
import concurrent.futures
from functools import partial
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from .base_conductor import BaseConductor
from agents import AgentResponse


class FastCollaborativeConductor(BaseConductor):
    """
    Fast orchestrator with parallel agent execution.

    Phases:
    1. Parallel Analysis & Design - Multiple agents work simultaneously
    2. Rapid Implementation - Build based on combined insights
    3. Quick Validation - Verify outputs
    """

    def __init__(self, agent_preset: str = "claude", base_dir: Optional[Path] = None,
                 max_workers: int = 3):
        """
        Initialize the fast conductor.

        Args:
            agent_preset: Name of the agent preset to use
            base_dir: Base directory for project outputs
            max_workers: Maximum number of parallel agent executions
        """
        super().__init__(agent_preset, base_dir)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def _run_agent_sync(self, prompt: str, role: str, working_dir: Path,
                        print_only: bool) -> Dict[str, Any]:
        """Synchronous agent execution for thread pool."""
        start_time = datetime.now()

        try:
            response = self.agent.execute_sync(
                prompt=prompt,
                working_dir=working_dir,
                print_only=print_only,
                skip_permissions=True
            )

            return {
                'success': response.success,
                'output': response.output,
                'error': response.error,
                'role': role,
                'duration': response.duration,
                'prompt': prompt
            }

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {
                'success': False,
                'error': str(e),
                'role': role,
                'duration': duration,
                'prompt': prompt
            }

    async def run_parallel_agents(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run multiple agent tasks in parallel.

        Args:
            tasks: List of task dicts with 'prompt', 'role', 'type' keys

        Returns:
            List of result dictionaries
        """
        loop = asyncio.get_event_loop()

        # Create futures for parallel execution
        futures = []
        for task in tasks:
            # Determine working directory based on task type
            if task.get('type') in ['analysis', 'design', 'review']:
                working_dir = self.working_dir / 'docs'
            else:
                working_dir = self.working_dir / 'src'

            print_only = task.get('type') in ['analysis', 'design', 'review']

            future = loop.run_in_executor(
                self.executor,
                partial(
                    self._run_agent_sync,
                    task['prompt'],
                    task['role'],
                    working_dir,
                    print_only
                )
            )
            futures.append(future)

        # Wait for all tasks to complete
        results = await asyncio.gather(*futures)

        # Process results and broadcast
        for i, result in enumerate(results):
            task = tasks[i]

            # Broadcast output
            await self.broadcast({
                'type': 'agent_output',
                'tool': self.agent_preset,
                'agent': f"{self.agent.name}-{task['role']}",
                'line': f"{task['role']}: {result.get('output', '')[:100]}...",
                'success': result.get('success', False),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })

            # Store communication
            self.communications.append({
                'agent': f"{self.agent.name}-{task['role']}",
                'timestamp': datetime.now().isoformat(),
                'prompt': task.get('prompt', ''),
                'response': result.get('output', ''),
                'success': result.get('success', False),
                'duration': result.get('duration', 0),
                'type': task.get('type', 'action')
            })

        return results

    async def orchestrate(self, task: str) -> Dict[str, Any]:
        """Run the fast parallel orchestration workflow."""
        return await self.fast_orchestrate(task)

    async def fast_orchestrate(self, task: str) -> Dict[str, Any]:
        """Fast orchestration with parallel execution and project folders."""
        # Set up project directory
        self._setup_project_directory(task)
        await self.broadcast_project_info()

        print(f"\n⚡ FAST COLLABORATIVE ORCHESTRATION: {task}")
        print("="*70)

        start_time = datetime.now()

        # === PHASE 1: Parallel Analysis & Design ===
        print("\n⚡ Phase 1: Parallel Analysis & Design")
        await self.broadcast({'type': 'phase', 'phase': 'Phase 1: Parallel Analysis & Design'})

        parallel_tasks = [
            {
                'role': 'Analyst',
                'prompt': f"Analyze and plan: {task}",
                'type': 'analysis'
            },
            {
                'role': 'Designer',
                'prompt': f"Design architecture for: {task}",
                'type': 'design'
            }
        ]

        analysis_results = await self.run_parallel_agents(parallel_tasks)

        # Save analysis results
        for i, result in enumerate(analysis_results):
            if result.get('success') and result.get('output'):
                filename = f"{parallel_tasks[i]['role'].lower()}_output.md"
                (self.working_dir / 'docs' / filename).write_text(result['output'])

        # === PHASE 2: Rapid Implementation ===
        print("\n⚡ Phase 2: Rapid Implementation")
        await self.broadcast({'type': 'phase', 'phase': 'Phase 2: Rapid Implementation'})

        # Combine insights from parallel analysis
        combined_insights = "\n".join([
            f"{r.get('role', 'Unknown')}: {r.get('output', '')[:200]}..."
            for r in analysis_results if r.get('success')
        ])

        impl_tasks = [{
            'role': 'Implementer',
            'prompt': f"Implement {task} based on these insights:\n{combined_insights}",
            'type': 'implementation'
        }]

        await self.run_parallel_agents(impl_tasks)

        # === PHASE 3: Quick Validation ===
        print("\n⚡ Phase 3: Rapid Validation")
        await self.broadcast({'type': 'phase', 'phase': 'Phase 3: Rapid Validation'})

        # Check created files
        created_files = list((self.working_dir / 'src').glob("*.*"))
        print(f"\n✅ Created {len(created_files)} source files")

        for file in created_files[:5]:  # Show first 5 files
            print(f"  • {file.name}")

        if len(created_files) > 5:
            print(f"  ... and {len(created_files) - 5} more files")

        # Summary
        total_time = (datetime.now() - start_time).total_seconds()
        print(f"\n⚡ Collaboration completed in {total_time:.1f} seconds!")
        print(f"📁 Project location: {self.working_dir}")

        # Update README
        self._update_readme_with_files()

        # Add performance info to README
        readme_path = self.working_dir / 'README.md'
        readme_content = readme_path.read_text()
        readme_content += f"\n\n## Performance\nGenerated in {total_time:.1f} seconds using parallel execution."
        readme_path.write_text(readme_content)

        # Save communication log
        self._save_communication_log("fast_communication_log.json")

        # Notify completion
        await self.broadcast({
            'type': 'orchestration_complete',
            'project_path': str(self.working_dir),
            'files_created': len(created_files),
            'duration': total_time,
            'communications': len(self.communications),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })

        return {
            'success': True,
            'duration': total_time,
            'files_created': len(created_files),
            'communications': len(self.communications),
            'project_path': str(self.working_dir)
        }

    def __del__(self):
        """Clean up thread pool on destruction."""
        self.executor.shutdown(wait=False)


async def demo_fast_collaboration():
    """Demo the fast collaborative conductor."""
    conductor = FastCollaborativeConductor()

    await conductor.fast_orchestrate(
        "Create a simple todo list web app"
    )


if __name__ == "__main__":
    print("⚡ Fast Collaborative Conductor - Parallel Execution")
    print("Streamlined 3-phase workflow with parallel agent execution\n")
    asyncio.run(demo_fast_collaboration())
