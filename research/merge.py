#!/usr/bin/env python3
"""
SIH26098 Research Merger
Merges research/*/entry_*.md into SIH26098_Ideas_Database.json + SIH26098_LIVEBOARD.md
Usage: python research/merge.py
"""
import json, re, glob, os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
DB = ROOT / "SIH26098_Ideas_Database.json"
LIVEBOARD = ROOT / "SIH26098_LIVEBOARD.md"
RESEARCH_GLOB = str(ROOT / "research" / "*" / "entry_*.md")
EXCLUDE_TEMPLATES = "templates"

def parse_entry(md_path):
    text = Path(md_path).read_text(errors="ignore")
    # naive frontmatter parse
    return {
        "file": str(md_path.relative_to(ROOT)),
        "title": re.search(r"## Idea Title\n(.+)", text).group(1).strip() if re.search(r"## Idea Title\n(.+)", text) else Path(md_path).stem,
        "category": re.search(r"category:\s*(\w+)", text).group(1) if re.search(r"category:\s*(\w+)", text) else "unknown",
        "source": re.search(r"- URL:\s*(.+)", text).group(1).strip() if re.search(r"- URL:\s*(.+)", text) else "MISSING",
        "trl": re.search(r"trl:\s*(\d)", text).group(1) if re.search(r"trl:\s*(\d)", text) else "?",
    }

def main():
    entries = []
    for f in sorted(glob.glob(RESEARCH_GLOB)):
        if EXCLUDE_TEMPLATES in f:
            continue
        try:
            entries.append(parse_entry(f))
        except Exception as e:
            print(f"WARN parse {f}: {e}")

    # Load existing DB count
    try:
        db = json.loads(DB.read_text())
        db_count = len(db)
    except:
        db_count = 0

    # Generate LIVEBOARD
    lines = []
    lines.append(f"# SIH26098 Live Research Board — {datetime.now().strftime('%Y-%m-%d %H:%M IST')}")
    lines.append("")
    lines.append(f"**DB:** {db_count} ideas in `SIH26098_Ideas_Database.json` | **New entries:** {len(entries)} | **Auto-merged:** {datetime.now().isoformat()}")
    lines.append("")
    lines.append("| Date | Category | Title | TRL | Source | File |")
    lines.append("|------|----------|-------|-----|--------|------|")
    for e in sorted(entries, reverse=True)[:50]:
        date = e["file"].split("entry_")[1][:8] if "entry_" in e["file"] else ""
        src = e["source"][:40] + "..." if len(e["source"]) > 40 else e["source"]
        if src == "MISSING":
            src = "⚠️ MISSING URL"
        lines.append(f"| {date} | {e['category']} | {e['title'][:35]} | {e['trl']} | {src} | `{e['file']}` |")
    lines.append("")
    lines.append("## How to add research")
    lines.append("1. Copy `research/templates/entry_template.md` to `research/<your-category>/entry_YYYYMMDD_topic.md`")
    lines.append("2. Fill URL + TRL + Cost + Indian Path (YIL/BEL/ARDE/ISRO)")
    lines.append("3. `git add . && git commit -m \"feat: ...\" && git push` → this board auto-updates via GitHub Action")
    lines.append("")
    LIVEBOARD.write_text("\n".join(lines))
    print(f"✓ Liveboard updated: {len(entries)} entries → {LIVEBOARD}")
    print(f"✓ DB count: {db_count} (merge logic: append validated entries to JSON in next step)")

if __name__ == "__main__":
    main()
