# TALLENTIN V2.2 Ingestion Process

## Objective
Start production ingestion without drifting away from the simple user experience.

The final UX remains:

> Type a word → get the answer.

The backend becomes:
- O*NET-backed
- ESCO-backed
- country-aware
- bias-screened
- alias-normalized
- Supabase-ready

## Evidence hierarchy
1. Official/government taxonomy
2. Open taxonomy: O*NET, ESCO
3. Labour-market reports
4. Licensed/API market feeds
5. Manual public observation
6. Practitioner-submitted terms

## O*NET import target files
Place extracted O*NET files in `raw_data/onet/`.

The parser looks for:
- Occupation Data
- Alternate Titles
- Task Statements
- Skills
- Knowledge
- Work Activities
- Technology Skills

Output:
- generated/onet_normalized.json

O*NET imported terms are marked:
- evidence: open_taxonomy_supported
- status: observed
- country_scope: USA_primary_global_reference
- needs_country_mapping: true

## ESCO import target files
Place extracted ESCO CSV files in `raw_data/esco/`.

The parser looks for:
- occupations
- skills
- occupationSkillRelations

Output:
- generated/esco_normalized.json

ESCO imported terms are marked:
- evidence: open_taxonomy_supported
- status: observed
- country_scope: EU_reference_global_mapping_candidate
- needs_country_mapping: true

## Why imported terms are not automatically verified
O*NET and ESCO are source-backed, but TALLENTIN routing needs:
- country mapping
- industry/capability mapping
- bias screening
- practitioner validation for ambiguous terms

So imports start as:
- observed

They are promoted only after review:
raw → observed → patterned → weak → verified → mature → retired

## Market-source rule
LinkedIn, Indeed, Glassdoor, ZipRecruiter, ATS job pages, and company career pages may inform:
- aliases
- emerging role titles
- keyword wording
- country/sector language

They must not be:
- scraped without permission
- copied as proprietary databases
- treated as verified truth without review
