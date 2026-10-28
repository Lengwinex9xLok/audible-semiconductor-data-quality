# Reproduce the four annual cost scenarios

Run from the repository root with Python 3.9+; the new replay uses only the
standard library. Download/extract the complete memo package for a standalone
copy. Its PDFs are unchanged, and its source_bundle.zip is byte-identical to
the already published v09 archive containing DERIVED summaries, not raw WRDS.

From a repository checkout (the maintained modular replay; 13 tests):

    python -m zipfile -e deliverables/attribution_v01/source_bundle.zip extracted_v09
    python -m unittest discover -s supporting_evidence -p "test*.py" -v
    python supporting_evidence/replay_v10_costs.py extracted_v09

From the preserved standalone package (its original replay and 7 tests), use its root source_bundle.zip instead:

    python -m zipfile -e source_bundle.zip extracted_v09
    python -m unittest discover -s supporting_evidence -p "test_replay_v10_costs.py" -v
    python supporting_evidence/replay_v10_costs.py extracted_v09

Use a new extraction folder. The replay prints a JSON PASS receipt and writes
nothing by default. Optional --receipt NEW_FILE.json refuses existing files.
It verifies the two fixed input hashes before/after reading, all four annual
2025 returns/gaps, the extra-drag identity, saved gross paths and sleeve weights.
The baseline has initial wealth one and may have a blank position; only actual
holding intervals require binary positions. No data or future-return screen
changes the existing ten-stock sample.

IMPORTANT PROVENANCE
This is a NEW cash/share implementation added after commit 5e622d6, not the
missing contributor M11 source. replay_run_20261027.json records the actual new
run. review_checks.json records this repair's review, not the original missing
contributor checks. docs/memo_contributor_evidence_status.md lists the latter.
The original uploaded 34-row log and three-file ZIP are preserved separately.

This reproduces hypothetical costs on saved derived inputs. It does not verify
raw market inputs, actual fills, independent human arithmetic, the historical
SOX sample or the continuous four-year cost comparison. Both portfolios pay
initial/final costs; cash yield is zero; annual cash-start cases cannot be
compounded. The ADI quote remains unresolved. No new PBIX or memo results were
created by this packaging repair.

## Current code organization

The entrypoint remains replay_v10_costs.py. Its arithmetic, input validation and
scenario/receipt handling now live in cost_replay/accounting.py, inputs.py and
replay.py. These use only the standard library. Legacy imports and module execution
remain supported; no trading rule, input hash, cost rate or output figure changes.

See [the cleanup note](../docs/code_cleanup_20261027.md) and
[the new validation receipt](refactor_validation_20261027.json). The historical
standalone ZIP and its receipts are retained unchanged; they describe the
pre-refactor replay. Current receipts hash the wrapper and every engine module.
