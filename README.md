# DS320 AI safety reporting — collection starter
Scope: 2023-01-01 through 2026-11-12 inclusive; OpenAI, Anthropic, Google/DeepMind, Meta, Moonshot AI, DeepSeek. The Epoch universe is a candidate census, not a complete release catalog. Include general-purpose language and multimodal language models in the analysis; retain other models in raw metadata. Screen minor snapshots, derivatives, joint developers and missing dates manually. Do not treat absence from Epoch or a missing report as evidence of non-disclosure.

## Run
Python 3.10+ with internet access:
```
pip install pandas requests beautifulsoup4
python collect.py
```
The script downloads Epoch metadata, filters companies and dates, saves source index HTML, and produces candidate document links for human review. It also downloads the few explicitly selected seed pages in source_manifest.csv. It does not download all discovered reports or classify passages. Review discovered links, add actual model-specific report URLs to the manifest, and mark download=yes. GitHub repository HTML is a landing page, not a PDF; locate the actual report before extraction. Dynamic pages may require manual browsing. Download MIT's full risk workbook from its index and the Epoch benchmark ZIP from its data page; keep their original files under raw/ with license/citation. METR time horizons data and AISI results require separate review. Do not republish report text without checking permissions.

## Proposed tables
models(model_id, developer, model_name, release_date, weight_access, epoch_name, source_url)
reports(report_id, publisher, title, publication_date, report_type, source_url, retrieval_date, sha256)
report_models(report_id, model_id, match_method, review_status)
passages(passage_id, report_id, page_or_section, text, evidence_type)
risk_categories(risk_id, domain, subdomain, definition, taxonomy_version)
passage_risks(passage_id, risk_id, method, confidence, review_status)
evaluations(eval_id, report_id, model_id, benchmark, metric, value, unit, protocol, evaluation_date)
coverage(model_id, search_date, source_type, status, search_notes)

Coverage statuses: not_checked, found, not_found_after_search, unavailable. Never equate missing documentation with no test or no risk. Preserve conflicting measurements and distinguish independent evaluator partnerships from fully external testing. Match exact model variants and compare scores only for compatible protocols. Use report_models for reports covering multiple models.

Source manifest is a verified entry-point list and seed documents, not a complete collected corpus. The script has not been live-tested here because external network access was unavailable. Epoch data is CC BY with attribution; benchmark data may have additional source terms. Record retrieval dates and snapshot versions for reproducibility.
