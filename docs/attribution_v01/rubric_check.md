# Project Audible rubric and lecture check

Recommendation: continue this as the independent Audible project, conditional on
instructor acceptance of the narrowed topic, source and team arrangement. Extra
charts alone do not establish course compliance or earn a guaranteed score.

## Rubric evidence

| Requirement | Evidence in this release | Remaining boundary |
|---|---|---|
| Dashboard story 10 | Recommendation on page 1; 2025 allocation effect and holding-path gap | Student should be able to explain the decision in 30 seconds |
| Appropriate visuals 8 | Annual comparison, cumulative path, stock/month contribution and drawdown | Accounting attribution, not causal AI attribution |
| Honest presentation 7 | Same starting weights, gross labels, costs and exposure limits | A valid complete 2025/four-year net estimate is unavailable |
| Works live 5 | Power BI v09 with independent period selectors and stock detail | Native checks recorded separately; no imaginary verification |
| Position memo 25 | Two pages, recommendation first, numeric evidence, strongest objection and main limitation | Student review and ownership remain pending |
| Technical memo 25 | Three pages, named sources/snapshot, formulas, code, tests, replay and choices | Vendor release ID unknown; licensed raw source retained on WRDS |
| LLM log 20 | Cumulative log plus exact task/prompt/output excerpts and corrections | Exact backend model version unknown; no independent new human checks claimed |

The original rubric is Project Audible Rubric.docx, Financial Decision Systems,
FINTECH 590-05, Fall 2026. It permits Power BI or equivalent. It contains no minimum
page count, mandatory drill-through, private-data, SHAP or machine-learning rule.
The separate bank-health/SHAP assignment is not silently imported into this rubric.

## Additional lecture rules

The supplied Lecture 05 screenshot, printed slide 5, requires a genuinely contested
finance question, programmatic primary-source pulls, a position on slide 1, a view
showing the strongest opposing evidence, Backwards First and teams of two.

- Finance and decision relevance: present the choice between this disclosed short-horizon
  rule and passive semiconductor exposure, rather than a generic dashboard about data quality.
- Genuine controversy: literature documents aggregate trading-cost penalties and some
  persistent trading skill. These are compatible findings, not fabricated direct disagreement
  over this exact toy rule. See controversy_context.md. Instructor acceptance of the narrowed
  case study still needs confirmation.
- Source: actual data were programmatically retrieved through WRDS. CRSP is a vendor-produced
  research database, not a directly collected exchange/broker feed. Confirm whether that meets
  this assignment's intended primary-source definition. The earlier approval of a separate
  group OptionMetrics/CRSP proposal is not approval of this independent Audible topic.
- Recommendation first: keep the rule in research; do not deploy it on current evidence.
- Opposing evidence: 2025 remains +1.93 pp ahead of the matched comparator gross, with a smaller
  daily-close drawdown. Page 2 shows it; it is not dismissed because the sector rose.
- Team size: the lecture says teams of two. This independent work's team/solo status is unconfirmed.

## Submission status

A stronger analytical draft is available. Do not describe it as instructor-approved
or fully submission-ready until topic/source/team questions and student review are
resolved. Neither the old negative three-year result nor this favorable gross year
answers the complete after-cost question. New private Trading data are unnecessary
for the current accounting/benchmark scope.

## Memo revision 2 evidence map

Checked against the supplied Project Audible Rubric.docx on October 26, 2026.
This maps content to the rubric; it is not an assigned grade.

| Memo criterion | Revised evidence |
|---|---|
| Position upfront 10 | First paragraph recommends research-only use and gives the 10.60 to 1.93 pp correction. |
| Evidence 8 | Page 1 table: four annual comparisons and full period; page 2: drawdowns, exposure and stock/month contributions. Values checked against existing v09 CSVs. |
| Limitations/counterarguments 4 | Page 2 retains favorable 2025 evidence, names the required crossed quote and explains why the recommendation still holds. |
| Professional and at most two pages 3 | Two pages, recommendation first, five rendered pages across both memos inspected. |
| Sources/provenance 8 | Technical page 1 names WRDS tables/query, access date, CIZ format, date scope, hashes and unknown vendor release ID. |
| Pipeline 8 | Technical pages 1-2 explain dated identity/calendar checks, field mapping, lagged rule, drifting weights, comparators, attribution and risk. |
| Reproducible 5 | Technical page 3 gives exact commands; fresh archive replay passed 10 tests and matched all five CSVs byte for byte. Raw-source extraction requires WRDS and is not reproduced by this summary replay. |
| Choices 4 | Technical page 3 explains matching start weights, retained original benchmark, no fitted leverage/alpha/causal claim, and retrospective timing. |

The v09 native PBIX export/reopen evidence is now included in the technical memo.
No human expanded-data verification, grade or instructor approval is invented.
