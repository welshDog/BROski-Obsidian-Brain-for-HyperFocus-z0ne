# xp-hooks — versioned mirror

**These are backup copies, not the live path.**

The canonical, executed copies live at the ecosystem root:

```
H:\HYPERFOCUSZONE\HperCore\scripts\git_xp_post_commit.py
H:\HYPERFOCUSZONE\HperCore\scripts\install_xp_hooks.sh
```

That root is **not a git repository**, so the files there are unversioned. Every
repo's `.git/hooks/post-commit` calls `git_xp_post_commit.py` by that absolute
path (see [[dev-xp-git-commit-hooks]] memory). If the root copy is lost, every
`install_xp_hooks.sh` run and every existing hook regresses — including the
2026-09-03 cp1252 / emoji class-fix (`encoding="utf-8", errors="replace"` on the
`subprocess.run` calls + `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` in the installer).

## Restore

```
cp scripts/xp-hooks/git_xp_post_commit.py  H:/HYPERFOCUSZONE/HperCore/scripts/
cp scripts/xp-hooks/install_xp_hooks.sh    H:/HYPERFOCUSZONE/HperCore/scripts/
chmod +x H:/HYPERFOCUSZONE/HperCore/scripts/git_xp_post_commit.py \
         H:/HYPERFOCUSZONE/HperCore/scripts/install_xp_hooks.sh
```

## Keeping the mirror current

When you edit either root script, re-copy it here and commit. Quick parity check:

```
for f in git_xp_post_commit.py install_xp_hooks.sh; do
  diff -q "H:/HYPERFOCUSZONE/HperCore/scripts/$f" "scripts/xp-hooks/$f" \
    && echo "$f: in sync" || echo "$f: DRIFT — re-copy"
done
```

Last synced: 2026-09-03 (md5 parity verified at copy time).
