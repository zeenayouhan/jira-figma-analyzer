import json
import os
from pathlib import Path
from datetime import datetime

# Ensure project root import
if __name__ == "__main__":
    try:
        from jira_figma_analyzer import JiraFigmaAnalyzer
    except Exception as e:
        print(f"❌ Failed to import analyzer: {e}")
        raise SystemExit(1)

    kb_path = Path("knowledge_base") / "figma_knowledge.json"
    if not kb_path.exists():
        print(f"❌ Knowledge file not found: {kb_path}")
        raise SystemExit(0)

    with open(kb_path, "r", encoding="utf-8") as f:
        try:
            kb = json.load(f)
        except Exception as e:
            print(f"❌ Failed to read knowledge file: {e}")
            raise SystemExit(1)

    print(f"🔧 Refreshing {len(kb)} Figma knowledge entries...")

    analyzer = JiraFigmaAnalyzer()
    updated = 0
    fixed_urls = 0
    failed = 0

    for entry in kb:
        url = (entry.get("figma_url") or "").strip()
        if not url:
            continue
        if url.startswith("@"):
            url = url.lstrip("@").strip()
            entry["figma_url"] = url
            fixed_urls += 1

        try:
            res = analyzer._analyze_figma_designs([url])
            if not res:
                print(f"⚠️ No result for: {url}")
                failed += 1
                continue
            r = res[0]
            entry["figma_analysis"] = {
                "total_screens": len(r.get("screens", [])),
                "total_components": len(r.get("ui_components", [])),
                "complexity_score": r.get("design_complexity", 0),
                "user_flows": r.get("user_flows", []),
                "screens": r.get("screens", []),
                "components": r.get("ui_components", []),
            }
            updated += 1
            print(f"✅ {entry.get('feature_name','(Unnamed)')}: screens={entry['figma_analysis']['total_screens']}, components={entry['figma_analysis']['total_components']}")
        except Exception as e:
            failed += 1
            print(f"❌ Error analyzing {url}: {e}")

    # Save
    try:
        with open(kb_path, "w", encoding="utf-8") as f:
            json.dump(kb, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Failed to write knowledge file: {e}")
        raise SystemExit(1)

    # Totals
    total_features = len(kb)
    total_screens = sum(e.get("figma_analysis", {}).get("total_screens", 0) for e in kb)
    total_components = sum(e.get("figma_analysis", {}).get("total_components", 0) for e in kb)

    print("\n📊 Refresh Summary")
    print(f"• Entries: {total_features}")
    print(f"• Screens: {total_screens}")
    print(f"• Components: {total_components}")
    print(f"• Updated: {updated} • URLs fixed: {fixed_urls} • Failed: {failed}")
    print("✅ Done. Reload the Streamlit page to see updated totals.") 