from __future__ import annotations

import argparse
from pathlib import Path
from common import load_json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()
    terms = load_json(Path(args.input))
    errors = []
    seen = set()
    for t in terms:
        for field in ["term", "label", "dimension", "definition", "status", "evidence", "confidence"]:
            if field not in t or t[field] in [None, ""]:
                errors.append(f"Missing {field}: {t.get('term')}")
        if t.get("term") in seen:
            errors.append(f"Duplicate term: {t.get('term')}")
        seen.add(t.get("term"))
        if t.get("bias") == "blocked" and t.get("status") in ["verified", "mature"]:
            errors.append(f"Blocked term cannot be verified: {t.get('term')}")
    if errors:
        print("VALIDATION FAILED")
        for e in errors[:100]:
            print("-", e)
        raise SystemExit(1)
    print("Generated data validation passed.")
    print(f"Terms: {len(terms)}")

if __name__ == "__main__":
    main()
