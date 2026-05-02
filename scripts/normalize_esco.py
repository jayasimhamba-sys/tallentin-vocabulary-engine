from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from common import dump_json, find_file, first, read_table, slug, unique_keep_order

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Folder containing extracted ESCO CSV files")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    folder = Path(args.input)
    if not folder.exists():
        raise SystemExit(f"Input folder not found: {folder}")

    occupations_file = find_file(folder, ["occupations", "occupations_en", "occupations_en.csv"])
    skills_file = find_file(folder, ["skills", "skills_en", "skills_en.csv"])
    relations_file = find_file(folder, ["occupationSkillRelations", "occupationSkillRelations_en", "occupationSkillRelations.csv"])

    if not occupations_file:
        raise SystemExit("Could not find ESCO occupations file. Put ESCO CSV files in raw_data/esco.")
    if not skills_file:
        raise SystemExit("Could not find ESCO skills file. Put ESCO CSV files in raw_data/esco.")

    occupations = {}
    for row in read_table(occupations_file):
        uri = first(row, ["conceptUri", "concept URI", "URI", "occupationUri"])
        pref = first(row, ["preferredLabel", "preferred label", "preferredTerm", "preferred term", "title"])
        desc = first(row, ["description", "Definition", "scopeNote"])
        alt = first(row, ["altLabels", "alternativeLabels", "nonPreferredTerms", "hiddenLabels"])
        if uri and pref:
            occupations[uri] = {
                "source": "ESCO",
                "esco_uri": uri,
                "occupation_title": pref,
                "definition": desc,
                "alternate_titles": [x.strip() for x in alt.split("\n") if x.strip()] if alt else [],
                "skills": []
            }

    skills_by_uri = {}
    for row in read_table(skills_file):
        uri = first(row, ["conceptUri", "concept URI", "URI", "skillUri"])
        pref = first(row, ["preferredLabel", "preferred label", "preferredTerm", "preferred term", "title"])
        desc = first(row, ["description", "Definition", "scopeNote"])
        alt = first(row, ["altLabels", "alternativeLabels", "nonPreferredTerms", "hiddenLabels"])
        if uri and pref:
            skills_by_uri[uri] = {
                "skill_name": pref,
                "definition": desc,
                "aliases": [x.strip() for x in alt.split("\n") if x.strip()] if alt else []
            }

    if relations_file:
        for row in read_table(relations_file):
            occ_uri = first(row, ["occupationUri", "occupation URI", "occupation", "conceptUri"])
            skill_uri = first(row, ["skillUri", "skill URI", "skill", "relatedSkill"])
            if not occ_uri or not skill_uri:
                # try generic URI columns
                vals = list(row.values())
                uris = [str(v) for v in vals if "http" in str(v).lower()]
                if len(uris) >= 2:
                    occ_uri, skill_uri = uris[0], uris[1]
            if occ_uri in occupations and skill_uri in skills_by_uri:
                occupations[occ_uri]["skills"].append(skills_by_uri[skill_uri]["skill_name"])

    normalized_terms = []
    aliases = []
    roles = []
    skills = []

    for uri, occ in occupations.items():
        term = slug(occ["occupation_title"])
        role_values = unique_keep_order([occ["occupation_title"]] + occ["alternate_titles"][:25])
        skill_values = unique_keep_order(occ["skills"][:250])
        normalized_terms.append({
            "source": "ESCO",
            "source_id": uri,
            "term": term,
            "label": occ["occupation_title"],
            "dimension": "role_title",
            "definition": occ["definition"],
            "aliases": unique_keep_order(occ["alternate_titles"][:50]),
            "roles": role_values,
            "skills": skill_values,
            "evidence": "open_taxonomy_supported",
            "confidence": 4,
            "country_scope": "EU_reference_global_mapping_candidate",
            "needs_country_mapping": True
        })
        for a in occ["alternate_titles"][:50]:
            aliases.append({"alias": a, "preferred_source_term": term, "source": "ESCO", "confidence": 4})
        for r in role_values:
            roles.append({"role_title": r, "mapped_source_term": term, "source": "ESCO", "confidence": 4})
        for s in skill_values:
            skills.append({"skill_name": s, "mapped_source_term": term, "source": "ESCO", "confidence": 4})

    result = {
        "source": "ESCO",
        "counts": {
            "occupations": len(normalized_terms),
            "aliases": len(aliases),
            "roles": len(roles),
            "skills": len(skills)
        },
        "terms": normalized_terms,
        "aliases": aliases,
        "roles": roles,
        "skills": skills
    }
    dump_json(Path(args.output), result)
    print(f"Wrote {args.output}")
    print(result["counts"])

if __name__ == "__main__":
    main()
