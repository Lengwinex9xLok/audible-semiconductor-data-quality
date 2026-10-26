# Review the v09 memos

Current revision: October 26, 2026, memo revision 2. Read these alongside the
v09 PBIX, not the preserved v08 net-cost dashboard.

## Read in this order

1. [Position memo](../../deliverables/attribution_v01/position_memo.pdf): two pages,
   recommendation first, the annual/full-period gross comparison, strongest
   favorable evidence, largest data limitation and conditions to reconsider.
2. [Power BI v09](../../deliverables/attribution_v01/Audible_Semiconductor_v09.pbix):
   page 1 for the decision; page 2 for stock/month attribution and drawdown;
   page 3 for stock detail. Each page has its own period selector.
3. [Technical memo](../../deliverables/attribution_v01/technical_memo.pdf): three
   pages explaining source/snapshot, source checks, financial accounting,
   comparator/decomposition, replay, design choices and validation limits.
4. [LLM validation log](llm_validation_log.csv) and
   [rubric/lecture check](rubric_check.md).

## Claims to review

| Question | Evidence and current answer |
|---|---|
| Does the rule earn money in 2025 before costs? | Yes: +76.35% gross. This is a historical modeled result, not actual account profit. |
| Does it outperform the matching-allocation passive benchmark? | +1.93 pp gross in 2025, with different cash/risk exposure. It is not alpha. |
| Why did the original comparison show +10.60 pp? | +8.67 pp is the starting-allocation term, about 82% of that gap. |
| What favors the rule? | 2025 maximum drawdown -18.21% versus -29.76%, despite lower average invested-dollar exposure of 54.95%. |
| Does the full period support a persistent gross advantage? | 2022-2025 public +71.40%, matched passive +125.92%; raw exposure differences remain. |
| Can we say it works after costs? | No complete new net result: required ADI crossed quote is unresolved. |
| Can annual matched returns be compounded? | No. Each starts from the public rule's actual weights for that selected year. |
| Did we identify an AI-boom effect? | No. Stock/month attribution is accounting, not causal event analysis. |

Student review remains needed: explain the lag and the two benchmarks; check one
selected year/stock contribution against the exported CSV; decide whether the
research-only recommendation is the position you can defend. No new independent
human check or agreement with the draft is recorded by publishing these files.
Confirm topic/source acceptance and the lecture's two-person team arrangement.

## Reproduction and version notes

The original source_bundle.zip remains unchanged, including its earlier memo drafts.
The PDFs and text files beside the PBIX are the current memo revision.
memo_source_v09_r2.zip contains the revised renderer, comparison summary and pinned
PDF dependencies. Extract it, install requirements, and run render_v09_memos.py
from any directory; it writes documents beside the script. It changes no analysis.
For the analysis replay use source_bundle.zip and the technical memo commands.
The memo-update replay passed ten tests and reproduced all five result CSVs byte
for byte on Python 3.12.14, pandas 3.0.1 and NumPy 2.3.5.

Historical versions remain in Git history and their original versioned folders.
No Trading or group-project data or files were used or changed.
