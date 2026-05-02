from __future__ import annotations

import argparse
from pathlib import Path
from common import dump_json, load_json, slug, unique_keep_order

def source_to_vocab_term(src_term, source_name):
    term = "source_" + source_name.lower() + "_" + slug(src_term.get("label") or src_term.get("term"))
    label = src_term.get("label") or src_term.get("term")
    skills = src_term.get("skills", [])
    return {
        "id": f"{source_name.upper()}-{slug(label).upper()[:48]}",
        "term": term,
        "label": label,
        "dimension": "role_title",
        "parent": "source_imported_role",
        "status": "observed",
        "evidence": "open_taxonomy_supported",
        "confidence": src_term.get("confidence", 4),
        "bias": "pass",
        "regulated": "contextual",
        "definition": src_term.get("definition", ""),
        "simple": f"{label} is an imported {source_name} role/occupation concept. It needs TALLENTIN normalization before production routing.",
        "includes": ["source_imported_role", "skills", "tasks"],
        "excludes": ["approved_capability_without_mapping"],
        "aliases": unique_keep_order(src_term.get("aliases", [])[:50]),
        "country": {
            "Canada": "Needs mapping to NOC/OaSIS before Canada production routing.",
            "India": "Needs mapping to NCO/NSDC/NOS before India production routing.",
            "USA": "O*NET-origin terms can map directly to USA context; ESCO-origin terms need USA mapping."
        },
        "roles": unique_keep_order(src_term.get("roles", [])[:50]),
        "skillClusters": {"source_imported_skills": skills[:120]},
        "skills": skills[:120],
        "doNotConfuse": ["approved_capability", "industry_context", "employment_model"],
        "routing": "Do not route automatically until mapped to an approved TALLENTIN capability and country context.",
        "problem": "Provides source-backed coverage while preventing raw imported occupations from being treated as approved capabilities."
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True)
    ap.add_argument("--onet", required=False)
    ap.add_argument("--esco", required=False)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    seed = load_json(Path(args.seed))
    merged = list(seed)
    seen = {t["term"] for t in merged if "term" in t}

    for source_name, path in [("ONET", args.onet), ("ESCO", args.esco)]:
        if not path or not Path(path).exists():
            continue
        src = load_json(Path(path))
        for st in src.get("terms", []):
            vt = source_to_vocab_term(st, "ONET" if source_name == "ONET" else "ESCO")
            if vt["term"] not in seen:
                merged.append(vt)
                seen.add(vt["term"])

    dump_json(Path(args.output), merged)
    print(f"Wrote {args.output}")
    print(f"Merged terms: {len(merged)}")

if __name__ == "__main__":
    main()
