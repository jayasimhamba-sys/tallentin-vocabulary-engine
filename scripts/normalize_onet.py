from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from common import dump_json, find_file, first, read_table, slug, unique_keep_order

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Folder containing extracted O*NET text or CSV files")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    folder = Path(args.input)
    if not folder.exists():
        raise SystemExit(f"Input folder not found: {folder}")

    occupation_file = find_file(folder, ["Occupation Data", "Occupation Data.txt", "Occupation Data.csv"])
    alternate_file = find_file(folder, ["Alternate Titles", "Alternate Titles.txt", "Alternate Titles.csv"])
    skills_file = find_file(folder, ["Skills", "Skills.txt", "Skills.csv"])
    tasks_file = find_file(folder, ["Task Statements", "Task Statements.txt", "Task Statements.csv"])
    tech_file = find_file(folder, ["Technology Skills", "Technology Skills.txt", "Technology Skills.csv"])
    work_activities_file = find_file(folder, ["Work Activities", "Work Activities.txt", "Work Activities.csv"])
    knowledge_file = find_file(folder, ["Knowledge", "Knowledge.txt", "Knowledge.csv"])

    if not occupation_file:
        raise SystemExit("Could not find O*NET Occupation Data file. Put extracted O*NET files in raw_data/onet.")

    occupations = {}
    for row in read_table(occupation_file):
        code = first(row, ["O*NET-SOC Code", "O*NET_SOC Code", "Code"])
        title = first(row, ["Title", "Occupation Title"])
        desc = first(row, ["Description", "Definition"])
        if code and title:
            occupations[code] = {
                "source": "O*NET",
                "onet_code": code,
                "occupation_title": title,
                "definition": desc,
                "alternate_titles": [],
                "reported_titles": [],
                "tasks": [],
                "skills": [],
                "knowledge": [],
                "work_activities": [],
                "technology_skills": []
            }

    def add_by_code(path, field, value_cols, code_cols=["O*NET-SOC Code", "O*NET_SOC Code", "Code"]):
        if not path:
            return
        for row in read_table(path):
            code = first(row, code_cols)
            if code not in occupations:
                continue
            val = first(row, value_cols)
            if val:
                occupations[code][field].append(val)

    add_by_code(alternate_file, "alternate_titles", ["Alternate Title", "Alternate Title Short", "Title"])
    add_by_code(tasks_file, "tasks", ["Task", "Task Statement"])
    add_by_code(tech_file, "technology_skills", ["Commodity Title", "Example", "Hot Technology", "Technology Skill", "Technology"])
    add_by_code(work_activities_file, "work_activities", ["Element Name", "Work Activity", "Data Value"])
    add_by_code(knowledge_file, "knowledge", ["Element Name", "Knowledge"])
    add_by_code(skills_file, "skills", ["Element Name", "Skill"])

    normalized_terms = []
    aliases = []
    skills = []
    roles = []

    for code, occ in occupations.items():
        term = slug(occ["occupation_title"])
        skill_values = unique_keep_order(occ["skills"] + occ["knowledge"] + occ["work_activities"] + occ["technology_skills"])
        role_values = unique_keep_order([occ["occupation_title"]] + occ["alternate_titles"][:25])
        normalized_terms.append({
            "source": "O*NET",
            "source_id": code,
            "term": term,
            "label": occ["occupation_title"],
            "dimension": "role_title",
            "definition": occ["definition"],
            "aliases": unique_keep_order(occ["alternate_titles"][:50]),
            "roles": role_values,
            "skills": skill_values[:200],
            "tasks": unique_keep_order(occ["tasks"][:100]),
            "evidence": "open_taxonomy_supported",
            "confidence": 4,
            "country_scope": "USA_primary_global_reference",
            "needs_country_mapping": True
        })
        for a in occ["alternate_titles"][:50]:
            aliases.append({"alias": a, "preferred_source_term": term, "source": "O*NET", "confidence": 4})
        for r in role_values:
            roles.append({"role_title": r, "mapped_source_term": term, "source": "O*NET", "confidence": 4})
        for s in skill_values:
            skills.append({"skill_name": s, "mapped_source_term": term, "source": "O*NET", "confidence": 4})

    result = {
        "source": "O*NET",
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
