# Deployment Guide

## Local preview
Open `index.html`.

## GitHub Pages
Upload the folder to GitHub, then enable Pages from Settings → Pages.

## Supabase setup
1. Run `supabase_schema.sql` in Supabase SQL Editor.
2. Create `.env` with `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`.
3. Install requirements: `pip install -r requirements.txt`.
4. Dry run: `python scripts/load_supabase_all.py --dry-run`.
5. Real load: `python scripts/load_supabase_all.py`.

## Runtime order
input term → blocked term check → alias normalization → preferred term lookup → country/context gate → maturity/bias gate → routing.
