#!/usr/bin/env python3
"""
Fetch ESCO occupations and skills through the official ESCO Web Services API.

This script is provided because the bulk ESCO download page requires privacy acceptance
and email delivery. The Web Services API is the permitted machine-access alternative
for applications that need ESCO classification data.

Run example:
  python scripts/fetch_esco_api.py --output raw_data/esco_api --language en --version latest

Notes:
- The API documentation lists /resource/occupation and /resource/skill endpoints.
- The public API returns HAL-style JSON. This parser is defensive because response
  shapes may vary slightly by ESCO version.
- Imported ESCO terms should remain `observed` until mapped to TALLENTIN capability,
  country context, bias status, and practitioner validation.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

import requests

ESCO_BASE = "https://ec.europa.eu/esco/api"
SCHEMES = {
    "occupations": "http://data.europa.eu/esco/concept-scheme/occupations",
    "skills": "http://data.europa.eu/esco/concept-scheme/skills",
}


def dump(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def pick_embedded(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract ESCO resources from common HAL response shapes."""
    if isinstance(payload.get("_embedded"), dict):
        emb = payload["_embedded"]
        for key in ["results", "concepts", "occupations", "skills", "resources"]:
            if isinstance(emb.get(key), list):
                return emb[key]
        # fallback: first list under _embedded
        for v in emb.values():
            if isinstance(v, list):
                return v
    for key in ["results", "concepts", "occupations", "skills", "resources"]:
        if isinstance(payload.get(key), list):
            return payload[key]
    if isinstance(payload, list):
        return payload
    return []


def fetch_collection(kind: str, output_dir: Path, base_url: str, language: str, version: str, limit: int, sleep: float, max_pages: int) -> List[Dict[str, Any]]:
    endpoint = f"{base_url.rstrip('/')}/resource/{'occupation' if kind == 'occupations' else 'skill'}"
    all_rows: List[Dict[str, Any]] = []
    offset = 0
    page = 0
    session = requests.Session()
    session.headers.update({"Accept": "application/json,application/json;charset=UTF-8", "Accept-Language": language})

    while True:
        params = {
            "isInScheme": SCHEMES[kind],
            "language": language,
            "offset": offset,
            "limit": limit,
            "viewObsolete": "false",
        }
        if version and version != "latest":
            params["selectedVersion"] = version
        r = session.get(endpoint, params=params, timeout=60)
        r.raise_for_status()
        payload = r.json()
        resources = pick_embedded(payload)
        dump(output_dir / f"{kind}_page_{page:05d}.json", payload)
        if not resources:
            break
        all_rows.extend(resources)
        print(f"{kind}: page={page} offset={offset} rows={len(resources)} total={len(all_rows)}")
        page += 1
        offset += limit
        if max_pages and page >= max_pages:
            break
        # stop if a short page arrives
        if len(resources) < limit:
            break
        time.sleep(sleep)
    dump(output_dir / f"{kind}_all.json", all_rows)
    return all_rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="raw_data/esco_api")
    ap.add_argument("--base-url", default=ESCO_BASE)
    ap.add_argument("--language", default="en")
    ap.add_argument("--version", default="latest", help="Use latest or explicit version such as v1.2.0")
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--sleep", type=float, default=0.25)
    ap.add_argument("--max-pages", type=int, default=0, help="0 means fetch all pages")
    args = ap.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    occupations = fetch_collection("occupations", out, args.base_url, args.language, args.version, args.limit, args.sleep, args.max_pages)
    skills = fetch_collection("skills", out, args.base_url, args.language, args.version, args.limit, args.sleep, args.max_pages)
    manifest = {
        "source": "ESCO Web Services API",
        "language": args.language,
        "version": args.version,
        "counts": {"occupations": len(occupations), "skills": len(skills)},
        "base_url": args.base_url,
    }
    dump(out / "esco_api_manifest.json", manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
