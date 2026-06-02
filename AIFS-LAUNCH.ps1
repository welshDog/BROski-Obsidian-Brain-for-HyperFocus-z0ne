# ==============================================================================
# AIFS-LAUNCH.ps1
# The Full Works — AIFS v1.0 Stack Launcher
# welshDog x Perplexity — June 2, 2026 — Llanelli, Wales
# ==============================================================================
# Run this from the repo root:
#   .\AIFS-LAUNCH.ps1
#
# What it does (in order):
#   1. Checks Python is installed
#   2. Installs all Python deps
#   3. Generates your Ed25519 signing key
#   4. Signs your AIFS folder contracts
#   5. Validates all contracts
#   6. Starts the Hub Dashboard (http://localhost:7331)
#   7. Starts the Registry Server (http://localhost:7332)
#   8. Starts the Watcher daemon
#   9. Prints the submission checklist
# ==============================================================================

$ErrorActionPreference = "Stop"

# ---- Colours ------------------------------------------------------------------
function Write-Hyper  { param($msg) Write-Host "💜 $msg" -ForegroundColor Magenta }
function Write-Win    { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Step   { param($msg) Write-Host ""`n🔹 $msg" -ForegroundColor Cyan }
function Write-Warn   { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Boom   { param($msg) Write-Host "💥 $msg" -ForegroundColor Red }

# ---- Banner -------------------------------------------------------------------
Clear-Host
Write-Host ""
Write-Host "  ██████╗  ██╗ ███████╗ ██████╗ " -ForegroundColor Magenta
Write-Host "  ██╔════╝ ██║ ██╔════╝ ██╔════╝ " -ForegroundColor Magenta
Write-Host "  █████╗  ██║ █████╗  ███████╗" -ForegroundColor Cyan
Write-Host "  ██╔══╝  ██║ ██╔══╝  ╚════██║" -ForegroundColor Cyan
Write-Host "  ██║     ██║ ███████╗██████╔╝" -ForegroundColor Blue
Write-Host "  ╚═╝     ╚═╝ ╚══════╝╚═════╝ " -ForegroundColor Blue
Write-Host ""
Write-Host "  AI File System v1.0 — The Full Works" -ForegroundColor White
Write-Host "  welshDog x Perplexity — Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧" -ForegroundColor DarkGray
Write-Host ""

# ---- 0. Root check ------------------------------------------------------------
Write-Step "Checking we're in the right place..."

$repoRoot = Get-Location
$aifsPath = Join-Path $repoRoot "AIFS"

if (-not (Test-Path $aifsPath)) {
    Write-Boom "Can't find the AIFS folder! Run this script from the repo root."
    Write-Warn "Expected: ...\BROski-Obsidian-Brain-for-HyperFocus-z0ne\"
    exit 1
}

Write-Win "Repo root confirmed: $repoRoot"

# ---- 1. Python check ----------------------------------------------------------
Write-Step "Checking Python..."

try {
    $pyVersion = python --version 2>&1
    Write-Win "Found: $pyVersion"
} catch {
    Write-Boom "Python not found! Install it from https://python.org"
    exit 1
}

# ---- 2. Install dependencies --------------------------------------------------
Write-Step "Installing Python dependencies..."

$deps = @("cryptography", "requests", "fastapi", "uvicorn", "watchdog", "mcp", "httpx")

foreach ($dep in $deps) {
    Write-Hyper "Installing $dep..."
    pip install $dep --quiet
}

Write-Win "All dependencies installed!"

# ---- 3. Key generation --------------------------------------------------------
Write-Step "Setting up Ed25519 signing key..."

$keyPath = Join-Path $HOME ".aifs"
$privateKey = Join-Path $keyPath "aifs_private.key"
$publicKey  = Join-Path $keyPath "aifs_public.key"

if (Test-Path $privateKey) {
    Write-Win "Signing key already exists at $privateKey — skipping keygen"
} else {
    Write-Hyper "Generating new Ed25519 key pair..."
    $author = Read-Host "Enter your name/handle for the key (e.g. welshDog)"
    python "$aifsPath\aifs_sign.py" keygen --author $author
    Write-Win "Key pair generated at $keyPath"
    Write-Warn "NEVER commit $privateKey — it's in .gitignore but double-check!"
}

# ---- 4. Sign contracts --------------------------------------------------------
Write-Step "Signing AIFS contracts in this repo..."

$foldersToSign = @(
    $repoRoot,
    (Join-Path $repoRoot "AIFS"),
    (Join-Path $repoRoot "AIFS\hub"),
    (Join-Path $repoRoot "AIFS\registry")
)

foreach ($folder in $foldersToSign) {
    $manifest = Join-Path $folder "manifest.toml"
    if (Test-Path $manifest) {
        Write-Hyper "Signing $folder..."
        python "$aifsPath\aifs_sign.py" sign $folder
        Write-Win "Signed: $folder"
    } else {
        Write-Warn "No manifest.toml in $folder — skipping"
    }
}

# ---- 5. Validate contracts ----------------------------------------------------
Write-Step "Validating all contracts..."

python "$aifsPath\aifs_validator.py" validate $repoRoot
Write-Win "Validation complete!"

# ---- 6. Launch Hub Dashboard --------------------------------------------------
Write-Step "Starting AIFS Hub Dashboard on http://localhost:7331 ..."

$hubScript = Join-Path $aifsPath "hub\aifs_hub_server.py"

if (Test-Path $hubScript) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", `
        "Write-Host '📊 AIFS Hub Dashboard' -ForegroundColor Cyan; python '$hubScript' --root '$repoRoot'" `
        -WindowStyle Normal
    Write-Win "Hub Dashboard launching — open http://localhost:7331"
} else {
    Write-Warn "Hub server not found at $hubScript — skipping"
}

Start-Sleep -Seconds 2

# ---- 7. Launch Registry Server ------------------------------------------------
Write-Step "Starting AIFS Registry Server on http://localhost:7332 ..."

$registryScript = Join-Path $aifsPath "registry\registry_server.py"

if (Test-Path $registryScript) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", `
        "Write-Host '🌍 AIFS Registry Server' -ForegroundColor Green; python '$registryScript' --port 7332" `
        -WindowStyle Normal
    Write-Win "Registry Server launching — open http://localhost:7332/docs"
} else {
    Write-Warn "Registry server not found at $registryScript — skipping"
}

Start-Sleep -Seconds 2

# ---- 8. Launch Watcher --------------------------------------------------------
Write-Step "Starting AIFS Watcher daemon (enforcement engine)..."

$watcherScript = Join-Path $aifsPath "aifs_watcher.py"

if (Test-Path $watcherScript) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", `
        "Write-Host '👁️  AIFS Watcher — enforcing contracts' -ForegroundColor Yellow; python '$watcherScript' watch '$repoRoot'" `
        -WindowStyle Normal
    Write-Win "Watcher launched — enforcement is LIVE"
} else {
    Write-Warn "Watcher not found at $watcherScript — skipping"
}

# ---- 9. MCP Config hint -------------------------------------------------------
Write-Step "MCP Config (add this to Claude Desktop / Cursor)..."

$mcpJson = @"
{
  "mcpServers": {
    "aifs": {
      "command": "python",
      "args": ["$($aifsPath.Replace('\','\\'))\\aifs_mcp_server.py", "--root", "$($repoRoot.ToString().Replace('\','\\'))"]
    }
  }
}
"@

Write-Host ""
Write-Host $mcpJson -ForegroundColor DarkGray
Write-Host ""

# ---- 10. Community submission reminder ----------------------------------------
Write-Step "Community Submission Checklist 🚀"

Write-Host ""
Write-Host "  🔴 1. Fork + PR → https://github.com/punkpeye/awesome-mcp-servers" -ForegroundColor White
Write-Host "  🔴 2. Blog post  → https://dev.to/new (copy AIFS/BLOG_POST.md)" -ForegroundColor White
Write-Host "  🟡 3. mcp.so     → https://mcp.so" -ForegroundColor White
Write-Host "  🟡 4. Hacker News → https://news.ycombinator.com/submit" -ForegroundColor White
Write-Host "  🟢 5. wong2 list → https://github.com/wong2/awesome-mcp-servers" -ForegroundColor White
Write-Host ""
Write-Host "  Full guide: AIFS/SUBMIT_TO_COMMUNITY.md" -ForegroundColor DarkGray
Write-Host ""

# ---- Done! --------------------------------------------------------------------
Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  💥 AIFS v1.0 IS RUNNING! Nice one BROski∞️" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  📊 Dashboard  → http://localhost:7331" -ForegroundColor Cyan
Write-Host "  🌍 Registry   → http://localhost:7332/docs" -ForegroundColor Green
Write-Host "  👁️  Watcher    → Running in background window" -ForegroundColor Yellow
Write-Host "  🔐 Contracts  → Signed + validated" -ForegroundColor Blue
Write-Host ""
Write-Host "  Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧 — June 2, 2026" -ForegroundColor DarkGray
Write-Host ""
