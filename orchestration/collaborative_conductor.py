#!/usr/bin/env python3
"""
Collaborative Conductor - Detailed multi-phase orchestration.

This conductor implements a thorough 5-phase collaboration workflow where
agents analyze, implement, review, improve, and validate tasks.
"""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from .base_conductor import BaseConductor


class CollaborativeConductor(BaseConductor):
    """
    Orchestrator with detailed 5-phase collaboration workflow.

    Phases:
    1. Initial Analysis - Understand requirements and plan approach
    2. Implementation - Build the solution
    3. Peer Review - Review implementation for issues
    4. Improvement - Apply review feedback
    5. Final Review - Validate improvements
    """

    def __init__(self, agent_preset: str = "claude", base_dir: Optional[Path] = None):
        """Initialize the collaborative conductor."""
        super().__init__(agent_preset, base_dir)

    async def orchestrate(self, task: str) -> Dict[str, Any]:
        """Run the detailed collaborative orchestration workflow."""
        return await self.orchestrate_with_dialogue(task)

    async def orchestrate_with_dialogue(self, task: str) -> Dict[str, Any]:
        """Orchestrate a task with full dialogue visibility."""
        # Set up project directory
        self._setup_project_directory(task)
        await self.broadcast_project_info()

        print(f"\n🎭 COLLABORATIVE ORCHESTRATION: {task}")
        print("="*70)
        print("Watch the AI agents communicate and collaborate!\n")

        start_time = datetime.now()

        # Save task context
        context_file = self.working_dir / "docs" / "task_context.md"
        context_file.write_text(f"# Task\n{task}\n\n# Communications Log\n")

        # === PHASE 1: Initial Analysis ===
        print("\n💬 PHASE 1: Initial Analysis")
        await self.broadcast({'type': 'phase', 'phase': 'Phase 1: Initial Analysis'})

        analysis_prompt = f"""Analyze this task and create a detailed implementation plan:
{task}

Please provide:
1. Your understanding of the requirements
2. Technical approach you would take
3. File structure needed
4. Key features to implement"""

        result1 = await self.run_agent(analysis_prompt, "Analyst", print_only=True)

        # Save analysis
        if result1.output:
            (self.working_dir / "docs" / "analysis.md").write_text(result1.output)

        # === PHASE 2: Implementation ===
        print("\n💬 PHASE 2: Implementation")
        await self.broadcast({'type': 'phase', 'phase': 'Phase 2: Implementation'})

        impl_prompt = f"Based on this plan, implement: {task}"

        result2 = await self.run_agent(impl_prompt, "Implementer", print_only=False)

        # Show what files were created
        print("\n📁 Files created:")
        src_files = list((self.working_dir / 'src').iterdir())
        for file in src_files:
            if file.is_file():
                print(f"  ✅ {file.name}")

        # === PHASE 3: Peer Review ===
        print("\n💬 PHASE 3: Peer Review")
        await self.broadcast({'type': 'phase', 'phase': 'Phase 3: Peer Review'})

        impl_files = [f for f in (self.working_dir / 'src').iterdir()
                      if f.is_file() and f.suffix in ['.py', '.js', '.html', '.css', '.ts', '.tsx', '.go', '.rs']]

        review_output = ""
        if impl_files:
            # Read first implementation file for context
            first_file = impl_files[0]
            file_content = first_file.read_text()[:500] + "..."

            review_prompt = f"""Review the implementation for: {task}

These files were created in src/: {', '.join(f.name for f in impl_files)}

Here's a preview of {first_file.name}:
{file_content}

Please review and provide:
1. What works well
2. Potential issues or bugs
3. Specific improvements needed
4. Code quality assessment"""

            result3 = await self.run_agent(review_prompt, "Reviewer", print_only=True)

            # Save review
            if result3.output:
                review_output = result3.output
                (self.working_dir / "docs" / "review.md").write_text(result3.output)

            # === PHASE 4: Improvement ===
            print("\n💬 PHASE 4: Improvement Implementation")
            await self.broadcast({'type': 'phase', 'phase': 'Phase 4: Improvement'})

            improve_prompt = f"""Based on this review feedback:
{review_output[:300]}...

Please improve the existing implementation in the src/ directory. Make it better, more robust, and address the feedback."""

            await self.run_agent(improve_prompt, "Improver", print_only=False)

            # === PHASE 5: Final Review ===
            print("\n💬 PHASE 5: Final Review")
            await self.broadcast({'type': 'phase', 'phase': 'Phase 5: Final Review'})

            final_prompt = f"""The implementation for '{task}' has been reviewed and improved.

Please check what improvements were made and provide your final assessment."""

            result5 = await self.run_agent(final_prompt, "Final Reviewer", print_only=True)

            if result5.output:
                (self.working_dir / "docs" / "final_review.md").write_text(result5.output)

        # === SUMMARY ===
        total_time = (datetime.now() - start_time).total_seconds()

        print("\n" + "="*70)
        print("🎉 COLLABORATION COMPLETE!")
        print("="*70)

        print(f"\n📊 Communication Summary:")
        print(f"  • Total exchanges: {len(self.communications)}")
        print(f"  • Analysis messages: {sum(1 for c in self.communications if c['type'] == 'analysis')}")
        print(f"  • Action messages: {sum(1 for c in self.communications if c['type'] == 'action')}")
        print(f"  • Total time: {total_time:.1f} seconds")

        # Update README with file list
        self._update_readme_with_files()

        # Save communication log
        log_file = self._save_communication_log()
        print(f"\n💾 Full communication log saved to: {log_file}")

        print(f"\n📁 Project location: {self.working_dir}")
        print(f"📋 Total files created: {len(list(self.working_dir.rglob('*.*')))}")

        # Notify completion
        await self.broadcast({
            'type': 'orchestration_complete',
            'project_path': str(self.working_dir),
            'files_created': len(list(self.working_dir.rglob('*.*'))),
            'duration': total_time,
            'communications': len(self.communications),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })

        return {
            'success': True,
            'duration': total_time,
            'files_created': len(list(self.working_dir.rglob('*.*'))),
            'communications': len(self.communications),
            'project_path': str(self.working_dir)
        }


async def demo_collaboration():
    """Demo the collaborative conductor."""
    conductor = CollaborativeConductor()

    await conductor.orchestrate(
        "Create an interactive countdown timer web app with start, pause, reset functions"
    )


if __name__ == "__main__":
    print("🎭 Collaborative Conductor - Detailed Multi-Phase Orchestration")
    print("Full 5-phase collaboration with comprehensive reviews\n")
    asyncio.run(demo_collaboration())
