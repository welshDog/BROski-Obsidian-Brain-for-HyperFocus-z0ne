"""
AIFS Registry Server v1.0
Self-hostable FastAPI registry backend.

Run:
    python AIFS/registry/registry_server.py
    python AIFS/registry/registry_server.py --port 7332 --data ./registry_data

Endpoints:
    POST /auth/login
    POST /auth/register
    POST /registry/publish
    POST /registry/unpublish
    GET  /registry/list
    GET  /registry/search?q=...
    GET  /registry/contract/{author}/{name}
    GET  /registry/stats
    GET  /health
"""

import sys
import json
import uuid
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException, Depends, Header
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("ERROR: pip install fastapi uvicorn pydantic", file=sys.stderr)
    sys.exit(1)

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
except ImportError:
    print("ERROR: pip install cryptography", file=sys.stderr)
    sys.exit(1)


DATA_DIR = Path("./registry_data")
app = FastAPI(title="AIFS Registry", version="1.0.0", description="The public registry for AIFS folder contracts.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ─── Storage helpers ─────────────────────────────────────────────────────────
def contracts_dir() -> Path:
    d = DATA_DIR / "contracts"
    d.mkdir(parents=True, exist_ok=True)
    return d

def users_dir() -> Path:
    d = DATA_DIR / "users"
    d.mkdir(parents=True, exist_ok=True)
    return d

def contract_path(name: str) -> Path:
    safe = name.replace("/", "__")
    return contracts_dir() / f"{safe}.json"

def load_contract(name: str) -> Optional[dict]:
    p = contract_path(name)
    if p.exists():
        return json.loads(p.read_text())
    return None

def save_contract(name: str, data: dict):
    contract_path(name).write_text(json.dumps(data, indent=2))

def all_contracts() -> list[dict]:
    return [json.loads(f.read_text()) for f in contracts_dir().glob("*.json")]


# ─── Auth ─────────────────────────────────────────────────────────────────────────
TOKENS: dict = {}  # token -> username (in-memory; use Redis/DB in prod)

def user_path(username: str) -> Path:
    return users_dir() / f"{username}.json"

def verify_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ")
    username = TOKENS.get(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


# ─── Pydantic models ──────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class PublishRequest(BaseModel):
    name: str
    description: str = ""
    tags: list[str] = []
    version: str = "1.0.0"
    files: dict[str, str]
    public_key: str = ""
    sig_hex: str = ""
    signed_by: str = ""
    signed_at: str = ""
    key_id: str = ""

class UnpublishRequest(BaseModel):
    name: str


# ─── Signature Verification ─────────────────────────────────────────────────────
def verify_sig(manifest_content: str, sig_hex: str, pub_hex: str) -> bool:
    """Verify Ed25519 signature against manifest.toml content."""
    if not sig_hex or not pub_hex:
        return False
    try:
        import tomllib, json as _json
        data = tomllib.loads(manifest_content)
        SIGNED = {"contract", "permissions", "output", "safety", "subfolders"}
        policy = {k: v for k, v in data.items() if k in SIGNED}
        canonical = _json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
        pub_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
        pub_key.verify(bytes.fromhex(sig_hex), canonical)
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False


# ─── Auth Routes ──────────────────────────────────────────────────────────────
@app.post("/auth/register")
def register(req: RegisterRequest):
    up = user_path(req.username)
    if up.exists():
        raise HTTPException(400, "Username taken")
    pw_hash = hashlib.sha256(req.password.encode()).hexdigest()
    up.write_text(json.dumps({"username": req.username, "pw_hash": pw_hash, "email": req.email, "created": datetime.now(timezone.utc).isoformat()}))
    return {"message": "Account created", "username": req.username}


@app.post("/auth/login")
def login(req: LoginRequest):
    up = user_path(req.username)
    if not up.exists():
        raise HTTPException(401, "Invalid credentials")
    user = json.loads(up.read_text())
    pw_hash = hashlib.sha256(req.password.encode()).hexdigest()
    if user["pw_hash"] != pw_hash:
        raise HTTPException(401, "Invalid credentials")
    token = str(uuid.uuid4())
    TOKENS[token] = req.username
    return {"token": token, "username": req.username}


# ─── Registry Routes ───────────────────────────────────────────────────────────
@app.post("/registry/publish")
def publish(req: PublishRequest, username: str = Depends(verify_token)):
    # Enforce author prefix
    if not req.name.startswith(f"{username}/"):
        raise HTTPException(403, f"Contract name must start with '{username}/'")

    # Verify signature if provided
    sig_valid = False
    manifest_content = req.files.get("manifest.toml", "")
    if req.sig_hex and req.public_key and manifest_content:
        sig_valid = verify_sig(manifest_content, req.sig_hex, req.public_key)

    entry = {
        "name": req.name,
        "author": username,
        "description": req.description,
        "tags": req.tags,
        "version": req.version,
        "files": req.files,
        "public_key": req.public_key,
        "sig_hex": req.sig_hex,
        "signed_by": req.signed_by,
        "signed_at": req.signed_at,
        "key_id": req.key_id,
        "signature_valid": sig_valid,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "downloads": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_contract(req.name, entry)
    return {"message": "Published", "name": req.name, "signature_valid": sig_valid}


@app.get("/registry/list")
def list_contracts(author: Optional[str] = None, tag: Optional[str] = None):
    contracts = all_contracts()
    if author:
        contracts = [c for c in contracts if c.get("author") == author]
    if tag:
        contracts = [c for c in contracts if tag in c.get("tags", [])]
    contracts.sort(key=lambda c: c.get("downloads", 0), reverse=True)
    return {"contracts": contracts, "total": len(contracts)}


@app.get("/registry/search")
def search(q: str = ""):
    contracts = all_contracts()
    q_lower = q.lower()
    results = [
        c for c in contracts
        if q_lower in c.get("name", "").lower()
        or q_lower in c.get("description", "").lower()
        or any(q_lower in t.lower() for t in c.get("tags", []))
    ]
    results.sort(key=lambda c: c.get("downloads", 0), reverse=True)
    return {"results": results, "total": len(results), "query": q}


@app.get("/registry/contract/{author}/{name}")
def get_contract(author: str, name: str):
    full_name = f"{author}/{name}"
    c = load_contract(full_name)
    if not c:
        raise HTTPException(404, f"Contract not found: {full_name}")
    c["downloads"] = c.get("downloads", 0) + 1
    save_contract(full_name, c)
    return c


@app.post("/registry/unpublish")
def unpublish(req: UnpublishRequest, username: str = Depends(verify_token)):
    if not req.name.startswith(f"{username}/"):
        raise HTTPException(403, "Can only unpublish your own contracts")
    p = contract_path(req.name)
    if not p.exists():
        raise HTTPException(404, "Contract not found")
    p.unlink()
    return {"message": "Unpublished", "name": req.name}


@app.get("/registry/stats")
def stats():
    contracts = all_contracts()
    total_downloads = sum(c.get("downloads", 0) for c in contracts)
    authors = list(set(c.get("author", "") for c in contracts))
    signed = sum(1 for c in contracts if c.get("signature_valid"))
    return {
        "total_contracts": len(contracts),
        "total_downloads": total_downloads,
        "total_authors": len(authors),
        "signed_contracts": signed,
        "unsigned_contracts": len(contracts) - signed,
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "service": "AIFS Registry"}


# ─── Entry point ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="AIFS Registry Server v1.0")
    parser.add_argument("--port", type=int, default=7332)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--data", default="./registry_data", help="Data directory")
    args = parser.parse_args()

    global DATA_DIR
    DATA_DIR = Path(args.data)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("\n🌍 AIFS Registry Server v1.0")
    print(f"📁 Data: {DATA_DIR.resolve()}")
    print(f"🌐 API:  http://{args.host}:{args.port}")
    print(f"📚 Docs: http://{args.host}:{args.port}/docs\n")

    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
