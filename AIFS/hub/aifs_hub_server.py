"""
AIFS Hub Server v0.5
FastAPI backend for the AIFS Hub Dashboard.

Run:
    python AIFS/hub/aifs_hub_server.py --root .
    python AIFS/hub/aifs_hub_server.py --root /path/to/project --port 7331

Open:
    http://localhost:7331

Endpoints:
    GET /              — Dashboard HTML
    GET /api/summary   — Overview stats
    GET /api/contracts — All contracts
    GET /api/in-flight — All in-flight files
    GET /api/locks     — All .ailock patterns
    GET /api/trust     — All agent trust tiers
    GET /api/audit     — Recent audit log entries
    GET /api/contract/{path} — Single folder contract
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("ERROR: Run: pip install fastapi uvicorn", file=sys.stderr)
    sys.exit(1)

# Import AIFS contract resolution
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from aifs_watcher import ContractResolver, AIFSEnforcer, FolderContract
except ImportError:
    print("ERROR: aifs_watcher.py must be in AIFS/", file=sys.stderr)
    sys.exit(1)

ROOT = Path(".").resolve()
app = FastAPI(title="AIFS Hub", version="0.5.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

IGNORED = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build", ".next"}
CONTRACT_FILES = {"AGENTS.md", "manifest.toml", "folder.prompt.md", ".ailock", "context.md", "TRUST.md"}


def get_resolver():
    return ContractResolver(ROOT)


def contract_to_dict(c: FolderContract, rel: str) -> dict:
    return {
        "folder": rel,
        "read_only": c.read_only,
        "inherit": c.inherit,
        "create_exts": c.create_exts,
        "edit_exts": c.edit_exts,
        "delete_allowed": c.delete_allowed,
        "rename_policy": c.rename_policy,
        "move_policy": c.move_policy,
        "require_approval_for": c.require_approval_for,
        "ailock_patterns": c.ailock_patterns,
        "trust_levels": c.trust_levels,
        "in_flight": c.in_flight,
        "active_task": c.active_task,
        "ttl_read_only": c.ttl_read_only,
        "ttl_read_only_until": str(c.ttl_read_only_until) if c.ttl_read_only_until else None,
    }


def find_contracts():
    results = []
    resolver = get_resolver()
    for folder in ROOT.rglob("*"):
        if not folder.is_dir():
            continue
        if any(p in IGNORED for p in folder.parts):
            continue
        found = [f.name for f in folder.iterdir() if f.name in CONTRACT_FILES]
        if found:
            rel = str(folder.relative_to(ROOT))
            dummy = folder / "_check.md"
            contract = resolver.resolve(dummy)
            results.append({
                **contract_to_dict(contract, rel),
                "contract_files": found
            })
    return results


def find_all_in_flight():
    results = []
    for ctx_file in ROOT.rglob("context.md"):
        if any(p in IGNORED for p in ctx_file.parts):
            continue
        folder = ctx_file.parent
        rel = str(folder.relative_to(ROOT))
        content = ctx_file.read_text(encoding="utf-8")
        section = None
        task = ""
        for line in content.splitlines():
            if "## Active Task" in line:
                section = "task"
            elif "## In-Flight" in line or "## Do Not Touch" in line:
                section = "inflight"
            elif line.startswith("##"):
                section = None
            elif section == "task" and line.strip():
                task = line.strip()
            elif section == "inflight" and line.strip().startswith("-"):
                part = line.strip("- ").split("—")[0].strip().strip("`")
                if part:
                    results.append({"folder": rel, "file": part, "active_task": task})
    return results


def find_all_locks():
    results = []
    for ailock in ROOT.rglob(".ailock"):
        if any(p in IGNORED for p in ailock.parts):
            continue
        folder = ailock.parent
        rel = str(folder.relative_to(ROOT))
        lines = ailock.read_text(encoding="utf-8").splitlines()
        for line in lines:
            if line.strip() and not line.strip().startswith("#"):
                results.append({"folder": rel, "pattern": line.strip()})
    return results


def find_all_trust():
    results = []
    for trust_file in ROOT.rglob("TRUST.md"):
        if any(p in IGNORED for p in trust_file.parts):
            continue
        folder = trust_file.parent
        rel = str(folder.relative_to(ROOT))
        content = trust_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            if ":" in line and line.strip().startswith("-"):
                parts = line.strip("- ").split(":")
                if len(parts) == 2:
                    results.append({
                        "folder": rel,
                        "agent": parts[0].strip(),
                        "tier": parts[1].strip().upper()
                    })
    return results


def find_audit_logs(limit: int = 50):
    entries = []
    for changelog in ROOT.rglob("CHANGELOG.ai.md"):
        if any(p in IGNORED for p in changelog.parts):
            continue
        folder = changelog.parent
        rel = str(folder.relative_to(ROOT))
        for line in changelog.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("-") and "`" in line:
                entries.append({"folder": rel, "entry": line.strip()})
    return entries[-limit:]


# ─── API Routes ─────────────────────────────────────────────────────────────

@app.get("/api/summary")
def api_summary():
    contracts = find_contracts()
    in_flight = find_all_in_flight()
    locks = find_all_locks()
    trust = find_all_trust()
    audit = find_audit_logs()
    read_only_count = sum(1 for c in contracts if c["read_only"])
    agents = list(set(t["agent"] for t in trust))
    return {
        "root": str(ROOT),
        "total_contracts": len(contracts),
        "total_in_flight": len(in_flight),
        "total_locks": len(locks),
        "total_agents": len(agents),
        "read_only_folders": read_only_count,
        "recent_audit_entries": len(audit),
        "generated_at": datetime.now().isoformat()
    }


@app.get("/api/contracts")
def api_contracts():
    return find_contracts()


@app.get("/api/in-flight")
def api_in_flight():
    return find_all_in_flight()


@app.get("/api/locks")
def api_locks():
    return find_all_locks()


@app.get("/api/trust")
def api_trust():
    return find_all_trust()


@app.get("/api/audit")
def api_audit(limit: int = 50):
    return find_audit_logs(limit)


@app.get("/api/contract/{path:path}")
def api_contract(path: str):
    folder = ROOT / path
    if not folder.exists():
        return JSONResponse(status_code=404, content={"error": f"Folder not found: {path}"})
    resolver = get_resolver()
    dummy = folder / "_check.md"
    contract = resolver.resolve(dummy)
    return contract_to_dict(contract, path)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>AIFS Hub</h1><p>index.html not found. Run from AIFS/hub/</p>")


# ─── Entry Point ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="AIFS Hub Server v0.5")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--port", type=int, default=7331, help="Port (default: 7331)")
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    args = parser.parse_args()

    global ROOT
    ROOT = Path(args.root).resolve()

    print("\n🧠 AIFS Hub v0.5")
    print(f"📁 Root: {ROOT}")
    print(f"🌐 Dashboard: http://{args.host}:{args.port}")
    print(f"🔌 API: http://{args.host}:{args.port}/api/summary\n")

    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
