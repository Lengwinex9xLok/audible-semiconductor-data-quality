# Expanded historical coverage

The user requested a multi-year check instead of extrapolating June 2024. Programmatic
queries of the same legacy CRSP dsf/dsi tables returned complete 2022-2024 coverage and
no 2025 records. The expansion uses 7,530 analysis records, 753 dates and 20 warmup records.
Ten labels and the financial engine remain fixed. The full period starts at the December
31, 2021 close and ends at the December 31, 2024 close; return intervals end in 2022-2024.

The 1x results are -30.08% (2022), +29.25% (2023), +1.34% (2024) and -8.41% compounded
across all three years. Always-long is +36.23% over the full period with different exposure.
This supersedes any broad extrapolation of the June sign reversal. The June files remain
as a dated development pilot. No 2025 or 2026 outcome is inferred.

Expanded quote results are a LOCKED-INCLUSIVE sensitivity. Of 7,550 quotes, 7,544 are
normal, five locked and one crossed. Only two locked quotes are used in transition costs;
their recorded width is zero, not a claim of zero actual execution costs. The crossed
quote is retained but unused in either strategy's cost events. No data row is dropped or
repaired, and a required crossed quote stops the calculation. The old strict-normal gate
is preserved; a complete strict-normal-only estimate for the expanded sample is unavailable.

Annual/monthly returns segment continuous capital. There is no yearly reset or rebalance.
Stock contributions use drifting period-start wealth weights. Three correlated historical
years and a 2026 convenience universe are not prospective or survivorship-free validation.

Dashboard period controls are independent on each page. Drill-through changes the stock;
choose the same reporting year on the detail page if desired. The annual comparison chart
always displays all three years under its cost case, independently of that page's period
choice. Empty dates return BLANK rather than a fabricated -100% return. Data rows are retained.
