# v10 cost sensitivity

Published October 27, 2026 as a dashboard review update.

## What changed

The first three v09 pages retain their gross charts, calculations and page
controls. Two homepage text boxes now point to the independent cost analysis
and disclose the pending historical sample test. The fourth page adds a native
table backed by a disconnected, embedded four-row summary table. It does not
filter or alter the existing model tables or relationships.

## Fixed 2025 scenarios

| One-way cost (bp) | Public net return | Matched passive net | Net gap (pp) | Extra return drag (pp) |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 76.35% | 74.42% | +1.93 | 0.00 |
| 0.5 | 75.23% | 74.40% | +0.82 | 1.11 |
| 1 | 74.11% | 74.38% | -0.27 | 2.20 |
| 2 | 71.90% | 74.35% | -2.45 | 4.38 |

The linked CSV retains full numeric precision; its return and gap columns are
decimal fractions (multiply by 100 for percent or percentage points). Values come from the saved
cost_review_v1 outputs, not a new extraction or a changed security sample.
Only selected scenarios are shown here; the full frozen cost grid remains
in the local computational record.

## Accounting conventions

Both portfolios begin the independent annual experiment in cash, use the same
saved v09 public gross period-start stock-sleeve weights, and pay initial buy
and final sell costs. The public rule retains its saved signals; passive holds
the same stock sleeves. There is no within-year cross-stock rebalance. The
same all-in one-way rate c = bp/10,000 applies to each traded notional: a buy
funded by V invests V/(1+c), and a sale receives V*(1-c). Cash yield is zero.
Costs compound through daily wealth. Nominal fee sums are not terminal return drag.

Net gap = gross gap - (public return drag - passive return drag).

Annual cash-start comparisons are independent conditional experiments and
must not be compounded. The separate continuous 2022-2025 comparison starts
with equal sleeves and carries holdings across year ends; its annual segments
have strategy-specific drifting allocations. At 1 bp its public return is
62.87%, versus passive 125.88%. It must not be substituted for the annual
matched experiment or hidden by the favorable 2025 observation.

## Limits

This is retrospective hypothetical sensitivity conditional on observed v09
allocations. It is not a measured execution-cost estimate, an ex-ante allocation
rule, risk-adjusted alpha, prospective validation or evidence that the ADI
2025-04-16 crossed quotation has been repaired. The original quote-based
complete net calculation remains unresolved. The ten-stock selection was made
in 2026; the full historical SOX roster and exit-event sample test remain pending.
Same initial stock weights do not equalize market exposure or risk.

## Checks and authorship

The four rows were checked against the saved cost outputs. The independent
cost review records ten fictional accounting tests, five zero-cost comparisons
to v09, and fourteen continuous compounding checks. Those are prior automated
computational checks; they were not rerun for this dashboard-only publication.
The saved WRDS cost replay receipt is prior evidence, not a new raw-data replay.

For v10, all four editable-project pages were visually checked. The PBIX was
exported natively, reopened from disk, and its overview and cost page inspected.
The file embeds data. Existing period switches and drill-through were not
retested for v10. Local v09 artifacts and prior cost outputs retained their hashes.
SHA256SUMS.txt records the delivered PBIX checksum.

AI assisted with the cost implementation, added dashboard table, explanatory
text, file checks and this publication. Loki requested the changes and publication.
No new independent human financial/source verification is asserted. This note
records the dashboard work; it does not replace the teammate's pending memo
and consolidated LLM-validation updates. Published memo revision 2 is preserved.
No licensed raw WRDS records, raw audit files or account credentials are added.
