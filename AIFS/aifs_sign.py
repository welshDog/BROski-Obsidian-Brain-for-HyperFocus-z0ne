"""
AIFS Contract Signer v0.6
Cryptographic signing and verification for AIFS folder contracts.

Uses Ed25519 (fast, small signatures, modern standard).
Signs the canonical JSON of the contract policy.
Stores signature in manifest.toml [signature] section.

Commands:
    python aifs_sign.py keygen                   # Generate a new keypair
    python aifs_sign.py sign <folder>            # Sign a folder's manifest.toml
    python aifs_sign.py verify <folder>          # Verify a folder's signature
    python aifs_sign.py inspect <folder>         # Show contract + sig info
    python aifs_sign.py sign-all <root>          # Sign all manifest.toml in repo
    python aifs_sign.py verify-all <root>        # Verify all — CI-ready exit codes
    python aifs_sign.py revoke <folder>          # Revoke / remove signature

Keystore:
    ~/.aifs/aifs_private.key   — Ed25519 private key (NEVER commit this)
    ~/.aifs/aifs_public.key    — Ed25519 public key (commit this)
    ~/.aifs/aifs_keystore.json — key metadata (author, created, key_id)

Signature storage (in manifest.toml):
    [signature]
    key_id     = "aifs-welshdog-2026"
    algorithm  = "Ed25519"
    signed_at  = "2026-06-02T22:30:00"
    signed_by  = "welshDog"
    sig_hex    = "<hex encoded signature>"
    public_key = "<hex encoded public key>"

Install deps:
    pip install cryptography

Exit codes (verify-all):
    0 = All contracts valid
    1 = One or more contracts invalid / tampered
    2 = No contracts found
"""

import sys
import json
import hashlib
import argparse
import tomllib
from pathlib import Path
from datetime import datetime, timezone

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PrivateFormat, PublicFormat,
        NoEncryption, load_pem_private_key, load_pem_public_key
    )
    from cryptography.exceptions import InvalidSignature
except ImportError:
    print("ERROR: Run: pip install cryptography", file=sys.stderr)
    sys.exit(1)


# ─── Colours ───────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
PURPLE = "\033[95m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):    print(f"{GREEN}{BOLD}✅ {msg}{RESET}")
def err(msg):   print(f"{RED}{BOLD}❌ {msg}{RESET}")
def warn(msg):  print(f"{YELLOW}⚠️  {msg}{RESET}")
def info(msg):  print(f"{BLUE}ℹ️  {msg}{RESET}")
def head(msg):  print(f"{PURPLE}{BOLD}{msg}{RESET}")


# ─── Keystore ──────────────────────────────────────────────────────────────
KEYSTORE_DIR = Path.home() / ".aifs"
PRIVATE_KEY_PATH = KEYSTORE_DIR / "aifs_private.key"
PUBLIC_KEY_PATH  = KEYSTORE_DIR / "aifs_public.key"
KEYSTORE_META    = KEYSTORE_DIR / "aifs_keystore.json"


def load_private_key() -> Ed25519PrivateKey:
    if not PRIVATE_KEY_PATH.exists():
        err(f"No private key found at {PRIVATE_KEY_PATH}")
        info("Run: python aifs_sign.py keygen")
        sys.exit(1)
    pem = PRIVATE_KEY_PATH.read_bytes()
    return load_pem_private_key(pem, password=None)


def load_public_key_from_pem() -> Ed25519PublicKey:
    if not PUBLIC_KEY_PATH.exists():
        err(f"No public key found at {PUBLIC_KEY_PATH}")
        sys.exit(1)
    pem = PUBLIC_KEY_PATH.read_bytes()
    return load_pem_public_key(pem)


def load_public_key_from_hex(hex_str: str) -> Ed25519PublicKey:
    """Load a public key from its hex-encoded raw bytes (stored in manifest)."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    raw = bytes.fromhex(hex_str)
    return Ed25519PublicKey.from_public_bytes(raw)


def get_key_id() -> str:
    if KEYSTORE_META.exists():
        meta = json.loads(KEYSTORE_META.read_text())
        return meta.get("key_id", "aifs-key")
    return "aifs-key"


def get_signed_by() -> str:
    if KEYSTORE_META.exists():
        meta = json.loads(KEYSTORE_META.read_text())
        return meta.get("author", "unknown")
    return "unknown"


# ─── Contract Canonicalisation ───────────────────────────────────────────────
SIGNED_SECTIONS = {"contract", "permissions", "output", "safety", "subfolders"}

def canonicalise(manifest_path: Path) -> bytes:
    """
    Extract only the policy sections from manifest.toml,
    sort keys, serialise to canonical JSON bytes.
    The [signature] section is EXCLUDED from signing.
    """
    with open(manifest_path, "rb") as f:
        data = tomllib.load(f)

    policy = {k: v for k, v in data.items() if k in SIGNED_SECTIONS}
    canonical = json.dumps(policy, sort_keys=True, separators=(",", ":"))
    return canonical.encode("utf-8")


def contract_digest(manifest_path: Path) -> str:
    """SHA256 hex digest of the canonical policy bytes."""
    return hashlib.sha256(canonicalise(manifest_path)).hexdigest()


# ─── Sign ───────────────────────────────────────────────────────────────────────
def sign_contract(folder: Path) -> bool:
    manifest = folder / "manifest.toml"
    if not manifest.exists():
        err(f"No manifest.toml in {folder}")
        return False

    private_key = load_private_key()
    public_key  = private_key.public_key()

    canonical_bytes = canonicalise(manifest)
    signature = private_key.sign(canonical_bytes)
    sig_hex = signature.hex()
    pub_hex = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
    signed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Read existing manifest content
    content = manifest.read_text(encoding="utf-8")

    # Remove any existing [signature] section
    lines = content.splitlines()
    filtered = []
    in_sig = False
    for line in lines:
        if line.strip() == "[signature]":
            in_sig = True
            continue
        if in_sig and line.startswith("["):
            in_sig = False
        if not in_sig:
            filtered.append(line)
    content = "\n".join(filtered).rstrip()

    # Append new [signature] block
    sig_block = f"""

[signature]
key_id     = \"{get_key_id()}\"
algorithm  = \"Ed25519\"
signed_at  = \"{signed_at}\"
signed_by  = \"{get_signed_by()}\"
sig_hex    = \"{sig_hex}\"
public_key = \"{pub_hex}\"
digest     = \"{contract_digest(manifest)}\"
"""
    manifest.write_text(content + sig_block, encoding="utf-8")
    ok(f"Signed: {folder}/manifest.toml")
    info(f"Key ID:    {get_key_id()}")
    info(f"Signed by: {get_signed_by()}")
    info(f"Signed at: {signed_at}")
    info(f"Digest:    {contract_digest(manifest)[:16]}...")
    return True


# ─── Verify ──────────────────────────────────────────────────────────────────────
def verify_contract(folder: Path, silent: bool = False) -> str:
    """
    Returns: "valid" | "unsigned" | "tampered" | "error"
    """
    manifest = folder / "manifest.toml"
    if not manifest.exists():
        return "error"

    with open(manifest, "rb") as f:
        data = tomllib.load(f)

    sig_block = data.get("signature", {})
    if not sig_block:
        if not silent:
            warn(f"Unsigned: {folder}/manifest.toml")
        return "unsigned"

    sig_hex    = sig_block.get("sig_hex", "")
    pub_hex    = sig_block.get("public_key", "")
    signed_by  = sig_block.get("signed_by", "unknown")
    signed_at  = sig_block.get("signed_at", "")
    key_id     = sig_block.get("key_id", "")

    if not sig_hex or not pub_hex:
        if not silent:
            err(f"Corrupt signature block: {folder}/manifest.toml")
        return "tampered"

    try:
        public_key = load_public_key_from_hex(pub_hex)
        canonical  = canonicalise(manifest)
        public_key.verify(bytes.fromhex(sig_hex), canonical)
        if not silent:
            ok(f"VALID: {folder}/manifest.toml")
            info(f"Signed by: {signed_by} ({key_id}) at {signed_at}")
        return "valid"
    except InvalidSignature:
        if not silent:
            err(f"TAMPERED: {folder}/manifest.toml — signature does not match!")
            warn("Contract has been modified after signing. DO NOT TRUST.")
        return "tampered"
    except Exception as e:
        if not silent:
            err(f"Verify error: {e}")
        return "error"


# ─── Commands ────────────────────────────────────────────────────────────────────
def cmd_keygen(args):
    head("\n🔑 AIFS Key Generation")
    KEYSTORE_DIR.mkdir(parents=True, exist_ok=True)

    if PRIVATE_KEY_PATH.exists() and not getattr(args, 'force', False):
        warn(f"Key already exists at {PRIVATE_KEY_PATH}")
        warn("Use --force to overwrite (this invalidates all existing signatures!)")
        sys.exit(1)

    author = getattr(args, 'author', None) or input("Author name (e.g. welshDog): ").strip() or "unknown"
    key_id = getattr(args, 'key_id', None) or f"aifs-{author.lower().replace(' ', '-')}-{datetime.now().year}"

    private_key = Ed25519PrivateKey.generate()
    public_key  = private_key.public_key()

    # Save private key PEM
    priv_pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    PRIVATE_KEY_PATH.write_bytes(priv_pem)
    PRIVATE_KEY_PATH.chmod(0o600)  # owner read-only

    # Save public key PEM
    pub_pem = public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    PUBLIC_KEY_PATH.write_bytes(pub_pem)

    # Save metadata
    meta = {
        "key_id": key_id,
        "author": author,
        "algorithm": "Ed25519",
        "created": datetime.now(timezone.utc).isoformat(),
        "private_key_path": str(PRIVATE_KEY_PATH),
        "public_key_path": str(PUBLIC_KEY_PATH)
    }
    KEYSTORE_META.write_text(json.dumps(meta, indent=2))

    pub_hex = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()

    ok("Keypair generated!")
    info(f"Key ID:      {key_id}")
    info(f"Author:      {author}")
    info(f"Private key: {PRIVATE_KEY_PATH}  ← NEVER COMMIT")
    info(f"Public key:  {PUBLIC_KEY_PATH}  ← safe to commit")
    info(f"Public hex:  {pub_hex[:32]}...")
    print(f"\n{YELLOW}Add {PUBLIC_KEY_PATH} to your repo. Keep {PRIVATE_KEY_PATH} secret.{RESET}\n")


def cmd_sign(args):
    folder = Path(args.folder).resolve()
    head(f"\n🔒 Signing: {folder}")
    sign_contract(folder)


def cmd_verify(args):
    folder = Path(args.folder).resolve()
    head(f"\n🔍 Verifying: {folder}")
    result = verify_contract(folder)
    if result == "tampered":
        sys.exit(1)


def cmd_inspect(args):
    folder = Path(args.folder).resolve()
    manifest = folder / "manifest.toml"
    head(f"\n🔎 Inspecting: {folder}")

    if not manifest.exists():
        err("No manifest.toml found")
        sys.exit(1)

    with open(manifest, "rb") as f:
        data = tomllib.load(f)

    # Print contract sections
    print(f"\n{BLUE}Contract Policy:{RESET}")
    for section in ["contract", "permissions", "safety"]:
        if section in data:
            print(f"  [{section}]")
            for k, v in data[section].items():
                print(f"    {k} = {v}")

    # Print signature block
    sig = data.get("signature", {})
    if sig:
        print(f"\n{PURPLE}Signature Block:{RESET}")
        for k, v in sig.items():
            if k in ("sig_hex", "public_key"):
                print(f"  {k} = {str(v)[:32]}...")
            else:
                print(f"  {k} = {v}")

        # Verify inline
        result = verify_contract(folder, silent=True)
        status_map = {
            "valid":    f"{GREEN}{BOLD}✅ VALID — signature matches{RESET}",
            "tampered": f"{RED}{BOLD}🚫 TAMPERED — DO NOT TRUST{RESET}",
            "unsigned": f"{YELLOW}⚠️  UNSIGNED{RESET}",
            "error":    f"{RED}❌ ERROR{RESET}",
        }
        print(f"\nVerification: {status_map.get(result, result)}")
    else:
        warn("No signature block found — contract is unsigned")

    # Print digest
    print(f"\nDigest: {contract_digest(manifest)}")
    print()


def cmd_sign_all(args):
    root = Path(args.root).resolve()
    IGNORED = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}
    head(f"\n🔒 Signing all contracts in: {root}")
    signed = 0
    failed = 0
    for manifest in root.rglob("manifest.toml"):
        if any(p in IGNORED for p in manifest.parts):
            continue
        success = sign_contract(manifest.parent)
        if success:
            signed += 1
        else:
            failed += 1
    print()
    ok(f"Signed: {signed} contracts")
    if failed:
        err(f"Failed: {failed} contracts")
    info(f"Total:  {signed + failed}")


def cmd_verify_all(args):
    root = Path(args.root).resolve()
    IGNORED = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}
    head(f"\n🔍 Verifying all contracts in: {root}")

    results = {"valid": [], "unsigned": [], "tampered": [], "error": []}

    for manifest in root.rglob("manifest.toml"):
        if any(p in IGNORED for p in manifest.parts):
            continue
        folder = manifest.parent
        rel = str(folder.relative_to(root))
        result = verify_contract(folder)
        results[result].append(rel)

    total = sum(len(v) for v in results.values())
    if total == 0:
        warn("No manifest.toml files found")
        sys.exit(2)

    print()
    ok(f"Valid:    {len(results['valid'])} contracts")
    if results["unsigned"]:
        warn(f"Unsigned: {len(results['unsigned'])} contracts")
        for f in results["unsigned"]:
            print(f"  • {f}")
    if results["tampered"]:
        err(f"TAMPERED: {len(results['tampered'])} contracts — DO NOT TRUST")
        for f in results["tampered"]:
            print(f"  • {f}")
    if results["error"]:
        err(f"Errors:   {len(results['error'])} contracts")

    info(f"Total:    {total}")

    if results["tampered"] or results["error"]:
        sys.exit(1)  # CI fail
    sys.exit(0)  # CI pass


def cmd_revoke(args):
    folder = Path(args.folder).resolve()
    manifest = folder / "manifest.toml"
    head(f"\n🗑️  Revoking signature: {folder}")

    if not manifest.exists():
        err("No manifest.toml found")
        sys.exit(1)

    content = manifest.read_text(encoding="utf-8")
    lines = content.splitlines()
    filtered = []
    in_sig = False
    for line in lines:
        if line.strip() == "[signature]":
            in_sig = True
            continue
        if in_sig and line.startswith("["):
            in_sig = False
        if not in_sig:
            filtered.append(line)

    manifest.write_text("\n".join(filtered).rstrip() + "\n", encoding="utf-8")
    ok(f"Signature revoked from {folder}/manifest.toml")


# ─── CLI Entry Point ────────────────────────────────────────────────────────────
def main():
    print(f"{PURPLE}{BOLD}")
    print("╔══════════════════════════════════════════════╗")
    print("║   🔐 AIFS Contract Signer v0.6              ║")
    print("║   Ed25519 Cryptographic Signing           ║")
    print("╚══════════════════════════════════════════════╝")
    print(RESET)

    parser = argparse.ArgumentParser(
        description="AIFS Contract Signer — Ed25519 cryptographic contract signing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python aifs_sign.py keygen --author welshDog
  python aifs_sign.py sign ./src
  python aifs_sign.py verify ./src
  python aifs_sign.py inspect ./migrations
  python aifs_sign.py sign-all .
  python aifs_sign.py verify-all .    # exit 1 if any tampered
  python aifs_sign.py revoke ./src
"""
    )
    sub = parser.add_subparsers(dest="command")

    kg = sub.add_parser("keygen", help="Generate Ed25519 keypair")
    kg.add_argument("--author", default="", help="Author name")
    kg.add_argument("--key-id", default="", dest="key_id", help="Key ID")
    kg.add_argument("--force", action="store_true", help="Overwrite existing key")

    s = sub.add_parser("sign", help="Sign a folder contract")
    s.add_argument("folder", help="Folder containing manifest.toml")

    v = sub.add_parser("verify", help="Verify a folder contract")
    v.add_argument("folder", help="Folder containing manifest.toml")

    i = sub.add_parser("inspect", help="Inspect contract + signature")
    i.add_argument("folder", help="Folder containing manifest.toml")

    sa = sub.add_parser("sign-all", help="Sign all contracts in repo")
    sa.add_argument("root", nargs="?", default=".", help="Root path")

    va = sub.add_parser("verify-all", help="Verify all contracts (CI-ready)")
    va.add_argument("root", nargs="?", default=".", help="Root path")

    r = sub.add_parser("revoke", help="Remove signature from contract")
    r.add_argument("folder", help="Folder containing manifest.toml")

    args = parser.parse_args()

    dispatch = {
        "keygen":     cmd_keygen,
        "sign":       cmd_sign,
        "verify":     cmd_verify,
        "inspect":    cmd_inspect,
        "sign-all":   cmd_sign_all,
        "verify-all": cmd_verify_all,
        "revoke":     cmd_revoke,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
