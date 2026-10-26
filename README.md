# Project Audible June semiconductor pilot

**Recommendation:** keep this disclosed daily rule in research. In this June pilot,
a +0.1631% gross return becomes -0.0380% under the quoted-width cost proxy.
This small hindsight-selected sample does not establish persistent profitability.

## Current deliverables

- [Three-page Power BI dashboard with stock drill-through](deliverables/june_pilot_v01/Audible_Semiconductor_v07.pbix)
- [Position memo, two pages](deliverables/june_pilot_v01/position_memo.pdf)
- [Technical memo](deliverables/june_pilot_v01/technical_memo.pdf)
- [Editable memo text and instructions](deliverables/june_pilot_v01/README.md)
- [Source bundle including editable PBIP and benchmark tests](deliverables/june_pilot_v01/source_bundle.zip)
- [Summary results](results/june_pilot_v01)
- [LLM validation log](docs/llm_validation_log.csv) and [selected prompt/output excerpts](docs/prompt_output_examples.md)
- [Current validation and remaining submission items](validation/june_pilot_v01/release_validation.json)

Download the PBIX using GitHub's **Download raw file** button; GitHub's preview does
not run Power BI. Or extract source_bundle.zip and open powerbi/Audible.pbip.
Embedded summary tables require no WRDS account. On Page 1, right-click a stock
contribution bar, then Drill through > 03 Stock detail. Pages 2 and 3 have separate
cost selectors. The saved detail ticker is AMD; a new drill-through replaces it.
In Desktop use Ctrl+click on Back. Its binding exists; that click was not separately tested.

## Evidence and scope

Ten stocks, 190 input records, 19 June 2024 dates and 17 holding intervals per stock
(June 4-28). Hold close(d) to close(d+1) if RET(d-1)>0, otherwise cash. Equal initial
sleeves; no daily cross-stock rebalance, shorts or leverage; cash yield zero.
The three cost scenarios use the same observations. Always-long returns +4.7781%
under the quote proxy, with different exposure. The gross deficit is already
4.6593 percentage points: costs are not its main explanation. Positive gross
performance and profitable stock sleeves remain visible as counterevidence.

Source: programmatic legacy CRSP through WRDS, pulled October 25, 2026 at
23:53:41 UTC. Hashes identify the retained snapshot; vendor release was not recorded.
This private coursework release contains derived summaries, not source prices,
quotes, account records or a private trading strategy. No redistribution rights
are asserted. Course source eligibility and team/solo approval remain unconfirmed.
One user-reported arithmetic check passed; a full independent human/source audit
is not claimed. Review the wording and recommendation before submission.

## Existing extraction source

Root config/src/tests/notebook files remain the earlier extraction and audit
scaffold. Their 2004-2024 setting is an available tutorial configuration, **not the
sample used here**. Do not enable full-history extraction to review this pilot.
The [earlier proposal](docs/revised_topic_proposal.md) predates the benchmark;
current memos supersede its pending-analysis status. The group checkout is unchanged.
Stock logic and shared scaffolding are attributed in docs/source_provenance.json.
Keep licensed source files, credentials and executed notebooks outside publication.
