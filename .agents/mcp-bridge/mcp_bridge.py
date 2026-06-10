#!/usr/bin/env python3
"""
mcp_bridge.py
MCP (Model Context Protocol) bridge for THE HYPER BRAIN.
Connects local LLMs (Ollama) to the Obsidian vault.
Enables RAG, agentic conversations, and vault manipulation.

Ollama endpoint: http://localhost:11434
Default model: mistral (swap to phi3, tinyllama, llama2:7b as needed)

BROski♾️
"""

import asyncio
import json
import os
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

import aiohttp

# ─── Ollama config ──────────────────────────────────────────────────
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.environ.get("OLLAMA_MODEL", "mistral")

# RAG context budget — keep small: CPU Ollama on this box times out (>120s)
# on fat prompts. 3 files x 600 chars proved workable; tune via env.
RAG_MAX_FILES      = int(os.environ.get("RAG_MAX_FILES", "3"))
RAG_CHARS_PER_FILE = int(os.environ.get("RAG_CHARS_PER_FILE", "600"))
RAG_NUM_PREDICT    = int(os.environ.get("RAG_NUM_PREDICT", "200"))
OLLAMA_TIMEOUT_S   = int(os.environ.get("OLLAMA_TIMEOUT_S", "180"))


class MCPBridge:
    """Bridge between Hyper Brain and Ollama local LLM."""

    def __init__(self, mcp_port: int = 11434, vault_path: str = "/vault",
                 ollama_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.mcp_port = mcp_port
        self.vault_path = vault_path
        self.base_url = ollama_url
        self.model = model
        self.connected = False
        self.session: Optional[aiohttp.ClientSession] = None
        self._graph_cache: Optional[tuple] = None  # (mtime, parsed graph)

    async def connect(self):
        """Establish connection to Ollama."""
        self.session = aiohttp.ClientSession()
        try:
            async with self.session.get(f"{self.base_url}/api/tags",
                                        timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    self.connected = True
                    print(f"🔗 Ollama connected at {self.base_url} (model: {self.model})")
                else:
                    print(f"⚠️ Ollama responded {resp.status}")
        except Exception as e:
            print(f"⚠️ Ollama connection failed: {e} — running in offline mode")
            self.connected = False

    async def disconnect(self):
        if self.session:
            await self.session.close()
            self.connected = False

    async def status(self) -> Dict[str, Any]:
        if not self.connected or not self.session:
            return {"connected": False, "mode": "offline"}
        try:
            async with self.session.get(f"{self.base_url}/api/tags",
                                        timeout=aiohttp.ClientTimeout(total=3)) as resp:
                data = await resp.json()
                models = [m["name"] for m in data.get("models", [])]
                return {"connected": True, "models": models, "active": self.model}
        except:
            self.connected = False
            return {"connected": False, "mode": "offline"}

    async def query_vault(self, query: str, context_files: List[str] = None) -> Dict[str, Any]:
        """Query vault via RAG + Ollama. Returns structured response."""
        if not self.connected:
            return {
                "answer": "Ollama offline. Query recorded for later processing.",
                "sources": [],
                "mode": "offline"
            }

        context, used_files = await self._build_context(query, context_files)

        # Ollama native /api/chat endpoint
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are THE HYPER BRAIN, a neurodivergent-first AI assistant.\n"
                        "You help an ADHD/dyslexic developer manage their Obsidian vault.\n"
                        "Be concise. Use bullet points. Bold key terms.\n"
                        f"Vault path: {self.vault_path}\n\n"
                        f"Vault context:\n{context}"
                    )
                },
                {"role": "user", "content": query}
            ],
            "options": {
                "temperature": 0.7,
                "num_predict": RAG_NUM_PREDICT
            }
        }

        try:
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=OLLAMA_TIMEOUT_S)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    answer = data["message"]["content"]
                    return {
                        "answer": answer,
                        "sources": used_files,
                        "mode": "online",
                        "model": self.model,
                        "tokens_used": data.get("eval_count", 0)
                    }
                else:
                    body = await resp.text()
                    return {"error": f"Ollama error {resp.status}: {body}", "mode": "error"}
        except Exception as e:
            return {"error": str(e), "mode": "error"}

    async def summarize_note(self, file_path: str) -> str:
        """Summarize a vault note via Ollama."""
        full_path = os.path.join(self.vault_path, file_path)
        if not os.path.exists(full_path):
            return f"File not found: {file_path}"
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file: {e}"

        if len(content) > 4000:
            content = content[:4000] + "\n... [truncated]"

        query = (
            "Summarize this note in 3 bullet points. "
            "Keep it ADHD-friendly (short, punchy):\n\n" + content
        )
        result = await self.query_vault(query, context_files=[file_path])
        return result.get("answer", "Summary unavailable")

    # ─── Graph-aware RAG (Memory Hub Phase 3) ────────────────────────────

    def graph_path(self) -> str:
        return os.environ.get(
            "BRAIN_GRAPH_PATH",
            os.path.join(self.vault_path, "06-AI-Context", "graph.json"),
        )

    def load_graph(self) -> Optional[Dict[str, Any]]:
        """Load the canonical graph.json, cached by mtime (regen-friendly)."""
        path = self.graph_path()
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            return None
        if self._graph_cache and self._graph_cache[0] == mtime:
            return self._graph_cache[1]
        try:
            with open(path, "r", encoding="utf-8") as f:
                graph = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
        self._graph_cache = (mtime, graph)
        return graph

    def related_nodes(self, seed_ids: List[str], limit: int = 5,
                      hops: int = 2, decay: float = 0.4) -> List[Dict[str, Any]]:
        """Multi-hop expansion over wikilink + mentions + skill-link edges
        with hop decay.
        Score = hop_weight * (1 + centrality); best score wins on revisit paths."""
        graph = self.load_graph()
        if not graph:
            return []
        nodes = {n["id"]: n for n in graph.get("nodes", [])}
        adjacency: Dict[str, set] = {}
        for e in graph.get("edges", []):
            if e.get("type") not in ("wikilink", "mentions", "skill-link"):
                continue
            adjacency.setdefault(e["from"], set()).add(e["to"])
            adjacency.setdefault(e["to"], set()).add(e["from"])
        seeds = {s for s in seed_ids if s in nodes}
        visited = set(seeds)
        frontier = set(seeds)
        scored: Dict[str, float] = {}
        weight = 1.0
        for _ in range(hops):
            nxt: set = set()
            for nid in frontier:
                for nb in adjacency.get(nid, ()):
                    if nb in visited or nb not in nodes:
                        continue
                    score = weight * (1 + (nodes[nb].get("centrality") or 0))
                    if score > scored.get(nb, 0.0):
                        scored[nb] = score
                    nxt.add(nb)
            visited |= nxt
            frontier = nxt
            weight *= decay
        ranked = sorted(scored.items(), key=lambda kv: -kv[1])
        return [nodes[nid] for nid, _ in ranked[:limit]]

    def graph_neighbors(self, rel_paths: List[str], limit: int = 5) -> List[str]:
        """Vault rel paths -> related note rel paths (2-hop, decayed).
        Phantom notes (no file yet) and code nodes are skipped for RAG."""
        graph = self.load_graph()
        if not graph:
            return []
        by_path = {n["path"]: n["id"] for n in graph.get("nodes", [])
                   if n.get("layer") == "note" and n.get("path")}
        seed_ids = [by_path[p] for p in
                    (rp.replace(os.sep, "/") for rp in rel_paths) if p in by_path]
        related = self.related_nodes(seed_ids, limit=limit * 3)
        paths = [n["path"] for n in related
                 if n.get("layer") == "note" and n.get("path")]
        return paths[:limit]

    async def find_related_notes(self, note_path: str) -> List[str]:
        """Find wiki-linked notes from a vault note."""
        full_path = os.path.join(self.vault_path, note_path)
        if not os.path.exists(full_path):
            return []
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return [m.group(1) for m in re.finditer(r"\[\[(.*?)\]\]", content)]

    async def _build_context(self, query: str,
                             context_files: List[str] = None) -> tuple:
        """Build RAG context from vault: keyword seeds + 1-hop graph expansion.
        Returns (context_str, used_files) so answers can cite real sources."""
        if not context_files:
            seeds = (await self._find_relevant_files(query))[:max(1, RAG_MAX_FILES - 1)]
            linked = [p for p in self.graph_neighbors(seeds, limit=2)
                      if p not in seeds]
            context_files = (seeds + linked)[:RAG_MAX_FILES]
        context_parts = []
        used_files = []
        for fpath in context_files[:RAG_MAX_FILES]:
            full = os.path.join(self.vault_path, fpath)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    content = f.read()[:RAG_CHARS_PER_FILE]
                context_parts.append(f"--- {fpath} ---\n{content}\n")
                used_files.append(fpath)
        context = "\n".join(context_parts) if context_parts else "No relevant context found."
        return context, used_files

    _STOPWORDS = {"what", "is", "the", "a", "an", "of", "for", "to", "in", "on",
                  "and", "or", "how", "why", "when", "where", "who", "do", "does",
                  "did", "are", "was", "were", "be", "this", "that", "with", "about"}

    async def _find_relevant_files(self, query: str) -> List[str]:
        """Keyword file search across vault — stopword-filtered, filename-boosted
        so real terms (not 'what'/'the') pick the graph-expansion seeds."""
        words = [w.strip("?!.,:;\"'()[]") for w in query.lower().split()]
        keywords = [w for w in words if len(w) > 2 and w not in self._STOPWORDS]
        if not keywords:
            keywords = [w for w in words if w]
        matches = []
        for root, dirs, files in os.walk(self.vault_path):
            dirs[:] = [d for d in dirs if d not in [".obsidian", "node_modules", "openhuman-build"]]
            for fname in files:
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, self.vault_path)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                    score = sum(1 for k in keywords if k in content)
                    score += sum(2 for k in keywords if k in rel.lower())
                    if score > 0:
                        matches.append((rel, score))
                except:
                    pass
        matches.sort(key=lambda x: -x[1])
        return [m[0] for m in matches[:10]]

    # ─── OpenHuman Integration ────────────────────────────────────────────

    async def query_openhuman_feed(self, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query OpenHuman-synced notes from the vault inbox."""
        feed_dir = os.path.join(self.vault_path, "00-Inbox", "OpenHuman-Feed")
        if not os.path.exists(feed_dir):
            return []
        notes = []
        try:
            for fname in os.listdir(feed_dir):
                if not fname.endswith(".md"):
                    continue
                if source and not fname.startswith(source):
                    continue
                fpath = os.path.join(feed_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
                    fm_text = fm_match.group(1) if fm_match else ""
                    body    = fm_match.group(2) if fm_match else content
                    meta = {"file": fname, "source": source or fname.split("-")[0]}
                    for line in fm_text.split("\n"):
                        if ":" in line:
                            k, v = line.split(":", 1)
                            k, v = k.strip().lower(), v.strip()
                            meta[k] = [t.strip("[] ") for t in v.split(",")] if k == "tags" else v
                    title_m = re.search(r"^#+ (.+)$", body, re.MULTILINE)
                    meta["title"] = title_m.group(1) if title_m else fname.replace(".md", "")
                    notes.append(meta)
                except Exception as e:
                    print(f"⚠️ Error parsing {fname}: {e}")
        except Exception as e:
            print(f"⚠️ Error reading OpenHuman feed: {e}")
        return notes

    async def get_openhuman_summary(self) -> Dict[str, Any]:
        """Get summary of OpenHuman-synced content by source."""
        all_notes = await self.query_openhuman_feed()
        summary = {"total": len(all_notes)}
        by_source: Dict[str, list] = {}
        for note in all_notes:
            src = note.get("source", "unknown")
            by_source.setdefault(src, []).append(note)
        for src, notes in by_source.items():
            status_counts: Dict[str, int] = {}
            for n in notes:
                s = n.get("status", "unknown")
                status_counts[s] = status_counts.get(s, 0) + 1
            summary[src] = {"total": len(notes), "status": status_counts}
        return summary


if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI, HTTPException

    _app = FastAPI(title="MCP Bridge Agent", version="1.0.0")
    _bridge = MCPBridge(vault_path=os.environ.get("OBSIDIAN_VAULT_PATH", "/vault"))

    @_app.on_event("startup")
    async def _startup():
        await _bridge.connect()

    @_app.on_event("shutdown")
    async def _shutdown():
        await _bridge.disconnect()

    @_app.get("/health")
    async def _health():
        return {"status": "ok", "agent": "mcp-bridge", **await _bridge.status()}

    @_app.post("/tools/call_mcp_tool")
    async def _call_tool(query: str, skip_context: bool = False, args: dict = None):
        # skip_context=true bypasses vault RAG — use when the query already carries
        # all needed context (e.g. AI prioritization) to keep the prompt small on CPU
        ctx_files = [] if skip_context else None
        return await _bridge.query_vault(query, context_files=ctx_files)

    @_app.get("/tools/list_mcp_tools")
    async def _list_tools():
        return await _bridge.get_openhuman_summary()

    def _load_graph() -> Dict[str, Any]:
        # canonical memory-hub artifact — see CLAUDE.md "Graph Brain"
        graph_path = os.environ.get(
            "BRAIN_GRAPH_PATH",
            os.path.join(_bridge.vault_path, "06-AI-Context", "graph.json"),
        )
        if not os.path.exists(graph_path):
            raise HTTPException(status_code=404,
                                detail=f"graph.json not found at {graph_path}")
        with open(graph_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @_app.get("/graph")
    async def _graph():
        return _load_graph()

    @_app.get("/graph/related/{node_id}")
    async def _graph_related(node_id: str, limit: int = 5):
        # multi-hop expansion over wikilink + mentions + skill-link edges.
        # Works for ANY node: note ids find linked/documenting notes, code ids
        # find the notes that mention them, skill ids (skill:HS-123) find the
        # notes AND modules AND sibling skills they connect to
        graph = _load_graph()
        node = next((n for n in graph.get("nodes", []) if n.get("id") == node_id), None)
        if node is None:
            raise HTTPException(status_code=404,
                                detail=f"node '{node_id}' not in graph")
        related = _bridge.related_nodes([node_id], limit=max(limit * 3, 15))
        return {
            "node": node_id,
            "related_paths": [n["path"] for n in related
                              if n.get("layer") == "note" and n.get("path")][:limit],
            "related_code": [n["id"] for n in related
                             if n.get("layer") not in ("note", "skill")][:limit],
            "related_skills": [n["id"] for n in related
                               if n.get("layer") == "skill"][:limit],
        }

    @_app.get("/graph/node/{node_id}")
    async def _graph_node(node_id: str):
        graph = _load_graph()
        node = next((n for n in graph.get("nodes", []) if n.get("id") == node_id), None)
        if node is None:
            raise HTTPException(status_code=404,
                                detail=f"node '{node_id}' not in graph")
        edges = [e for e in graph.get("edges", [])
                 if node_id in (e.get("from"), e.get("to"))]
        return {"node": node, "edges": edges, "meta": graph.get("meta", {})}

    uvicorn.run(_app, host="0.0.0.0", port=int(os.environ.get("PORT", 3302)))
