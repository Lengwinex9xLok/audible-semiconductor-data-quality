# Current v10 handoff

[Current position memo](../../position_memo.pdf) |
[Current technical memo](../../technical_memo.pdf) |
[Current LLM log](../../docs/llm_validation_log.csv) |
[Complete runnable memo package](../../Audible_Memos_LLM_v10_complete_20261027.zip)

The root PDFs contain the v10 cost update. This directory preserves the earlier
v09 memo PDFs without overwriting them. Use the new package or the root
supporting_evidence folder to run the supplemental annual cost replay.
Original contributor-local records were not supplied; their availability is
explicitly documented rather than reconstructed as historical evidence.

# Power BI v10 cost sensitivity update

Open [Audible_Semiconductor_v10.pbix](Audible_Semiconductor_v10.pbix) in Power BI
Desktop. This native PBIX embeds its summary data; no WRDS connection is needed.
Its default page is the 2025 allocation overview. The original three gross
pages remain; **04 Cost sensitivity** shows four fixed 2025 scenarios.

The cost page is independent of the other pages' period selectors. Both
strategies pay the same hypothetical cost on traded notional, including initial
purchases and terminal sales. Cash earns zero; costs compound through wealth.
At 1 one-way bp, public net return is 74.11%, matched passive net is 74.38%,
and the net gap is -0.27 percentage points. This is not a measured execution-cost
estimate or a repair of the ADI quote. Historical SOX/exit-event sample testing
remains unexecuted.

[Assumptions and validation scope](../../docs/attribution_v01/v10_cost_sensitivity.md)
| [Selected derived results](cost_sensitivity_2025_v10.csv)

The PBIX was natively exported and reopened from disk; its overview and new
cost table were checked. All four pages were visually inspected in the editable
project. Existing drill-through and period-switch interactions were not retested
for v10. The table rows match the saved cost-review outputs.

The v09 PBIX, memos, analysis outputs and old source ZIPs are preserved. The
source_bundle.zip below is the **v09** reproducibility archive; it does not
contain the v10 cost-page changes. The directly linked memos below are preserved v09 revision 2. Current v10
memos are at the repository root; use the current handoff links above.
No final student/instructor sign-off is asserted.

---

## Preserved v09 release notes


Download Audible_Semiconductor_v09.pbix with GitHub's Download raw file button, then
open it in Power BI Desktop. The PBIX was exported natively, reopened from disk,
and checked on all three pages, including a 2025/2024 year switch and MU detail.
It embeds its data and requires no WRDS or broker connection.

For editable sources and reproducible analysis, extract source_bundle.zip and open
powerbi/Audible.pbip. Each page has an independent period selector defaulting to
2025. Page 1 annual bars always show all four years. On page 2 right-click a stock
column, then Drill through > 03 Stock detail; select its year separately. MU is the
saved detail stock. Ctrl-click Back in Desktop; this action was not separately tested.

The source bundle is the retained earlier reproducibility package and is unchanged
by this export. The new PBIX is delivered separately. Earlier export-failure receipts
are retained as history; pbix_export_validation.json records the successful export.

Position memo: two pages. Technical memo: three pages. Both are AI-assisted drafts
for student review. All new returns and comparisons remain gross; complete net
results are blocked by quote quality. Source, topic and teams-of-two acceptance by
the instructor remain unconfirmed. No group or private Trading file was changed.

## Updated memos for review

October 26, 2026: the separate position_memo.pdf (two pages) and technical_memo.pdf
(three pages), with editable .txt copies, are memo revision 2 for v09. The position
leads with a research-only recommendation, preserves favorable 2025 counterevidence,
and separates gross performance from the unresolved after-cost question. The
technical memo clarifies the source-to-dashboard pipeline, replay steps and the
successful native PBIX check. Financial results and assumptions are unchanged.

Start with [the review guide](../../docs/attribution_v01/v09_review_guide.md).
The revised memo renderer and its table input are in memo_source_v09_r2.zip.
The unchanged source_bundle.zip contains the earlier memo draft and the original
analysis/Power BI sources; use the separate PDFs/text here as the current memos.
