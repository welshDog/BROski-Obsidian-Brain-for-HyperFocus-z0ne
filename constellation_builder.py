#!/usr/bin/env python3
"""
constellation_builder.py
THE HYPER BRAIN v3.0 — Level 20 Phase 2

Generates the LIVE ecosystem map: a JSON snapshot of system state plus an
auto-written Obsidian note (`Hub/Brain-Constellation-Live.md`). The static,
hand-authored map lives in `Hub/Brain-Constellation.md` (Phase 1) — this
module is the dynamic counterpart that refreshes from real engine state.
BROski♾️
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import aiofiles

LEVELS_TOTAL = 20
LEVELS_LIVE = 20  # 18 (distraction) · 19 (difficulty dial) · 20 (this) — closed

# Static ecosystem topology — the 5 layers of the constellation.
ENGINE_MODULES = [
    "hyper_brain_core", "focus_tracker", "analytics_engine",
    "morning_briefing_ai", "github_webhook_server", "mcp_bridge",
    "hyper_split", "session_snapshot", "ai_distraction_filter",
    "gamification_summary", "difficulty_dial", "constellation_builder",
    "events_feed",
]
VAULT_FOLDERS = [
    "00-Inbox", "01-Projects", "02-Areas", "03-Resources", "04-Archive",
    "05-Focus-Sessions", "06-AI-Context", "07-Streaks-Achievements",
    "99-Templates", "Hub",
]
ECOSYSTEM_REPOS = [
    "HyperCode-V2.4", "HyperAgent-SDK", "Hyper-Vibe-Coding-Course",
    "BROskiPets-LLM-dNFT", "BROski-Obsidian-Brain",
    "WelshDog-Mission-Control",
]

# Real ecosystem wiring (source repo → target repo, relationship).
REPO_EDGES = [
    ("Hyper-Vibe-Coding-Course", "HyperCode-V2.4", "manifest (hyper-agent-spec)"),
    ("Hyper-Vibe-Coding-Course", "BROskiPets-LLM-dNFT", "/pets funnel"),
    ("HyperCode-V2.4", "HyperAgent-SDK", "npm agent framework"),
    ("HyperCode-V2.4", "BROski-Obsidian-Brain", "brain agents (compose)"),
    ("HyperCode-V2.4", "WelshDog-Mission-Control", "course-ops dashboard"),
    ("HyperCode-V2.4", "BROskiPets-LLM-dNFT", "pets bridge :8098"),
]

# Obsidian Canvas colour presets (1=red 2=orange 3=yellow 4=green 5=cyan 6=purple).
# Orange (2) is banned by the HFZ brand rule — never use it.
_CANVAS_COLOR = {
    "zone": "6", "engine": "4", "module": "5", "repo": "5", "economy": "3", "vault": "6",
}


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ConstellationBuilder:
    """Builds the live ecosystem map and writes it into the vault."""

    def __init__(self, vault_path: str):
        self.vault_path = vault_path

    async def build(
        self,
        health: Dict[str, Any],
        gamification: Dict[str, Any],
        focus_status: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assemble a live snapshot of the whole ecosystem."""
        services = health.get("services", {}) or {}
        online = sum(1 for v in services.values() if v)
        total = len(services) or 1
        streaks = gamification.get("streaks", {}) or {}
        session = focus_status.get("session", {}) or {}

        return {
            "generated_at": _utcnow_iso(),
            "system": {
                "status": health.get("status", "unknown"),
                "version": health.get("version", "3.0.0"),
                "level": f"{LEVELS_LIVE}/{LEVELS_TOTAL}",
                "completion_pct": round(LEVELS_LIVE / LEVELS_TOTAL * 100),
                "services_online": f"{online}/{total}",
            },
            "engine": {
                "container": 30,
                "port": 8100,
                "modules": ENGINE_MODULES,
            },
            "focus": {
                "active": bool(focus_status.get("active", False)),
                "intent": focus_status.get("intent") or session.get("intent"),
            },
            "economy": {
                "broski_coins_7d": gamification.get("coins_total_7d", 0),
                "xp_7d": gamification.get("xp_total_7d", 0),
                "sessions_7d": gamification.get("sessions_7d", 0),
                "current_streak": streaks.get("current_streak", 0),
                "longest_streak": streaks.get("longest_streak", 0),
                "recovery_tokens": streaks.get("recovery_tokens", 0),
            },
            "vault": VAULT_FOLDERS,
            "ecosystem_repos": ECOSYSTEM_REPOS,
        }

    def build_graph(self, map_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a live snapshot into a node/edge graph for the constellation.

        Nodes = the zone root + engine + engine modules + ecosystem repos +
        a vault node + an economy node. Edges = real connections.
        """
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        sys_ = map_data.get("system", {})
        econ = map_data.get("economy", {})
        focus = map_data.get("focus", {})

        def node(nid: str, label: str, ntype: str, **meta) -> None:
            nodes.append({"id": nid, "label": label, "type": ntype, "meta": meta})

        def edge(src: str, dst: str, rel: str) -> None:
            edges.append({"source": src, "target": dst, "type": rel})

        # Root
        node("zone", "🌌 HyperFocus Zone", "zone",
             level=sys_.get("level"), completion_pct=sys_.get("completion_pct"),
             status=sys_.get("status"))

        # Engine + modules
        node("engine", "🧠 Hyper Brain :8100", "engine",
             services_online=sys_.get("services_online"),
             focus_active=bool(focus.get("active")), intent=focus.get("intent"))
        edge("zone", "engine", "runs")
        for m in map_data.get("engine", {}).get("modules", []):
            node(f"module:{m}", m, "module")
            edge("engine", f"module:{m}", "module")

        # Economy
        node("economy", "🪙 BROski$ Economy", "economy",
             xp_7d=econ.get("xp_7d"), coins_7d=econ.get("broski_coins_7d"),
             current_streak=econ.get("current_streak"))
        edge("engine", "economy", "awards")

        # Vault
        node("vault", "🗂️ PARA Vault", "vault", folders=map_data.get("vault", []))
        edge("engine", "vault", "reads/writes")

        # Ecosystem repos + cross-repo wiring
        repo_ids = set()
        for r in map_data.get("ecosystem_repos", []):
            rid = f"repo:{r}"
            repo_ids.add(rid)
            node(rid, r, "repo")
            edge("zone", rid, "repo")
        # Only wire a cross-repo edge when BOTH endpoints are present (no dangling edges).
        for src, dst, rel in REPO_EDGES:
            sid, did = f"repo:{src}", f"repo:{dst}"
            if sid in repo_ids and did in repo_ids:
                edges.append({"source": sid, "target": did, "type": rel})

        return {
            "generated_at": map_data.get("generated_at", _utcnow_iso()),
            "nodes": nodes,
            "edges": edges,
            "counts": {"nodes": len(nodes), "edges": len(edges)},
        }

    async def write_canvas(self, graph: Dict[str, Any]) -> str:
        """Auto-generate an Obsidian Canvas (`Hub/Brain-Constellation.canvas`) from the graph."""
        hub = os.path.join(self.vault_path, "Hub")
        os.makedirs(hub, exist_ok=True)
        path = os.path.join(hub, "Brain-Constellation.canvas")

        # Lay nodes out in columns by type so the canvas is readable.
        columns = {"repo": -1100, "zone": -300, "economy": 250, "engine": 250, "vault": 250, "module": 800}
        col_counts: Dict[str, int] = {}
        W, H, GAP = 240, 60, 40

        canvas_nodes: List[Dict[str, Any]] = []
        for n in graph["nodes"]:
            ntype = n["type"]
            x = columns.get(ntype, 800)
            idx = col_counts.get(ntype, 0)
            col_counts[ntype] = idx + 1
            y = idx * (H + GAP) - 200
            # stagger economy/engine/vault which share a column band
            if ntype in ("economy", "engine", "vault"):
                y = {"economy": -260, "engine": 0, "vault": 260}[ntype]
            canvas_nodes.append({
                "id": n["id"],
                "type": "text",
                "text": f"**{n['label']}**",
                "x": x, "y": y, "width": W, "height": H,
                "color": _CANVAS_COLOR.get(ntype, "5"),
            })

        canvas_edges: List[Dict[str, Any]] = []
        for i, e in enumerate(graph["edges"]):
            canvas_edges.append({
                "id": f"e{i}",
                "fromNode": e["source"],
                "toNode": e["target"],
                "label": e.get("type", ""),
            })

        canvas = {"nodes": canvas_nodes, "edges": canvas_edges}
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(canvas, indent=2))
        return path

    async def write_to_vault(self, map_data: Dict[str, Any]) -> str:
        """Render the snapshot to `Hub/Brain-Constellation-Live.md`."""
        hub = os.path.join(self.vault_path, "Hub")
        os.makedirs(hub, exist_ok=True)
        path = os.path.join(hub, "Brain-Constellation-Live.md")

        sys_ = map_data["system"]
        econ = map_data["economy"]
        focus = map_data["focus"]
        focus_line = (
            f"🔥 **ACTIVE** — {focus.get('intent') or 'focusing'}"
            if focus.get("active")
            else "💤 idle — no active session"
        )
        modules_md = "\n".join(f"- `{m}`" for m in map_data["engine"]["modules"])
        repos_md = "\n".join(f"- {r}" for r in map_data["ecosystem_repos"])

        md = f"""---
generated: {map_data['generated_at']}
type: constellation-live
auto: true
tags: [constellation, live, auto-generated]
---
# 🌌 Brain Constellation — LIVE

> Auto-generated by `constellation_builder.py` (Level 20 Phase 2).
> Do not hand-edit — regenerate with `GET /constellation/map`.

> [!success] {sys_['status'].upper()} · v{sys_['version']} · Level {sys_['level']} ({sys_['completion_pct']}%)
> Engine services online: {sys_['services_online']} · snapshot {map_data['generated_at']}

## 🎯 Focus
{focus_line}

## 🪙 Economy — last 7 days
| Metric | Value |
|---|---|
| BROski$ earned | {econ['broski_coins_7d']} |
| XP earned | {econ['xp_7d']} |
| Focus sessions | {econ['sessions_7d']} |
| Current streak | {econ['current_streak']} 🔥 |
| Longest streak | {econ['longest_streak']} |
| Recovery tokens | {econ['recovery_tokens']} |

## 🧠 Engine — Container #{map_data['engine']['container']} · port {map_data['engine']['port']}
{modules_md}

## 🌍 Ecosystem
{repos_md}

---
> Static navigable map: [[Brain-Constellation]] · THE HYPER BRAIN v3.0 ♾️🧠⚡
"""
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(md)
        return path
