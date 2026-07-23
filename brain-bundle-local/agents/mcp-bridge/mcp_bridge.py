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

import os
import re
from typing import Dict, Any, Optional, List

import aiohttp

# ─── Ollama config ──────────────────────────────────────────────────
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.environ.get("OLLAMA_MODEL", "mistral")


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

        context = await self._build_context(query, context_files)

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
                "num_predict": 800
            }
        }

        try:
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    answer = data["message"]["content"]
                    return {
                        "answer": answer,
                        "sources": context_files or [],
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

    async def find_related_notes(self, note_path: str) -> List[str]:
        """Find wiki-linked notes from a vault note."""
        full_path = os.path.join(self.vault_path, note_path)
        if not os.path.exists(full_path):
            return []
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return [m.group(1) for m in re.finditer(r"\[\[(.*?)\]\]", content)]

    async def _build_context(self, query: str, context_files: List[str] = None) -> str:
        """Build RAG context from vault."""
        if not context_files:
            context_files = await self._find_relevant_files(query)
        context_parts = []
        for fpath in context_files[:5]:
            full = os.path.join(self.vault_path, fpath)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    content = f.read()[:1000]
                context_parts.append(f"--- {fpath} ---\n{content}\n")
        return "\n".join(context_parts) if context_parts else "No relevant context found."

    async def _find_relevant_files(self, query: str) -> List[str]:
        """Simple keyword-based file search across vault."""
        keywords = query.lower().split()
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
                    score = sum(1 for k in keywords if k in content or k in rel.lower())
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
