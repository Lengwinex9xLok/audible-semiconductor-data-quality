# Project Audible semiconductor trading costs

**Current version: expanded 2022-2024 historical check.** The public daily rule's 1x
quoted-width sensitivity returns -30.08% in 2022, +29.25% in 2023 and +1.34% in 2024.
The continuous three-year return is -8.41%; always-long returns +36.23%, with different exposure.
The recommendation is to keep the rule in research. Positive years challenge a blanket failure claim.
No 2025 or 2026 performance is inferred.

## Open the current deliverables

- [Three-page Power BI dashboard v08](deliverables/expanded_2022_2024_v01/Audible_Semiconductor_v08.pbix)
- [Position memo, two pages](deliverables/expanded_2022_2024_v01/position_memo.pdf)
- [Technical memo, three pages](deliverables/expanded_2022_2024_v01/technical_memo.pdf)
- [Editable PBIP, code, tests and all summary inputs](deliverables/expanded_2022_2024_v01/source_bundle.zip)
- [Results and complete summary ZIP](results/expanded_2022_2024_v01)
- [Time coverage and interpretation](docs/expanded_time_coverage.md)
- [Cumulative LLM log](docs/llm_validation_log.csv)
- [Validation and remaining submission items](validation/expanded_2022_2024_v01/release_validation.json)

Use GitHub's **Download raw file** for PBIX, then open it in Power BI Desktop. It embeds its
summary tables and needs no broker/WRDS connection. Or extract source_bundle.zip and open
powerbi/Audible.pbip. Page 1 selects Full or an individual year and supports right-click
stock drill-through. Page 2 compares all annual returns under a selected cost case and
shows a selectable-period path. Page 3 has independent stock-period and cost controls.
After drilling, choose the desired year on that page separately. The saved stock is NVDA.
Ctrl+click Back in Desktop; the binding is retained, but that specific click is not separately tested.

## Source and limits

Programmatic WRDS extraction on October 26, 2026 found complete same-source 2022-2024 coverage,
with 7,530 analysis records and 20 warmup records. Those legacy tables returned no 2025 records.
The unchanged rule holds close(d) to close(d+1) when RET(d-1)>0, otherwise cash. Equal initial
sleeves retain their capital; no daily or annual cross-stock rebalance, shorts or leverage;
cash yield zero. Annual/monthly returns segment a continuous portfolio. Annual contributions
use drifting starting wealth weights and are not reset to 10% each January.

Cost results are a **locked-inclusive quoted-width sensitivity**. Two transactions require
positive locked quotes with zero recorded width, which is not evidence of free execution.
One crossed quote is retained but not required for costs. No row is dropped, repaired or
imputed. A complete strict-normal-only cost estimate is unavailable. Returns are modeled,
not actual fills; fees, impact, taxes, cash yield and intraday latency are omitted.

The 2026 convenience universe is not historically investable or survivorship-free. Extra
historical years are not prospective validation. Instructor acceptance of the source,
narrowed controversy and team/solo arrangement remains unconfirmed. Full independent human
verification of the expansion is not claimed. Review the prose and recommendation before submission.

## Preserved June pilot and existing code

[The original June pilot](deliverables/june_pilot_v01) remains available as a development
and verification record, with its [results](results/june_pilot_v01). Its negative-cost
sign reversal must not be extrapolated to every year. Root extraction config/src/tests/notebook
files are the earlier source scaffold; their 2004-2024 setting is not this release's sample.
Do not enable full-history extraction to inspect either dashboard. No group checkout or
private strategy was changed. Shared scaffolding is attributed in docs/source_provenance.json.
This private coursework repository contains derived summaries, not original source prices,
quotes, account records or private research. No redistribution rights are asserted.
