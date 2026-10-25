# Semiconductor Data Quality for Project Audible

This separate coursework version reuses Loki's historical stock-data audit. It
asks how a researcher should screen and label data before using it in an analysis.
It contains no private Trading strategy or research finding.

## Sample and status

Ten labels: NVDA, AMD, INTC, MU, QCOM, TXN, ADI, AMAT, LRCX, KLAC. The scope includes
seven chip businesses and three equipment/process-control suppliers. Segment
labels are broad descriptions, not claims of pure exposure to one business.

Requested history: 2004-01-01 to 2024-12-31. Identifier anchor: 2024-12-31.
Selection date: 2026-10-25. This is a convenience sample chosen with present
knowledge, not a historical index universe or a survivorship-free study.
No live semiconductor data or real semiconductor findings are bundled. All ten
IDs and their actual historical coverage still require a new WRDS check.
The old group sample's counts are not findings for this sample.

## Start here

1. Read docs/selection.md, then run `python run_audible.py plan` locally. Plan reads
   configuration only; it opens no account or data connection.
2. Transfer this source folder to a separate WRDS directory. Open
   notebooks/audible_semiconductors_wrds.ipynb there.
3. Run setup and identity check first. Review the ten resolved IDs before pulling.
   The default data example is June 2024, using the same 2024-12-31 identity anchor.
4. After the example works, change FULL_HISTORY to True in the configuration cell
   for 2004-2024. The new date window uses a different raw/processed folder.
5. Run the guarded pull/build/audit cells. Inspect quality_status and flagged rows.
6. The final cell collects existing summary tables into a separate handoff folder.
   Review intended coursework use before export; raw price rows are not included.

The notebook prompts for WRDS username only as needed. Authenticate through the
normal WRDS password/Duo flow; never put a password in source. Check installed
kernel packages first. This notebook does not install or upgrade packages.

## Isolation and preservation

This version has its own config, source, tests, notebook and data root. No .git,
virtual environment, credentials, group market records or group result reports
were copied. STOCKS_DATA_ROOT is ignored; Audible has an AUDIBLE_DATA_ROOT name.
The recommended notebook explicitly uses this project's data/semiconductors root.
Do not point any manual low-level command at the original group's data root.

Raw runs are immutable. The notebook refuses to build over existing processed
output. Audit runs write fresh directories. The inherited low-level build CLI
retains its explicit rebuilding behavior; use the guarded notebook workflow.

## Audit interpretation

The code resolves research labels to dated permnos, pulls history by permno,
attaches dated names and S&P membership, and preserves source-row provenance.
It flags normal/locked/crossed quotes, checks missing returns against source-first
observations, and reconciles dates with CRSP. It does not repair quotes, impute
returns, or silently remove original rows. S&P membership is context in this
version; a nonmember row is not automatically a bad semiconductor observation.
Closing quoted spreads are not executable prices or total trading costs.

## Remaining deliverables

This is a source/configuration version. Real semiconductor results, a live
dashboard, position memo, technical memo and completed LLM log are still needed.
See docs/audible_checklist.md and docs/llm_validation_log.csv. Reuse permission and
contribution attribution remain submission-planning items. Nothing is published.

## Offline tests

Use an existing Python environment with pandas and pytest:

```text
python -m pytest -q -p no:cacheprovider tests --basetemp .test-tmp
```

Tests use fictional records and do not verify WRDS access or real coverage.
Keep generated evidence and executed notebooks out of source-only transfers.

## Attribution

Stock audit logic/tests are adapted from Loki's stocks module in Group 2's
590-Data-Wrangling-Project. Shared SQL, connection and configuration scaffolding
originated in that team repository. This version adds the independent sample,
workflow and summary handoff. Exact original commit/hashes are recorded in
docs/source_provenance.json. It does not claim sole authorship of team code.
