# Audible completion checklist

Question: How should researchers screen and label historical semiconductor stock
data before using it in an analysis?

Prepared: independent sample/config, inherited audit, guarded WRDS notebook,
offline tests and summary-only handoff. Real semiconductor results are pending.

| Rubric item | Points | Smallest useful completion |
| --- | ---: | --- |
| Dashboard | 30 | One live page; stock selector, quote-rule toggle, quote counts, coverage and mean-spread sensitivity. Scope/limits visible. |
| Position memo | 25 | At most two pages; recommendation first, actual numbers/charts, strongest objection and specific usage rules. |
| Technical memo | 25 | Source/access date/version, extraction/joins, raw-to-dashboard steps, runnable instructions, parameters and rejected methods. |
| LLM validation log | 20 | Tool/model/version/date/task, prompts/outputs, validation/errors/corrections and human decisions. |

Run identity checks, then the bounded example, then the requested full history.
The summary handoff collects quote_sensitivity.csv, coverage_by_security.csv,
coverage.csv and quality_summary.json. It does not contain raw price rows.
Use reviewed real values for the dashboard; never replace missing data with zero.
An overall mean spread must weight each stock mean by its eligible-quote count.
Start with stock and quote-rule controls. Year controls would require new verified
period-level aggregates, so they are outside the smallest first version.

Locked and crossed quotes are different categories. Preserve all raw records.
Main spread uses finite positive bid < ask. Sensitivity also includes positive
locked quotes at zero; crossed quotes remain excluded from both spreads.
Missing returns stay missing. Membership is context, not a required sector filter.
Closing quotes are not executable costs; this is not a full historical industry.
Complete the memos after actual semiconductor results exist.

Rubric source: user-provided Project Audible Grading Rubric, FINTECH 590-05,
Fall 2026, reviewed October 25, 2026. The original Word file is not bundled.
