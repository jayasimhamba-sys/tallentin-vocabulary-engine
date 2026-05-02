from __future__ import annotations

import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from common import load_json

def main():
    load_dotenv()
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Merged vocab terms JSON")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not args.dry_run and (not url or not key):
        raise SystemExit("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env, or use --dry-run")

    terms = load_json(Path(args.input))
    rows = []
    for t in terms:
        rows.append({
            "term_id": t.get("id"),
            "preferred_term": t.get("term"),
            "display_label": t.get("label"),
            "dimension": t.get("dimension"),
            "parent_term": t.get("parent"),
            "definition": t.get("definition"),
            "simple_definition": t.get("simple"),
            "includes": t.get("includes", []),
            "excludes": t.get("excludes", []),
            "evidence_status": t.get("evidence"),
            "maturity_status": t.get("status"),
            "bias_status": t.get("bias"),
            "regulated_flag": t.get("regulated"),
            "source_confidence_score": t.get("confidence"),
            "country_notes": t.get("country", {}),
            "routing_use": t.get("routing"),
            "problem_solved": t.get("problem"),
        })

    if args.dry_run:
        print(f"Dry run: would upsert {len(rows)} vocab_terms rows.")
        print(rows[0] if rows else {})
        return

    sb = create_client(url, key)
    # batch upsert
    for i in range(0, len(rows), 500):
        chunk = rows[i:i+500]
        sb.table("vocab_terms").upsert(chunk, on_conflict="preferred_term").execute()
        print(f"Upserted {i+len(chunk)}/{len(rows)}")
    print("Done.")

if __name__ == "__main__":
    main()
