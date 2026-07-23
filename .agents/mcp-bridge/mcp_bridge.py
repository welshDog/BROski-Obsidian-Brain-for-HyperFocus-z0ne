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
# Phase 7 — embedding seeds. nomic-embed-text is CPU-fine (~330ms warm on
# this box); keep_alive keeps the 274MB model from squatting RAM for long.
EMBED_MODEL        = os.environ.get("EMBED_MODEL", "nomic-embed-text")
EMBED_KEEP_ALIVE   = os.environ.get("EMBED_KEEP_ALIVE", "5m")
EMBED_MAX_CHARS    = int(os.environ.get("EMBED_MAX_CHARS", "4000"))


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

    def route_skills(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Graph-aware skill routing (Memory Hub Phase 6) — deterministic, no LLM.
        Token-matches the query against EVERY node (skills by title/description/
        category, notes/code by id/path), then expands the matches 2-hop through
        the graph so a task about 'docker healthcheck' also surfaces skills
        linked to the code/notes that matched — not just name hits."""
        graph = self.load_graph()
        if not graph:
            return {"query": query, "seeds": [], "skills": [], "notes": [], "code": []}
        words = [w.strip("?!.,:;\"'()[]`") for w in query.lower().split()]
        keywords = [w for w in words if len(w) > 2 and w not in self._STOPWORDS]
        if not keywords:
            keywords = [w for w in words if w]

        def node_text(n: Dict[str, Any]) -> str:
            return " ".join(str(n.get(k) or "") for k in
                            ("id", "title", "description", "path",
                             "category", "pack")).lower()

        scored: List[tuple] = []
        for n in graph.get("nodes", []):
            text = node_text(n)
            tokens = {t for t in re.split(r"[^a-z0-9]+", text) if len(t) > 3}
            name = str(n.get("title") or n.get("id") or "").lower()
            score = 0
            for k in keywords:
                # both directions so compound query words still hit:
                # 'healthcheck' matches token 'health', 'docker' matches text
                if k in text or any(t in k for t in tokens):
                    score += 2 if k in name else 1
            if score:
                scored.append((score, n))
        scored.sort(key=lambda x: -x[0])
        seeds = [n for _, n in scored[:6]]
        seed_ids = [n["id"] for n in seeds]

        expanded = self.related_nodes(seed_ids, limit=30)

        skill_rank: Dict[str, float] = {}
        skill_meta: Dict[str, Dict[str, Any]] = {}
        for score, n in scored:
            if n.get("layer") == "skill":
                skill_rank[n["id"]] = skill_rank.get(n["id"], 0.0) + score + 2.0
                skill_meta[n["id"]] = n
        for i, n in enumerate(expanded):
            if n.get("layer") == "skill":
                skill_rank[n["id"]] = (skill_rank.get(n["id"], 0.0)
                                       + max(0.5, 2.0 - i * 0.05))
                skill_meta[n["id"]] = n

        ranked = sorted(skill_rank.items(), key=lambda kv: -kv[1])[:limit]
        skills = [{
            "id": nid,
            "title": skill_meta[nid].get("title"),
            "emoji": skill_meta[nid].get("emoji"),
            "description": skill_meta[nid].get("description"),
            "category": skill_meta[nid].get("category"),
            "path": skill_meta[nid].get("path"),
            "score": round(score, 2),
        } for nid, score in ranked]
        notes = [n["path"] for n in expanded
                 if n.get("layer") == "note" and n.get("path")][:limit]
        code = [n["id"] for n in expanded
                if n.get("layer") not in ("note", "skill")][:limit]
        return {"query": query, "seeds": seed_ids, "skills": skills,
                "notes": notes, "code": code}

    # ─── Embedding seeds (Memory Hub Phase 7) ────────────────────────────

    def _embed_cache_path(self) -> str:
        return os.path.join(self.vault_path, "06-AI-Context", "embeddings.json")

    async def _embed(self, text: str) -> Optional[List[float]]:
        """Embed one text via Ollama. None on any failure (fail-open)."""
        if not self.session:
            return None
        try:
            async with self.session.post(
                f"{self.base_url}/api/embed",
                json={"model": EMBED_MODEL, "input": text[:EMBED_MAX_CHARS],
                      "keep_alive": EMBED_KEEP_ALIVE},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                vecs = data.get("embeddings") or []
                return vecs[0] if vecs else None
        except Exception:
            return None

    def _vault_notes(self) -> List[str]:
        notes = []
        for root, dirs, files in os.walk(self.vault_path):
            dirs[:] = [d for d in dirs if d not in [".obsidian", "node_modules", "openhuman-build"]]
            for fname in files:
                if fname.endswith(".md"):
                    notes.append(os.path.relpath(os.path.join(root, fname), self.vault_path))
        return notes

    async def refresh_embeddings(self) -> Dict[str, Any]:
        """(Re)embed vault notes whose content changed into embeddings.json.
        Incremental: unchanged md5 = kept; deleted notes = dropped."""
        import hashlib
        path = self._embed_cache_path()
        cache: Dict[str, Any] = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except (OSError, json.JSONDecodeError):
            cache = {}

        embedded = kept = failed = 0
        fresh: Dict[str, Any] = {}
        for rel in self._vault_notes():
            full = os.path.join(self.vault_path, rel)
            try:
                with open(full, "r", encoding="utf-8") as f:
                    content = f.read()
            except OSError:
                continue
            digest = hashlib.md5(content[:EMBED_MAX_CHARS].encode()).hexdigest()
            entry = cache.get(rel)
            if entry and entry.get("md5") == digest:
                fresh[rel] = entry
                kept += 1
                continue
            vec = await self._embed(content)
            if vec is None:
                failed += 1
                if entry:  # keep the stale vector rather than losing the note
                    fresh[rel] = entry
                continue
            fresh[rel] = {"md5": digest, "vec": [round(v, 5) for v in vec]}
            embedded += 1

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(fresh, f, separators=(",", ":"))
        except OSError as exc:
            return {"status": "error", "reason": str(exc)}
        stats = {"status": "ok", "notes": len(fresh), "embedded": embedded,
                 "kept": kept, "failed": failed}
        print(f"🧲 Embedding cache: {stats}")
        return stats

    async def embedding_seeds(self, query: str, k: int = 10) -> List[str]:
        """Semantic seeds: cosine(query vec, cached note vecs) top-k.
        Empty list on ANY failure — caller falls back to keyword seeds."""
        try:
            with open(self._embed_cache_path(), "r", encoding="utf-8") as f:
                cache = json.load(f)
        except (OSError, json.JSONDecodeError):
            return []
        if not cache:
            return []
        qvec = await self._embed(query)
        if not qvec:
            return []
        import math
        qnorm = math.sqrt(sum(v * v for v in qvec)) or 1.0
        scored = []
        for rel, entry in cache.items():
            vec = entry.get("vec") or []
            if len(vec) != len(qvec):
                continue
            dot = sum(a * b for a, b in zip(qvec, vec))
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            scored.append((dot / (qnorm * norm), rel))
        scored.sort(key=lambda x: -x[0])
        return [rel for _score, rel in scored[:k]]

    async def _find_relevant_files(self, query: str) -> List[str]:
        """RAG seed search: embedding seeds first (Phase 7, semantic), keyword
        walk as the always-works fallback."""
        seeds = await self.embedding_seeds(query)
        if seeds:
            return seeds
        return await self._keyword_relevant_files(query)

    async def _keyword_relevant_files(self, query: str) -> List[str]:
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
    from fastapi.responses import FileResponse

    # Skill loadout boot-check — HYPER-SILLs canonical resolver (mounted). Fail-open.
    try:
        import sys as _sys
        _sys.path.insert(0, os.environ.get("HYPER_SILLS_SCRIPTS", "/hyper-sills/scripts"))
        from agent_boot import boot_check as _boot_check
        _boot_check("agent-mcp-bridge",
                    root=os.environ.get("HYPER_SILLS_ROOT", "/hyper-sills"),
                    strict=os.environ.get("LOADOUT_STRICT", "false").lower() in ("1", "true", "yes"))
    except Exception as _e:
        print(f"[loadout] boot-check skipped: {_e}")

    _app = FastAPI(title="MCP Bridge Agent", version="1.0.0")
    _bridge = MCPBridge(vault_path=os.environ.get("OBSIDIAN_VAULT_PATH", "/vault"))

    @_app.on_event("startup")
    async def _startup():
        await _bridge.connect()
        # Phase 7: build/refresh the embedding cache in the background —
        # cold model load (~23s) + ~80 notes never blocks /health
        asyncio.get_event_loop().create_task(_bridge.refresh_embeddings())

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

    @_app.get("/route")
    async def _route(query: str, limit: int = 5):
        # Phase 6: graph-aware skill routing for agents — deterministic, no LLM
        return _bridge.route_skills(query, limit=max(1, min(limit, 20)))

    @_app.get("/seeds")
    async def _seeds(query: str):
        # Phase 7 debug: compare semantic vs keyword seeding — no LLM call
        embedding = await _bridge.embedding_seeds(query)
        keyword = await _bridge._keyword_relevant_files(query)
        return {
            "query": query,
            "used": "embedding" if embedding else "keyword",
            "embedding": embedding,
            "keyword": keyword,
        }

    @_app.post("/embeddings/refresh")
    async def _embeddings_refresh():
        # Phase 7: incremental re-embed of changed vault notes
        return await _bridge.refresh_embeddings()

    @_app.get("/constellation")
    async def _constellation():
        # D3 force-graph of graph.json — served same-origin so the page can
        # hit /graph and /graph/related without CORS
        page = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "constellation.html")
        if not os.path.exists(page):
            raise HTTPException(status_code=404,
                                detail="constellation.html missing from image")
        return FileResponse(page, media_type="text/html")

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
