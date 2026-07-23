"""
AIFS Registry CLI v1.0
Publish, discover and install verified AIFS folder contracts.

Like npm for AI governance rules.

Commands:
    publish <folder>         — sign + publish contract to registry
    search <query>           — search by name, tag, description
    install <name> [target]  — download + apply contract
    verify <name>            — verify registry contract signature
    list                     — browse all contracts
    info <name>              — full contract details
    unpublish <name>         — remove your contract
    login                    — save registry token

Install deps:
    pip install cryptography requests

Registry API base URL:
    Default: https://aifs-registry.hyperfocuszone.com (when live)
    Self-hosted: python AIFS/registry/registry_server.py

Set custom registry:
    export AIFS_REGISTRY=http://localhost:7332
    OR use --registry flag
"""

import os
import sys
import json
import argparse
import tomllib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

try:
    import requests
except ImportError:
    print("ERROR: pip install requests", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))


# ─── Config ───────────────────────────────────────────────────────────────────
DEFAULT_REGISTRY = os.environ.get("AIFS_REGISTRY", "https://aifs-registry.hyperfocuszone.com")
CONFIG_DIR  = Path.home() / ".aifs"
TOKEN_PATH  = CONFIG_DIR / "registry_token.json"
CACHE_DIR   = CONFIG_DIR / "registry_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

IGNORED = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}

# ─── Colours ───────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
PURPLE = "\033[95m"
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

def ok(m):   print(f"{GREEN}{BOLD}✅ {m}{RESET}")
def err(m):  print(f"{RED}{BOLD}❌ {m}{RESET}")
def warn(m): print(f"{YELLOW}⚠️  {m}{RESET}")
def info(m): print(f"{BLUE}ℹ️  {m}{RESET}")
def head(m): print(f"{PURPLE}{BOLD}{m}{RESET}")
def dim(m):  print(f"{DIM}{m}{RESET}")


# ─── Auth ─────────────────────────────────────────────────────────────────────────
def load_token() -> Optional[str]:
    if TOKEN_PATH.exists():
        return json.loads(TOKEN_PATH.read_text()).get("token")
    return None

def save_token(token: str, username: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps({"token": token, "username": username, "saved_at": datetime.now().isoformat()}))

def auth_headers() -> dict:
    token = load_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


# ─── Contract Loader ─────────────────────────────────────────────────────────
def load_contract_files(folder: Path) -> dict:
    """Load all AIFS contract files from a folder into a dict."""
    files = {}
    CONTRACT_FILES = ["manifest.toml", "AGENTS.md", "folder.prompt.md", ".ailock", "context.md", "TRUST.md"]
    for fname in CONTRACT_FILES:
        fpath = folder / fname
        if fpath.exists():
            files[fname] = fpath.read_text(encoding="utf-8")
    return files


def read_manifest_meta(folder: Path) -> dict:
    manifest = folder / "manifest.toml"
    if not manifest.exists():
        return {}
    with open(manifest, "rb") as f:
        return tomllib.load(f)


# ─── Local Registry Cache (works offline too) ─────────────────────────────
def cache_path(name: str) -> Path:
    safe = name.replace("/", "__")
    return CACHE_DIR / f"{safe}.json"

def write_cache(name: str, data: dict):
    cache_path(name).write_text(json.dumps(data, indent=2))

def read_cache(name: str) -> Optional[dict]:
    p = cache_path(name)
    if p.exists():
        return json.loads(p.read_text())
    return None


# ─── API helpers ───────────────────────────────────────────────────────────────
def api_get(url: str, registry: str) -> Optional[dict]:
    try:
        r = requests.get(f"{registry}{url}", headers=auth_headers(), timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        warn(f"Registry offline: {registry}")
        return None
    except Exception as e:
        err(f"API error: {e}")
        return None

def api_post(url: str, data: dict, registry: str) -> Optional[dict]:
    try:
        r = requests.post(f"{registry}{url}", json=data, headers=auth_headers(), timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        warn(f"Registry offline: {registry}")
        return None
    except Exception as e:
        err(f"API error: {e}")
        return None


# ─── Commands ─────────────────────────────────────────────────────────────────────
def cmd_login(args):
    head("\n🔑 AIFS Registry Login")
    registry = getattr(args, 'registry', DEFAULT_REGISTRY)
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    result = api_post("/auth/login", {"username": username, "password": password}, registry)
    if result and "token" in result:
        save_token(result["token"], username)
        ok(f"Logged in as {username}")
    else:
        err("Login failed")
        sys.exit(1)


def cmd_publish(args):
    folder = Path(args.folder).resolve()
    registry = getattr(args, 'registry', DEFAULT_REGISTRY)
    head(f"\n📦 Publishing: {folder}")

    token = load_token()
    if not token:
        err("Not logged in. Run: aifs_registry.py login")
        sys.exit(1)

    manifest = folder / "manifest.toml"
    if not manifest.exists():
        err("No manifest.toml found. Create one first.")
        sys.exit(1)

    # Load manifest meta
    meta = read_manifest_meta(folder)
    contract_section = meta.get("contract", {})
    sig_section = meta.get("signature", {})

    if not sig_section:
        warn("Contract is unsigned. Sign it first with: python AIFS/aifs_sign.py sign <folder>")
        resp = input("Publish unsigned? [y/N]: ").strip().lower()
        if resp != "y":
            info("Aborted. Sign the contract first.")
            sys.exit(0)

    # Build publish payload
    name_arg = getattr(args, 'name', None) or contract_section.get("name", folder.name)
    username = json.loads(TOKEN_PATH.read_text()).get("username", "unknown") if TOKEN_PATH.exists() else "unknown"
    full_name = f"{username}/{name_arg}"
    tags = getattr(args, 'tags', "") or contract_section.get("tags", "")
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    files = load_contract_files(folder)
    payload = {
        "name": full_name,
        "description": getattr(args, 'description', None) or contract_section.get("description", ""),
        "tags": tags,
        "version": getattr(args, 'version', None) or contract_section.get("version", "1.0.0"),
        "files": files,
        "public_key": sig_section.get("public_key", ""),
        "sig_hex": sig_section.get("sig_hex", ""),
        "signed_by": sig_section.get("signed_by", ""),
        "signed_at": sig_section.get("signed_at", ""),
        "key_id": sig_section.get("key_id", ""),
    }

    info(f"Publishing as: {full_name}")
    info(f"Tags: {', '.join(tags) or 'none'}")
    info(f"Files: {', '.join(files.keys())}")
    info(f"Signed: {'yes ✅' if sig_section else 'no ⚠️'}")

    result = api_post("/registry/publish", payload, registry)
    if result:
        write_cache(full_name, result)
        ok(f"Published: {full_name}")
        info(f"Registry: {registry}/registry/{full_name}")
    else:
        # Fallback: save locally so it still works
        local_export = CONFIG_DIR / "published" / f"{full_name.replace('/', '__')}.json"
        local_export.parent.mkdir(parents=True, exist_ok=True)
        local_export.write_text(json.dumps(payload, indent=2))
        warn(f"Registry offline. Saved locally: {local_export}")
        info("Will sync when registry is available.")


def cmd_search(args):
    query = args.query
    registry = getattr(args, 'registry', DEFAULT_REGISTRY)
    head(f"\n🔍 Searching: \"{query}\"")

    result = api_get(f"/registry/search?q={query}", registry)

    if result is None:
        # Try local cache
        warn("Registry offline — searching local cache...")
        cached = list(CACHE_DIR.glob("*.json"))
        results = []
        for f in cached:
            try:
                data = json.loads(f.read_text())
                if query.lower() in json.dumps(data).lower():
                    results.append(data)
            except Exception:
                pass
        if not results:
            info("No cached results found.")
            return
        result = {"results": results, "total": len(results)}

    results = result.get("results", [])
    if not results:
        info(f"No contracts found for \"{query}\"")
        return

    print(f"\nFound {len(results)} contract(s):\n")
    for c in results:
        sig_badge = f"{GREEN}✅ signed{RESET}" if c.get("signature_valid") else f"{YELLOW}⚠️  unsigned{RESET}"
        tags = ", ".join(c.get("tags", [])) or "no tags"
        print(f"  {BOLD}{PURPLE}{c['name']}{RESET}  {sig_badge}")
        print(f"  {c.get('description', 'No description')}")
        print(f"  {DIM}Tags: {tags} | v{c.get('version', '?')} | {c.get('downloads', 0)} downloads{RESET}")
        print()


def cmd_install(args):
    name = args.name
    target = Path(getattr(args, 'target', None) or ".").resolve()
    registry = getattr(args, 'registry', DEFAULT_REGISTRY)
    head(f"\n📥 Installing: {name} → {target}")

    result = api_get(f"/registry/contract/{name}", registry)

    if result is None:
        # Try local cache
        cached = read_cache(name)
        if cached:
            warn("Registry offline — using cached version")
            result = cached
        else:
            err(f"Contract not found: {name}")
            sys.exit(1)

    # Verify signature before installing
    sig_valid = result.get("signature_valid", False)
    if not sig_valid and result.get("sig_hex"):
        err("Signature verification FAILED. Refusing to install.")
        warn("This contract may have been tampered with.")
        sys.exit(1)

    if not sig_valid:
        warn("Contract is unsigned. Installing anyway (use caution).")
        resp = input("Install unsigned contract? [y/N]: ").strip().lower()
        if resp != "y":
            sys.exit(0)

    # Write contract files
    target.mkdir(parents=True, exist_ok=True)
    files = result.get("files", {})
    written = []
    for fname, content in files.items():
        fpath = target / fname
        fpath.write_text(content, encoding="utf-8")
        written.append(fname)

    # Write .aifs-source file so we know where it came from
    source_meta = {
        "registry_name": name,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "registry": registry,
        "version": result.get("version", "?"),
        "author": result.get("author", "?"),
    }
    (target / ".aifs-source").write_text(json.dumps(source_meta, indent=2))

    write_cache(name, result)
    ok(f"Installed: {name} → {target}")
    info(f"Files: {', '.join(written)}")
    info(f"Version: {result.get('version', '?')} by {result.get('author', '?')}")


def cmd_verify(args):
    name = args.name
    registry = getattr(args, 'registry', DEFAULT_REGISTRY)
    head(f"\n🔍 Verifying registry contract: {name}")

    result = api_get(f"/registry/contract/{name}", registry)
    if result is None:
        result = read_cache(name)
    if not result:
        err(f"Contract not found: {name}")
        sys.exit(1)

    sig_valid = result.get("signature_valid", False)
    if sig_valid:
        ok(f"VALID: {name}")
        info(f"Signed by: {result.get('signed_by', '?')} at {result.get('signed_at', '?')}")
        info(f"Key ID: {result.get('key_id', '?')}")
    else:
        warn(f"UNSIGNED: {name} has no valid signature")


def cmd_list(args):
    registry = getattr(args, 'registry', DEFAULT_REGISTRY)
    author = getattr(args, 'author', None)
    tag = getattr(args, 'tag', None)
    head("\n📚 AIFS Registry")

    url = "/registry/list"
    params = []
    if author:
        params.append(f"author={author}")
    if tag:
        params.append(f"tag={tag}")
    if params:
        url += "?" + "&".join(params)

    result = api_get(url, registry)
    if result is None:
        # Show cached contracts
        warn("Registry offline — showing cached contracts")
        cached = list(CACHE_DIR.glob("*.json"))
        if not cached:
            info("No cached contracts.")
            return
        result = {"contracts": [json.loads(f.read_text()) for f in cached[:20]], "total": len(cached)}

    contracts = result.get("contracts", [])
    total = result.get("total", len(contracts))
    print(f"\n{total} contract(s) in registry:\n")
    for c in contracts:
        sig_badge = f"{GREEN}✅{RESET}" if c.get("signature_valid") else f"{YELLOW}⚠️ {RESET}"
        print(f"  {sig_badge} {BOLD}{PURPLE}{c['name']}{RESET}  {DIM}v{c.get('version', '?')} | {c.get('downloads', 0)}dl{RESET}")
        print(f"     {c.get('description', '')}")
        tags = ", ".join(c.get('tags', []))
        if tags:
            print(f"     {DIM}{tags}{RESET}")
        print()


def cmd_info(args):
    name = args.name
    registry = getattr(args, 'registry', DEFAULT_REGISTRY)
    head(f"\n📄 Contract Info: {name}")

    result = api_get(f"/registry/contract/{name}", registry)
    if result is None:
        result = read_cache(name)
    if not result:
        err(f"Not found: {name}")
        sys.exit(1)

    sig_badge = f"{GREEN}✅ signed{RESET}" if result.get("signature_valid") else f"{YELLOW}⚠️  unsigned{RESET}"
    print(f"\n  Name:        {BOLD}{result.get('name', name)}{RESET}")
    print(f"  Author:      {result.get('author', '?')}")
    print(f"  Version:     {result.get('version', '?')}")
    print(f"  Description: {result.get('description', '')}")
    print(f"  Tags:        {', '.join(result.get('tags', []))}")
    print(f"  Published:   {result.get('published_at', '?')}")
    print(f"  Downloads:   {result.get('downloads', 0)}")
    print(f"  Signature:   {sig_badge}")
    if result.get("signed_by"):
        print(f"  Signed by:   {result['signed_by']} ({result.get('key_id', '?')}) at {result.get('signed_at', '?')}")
    files = list(result.get("files", {}).keys())
    print(f"  Files:       {', '.join(files)}")
    print()


def cmd_unpublish(args):
    name = args.name
    registry = getattr(args, 'registry', DEFAULT_REGISTRY)
    head(f"\n🗑️  Unpublishing: {name}")
    resp = input(f"Remove {name} from registry? [y/N]: ").strip().lower()
    if resp != "y":
        return
    result = api_post("/registry/unpublish", {"name": name}, registry)
    if result:
        ok(f"Unpublished: {name}")
        cp = cache_path(name)
        if cp.exists():
            cp.unlink()
    else:
        err("Unpublish failed")


# ─── CLI Entry Point ────────────────────────────────────────────────────────────
def main():
    print(f"{PURPLE}{BOLD}")
    print("╔══════════════════════════════════════════════╗")
    print("║   🌍 AIFS Registry CLI v1.0                ║")
    print("║   Publish. Discover. Install. Trust.    ║")
    print("╚══════════════════════════════════════════════╝")
    print(RESET)

    parser = argparse.ArgumentParser(
        description="AIFS Registry — publish, discover and install verified AIFS contracts"
    )
    parser.add_argument("--registry", default=DEFAULT_REGISTRY, help="Registry URL")
    sub = parser.add_subparsers(dest="command")

    # login
    sub.add_parser("login", help="Login to registry")

    # publish
    p = sub.add_parser("publish", help="Publish a contract")
    p.add_argument("folder", help="Folder with manifest.toml")
    p.add_argument("--name", help="Contract name (default: folder name)")
    p.add_argument("--description", help="Description")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--version", help="Version (default: 1.0.0)")

    # search
    s = sub.add_parser("search", help="Search contracts")
    s.add_argument("query", help="Search query")

    # install
    i = sub.add_parser("install", help="Install a contract")
    i.add_argument("name", help="Contract name (author/name)")
    i.add_argument("--target", help="Target folder (default: .)")

    # verify
    v = sub.add_parser("verify", help="Verify registry contract")
    v.add_argument("name", help="Contract name")

    # list
    li = sub.add_parser("list", help="List contracts")
    li.add_argument("--author", help="Filter by author")
    li.add_argument("--tag", help="Filter by tag")

    # info
    inf = sub.add_parser("info", help="Contract details")
    inf.add_argument("name", help="Contract name")

    # unpublish
    un = sub.add_parser("unpublish", help="Remove contract")
    un.add_argument("name", help="Contract name")

    args = parser.parse_args()
    dispatch = {
        "login":     cmd_login,
        "publish":   cmd_publish,
        "search":    cmd_search,
        "install":   cmd_install,
        "verify":    cmd_verify,
        "list":      cmd_list,
        "info":      cmd_info,
        "unpublish": cmd_unpublish,
    }
    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
