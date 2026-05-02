from __future__ import annotations
import argparse, os
from pathlib import Path
from dotenv import load_dotenv
from common import load_json

BASE = Path(__file__).resolve().parents[1]

def chunks(rows, n=500):
    for i in range(0, len(rows), n):
        yield rows[i:i+n]

def upsert_table(sb, table, rows, conflict=None):
    if not rows:
        print(f"{table}: no rows")
        return
    for i, chunk in enumerate(chunks(rows), start=1):
        q = sb.table(table).upsert(chunk, on_conflict=conflict) if conflict else sb.table(table).upsert(chunk)
        q.execute()
        print(f"{table}: upserted batch {i} ({len(chunk)} rows)")

def build_rows(args):
    terms = load_json(BASE / args.terms)
    aliases = load_json(BASE / args.aliases)
    roles = load_json(BASE / args.roles)
    skills = load_json(BASE / args.skills)
    relationships = load_json(BASE / args.relationships)
    term_rows = [{
        'term_id': t.get('id'), 'preferred_term': t.get('term'), 'display_label': t.get('label'),
        'dimension': t.get('dimension'), 'parent_term': t.get('parent'), 'definition': t.get('definition') or '',
        'simple_definition': t.get('simple') or '', 'includes': t.get('includes', []), 'excludes': t.get('excludes', []),
        'evidence_status': t.get('evidence') or 'platform_candidate', 'maturity_status': t.get('status') or 'raw',
        'bias_status': t.get('bias') or 'pass', 'regulated_flag': t.get('regulated') or 'no',
        'source_confidence_score': t.get('confidence') or 1, 'country_notes': t.get('country', {}),
        'routing_use': t.get('routing') or '', 'problem_solved': t.get('problem') or ''
    } for t in terms]
    alias_rows = [{'alias': a.get('alias'), 'preferred_term': a.get('preferred_term'), 'alias_type': a.get('alias_type','alias'), 'country_scope': a.get('country_scope','all'), 'source': a.get('source'), 'confidence': a.get('confidence',3)} for a in aliases if a.get('alias') and a.get('preferred_term')]
    role_rows = [{'role_title': r.get('role_title'), 'role_family': r.get('role_family'), 'mapped_term': r.get('mapped_term'), 'mapped_dimension': r.get('mapped_dimension'), 'country_scope': r.get('country_scope','Canada/India/USA'), 'source': r.get('source'), 'confidence': r.get('confidence',3)} for r in roles if r.get('role_title') and r.get('mapped_term')]
    skill_rows = [{'skill_name': s.get('skill_name'), 'skill_cluster': s.get('skill_cluster'), 'mapped_term': s.get('mapped_term'), 'mapped_dimension': s.get('mapped_dimension'), 'skill_type': s.get('skill_type','skill_or_keyword'), 'country_scope': s.get('country_scope','all'), 'evidence_status': s.get('evidence_status'), 'confidence': s.get('confidence',3)} for s in skills if s.get('skill_name') and s.get('mapped_term')]
    rel_rows = [{'from_term': r.get('from_term'), 'relationship': r.get('relationship'), 'to_term': r.get('to_term'), 'reason': r.get('reason'), 'source': r.get('source'), 'confidence': r.get('confidence',3)} for r in relationships if r.get('from_term') and r.get('relationship') and r.get('to_term')]
    return term_rows, alias_rows, role_rows, skill_rows, rel_rows

def main():
    load_dotenv()
    ap = argparse.ArgumentParser()
    ap.add_argument('--terms', default='generated/final_vocab_terms.json')
    ap.add_argument('--aliases', default='generated/final_aliases.json')
    ap.add_argument('--roles', default='generated/final_role_titles.json')
    ap.add_argument('--skills', default='generated/final_skills.json')
    ap.add_argument('--relationships', default='generated/final_relationships.json')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    term_rows, alias_rows, role_rows, skill_rows, rel_rows = build_rows(args)
    counts = {'vocab_terms': len(term_rows), 'vocab_aliases': len(alias_rows), 'vocab_roles': len(role_rows), 'vocab_skills': len(skill_rows), 'vocab_relationships': len(rel_rows)}
    print(counts)
    if args.dry_run:
        print('Dry run only. No Supabase writes performed.')
        return
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if not url or not key:
        raise SystemExit('Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env, or run --dry-run')
    from supabase import create_client
    sb = create_client(url, key)
    upsert_table(sb, 'vocab_terms', term_rows, conflict='preferred_term')
    upsert_table(sb, 'vocab_aliases', alias_rows, conflict='alias,preferred_term')
    upsert_table(sb, 'vocab_roles', role_rows)
    upsert_table(sb, 'vocab_skills', skill_rows)
    upsert_table(sb, 'vocab_relationships', rel_rows)
    print('Done.')
if __name__ == '__main__':
    main()
