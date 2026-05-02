from __future__ import annotations
from pathlib import Path
from common import load_json

BASE = Path(__file__).resolve().parents[1]
terms = load_json(BASE / 'generated/final_vocab_terms.json')
aliases = load_json(BASE / 'generated/final_aliases.json')
blocked = load_json(BASE / 'data/blocked_terms.json')

term_by_key = {t['term'].lower(): t for t in terms}
term_by_label = {t.get('label','').lower(): t for t in terms}
alias_to_term = {a['alias'].lower(): a['preferred_term'] for a in aliases if a.get('alias') and a.get('preferred_term')}
blocked_terms = {b['term'].lower(): b for b in blocked}

def normalize(input_term: str):
    q = input_term.strip().lower()
    if q in blocked_terms:
        return {'status': 'blocked', 'reason': blocked_terms[q].get('reason'), 'preferred_term': None}
    preferred = alias_to_term.get(q)
    if preferred:
        t = term_by_key.get(preferred.lower())
        return {'status': 'normalized', 'preferred_term': preferred, 'term': t}
    if q in term_by_key:
        return {'status': 'exact', 'preferred_term': q, 'term': term_by_key[q]}
    if q in term_by_label:
        t = term_by_label[q]
        return {'status': 'label_match', 'preferred_term': t['term'], 'term': t}
    return {'status': 'review_required', 'preferred_term': None, 'reason': 'No match. Add to review queue.'}

def can_route(practitioner_terms, signal_terms):
    p = [normalize(x) for x in practitioner_terms]
    s = [normalize(x) for x in signal_terms]
    if any(x['status'] == 'blocked' for x in p+s):
        return {'route': False, 'reason': 'Blocked term present', 'practitioner': p, 'signal': s}
    p_terms = {x.get('preferred_term') for x in p if x.get('preferred_term')}
    s_terms = {x.get('preferred_term') for x in s if x.get('preferred_term')}
    overlap = p_terms.intersection(s_terms)
    return {'route': bool(overlap), 'overlap': sorted(overlap), 'practitioner': p, 'signal': s}

if __name__ == '__main__':
    for q in ['recruiting', 'talent acquisition', 'SQL', 'culture_fit', 'project manager']:
        print(q, '=>', normalize(q)['status'], normalize(q).get('preferred_term'))
    print(can_route(['financial services', 'quality assurance'], ['banking', 'QA']))
