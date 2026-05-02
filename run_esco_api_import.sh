#!/usr/bin/env bash
set -euo pipefail

echo "Installing requirements..."
pip install -r requirements.txt

echo "Fetching ESCO API data..."
python scripts/fetch_esco_api.py   --output raw_data/esco_api   --language en   --version latest

echo "Normalizing ESCO API data..."
python scripts/normalize_esco_api.py   --input raw_data/esco_api   --output generated/esco_api_normalized.json

echo "Merging ESCO + O*NET + TALLENTIN seed..."
python scripts/merge_vocab.py   --seed data/vocab_terms.json   --onet generated/onet_normalized.json   --esco generated/esco_api_normalized.json   --output generated/tallentin_vocab_merged_with_esco_api.json

echo "Validating merged vocabulary..."
python scripts/validate_generated.py   --input generated/tallentin_vocab_merged_with_esco_api.json

echo "Rebuilding browser data.js..."
python scripts/build_data_js.py   --input generated/tallentin_vocab_merged_with_esco_api.json   --output data.js

echo "ESCO API ingestion complete."
