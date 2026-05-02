# ESCO Completion Runbook — TALLENTIN V2.6

Finalized: 2026-05-02

## Registered download email to use

Use this email for the ESCO download workflow:

```text
projectxtalentin@gmail.com
```

## What is already completed

The package already includes:

- O*NET-expanded vocabulary data
- Search-first finder page
- ESCO CSV parser
- ESCO API importer
- ESCO API normalizer
- Merge script
- Data rebuild script
- Supabase schema
- Supabase loaders
- Validation scripts

## What remains outside this environment

ESCO bulk download requires the user/team to complete the ESCO website workflow:

1. Open the ESCO download page.
2. Select the English CSV package.
3. Accept the privacy statement.
4. Enter:

```text
projectxtalentin@gmail.com
```

5. Wait for ESCO to send the download link to that inbox.
6. Download and extract the ESCO files.
7. Copy the extracted CSV files into:

```text
raw_data/esco/
```

## After ESCO files are copied into raw_data/esco

Run:

```bash
pip install -r requirements.txt

python scripts/normalize_esco.py \
  --input raw_data/esco \
  --output generated/esco_normalized.json

python scripts/merge_vocab.py \
  --seed data/vocab_terms.json \
  --onet generated/onet_normalized.json \
  --esco generated/esco_normalized.json \
  --output generated/tallentin_vocab_merged_with_esco.json

python scripts/validate_generated.py \
  --input generated/tallentin_vocab_merged_with_esco.json

python scripts/build_data_js.py \
  --input generated/tallentin_vocab_merged_with_esco.json \
  --output data.js
```

## Optional ESCO API route

The package also includes an API-based route:

```bash
python scripts/fetch_esco_api.py \
  --output raw_data/esco_api \
  --language en \
  --version latest

python scripts/normalize_esco_api.py \
  --input raw_data/esco_api \
  --output generated/esco_api_normalized.json

python scripts/merge_vocab.py \
  --seed data/vocab_terms.json \
  --onet generated/onet_normalized.json \
  --esco generated/esco_api_normalized.json \
  --output generated/tallentin_vocab_merged_with_esco_api.json
```

## Truth status

Until ESCO CSV/API data is actually downloaded and imported, this package status is:

```text
ESCO-ready, not ESCO-bundled
```

No false claim is made that ESCO bulk data is already physically included.
