---
pretty_name: Warning Shots — The AI Incident Index
license: TBD  # pending: CC BY 4.0 recommended
language: [en]
tags: [ai-safety, ai-incidents, ai-security, risk, incident-database]
size_categories: [n<1K]
---
<!-- DRAFT for Hugging Face Datasets and Kaggle. Upload needs Colin's accounts. -->

# Warning Shots — The AI Incident Index

160 significant AI incidents since 2023, each scored 0–100 by a published formula and linked to its sources. Updated three times a day at https://warningshots.ai/.

## Fields
`id`, `date`, `date_precision`, `disclosed`, `title`, `actors`, `category`, `setting` (wild or lab), `summary`, `harm`, `H` (harm 0–5), `R` (reach 0–5), `A` (autonomy 0–4), `N` (novelty 0–5), `I` (irreversibility 0–5), `source_url`, `source2_url`, `confidence`, `notes`.

## Scoring
Harm score = 100 × (0.5·H/5 + 0.25·R/5 + 0.25·I/5); signal score = 100 × (0.6·A/4 + 0.4·N/5); severity = 0.55 × harm + 0.45 × signal. Tiers: <20 Minor, 20–39 Moderate, 40–59 Serious, 60–79 Severe, 80+ Critical.

## Findings
Severe incidents went from 3 to 13 in a year. In 42% of this year's real-world incidents the AI system itself did the acting.

## Limits
Curated, not a census; ratings are the index's judgments under a fixed rubric; facts and figures come from the linked sources. Corrections are logged publicly.

## Files
https://warningshots.ai/data/incidents.json · https://warningshots.ai/data/incidents.csv

## Citation
Warning Shots, The AI Incident Index, warningshots.ai.
