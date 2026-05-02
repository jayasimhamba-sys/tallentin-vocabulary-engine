# TALLENTIN Vocabulary Engine V2.3 — Actual O*NET Import Completed

This package includes the V2.2 ingestion-ready structure plus an actual O*NET import run.

## Actual import completed
- O*NET occupations imported: 1,016
- O*NET aliases extracted: 36,000
- O*NET role rows extracted: 24,219
- O*NET skill/knowledge/work-activity rows extracted: 109,460
- Final merged terms: 1,061

Open `index.html` to use the finder.
See `RUN_REPORT_V2_3.md` for the full run report.

---

# TALLENTIN Vocabulary Engine V2.2 — Ingestion Ready

Built: 2026-05-02

## What changed from V2.1
This package starts the real ingestion layer.

It adds:
- O*NET parser
- ESCO parser
- merge script
- data.js rebuild script
- generated-data validator
- Supabase loader
- import manifest
- raw-data folder structure

## What stays the same
The front page remains simple:

> Type a word → get the answer.

## Folder structure
```text
index.html
data.js
data/
scripts/
raw_data/
  onet/
  esco/
generated/
README.md
ingestion_process.md
supabase_schema.sql
import_manifest.json
requirements.txt
```

## Run order

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Validate current seed
```bash
python scripts/validate_seed.py
```

### 3. Download and extract source datasets

O*NET:
- Download text/CSV database files from the O*NET Resource Center.
- Put extracted files into:
```text
raw_data/onet/
```

ESCO:
- Download ESCO v1.2.1 classification in English CSV.
- Put extracted files into:
```text
raw_data/esco/
```

### 4. Normalize O*NET
```bash
python scripts/normalize_onet.py --input raw_data/onet --output generated/onet_normalized.json
```

### 5. Normalize ESCO
```bash
python scripts/normalize_esco.py --input raw_data/esco --output generated/esco_normalized.json
```

### 6. Merge with TALLENTIN seed
```bash
python scripts/merge_vocab.py --seed data/vocab_terms.json --onet generated/onet_normalized.json --esco generated/esco_normalized.json --output generated/tallentin_vocab_merged.json
```

### 7. Validate generated output
```bash
python scripts/validate_generated.py --input generated/tallentin_vocab_merged.json
```

### 8. Rebuild browser data
```bash
python scripts/build_data_js.py --input generated/tallentin_vocab_merged.json --output data.js
```

### 9. Optional Supabase dry run
```bash
python scripts/load_supabase.py --input generated/tallentin_vocab_merged.json --dry-run
```

## Legal/source rule
O*NET and ESCO can be used as open backbone sources with attribution.
LinkedIn, Indeed, Glassdoor, ZipRecruiter, ATS pages, and company career pages remain market-signal references only unless licensed or permissioned.

## V2.5 ESCO API completion path

This package includes a new official ESCO API ingestion path:

```bash
python scripts/fetch_esco_api.py --output raw_data/esco_api --language en --version latest
python scripts/normalize_esco_api.py --input raw_data/esco_api --output generated/esco_api_normalized.json
python scripts/merge_vocab.py --seed data/vocab_terms.json --onet generated/onet_normalized.json --esco generated/esco_api_normalized.json --output generated/tallentin_vocab_merged_with_esco.json
python scripts/validate_generated.py --input generated/tallentin_vocab_merged_with_esco.json
python scripts/build_data_js.py --input generated/tallentin_vocab_merged_with_esco.json --output data.js
```

The manual ESCO bulk CSV route remains supported through `scripts/normalize_esco.py`.


## V2.6 ESCO email-ready update

Use this email for ESCO's manual download workflow:

```text
projectxtalentin@gmail.com
```

See:
- `ESCO_COMPLETION.md`
- `ESCO_EMAIL_TEMPLATE.txt`

Status:
- ESCO parser ready
- ESCO API importer ready
- ESCO bulk file not bundled until the download link/file is received


## V2.7 ESCO API attempt update

The ESCO API route was attempted from the sandbox environment, but outbound Python DNS resolution failed for `ec.europa.eu`.

This package now includes:
- `ESCO_API_ATTEMPT_LOG.md`
- `run_esco_api_import.sh`
- `run_esco_api_import_windows.bat`

Run locally or in GitHub Codespaces:

```bash
bash run_esco_api_import.sh
```

On Windows:

```bat
run_esco_api_import_windows.bat
```
