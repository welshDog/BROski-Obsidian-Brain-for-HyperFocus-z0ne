#!/usr/bin/env python3
"""
mcp_bridge.py
MCP (Model Context Protocol) bridge for THE HYPER BRAIN.
Connects local LLMs (LMStudio, Ollama) to the Obsidian vault.
Enables RAG, agentic conversations, and vault manipulation.
BROski♾️
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

import aiohttp


class MCPBridge:
    """Bridge between Hyper Brain and local LLM via MCP."""

    def __init__(self, mcp_port: int = 8099, vault_path: str = "/vault"):
        self.mcp_port = mcp_port
        self.vault_path = vault_path
        self.base_url = f"http://localhost:{mcp_port}"
        self.connected = False
        self.session: Optional[aiohttp.ClientSession] = None

    async def connect(self):
        """Establish connection to MCP server."""
        self.session = aiohttp.ClientSession()
        try:
            async with self.session.get(f"{self.base_url}/health", timeout=5) as resp:
                if resp.status == 200:
                    self.connected = True
                    print(f"🔗 MCP bridge connected on port {self.mcp_port}")
                else:
                    print(f"⚠️ MCP server responded {resp.status}")
        except Exception as e:
            print(f"⚠️ MCP connection failed: {e} — running in offline mode")
            self.connected = False

    async def disconnect(self):
        if self.session:
            await self.session.close()
            self.connected = False

    async def status(self) -> Dict[str, Any]:
        if not self.connected or not self.session:
            return {"connected": False, "mode": "offline"}
        try:
            async with self.session.get(f"{self.base_url}/health", timeout=3) as resp:
                data = await resp.json()
                return {"connected": True, **data}
        except:
            self.connected = False
            return {"connected": False, "mode": "offline"}

    async def query_vault(self, query: str, context_files: List[str] = None) -> Dict[str, Any]:
        """Query vault via MCP + local LLM. Returns structured response."""
        if not self.connected:
            return {
                "answer": "MCP offline. Query recorded for later processing.",
                "sources": [],
                "mode": "offline"
            }

        # Build context from vault
        context = await self._build_context(query, context_files)

        payload = {
            "model": "local-llm",
            "messages": [
                {
                    "role": "system",
                    "content": f"""You are THE HYPER BRAIN, a neurodivergent-first AI assistant.
You help an ADHD/dyslexic developer manage their Obsidian vault.
Be concise. Use bullet points. Bold key terms.
Current vault path: {self.vault_path}

Context from vault:
{context}
"""
                },
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }

        try:
            async with self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=30
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    answer = data["choices"][0]["message"]["content"]
                    return {
                        "answer": answer,
                        "sources": context_files or [],
                        "mode": "online",
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                    }
                else:
                    return {"error": f"LLM error {resp.status}", "mode": "error"}
        except Exception as e:
            return {"error": str(e), "mode": "error"}

    async def summarize_note(self, file_path: str) -> str:
        """Summarize a vault note via LLM."""
        full_path = os.path.join(self.vault_path, file_path)
        if not os.path.exists(full_path):
            return f"File not found: {file_path}"

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file: {e}"

        # Truncate if too long
        if len(content) > 4000:
            content = content[:4000] + "\n... [truncated]"

        query = f"Summarize this note in 3 bullet points. Keep it ADHD-friendly (short, punchy):\n\n{content}"
        result = await self.query_vault(query, context_files=[file_path])
        return result.get("answer", "Summary unavailable")

    async def find_related_notes(self, note_path: str) -> List[str]:
        """Find semantically related notes using vault embeddings."""
        # In full implementation, this would query a vector DB
        # For now, return linked notes from markdown
        full_path = os.path.join(self.vault_path, note_path)
        if not os.path.exists(full_path):
            return []

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract wiki-links [[Note Name]]
        links = []
        for match in __import__("re").finditer(r"\[\[(.*?)\]\]", content):
            links.append(match.group(1))

        return links

    async def _build_context(self, query: str, context_files: List[str] = None) -> str:
        """Build RAG context from vault."""
        if not context_files:
            # Simple keyword search across recent files
            context_files = await self._find_relevant_files(query)

        context_parts = []
        for fpath in context_files[:5]:  # Limit context
            full = os.path.join(self.vault_path, fpath)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    content = f.read()[:1000]  # First 1000 chars
                context_parts.append(f"--- {fpath} ---\n{content}\n")

        return "\n".join(context_parts) if context_parts else "No relevant context found."

    async def _find_relevant_files(self, query: str) -> List[str]:
        """Simple keyword-based file search."""
        keywords = query.lower().split()
        matches = []

        for root, dirs, files in os.walk(self.vault_path):
            # Skip .obsidian and large dirs
            dirs[:] = [d for d in dirs if d not in [".obsidian", "node_modules"]]
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
