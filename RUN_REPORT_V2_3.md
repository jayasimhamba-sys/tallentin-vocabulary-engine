# TALLENTIN Vocabulary Engine V2.3 — Actual O*NET Import Run Report

Date: 2026-05-02

## Completed
- Downloaded official O*NET text files individually.
- Copied O*NET files into `raw_data/onet/`.
- Ran `scripts/validate_seed.py` successfully.
- Ran `scripts/normalize_onet.py` successfully.
- Ran `scripts/merge_vocab.py` successfully.
- Ran `scripts/validate_generated.py` successfully.
- Ran `scripts/build_data_js.py` successfully.

## O*NET import counts
- Occupations imported: 1,016
- Alias rows extracted: 36,000
- Role rows extracted: 24,219
- Skill/knowledge/work-activity rows extracted: 109,460

## Final merged finder counts
- Merged vocabulary terms: 1,061

## ESCO status
ESCO has not been bulk-downloaded inside this package because the ESCO download page requires the user to select a package, accept a privacy statement, enter an email address, and receive a download link. The ESCO parser remains ready in `scripts/normalize_esco.py`.

## Next step
After obtaining ESCO CSV files, place them into `raw_data/esco/` and run:

```bash
python scripts/normalize_esco.py --input raw_data/esco --output generated/esco_normalized.json
python scripts/merge_vocab.py --seed data/vocab_terms.json --onet generated/onet_normalized.json --esco generated/esco_normalized.json --output generated/tallentin_vocab_merged.json
python scripts/validate_generated.py --input generated/tallentin_vocab_merged.json
python scripts/build_data_js.py --input generated/tallentin_vocab_merged.json --output data.js
```

## Honest production note
The imported O*NET role concepts are marked as `observed`, not automatically `verified`, because they still need TALLENTIN capability mapping, country mapping for Canada/India, bias screening, and practitioner validation before automatic signal routing.
