from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")

def read_table(path: Path):
    """Read tab, pipe, comma, or semicolon separated source file into list of dicts."""
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    sample = raw[:4096]
    delimiter = "\t"
    if sample.count("\t") == 0:
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=[",", ";", "|", "\t"]).delimiter
        except Exception:
            delimiter = ","
    rows = list(csv.DictReader(raw.splitlines(), delimiter=delimiter))
    return rows

def find_file(folder: Path, candidates: List[str]) -> Optional[Path]:
    files = [p for p in folder.rglob("*") if p.is_file()]
    normalized = {slug(p.stem): p for p in files}
    for c in candidates:
        key = slug(c)
        if key in normalized:
            return normalized[key]
    # fuzzy-ish contains fallback
    for c in candidates:
        key = slug(c)
        for k, p in normalized.items():
            if key in k or k in key:
                return p
    return None

def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def first(row: Dict[str, Any], names: Iterable[str], default: str = "") -> str:
    lookup = {slug(k): k for k in row.keys()}
    for n in names:
        k = lookup.get(slug(n))
        if k is not None and row.get(k) is not None:
            return str(row.get(k)).strip()
    return default

def unique_keep_order(values: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for v in values:
        v = str(v).strip()
        if not v:
            continue
        key = v.lower()
        if key not in seen:
            seen.add(key)
            out.append(v)
    return out
