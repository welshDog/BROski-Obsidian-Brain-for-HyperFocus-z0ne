#!/usr/bin/env python3
"""
github_to_obsidian.py
Pulls open issues from all 4 welshDog repos → Obsidian vault.
Run every 4hrs via Docker cron or manually.
BROski♾️
"""

import requests
import os
from datetime import datetime

GITHUB_TOKEN = os.environ.get("GITHUB_PAT", "")
VAULT_PATH = os.environ.get(
    "OBSIDIAN_VAULT_PATH",
    r"C:\Users\Lyndz\Obsidian\HYPERFOCUS_ZONE\00-Inbox\GitHub"
)
REPOS = [
    "welshDog/HyperCode-V2.4",
    "welshDog/HyperAgent-SDK",
    "welshDog/BROskiPets-LLM-dNFT",
    "welshDog/Hyper-Vibe-Coding-Course"
]

if not GITHUB_TOKEN:
    print("❌ GITHUB_PAT not set. Export it first.")
    exit(1)

headers = {"Authorization": f"token {GITHUB_TOKEN}"}
os.makedirs(VAULT_PATH, exist_ok=True)

for repo in REPOS:
    url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=50"
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        print(f"⚠️  {repo}: HTTP {resp.status_code}")
        continue

    issues = [i for i in resp.json() if "pull_request" not in i]
    repo_name = repo.split("/")[1]

    lines = [
        f"# 🐛 {repo_name} — Open Issues\n",
        f"*Synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
        f"*Total: {len(issues)} open issues*\n",
        "---\n"
    ]

    if not issues:
        lines.append("✅ No open issues. BROski clean!\n")
    else:
        for issue in issues:
            assignee = issue["assignee"]["login"] if issue.get("assignee") else "unassigned"
            labels = ", ".join([l["name"] for l in issue.get("labels", [])]) or "none"
            lines.append(f"- [ ] #{issue['number']} — {issue['title']}")
            lines.append(f"  - 🔗 {issue['html_url']}")
            lines.append(f"  - 👤 {assignee} | 🏷️ {labels}")
            lines.append("")

    out_file = os.path.join(VAULT_PATH, f"{repo_name}.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Synced: {repo_name} ({len(issues)} issues)")

print("\n🧠 GitHub → Obsidian DONE BROski♾️!")
