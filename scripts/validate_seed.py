from pathlib import Path
from common import load_json

base = Path(__file__).resolve().parents[1]
required = [
    "data/vocab_terms.json",
    "data/aliases.json",
    "data/role_titles.json",
    "data/skills.json",
    "data/relationships.json",
    "data/source_register.json",
    "data/blocked_terms.json",
]
errors = []
for rel in required:
    p = base / rel
    if not p.exists():
        errors.append(f"Missing {rel}")
    else:
        try:
            data = load_json(p)
            if not isinstance(data, list):
                errors.append(f"{rel} is not a JSON array")
        except Exception as e:
            errors.append(f"{rel} cannot be read: {e}")

terms = load_json(base / "data/vocab_terms.json") if (base / "data/vocab_terms.json").exists() else []
term_keys = set()
for t in terms:
    for f in ["term", "label", "dimension", "definition", "status", "evidence", "confidence"]:
        if f not in t:
            errors.append(f"Term missing field {f}: {t.get('term')}")
    k = t.get("term")
    if k in term_keys:
        errors.append(f"Duplicate preferred term: {k}")
    term_keys.add(k)

if errors:
    print("VALIDATION FAILED")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("Seed validation passed.")
print(f"Terms: {len(terms)}")
