#!/usr/bin/env python3
"""
hyper_split.py
Recursive task decomposition engine for ADHD brains.
Breaks overwhelming tasks into micro-tasks (≤15 min each).
Uses heuristics + optional local LLM via MCP.
BROski♾️
"""

import asyncio
import json
import os
import re
from typing import Dict, Any, List
from datetime import datetime

import aiofiles


class HyperSplitEngine:
    """Decomposes tasks into ADHD-friendly micro-tasks."""

    # Task type patterns for heuristic decomposition
    PATTERNS = {
        "api_endpoint": [
            "Define route + HTTP method",
            "Write request/response schemas (Pydantic)",
            "Implement handler logic",
            "Add auth middleware",
            "Write tests (pytest)",
            "Update OpenAPI docs"
        ],
        "ui_component": [
            "Sketch layout + props interface",
            "Build static markup (no state)",
            "Add state management",
            "Wire events + handlers",
            "Style + accessibility pass",
            "Write Storybook / test"
        ],
        "database_migration": [
            "Backup current schema",
            "Write migration script",
            "Test migration on staging",
            "Update model definitions",
            "Update queries + indexes",
            "Verify data integrity"
        ],
        "bug_fix": [
            "Reproduce bug locally",
            "Add failing test case",
            "Identify root cause",
            "Implement fix",
            "Verify test passes",
            "Deploy + monitor"
        ],
        "documentation": [
            "Outline sections",
            "Write draft (brain dump)",
            "Add code examples",
            "Review for clarity",
            "Add diagrams / visuals",
            "Publish + share"
        ],
        "refactor": [
            "Identify smell + scope",
            "Write characterization tests",
            "Extract method / class",
            "Update call sites",
            "Run full test suite",
            "Clean up + commit"
        ]
    }

    def __init__(self, vault_path: str):
        self.vault_path = vault_path

    async def decompose(self, title: str, description: str, max_depth: int = 3,
                       target_minutes: int = 15) -> Dict[str, Any]:
        """
        Recursively decompose a task into micro-tasks.
        Returns a tree structure with estimated times.
        """
        tree = {
            "root": title,
            "description": description,
            "estimated_total_minutes": 0,
            "micro_tasks": [],
            "count": 0,
            "depth": 0
        }

        # Detect task type from description
        task_type = self._detect_task_type(description)

        # Get base steps
        base_steps = self.PATTERNS.get(task_type, self._generate_generic_steps(description))

        # Build micro-task tree
        for i, step in enumerate(base_steps, 1):
            micro = await self._create_micro_task(
                step, i, depth=1, max_depth=max_depth, target_minutes=target_minutes
            )
            tree["micro_tasks"].append(micro)
            tree["count"] += micro["sub_count"] + 1
            tree["estimated_total_minutes"] += micro["estimated_minutes"]

        tree["depth"] = max(t["depth"] for t in tree["micro_tasks"])

        return tree

    async def write_to_vault(self, tree: Dict[str, Any], vault_path: str) -> str:
        """Write decomposed task tree as markdown with checkboxes."""
        tasks_dir = os.path.join(vault_path, "01-Projects", "HyperSplit-Tasks")
        os.makedirs(tasks_dir, exist_ok=True)

        safe_title = re.sub(r"[^\w\-]+", "_", tree["root"])[:40]
        fname = f"HyperSplit_{safe_title}_{datetime.utcnow().strftime('%Y%m%d')}.md"
        fpath = os.path.join(tasks_dir, fname)

        def render_task(task: Dict, indent: int = 0) -> str:
            prefix = "  " * indent
            lines = [
                f"{prefix}- [ ] **{task['title']}** ({task['estimated_minutes']}m)",
                f"{prefix}  - {task.get('hint', '')}",
            ]
            for sub in task.get("sub_tasks", []):
                lines.append(render_task(sub, indent + 1))
            return "\n".join(lines)

        task_lines = "\n\n".join(render_task(t) for t in tree["micro_tasks"])

        note = f"""---
created: {datetime.utcnow().isoformat()}
type: hypersplit
parent_task: {tree['root']}
estimated_total: {tree['estimated_total_minutes']}m
micro_tasks: {tree['count']}
depth: {tree['depth']}
tags: [hypersplit, project, task-tree]
---
# 🪓 HyperSplit: {tree['root']}

> {tree['description']}

**Total Time**: {tree['estimated_total_minutes']} minutes  
**Micro-tasks**: {tree['count']}  
**Max Depth**: {tree['depth']}

---

## Micro-Task Tree

{task_lines}

---

## Focus Strategy
- Start with the **smallest** micro-task to build momentum
- Each checkbox = dopamine hit 💥
- If stuck >10 min, use recovery token or switch micro-task
- Celebrate every 3 checkboxes 🎉

---
*Generated by HyperSplit Engine v3.0*
"""
        async with aiofiles.open(fpath, "w", encoding="utf-8") as f:
            await f.write(note)
        return fpath

    def _detect_task_type(self, description: str) -> str:
        """Heuristic task type detection from keywords."""
        desc_lower = description.lower()

        if any(k in desc_lower for k in ["api", "endpoint", "route", "fastapi", "handler"]):
            return "api_endpoint"
        if any(k in desc_lower for k in ["ui", "component", "react", "vue", "frontend", "button", "modal"]):
            return "ui_component"
        if any(k in desc_lower for k in ["migration", "schema", "database", "postgres", "table"]):
            return "database_migration"
        if any(k in desc_lower for k in ["bug", "fix", "crash", "error", "broken", "issue"]):
            return "bug_fix"
        if any(k in desc_lower for k in ["doc", "readme", "guide", "tutorial", "explain"]):
            return "documentation"
        if any(k in desc_lower for k in ["refactor", "clean", "restructure", "extract", "simplify"]):
            return "refactor"

        return "generic"

    def _generate_generic_steps(self, description: str) -> List[str]:
        """Generate generic steps when type is unknown."""
        return [
            "Clarify goal + define done criteria",
            "Research / gather context",
            "Create minimal prototype / spike",
            "Implement core logic",
            "Test + validate",
            "Polish + document"
        ]

    async def _create_micro_task(self, title: str, index: int, depth: int,
                                 max_depth: int, target_minutes: int) -> Dict[str, Any]:
        """Create a micro-task node, optionally with sub-tasks."""
        task = {
            "id": f"T{index}",
            "title": title,
            "estimated_minutes": target_minutes,
            "depth": depth,
            "sub_tasks": [],
            "sub_count": 0,
            "hint": self._generate_hint(title)
        }

        # If task seems complex and we haven't hit max depth, split further
        if depth < max_depth and self._is_complex(title):
            sub_steps = self._split_further(title)
            for j, sub in enumerate(sub_steps, 1):
                sub_task = await self._create_micro_task(
                    sub, int(f"{index}{j}"), depth + 1, max_depth, target_minutes // 2
                )
                task["sub_tasks"].append(sub_task)
                task["sub_count"] += sub_task["sub_count"] + 1
                task["estimated_minutes"] += sub_task["estimated_minutes"]

        return task

    def _is_complex(self, title: str) -> bool:
        """Heuristic: does this step need further splitting?"""
        complex_indicators = ["implement", "build", "create", "design", "refactor", "migrate"]
        return any(ind in title.lower() for ind in complex_indicators)

    def _split_further(self, title: str) -> List[str]:
        """Generic further split for complex steps."""
        return [
            f"Plan: {title} — outline approach",
            f"Draft: {title} — first pass",
            f"Refine: {title} — polish + edge cases"
        ]

    def _generate_hint(self, title: str) -> str:
        """Generate ADHD-friendly hint for a micro-task."""
        hints = {
            "test": "Write ONE failing test first. Red → Green → Refactor.",
            "schema": "Draw the relationship on paper first. Then code.",
            "auth": "Start with hardcoded token. Wire real auth after.",
            "style": "Use browser dev tools. Tweak live. Copy values back.",
            "doc": "Speak into voice recorder. Transcribe. Edit.",
            "deploy": "Checklist: tests green → build → push → verify health endpoint"
        }
        for key, hint in hints.items():
            if key in title.lower():
                return hint
        return "Set a 15-min timer. Stop when it rings. Document where you are."
