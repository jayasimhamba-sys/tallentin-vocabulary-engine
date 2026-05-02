#!/usr/bin/env python3
"""Normalize ESCO API JSON output into TALLENTIN ingestion JSON."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def text_value(v: Any, lang: str = "en") -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, dict):
        # ESCO often returns language maps or typed labels
        for key in [lang, "en", "literal", "value", "label"]:
            if key in v:
                return text_value(v[key], lang)
        # fallback first scalar/list value
        for val in v.values():
            out = text_value(val, lang)
            if out:
                return out
    if isinstance(v, list):
        vals = [text_value(x, lang) for x in v]
        vals = [x for x in vals if x]
        return "; ".join(vals)
    return str(v).strip()


def list_values(v: Any, lang: str = "en") -> List[str]:
    if v is None:
        return []
    if isinstance(v, list):
        out = []
        for item in v:
            txt = text_value(item, lang)
            if txt:
                out.extend([x.strip() for x in re.split(r"[;\n]", txt) if x.strip()])
        return list(dict.fromkeys(out))
    txt = text_value(v, lang)
    return [x.strip() for x in re.split(r"[;\n]", txt) if x.strip()]


def field(row: Dict[str, Any], names: Iterable[str], lang: str = "en") -> str:
    lookup = {slug(k): k for k in row.keys()}
    for n in names:
        k = lookup.get(slug(n))
        if k is not None:
            v = text_value(row.get(k), lang)
            if v:
                return v
    return ""


def field_list(row: Dict[str, Any], names: Iterable[str], lang: str = "en") -> List[str]:
    lookup = {slug(k): k for k in row.keys()}
    for n in names:
        k = lookup.get(slug(n))
        if k is not None:
            vals = list_values(row.get(k), lang)
            if vals:
                return vals
    return []


def normalize_occupation(row: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
    uri = field(row, ["uri", "conceptUri", "concept_uri", "id"], lang) or str(row.get("uri", ""))
    label = field(row, ["preferredLabel", "title", "label"], lang) or uri.rsplit("/", 1)[-1]
    description = field(row, ["description", "definition", "scopeNote"], lang)
    aliases = field_list(row, ["altLabels", "alternativeLabels", "hiddenLabels", "nonPreferredTerms"], lang)
    return {
        "source": "ESCO_API",
        "source_id": uri,
        "term": "source_esco_" + slug(label),
        "label": label,
        "dimension": "role_title",
        "definition": description,
        "aliases": aliases[:50],
        "roles": [label] + aliases[:25],
        "skills": [],
        "evidence": "open_taxonomy_supported",
        "confidence": 4,
        "country_scope": "EU_reference_global_mapping_candidate",
        "needs_country_mapping": True,
    }


def normalize_skill(row: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
    uri = field(row, ["uri", "conceptUri", "concept_uri", "id"], lang) or str(row.get("uri", ""))
    label = field(row, ["preferredLabel", "title", "label"], lang) or uri.rsplit("/", 1)[-1]
    description = field(row, ["description", "definition", "scopeNote"], lang)
    aliases = field_list(row, ["altLabels", "alternativeLabels", "hiddenLabels", "nonPreferredTerms"], lang)
    return {
        "source": "ESCO_API",
        "source_id": uri,
        "term": "source_esco_skill_" + slug(label),
        "label": label,
        "dimension": "skill",
        "definition": description,
        "aliases": aliases[:50],
        "roles": [],
        "skills": [label] + aliases[:25],
        "evidence": "open_taxonomy_supported",
        "confidence": 4,
        "country_scope": "EU_reference_global_mapping_candidate",
        "needs_country_mapping": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="raw_data/esco_api")
    ap.add_argument("--output", default="generated/esco_api_normalized.json")
    ap.add_argument("--language", default="en")
    args = ap.parse_args()
    inp = Path(args.input)
    occ_path = inp / "occupations_all.json"
    skill_path = inp / "skills_all.json"
    if not occ_path.exists() or not skill_path.exists():
        raise SystemExit("Run fetch_esco_api.py first. Missing occupations_all.json or skills_all.json")
    occupations = load(occ_path)
    skills = load(skill_path)
    norm_occ = [normalize_occupation(x, args.language) for x in occupations]
    norm_skills = [normalize_skill(x, args.language) for x in skills]
    aliases = []
    role_rows = []
    skill_rows = []
    for t in norm_occ + norm_skills:
        for a in t.get("aliases", []):
            aliases.append({"alias": a, "preferred_source_term": t["term"], "source": "ESCO_API", "confidence": 4})
        for r in t.get("roles", []):
            role_rows.append({"role_title": r, "mapped_source_term": t["term"], "source": "ESCO_API", "confidence": 4})
        for s in t.get("skills", []):
            skill_rows.append({"skill_name": s, "mapped_source_term": t["term"], "source": "ESCO_API", "confidence": 4})
    result = {
        "source": "ESCO_API",
        "counts": {"occupations": len(norm_occ), "skill_terms": len(norm_skills), "aliases": len(aliases), "roles": len(role_rows), "skills": len(skill_rows)},
        "terms": norm_occ + norm_skills,
        "aliases": aliases,
        "roles": role_rows,
        "skills": skill_rows,
    }
    dump(Path(args.output), result)
    print(json.dumps(result["counts"], indent=2))


if __name__ == "__main__":
    main()
