# CIZ 2022-2025 supplementary evidence: gross only

The 2025 extension changes the historical evidence, but the complete quoted-width
net result is unavailable under the frozen quote-quality policy. Retain the rule
as research while resolving source quality and assessing execution. The negative
2022-2024 result no longer describes all available historical evidence.

| Period | Public daily rule, gross | Always long, gross |
|---|---:|---:|
| 2022 | -28.73% | -34.07% |
| 2023 | 31.48% | 69.76% |
| 2024 | 3.72% | 21.79% |
| 2025 | 76.35% | 65.75% |
| 2022-2025 | 71.40% | 125.92% |

All new returns are cumulative gross returns, not actual fills or risk-adjusted
alpha. Annual returns segment one continuous portfolio with drifting sleeve weights.
The 2025 return is not a newly equal-weighted portfolio begun in January 2025.
The unchanged public rule holds close(d) to close(d+1) if RET(d-1)>0, otherwise cash.
No daily/annual cross-stock rebalance, shorts or leverage; cash yield stays zero.

## Coverage and source

Programmatic WRDS source: crsp_a_stock.dsf_v2 (CIZ/Version 2), dated stocknames_v2
identities, wrds_dailyindexret_query source-relative calendar. There are 10,050 rows
including 20 warmup records, 1,003 holding intervals per stock, first entry 2021-12-31
and final exit 2025-12-31. The ten saved labels and PERMNOs remain ADI, AMAT, AMD,
INTC, KLAC, LRCX, MU, NVDA, QCOM and TXN. Dated name and previous-date checks passed.
This remains a 2026 hindsight convenience sample, not historical index membership.

Legacy SIZ ended in December 2024. No 2025 rows in crsp.dsf did not mean that WRDS
lacked 2025 data. The accessible annual CIZ source contains the full 2025 year.
It ends 2025-12-31; monthly and quarterly schemas denied this account access.
No 2026 rows or performance have been invented or inferred.

The entire 2022-2025 run uses CIZ, without splicing legacy data. Among 2,520 overlapping
2024 records, maximum absolute differences were 0.000001 for RET/RETX and 0.00006
for bid/ask. No 2024 signal-sign difference was found. The two snapshots are not
numerically identical. Vendor release ID was not recorded; hashes pin this snapshot.

## Net result blocked by a required crossed quote

The source has 10,032 normal, 15 locked and 3 crossed quotes. One crossed quote,
ADI 2025-04-16, is required for transaction costs and was confirmed against the
CIZ security-data base table. It produces a negative quoted width. The frozen
net calculator correctly rejects it; no quote is swapped, absolutized, imputed,
or deleted. Six required locked events also have zero recorded width, which is
not evidence of free execution. A complete new 2025/four-year net return is unavailable.

Only zero-cost results are reported. The adapter permits required crossed quotes
only when all cost multipliers are zero. Its gross-only entry point rejects every
nonzero-cost configuration; the original sleeve_path financial engine is unchanged.
Twelve fictional tests passed on WRDS and locally. Saved replay, hashes, 4,022
portfolio paths, stock contributions and annual/month compounding passed.
These are AI-assisted checks; independent human/source validation is not claimed.

## What changes in the interpretation

The 2025 gross return is strong counterevidence against extrapolating the earlier
negative three-year finding. It does not answer the after-cost question. Comparators
have different exposure; actual fills, fees, impact, taxes, latency and cash yield
remain unmeasured. No significance, annualized return or deployable edge is asserted.

June and 2022-2024 Power BI v08/memos are preserved historical artifacts. Their
absence-of-2025 statement is superseded by this supplement. The PBIX still displays
2022-2024; do not combine its net cards with new gross values as a common-scope result.

Resolve the required crossed quote with a documented independent source, or freeze
and label a separate cost sensitivity before inspecting its net result. New data
permissions are needed for compatible 2026 CRSP coverage. Private broker research
or account data are not needed to fill this evidence gap.

## Reproduce and inspect

Raw data remain on WRDS. summary_and_code_bundle.zip contains all six derived
result tables, manifests and source code, with no source prices, quotes, credentials
or account data. On WRDS, replay against the saved immutable run:

```sh
python code/replay_saved.py --run-root /path/to/saved/ciz_2022_2025_run
python -m unittest discover -s code -p 'test*.py'
```

Replay requires licensed source files on WRDS and writes no files or network query.
The tests use fictional data only. Original 70 WRDS data files and 130 local June
artifacts passed preservation checks. Original v08 PBIX bytes are unchanged.

Official documentation reviewed October 26, 2026:
- [WRDS transition](https://wrds-www.wharton.upenn.edu/pages/data-announcements/changes-to-crsp-data/)
- [CRSP CIZ guide](https://www.crsp.org/crsp_pdf/crsp-us-stock-indexes-databases-guide-flat-file-format-2-0/)
- [CRSP cross-reference guide](https://www.crsp.org/crsp_pdf/crsp-us-stock-indexes-databases-siz-to-ciz-cross-reference-guide/)
