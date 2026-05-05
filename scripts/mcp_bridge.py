"""HYPER BRAIN v3.0 — MCP Bridge
Level 15 | Local LLM gateway for LMStudio / Ollama + Vault RAG
"""
import os
import json
import httpx
from datetime import datetime
from pathlib import Path
from typing import Optional

VAULT_PATH = Path(os.environ.get("VAULT_PATH", "/vault"))
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:11434")  # Ollama default
LMSTUDIO_URL = os.environ.get("LMSTUDIO_URL", "http://localhost:1234")  # LMStudio default
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3")


class MCPBridge:
    """Bridge between HYPER BRAIN and local LLMs via MCP protocol."""

    def __init__(self):
        self.ollama_url = LLM_BASE_URL
        self.lmstudio_url = LMSTUDIO_URL
        self.model = LLM_MODEL
        self.vault_path = VAULT_PATH

    async def query_ollama(self, prompt: str, system: Optional[str] = None) -> str:
        """Query local Ollama LLM."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system or "You are BROski, a neurodivergent-first AI assistant.",
            "stream": False
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self.ollama_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "No response")

    async def query_lmstudio(self, prompt: str, system: Optional[str] = None) -> str:
        """Query local LMStudio LLM via OpenAI-compatible API."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system or "You are BROski, a neurodivergent-first AI."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.lmstudio_url}/v1/chat/completions", json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    def read_vault_context(self, query: str, max_files: int = 5) -> str:
        """Simple RAG: search vault for relevant markdown files."""
        results = []
        query_lower = query.lower()

        for md_file in self.vault_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                if any(word in content.lower() for word in query_lower.split()):
                    results.append({
                        "file": str(md_file.relative_to(self.vault_path)),
                        "snippet": content[:500]
                    })
                    if len(results) >= max_files:
                        break
            except Exception:
                continue

        if not results:
            return "No relevant vault context found."

        context = "\n\n---\n\n".join(
            f"**{r['file']}**:\n{r['snippet']}" for r in results
        )
        return f"Vault context:\n{context}"

    async def rag_query(self, question: str, use_lmstudio: bool = False) -> str:
        """Vault RAG + LLM combined query."""
        vault_context = self.read_vault_context(question)
        prompt = f"""Based on the following vault notes, answer this question:\n\nQuestion: {question}\n\n{vault_context}"""

        if use_lmstudio:
            return await self.query_lmstudio(prompt)
        return await self.query_ollama(prompt)


if __name__ == "__main__":
    import asyncio
    bridge = MCPBridge()
    print(f"🧠 MCP Bridge v3.0")
    print(f"Ollama: {bridge.ollama_url}")
    print(f"LMStudio: {bridge.lmstudio_url}")
    print(f"Model: {bridge.model}")
    context = bridge.read_vault_context("focus session")
    print(f"Vault RAG test: {context[:200]}...")
