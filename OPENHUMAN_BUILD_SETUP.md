# OpenHuman Build Setup

The OpenHuman binary image isn't publicly available on Docker Hub or GHCR yet. **We build it locally from source** — takes ~5-10 min on first run, then cached.

---

## Quick Start

### Step 1: Clone OpenHuman source

```bash
# One time only — clones the repo for Docker build
git clone https://github.com/tinyhumansai/openhuman.git openhuman-build
```

### Step 2: Set your vault path

```bash
# macOS/Linux
export VAULT_PATH=$HOME/BROski-Obsidian-Brain-for-HyperFocus-z0ne

# Windows (PowerShell)
$env:VAULT_PATH = "H:\HYPERFOCUSZONE\HperCore\BROski-Obsidian-Brain-for-HyperFocus-z0ne"
```

### Step 3: Build and start

```bash
# First run: builds the image + starts container (~5-10 min)
docker compose -f docker-compose.openhuman.yml up -d

# Subsequent runs: uses cached image (instant)
docker compose -f docker-compose.openhuman.yml up -d
```

### Step 4: Access UI

```
http://127.0.0.1:3210
```

---

## How It Works

1. **`docker-compose.openhuman.yml`** has:
   ```yaml
   build:
     context: ./openhuman-build
     dockerfile: Dockerfile
   image: openhuman:local
   ```

2. This tells Docker: "Build from the `openhuman-build/` folder (which contains the Dockerfile)"

3. First build takes ~5-10 min. Subsequent runs use the cached `openhuman:local` image (instant).

---

## File Structure

```
BROski-Obsidian-Brain-for-HyperFocus-z0ne/
  ├── docker-compose.openhuman.yml  ← You run this
  ├── .env.openhuman  ← Your config
  ├── openhuman-build/  ← Source code (cloned via git)
  │   ├── Dockerfile
  │   ├── src/
  │   ├── Cargo.toml
  │   └── ... (rest of OpenHuman repo)
  └── HYPERFOCUS_ZONE/
      └── 00-Inbox/
          └── OpenHuman-Feed/  ← Auto-synced notes here
```

---

## Troubleshooting

### Q: "openhuman-build/ not found"

**A:** You skipped Step 1. Run:
```bash
git clone https://github.com/tinyhumansai/openhuman.git openhuman-build
```

### Q: Build fails — "Dockerfile not found"

**A:** Make sure you cloned into the right folder:
```bash
ls openhuman-build/Dockerfile
# Should return: openhuman-build/Dockerfile
```

If it says "No such file", the clone failed. Try again:
```bash
rm -rf openhuman-build
git clone https://github.com/tinyhumansai/openhuman.git openhuman-build
```

### Q: Build timeout after 10 min

**A:** Rust compilation can be slow. Either:
- Wait longer (might take 15-20 min on slow connections)
- Check Docker resources: Settings → Resources → increase CPU/RAM

### Q: How do I rebuild from scratch?

**A:** 
```bash
# Remove the cached image
docker rmi openhuman:local

# Next compose up will rebuild
docker compose -f docker-compose.openhuman.yml up -d
```

### Q: Update to latest OpenHuman source

**A:**
```bash
cd openhuman-build
git pull origin main
cd ..

# Rebuild
docker rmi openhuman:local
docker compose -f docker-compose.openhuman.yml up -d --build
```

---

## .gitignore Note

Add to `.gitignore` so you don't commit the source repo:

```bash
# OpenHuman source (too large, rebuild from GitHub)
openhuman-build/
```

Already included if you cloned from BROski-Obsidian-Brain repo.

---

## What Gets Synced

After OpenHuman starts and you connect integrations:

```
~/.openhuman/memory/
    ↓ (mounted as volume)
vault/00-Inbox/OpenHuman-Feed/
    ↓
github-issue-123.md
github-pr-45.md
slack-channel.md
gmail-thread.md
```

All auto-synced notes from GitHub, Slack, Gmail end up here, queryable via `mcp_bridge.py`.

---

> 🐶♾️ Build once, sync forever. No glibc pain, no system contamination. Just Docker.

