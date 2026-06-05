# OpenHuman via Docker — Quick Start

**TL;DR:** You're already Docker-native. No glibc pain. Just one command.

```bash
# 1. Set your vault path
export VAULT_PATH=$HOME/BROski-Obsidian-Brain-for-HyperFocus-z0ne

# 2. Start OpenHuman (UI + sync)
docker compose -f docker-compose.openhuman.yml up -d

# 3. Open browser
open http://127.0.0.1:3210

# 4. Connect integrations (GitHub OAuth, etc)
# 5. Wait 20 mins for first sync
```

---

## Why Docker?

| Issue | Binary | Docker |
|-------|--------|--------|
| glibc 2.38 required | ❌ Ubuntu 22.04 doesn't have it | ✅ Already included in image |
| System contamination | ⚠️ Modifies your system | ✅ Isolated container |
| Setup friction | 🔧 Symlinks, env files, PATH | ✅ One docker compose up |
| Already in your stack? | ❌ New dependency | ✅ docker-ce-cli exists |

---

## Setup (5 min)

### Step 1: Copy the compose file to your vault repo

```bash
cd BROski-Obsidian-Brain-for-HyperFocus-z0ne
# Files already in repo:
# - docker-compose.openhuman.yml
# - .env.openhuman (template)
```

### Step 2: Update .env.openhuman with your vault path

```bash
# Edit .env.openhuman and set:
VAULT_PATH=/path/to/your/BROski-Obsidian-Brain-for-HyperFocus-z0ne
```

**On Windows (PowerShell):**
```powershell
$env:VAULT_PATH = "H:\HYPERFOCUSZONE\HperCore\BROski-Obsidian-Brain-for-HyperFocus-z0ne"
```

**On Mac/Linux:**
```bash
export VAULT_PATH=$HOME/BROski-Obsidian-Brain-for-HyperFocus-z0ne
```

### Step 3: Start the container

**Option A — With UI (recommended for first-time setup)**

```bash
docker compose -f docker-compose.openhuman.yml up -d openhuman-ui
```

**Option B — Headless sync only (if you just want background syncing)**

```bash
docker compose -f docker-compose.openhuman.yml up -d openhuman-sync
```

**Option C — Both (UI + background sync)**

```bash
docker compose -f docker-compose.openhuman.yml up -d
```

### Step 4: Access the UI

```
http://127.0.0.1:3210
```

(Localhost only, for security)

### Step 5: Connect your integrations

In OpenHuman UI:
- Settings → Integrations
- Click **GitHub** → one-click OAuth
- (Optional) Connect Gmail, Slack, etc.

### Step 6: Wait for first sync

OpenHuman polls every 20 minutes by default. After the first sync:

```bash
# Check what synced
ls BROski-Obsidian-Brain-for-HyperFocus-z0ne/HYPERFOCUS_ZONE/00-Inbox/OpenHuman-Feed/

# You should see:
# - github-issue-*.md
# - github-pr-*.md
# - slack-*.md (if connected)
# - gmail-*.md (if connected)
```

---

## Managing the Container

### View logs

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

### Restart (e.g., after changing config)

```bash
docker compose -f docker-compose.openhuman.yml restart
```

### Check container health

```bash
docker ps | grep openhuman
```

Should show:
```
openhuman-ui     Up X minutes (healthy)
openhuman-sync   Up X minutes (healthy)
```

---

## Volumes Explained

### openhuman-config

Stores OpenHuman's persistent state:
- Credentials (encrypted)
- Integration settings
- Sync metadata

Lives in Docker volume (not your filesystem). Safe to delete and recreate.

### vault/00-Inbox/OpenHuman-Feed

Auto-synced notes from GitHub, Slack, Gmail.

**This is a real directory on your machine** — synced notes appear here instantly.

### vault (read-only)

OpenHuman can read your entire vault for context. Notes it writes go to `00-Inbox/OpenHuman-Feed/` only.

---

## Troubleshooting

### Q: Container won't start — "image not found"

**A:** Pull the image first:
```bash
docker pull ghcr.io/tinyhumansai/openhuman:latest
```

Then try again:
```bash
docker compose -f docker-compose.openhuman.yml up -d
```

### Q: Health check failing

**A:** Container might still be starting (30s startup period). Wait 1 min and check:
```bash
docker compose -f docker-compose.openhuman.yml ps
```

If still failing after 2 mins:
```bash
docker compose -f docker-compose.openhuman.yml logs openhuman-ui | tail -50
```

### Q: No notes syncing after 20 mins

**A:** Check:
1. Is OpenHuman running? `docker ps | grep openhuman`
2. Are integrations connected? (GitHub OAuth, etc.)
3. Check logs: `docker compose -f docker-compose.openhuman.yml logs openhuman-sync | tail -20`
4. Check sync folder: `ls HYPERFOCUS_ZONE/00-Inbox/OpenHuman-Feed/` (should have files)

### Q: Can't access UI at 127.0.0.1:3210

**A:** 
- Make sure container is running: `docker ps | grep openhuman-ui`
- Try: `curl -v http://127.0.0.1:3210`
- Check firewall isn't blocking port 3210

### Q: How do I manually trigger a sync?

**A:** 
```bash
# Restart the sync service (will sync immediately)
docker compose -f docker-compose.openhuman.yml restart openhuman-sync
```

Or from the UI: Settings → Manual Sync (if available)

---

## Integration with HyperCode Stack

If you're running `HyperCode-V2.4` docker stack:

```bash
# Start HyperCode stack
cd ../HyperCode-V2.4
docker compose up -d

# Start OpenHuman (uses same app-net network)
cd ../BROski-Obsidian-Brain-for-HyperFocus-z0ne
docker compose -f docker-compose.openhuman.yml up -d
```

Both stacks can talk to each other via Docker network.

**Future:** Wire `mcp_bridge.py` into the same network so hyper-brain can query OpenHuman directly.

---

## Next Steps

1. ✅ Start container: `docker compose -f docker-compose.openhuman.yml up -d`
2. ✅ Open UI: `http://127.0.0.1:3210`
3. ✅ Connect GitHub/Slack/Gmail
4. ✅ Wait 20 mins for sync
5. ✅ Check vault: `HYPERFOCUS_ZONE/00-Inbox/OpenHuman-Feed/`
6. ✅ Query via `mcp_bridge.py`: `await bridge.query_openhuman_feed(source="github")`

---

## Docker Cleanup (optional)

If things get messy:

```bash
# Stop and remove OpenHuman containers
docker compose -f docker-compose.openhuman.yml down

# Remove the config volume (fresh start)
docker volume rm broskiobsidianbrain_openhuman-config

# Start fresh
docker compose -f docker-compose.openhuman.yml up -d
```

---

> 🐶♾️ No glibc pain. Just Docker. One command. Your brain, unified.

