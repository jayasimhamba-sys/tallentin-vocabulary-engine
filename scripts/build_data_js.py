from __future__ import annotations

import argparse
from pathlib import Path
from common import dump_json, load_json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Merged vocab terms JSON")
    ap.add_argument("--output", required=True, help="data.js output")
    args = ap.parse_args()

    terms = load_json(Path(args.input))
    aliases = []
    roles = []
    skills = []
    relationships = []
    for t in terms:
        for a in t.get("aliases", []):
            aliases.append({"alias": a, "preferred_term": t["term"], "alias_type": "alias", "country_scope": "all", "source": t.get("evidence"), "confidence": t.get("confidence", 3)})
            relationships.append({"from_term": a, "relationship": "alias_of", "to_term": t["term"], "reason": "Normalize alias before matching.", "confidence": t.get("confidence", 3)})
        for r in t.get("roles", []):
            roles.append({"role_title": r, "mapped_term": t["term"], "mapped_dimension": t.get("dimension"), "role_family": t.get("parent"), "country_scope": "Canada/India/USA", "source": t.get("evidence"), "confidence": t.get("confidence", 3)})
        for cluster, vals in t.get("skillClusters", {}).items():
            for s in vals:
                skills.append({"skill_name": s, "skill_cluster": cluster, "mapped_term": t["term"], "mapped_dimension": t.get("dimension"), "skill_type": "skill_or_keyword", "country_scope": "all", "evidence_status": t.get("evidence"), "confidence": t.get("confidence", 3)})
        for d in t.get("doNotConfuse", []):
            relationships.append({"from_term": t["term"], "relationship": "do_not_confuse_with", "to_term": d, "reason": "Prevent false-positive routing.", "confidence": t.get("confidence", 3)})

    package = {
        "vocab_terms.json": terms,
        "aliases.json": aliases,
        "role_titles.json": roles,
        "skills.json": skills,
        "relationships.json": relationships,
        "source_register.json": load_json(Path("data/source_register.json")) if Path("data/source_register.json").exists() else [],
        "blocked_terms.json": load_json(Path("data/blocked_terms.json")) if Path("data/blocked_terms.json").exists() else [],
        "country_notes.json": load_json(Path("data/country_notes.json")) if Path("data/country_notes.json").exists() else [],
        "signal_scope_rules.json": load_json(Path("data/signal_scope_rules.json")) if Path("data/signal_scope_rules.json").exists() else []
    }
    Path(args.output).write_text("window.TALLENTIN_DATA = " + __import__("json").dumps(package, ensure_ascii=False) + ";", encoding="utf-8")
    print(f"Wrote {args.output}")
    print({"terms": len(terms), "aliases": len(aliases), "roles": len(roles), "skills": len(skills), "relationships": len(relationships)})

if __name__ == "__main__":
    main()
