import json
from pathlib import Path

kb_path = Path('knowledge_base') / 'figma_knowledge.json'
if not kb_path.exists():
    print(f"❌ Knowledge file not found: {kb_path}")
    raise SystemExit(0)

kb = json.load(open(kb_path, 'r', encoding='utf-8'))
print(f"📚 Loaded entries: {len(kb)}")

seen_ids = set()
clean = []
removed = 0
for e in kb:
    url = (e.get('figma_url') or '').strip()
    if not url or url.lower() in {'dd', 'na', 'n/a'}:
        removed += 1
        continue
    eid = e.get('id') or url
    if eid in seen_ids:
        removed += 1
        continue
    seen_ids.add(eid)
    clean.append(e)

json.dump(clean, open(kb_path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print(f"✅ Deduped: {len(kb)} -> {len(clean)} (removed {removed})") 