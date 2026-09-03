#!/usr/bin/env bash
# HyperFocus Z0ne -- install the dev-action XP post-commit hook into every
# sibling repo under HperCore. Idempotent: re-runnable, chains onto an existing
# post-commit hook instead of clobbering it. HyperCode-V2.4 is skipped (it has
# its own richer hook: scripts/pets/git_post_commit.py).
#
# Run:  bash scripts/install_xp_hooks.sh
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PUBLISHER="H:/HYPERFOCUSZONE/HperCore/scripts/git_xp_post_commit.py"
# PYTHONUTF8=1 forces utf-8 for subprocess pipe decoding regardless of the
# Windows locale (cp1252) -- otherwise a commit diff with an emoji / arrow /
# accented char crashes the hook's reader thread. Belt-and-braces with the
# encoding= args pinned inside git_xp_post_commit.py itself.
CALL="PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python \"$PUBLISHER\" || exit 0"
MARKER="git_xp_post_commit.py"
SKIP="HyperCode-V2.4"

installed=0; chained=0; skipped=0
for d in "$ROOT"/*/; do
  d="${d%/}"; name="$(basename "$d")"
  [ -d "$d/.git" ] || continue
  if [ "$name" = "$SKIP" ]; then echo "skip   $name (own hook)"; skipped=$((skipped+1)); continue; fi

  hook="$d/.git/hooks/post-commit"
  if [ ! -f "$hook" ]; then
    printf '#!/usr/bin/env sh\n# HyperFocus Z0ne dev-action XP (install_xp_hooks.sh)\n%s\n' "$CALL" > "$hook"
    chmod +x "$hook"
    echo "install $name"; installed=$((installed+1))
  elif grep -q "$MARKER" "$hook"; then
    echo "ok     $name (already wired)"
  else
    printf '\n# HyperFocus Z0ne dev-action XP (install_xp_hooks.sh)\n%s\n' "$CALL" >> "$hook"
    chmod +x "$hook"
    echo "chain  $name (appended to existing hook)"; chained=$((chained+1))
  fi
done
echo "--- installed=$installed chained=$chained skipped=$skipped ---"
