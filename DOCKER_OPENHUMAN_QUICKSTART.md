# OpenHuman via Docker — Quick Start (Build from Source)

**TL;DR:** OpenHuman image isn't public yet. We build it locally (5-10 min first run).

```bash
# 1. Clone source once
git clone https://github.com/tinyhumansai/openhuman.git openhuman-build

# 2. Set vault path
export VAULT_PATH=$HOME/BROski-Obsidian-Brain-for-HyperFocus-z0ne

# 3. Start (builds image on first run)
docker compose -f docker-compose.openhuman.yml up -d

# 4. Open UI
open http://127.0.0.1:3210
```

**That's it.** No glibc. No system changes. Just Docker + source build.

---

## Why Build from Source?

| Method | Status | Friction |
|--------|--------|----------|
| Pre-built public image | ❌ Not available yet | — |
| Docker build from source | ✅ Available now | 5-10 min first run, instant after |
| Binary install | ❌ glibc 2.38+ required (Ubuntu 22.04 only has 2.35) | System blocker |

Docker build is the **only friction-free path today**.

---

## Prerequisites

- ✅ Docker installed (you have it)
- ✅ Git installed (you have it)
- ✅ ~3GB disk space (for build cache)
- ✅ 10 mins for first build

---

## Step-by-Step Setup

### Step 1: Clone OpenHuman source (one time)

```bash
cd BROski-Obsidian-Brain-for-HyperFocus-z0ne
git clone https://github.com/tinyhumansai/openhuman.git openhuman-build
```

Expected output:
```
Cloning into 'openhuman-build'...
remote: Enumerating objects: 2000+, done.
...
Receiving objects: 100% (2000/2000), done.
```

### Step 2: Set vault path

**macOS/Linux:**
```bash
export VAULT_PATH=$HOME/BROski-Obsidian-Brain-for-HyperFocus-z0ne
```

**Windows (PowerShell):**
```powershell
$env:VAULT_PATH = "C:\path\to\BROski-Obsidian-Brain-for-HyperFocus-z0ne"
```

### Step 3: Update .env.openhuman (optional)

If you want to customize beyond defaults:
```bash
# Edit .env.openhuman
VAULT_PATH=/your/path
OPENHUMAN_SYNC_INTERVAL=1200  # 20 mins
```

### Step 4: Start containers (builds image on first run)

```bash
docker compose -f docker-compose.openhuman.yml up -d
```

**First run output (5-10 min):**
```
Building openhuman:local
Step 1/XX : FROM rust:latest
...
Successfully built openhuman:local
Creating openhuman-ui ... done
Creating openhuman-sync ... done
```

**Subsequent runs (instant):**
```
Container openhuman-ui is already running
Container openhuman-sync is already running
```

### Step 5: Access the UI

```
http://127.0.0.1:3210
```

(Localhost only, secure)

### Step 6: Connect integrations

In OpenHuman UI:
- **Settings** → **Integrations**
- Click **GitHub** → one-click OAuth
- (Optional) Connect Slack, Gmail, etc.

### Step 7: Wait for first sync

OpenHuman polls every 20 mins by default.

After sync completes:
```bash
ls HYPERFOCUS_ZONE/00-Inbox/OpenHuman-Feed/
# Should show:
# github-issue-123.md
# github-pr-45.md
# (and slack-*.md, gmail-*.md if connected)
```

---

## Managing Containers

### View logs (useful for debugging)

```bash
# All services
docker compose -f docker-compose.openhuman.yml logs -f

# Just UI
docker compose -f docker-compose.openhuman.yml logs -f openhuman-ui

# Just sync
docker compose -f docker-compose.openhuman.yml logs -f openhuman-sync
```

### Stop OpenHuman

```bash
docker compose -f docker-compose.openhuman.yml down
```

### Restart

```bash
docker compose -f docker-compose.openhuman.yml restart
```

### Check health

```bash
docker ps | grep openhuman
```

Should show:
```
openhuman-ui     Up 5 minutes (healthy)
openhuman-sync   Up 5 minutes (healthy)
```

### Rebuild from latest source

```bash
# Update source
cd openhuman-build && git pull origin main && cd ..

# Remove old image
docker rmi openhuman:local

# Rebuild and start
docker compose -f docker-compose.openhuman.yml up -d --build
```

---

## Volumes Explained

### openhuman-config

Docker volume storing OpenHuman state:
- Encrypted credentials
- Integration settings
- Sync metadata

Safe to delete (starts fresh):
```bash
docker volume rm broskiobsidianbrain_openhuman-config
docker compose -f docker-compose.openhuman.yml up -d
```

### vault/00-Inbox/OpenHuman-Feed

**Real directory on your machine** — synced notes appear here immediately.

Tracked by Obsidian. Queryable by `mcp_bridge.py`.

### vault (read-only)

OpenHuman can read your entire vault for context (optional). Writes only go to `OpenHuman-Feed/`.

---

## Troubleshooting

### Q: Clone failed — "fatal: destination path 'openhuman-build' already exists"

**A:** You already cloned it. That's fine. Skip Step 1 and go to Step 2.

### Q: Build timeout (>15 min)

**A:** Rust compilation is slow. Either:
- Wait longer
- Increase Docker resources: Settings → Resources → CPU/RAM
- Check internet speed (large source download)

### Q: "openhuman-build/Dockerfile not found"

**A:** Clone failed. Try again:
```bash
rm -rf openhuman-build
git clone https://github.com/tinyhumansai/openhuman.git openhuman-build
docker compose -f docker-compose.openhuman.yml up -d
```

### Q: Container won't start — "exit code 127"

**A:** Build might have failed silently. Check:
```bash
docker compose -f docker-compose.openhuman.yml logs openhuman-ui
```

If build errors shown, try:
```bash
docker rmi openhuman:local
docker compose -f docker-compose.openhuman.yml up -d --build
```

### Q: UI is slow or won't load

**A:** Might still be starting. Wait 30 seconds, then:
```bash
curl -v http://127.0.0.1:3210
```

If 404, container may have crashed:
```bash
docker logs openhuman-ui
```

### Q: No notes syncing after 30 mins

**A:** Check:
1. Integrations connected? (GitHub OAuth, etc.)
2. Logs: `docker logs openhuman-sync | tail -20`
3. Folder: `ls HYPERFOCUS_ZONE/00-Inbox/OpenHuman-Feed/`
4. Permissions: folder writable by Docker user

### Q: How much disk space does build take?

**A:** ~3GB for Docker build cache + image. Safe to prune:
```bash
docker system prune -a
# Frees up all unused images/containers
# Will rebuild next time
```

---

## Integration with HyperCode Stack

If running `HyperCode-V2.4` docker-compose:

```bash
# Start HyperCode stack
cd ../HyperCode-V2.4
docker compose up -d

# Start OpenHuman (shares docker network)
cd ../BROski-Obsidian-Brain-for-HyperFocus-z0ne
docker compose -f docker-compose.openhuman.yml up -d
```

Both stacks talk via Docker network.

**Future:** Wire hyper-brain to query OpenHuman directly for unified agent context.

---

## .gitignore

The `openhuman-build/` folder is large (~200MB+). Don't commit it:

```bash
# .gitignore
openhuman-build/
```

Already included in this repo. Safe.

---

## Next Steps

1. ✅ Clone source: `git clone https://...`
2. ✅ Start: `docker compose -f docker-compose.openhuman.yml up -d`
3. ✅ Open UI: `http://127.0.0.1:3210`
4. ✅ Connect GitHub/Slack/Gmail
5. ✅ Wait 20 mins for first sync
6. ✅ Check vault: `ls HYPERFOCUS_ZONE/00-Inbox/OpenHuman-Feed/`
7. ✅ Query via `mcp_bridge.py`: `await bridge.query_openhuman_feed(source="github")`

---

> 🐶♾️ Build once, sync forever. No glibc, no system pain. Just Docker doing what it does.

