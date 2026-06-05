#!/usr/bin/env python3
"""
mcp_bridge.py
MCP (Model Context Protocol) bridge for THE HYPER BRAIN.
Connects local LLMs (LMStudio, Ollama) to the Obsidian vault.
Enables RAG, agentic conversations, and vault manipulation.

UPDATED: OpenHuman integration — query auto-synced notes from GitHub, Slack, Gmail.

BROski♾️
"""

import asyncio
import json
import os
import re
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
        for match in re.finditer(r"\[\[(.*?)\]\]", content):
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

    # ─── OpenHuman Integration ──────────────────────────────────────────────
    # Query auto-synced notes from GitHub, Slack, Gmail
    
    async def query_openhuman_feed(self, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query OpenHuman-synced notes from the vault.
        
        OpenHuman writes auto-synced notes to:
          HYPERFOCUS_ZONE/00-Inbox/OpenHuman-Feed/
        
        Filenames follow pattern: {source}-{type}-{id}.md
        Examples:
          - github-issue-123.md (GitHub issue #123)
          - github-pr-45.md (GitHub pull request #45)
          - slack-channel-msg.md
          - gmail-thread-xyz.md
        
        Args:
            source: Filter by source ('github', 'slack', 'gmail') or None for all
        
        Returns:
            List of parsed note metadata dicts with keys:
              - file: filename
              - source: 'github', 'slack', 'gmail'
              - title: note title
              - created: ISO timestamp
              - url: external link (if present)
              - tags: list of tags from frontmatter
              - status: 'open', 'closed', etc.
        """
        feed_dir = os.path.join(self.vault_path, "00-Inbox", "OpenHuman-Feed")
        
        if not os.path.exists(feed_dir):
            return []
        
        notes = []
        
        try:
            for fname in os.listdir(feed_dir):
                if not fname.endswith(".md"):
                    continue
                
                # Filter by source if requested
                if source and not fname.startswith(source):
                    continue
                
                fpath = os.path.join(feed_dir, fname)
                
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Parse YAML frontmatter
                    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
                    
                    if fm_match:
                        fm_text = fm_match.group(1)
                        body = fm_match.group(2)
                    else:
                        fm_text = ""
                        body = content
                    
                    # Parse frontmatter
                    meta = {"file": fname, "source": source or fname.split("-")[0]}
                    
                    for line in fm_text.split("\n"):
                        if ":" in line:
                            key, val = line.split(":", 1)
                            key = key.strip().lower()
                            val = val.strip()
                            
                            if key == "tags":
                                # Parse tags: [tag1, tag2]
                                meta[key] = [t.strip("[] ") for t in val.split(",")]
                            else:
                                meta[key] = val
                    
                    # Extract title from first heading or filename
                    title_match = re.search(r"^#+ (.+)$", body, re.MULTILINE)
                    if title_match:
                        meta["title"] = title_match.group(1)
                    else:
                        meta["title"] = fname.replace(".md", "")
                    
                    notes.append(meta)
                
                except Exception as e:
                    print(f"⚠️ Error parsing {fname}: {e}")
                    continue
        
        except Exception as e:
            print(f"⚠️ Error reading OpenHuman feed: {e}")
        
        return notes
    
    async def get_openhuman_summary(self) -> Dict[str, Any]:
        """
        Get summary of OpenHuman-synced content by source.
        
        Returns:
            Dict with counts and status breakdown
        """
        all_notes = await self.query_openhuman_feed()
        
        summary = {"total": len(all_notes)}
        
        # Group by source
        by_source = {}
        for note in all_notes:
            src = note.get("source", "unknown")
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(note)
        
        # Summarize each source
        for src, notes in by_source.items():
            summary[src] = {
                "total": len(notes),
                "status": {}
            }
            
            for note in notes:
                status = note.get("status", "unknown")
                summary[src]["status"][status] = summary[src]["status"].get(status, 0) + 1
        
        return summary
