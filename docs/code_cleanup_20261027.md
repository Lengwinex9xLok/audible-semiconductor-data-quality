# Current v10 cost replay cleanup

Review baseline: 61944f61a916749bcf7c0395106b77a668716b39.
Scope: the maintained 2025 annual matched cost replay. The extraction scaffold,
frozen v09 analysis archive, memo PDFs, PBIX files and historical packages remain
unchanged. This is a code-maintenance change, not a new economic experiment.

## Code organization

| File | Responsibility |
|---|---|
| supporting_evidence/replay_v10_costs.py | Existing CLI and import compatibility |
| supporting_evidence/cost_replay/accounting.py | Cash/share and portfolio arithmetic; no file access |
| supporting_evidence/cost_replay/inputs.py | Frozen input hashes, indexing, calendars, saved paths, weights and reference cases |
| supporting_evidence/cost_replay/replay.py | Four scenarios, comparisons and evidence receipt |

The old script mixed all four responsibilities and repeatedly scanned rows for
each ticker and strategy. The new input reader indexes rows once, and stock
sleeves expose named fields while retaining tuple compatibility. There is no
new third-party dependency or financial parameter. The frozen hashes, sample,
2025 convention, cost grid and tolerance are deliberately retained as evidence
constraints, rather than turned into arbitrary configurable strategy settings.

Existing commands and legacy public imports still work. In a repository checkout:

    python -m unittest discover -s supporting_evidence -p "test*.py" -v
    python supporting_evidence/replay_v10_costs.py extracted_v09

Module execution also works:

    python -m supporting_evidence.replay_v10_costs extracted_v09

The extraction argument is the directory produced from the unchanged v09
source_bundle.zip; see supporting_evidence/README.md for the extraction command.
Use a new directory and a new --receipt path. No database or broker connection
is opened. Old standalone packages retain their original source/tests; use the
checkout for this modular version.

## One validation correction

The former require_close validated only the calculated value's finiteness.
If the reference contained NaN, abs(calculated - NaN) > tolerance evaluated False,
so an invalid reference could pass. A real four-row CSV with one NaN reproduces
the old PASS and is rejected by the new reader. Both comparison operands must
now be finite. None of the published reference values has this problem.

## Checks

- All seven existing fictional accounting tests pass without changing them.
- Six focused tests cover finite references, the four-case convention and a
  hand-derived two-stock weighted portfolio; thirteen tests pass in total.
- The four published cases, including 640 public entries/exits per case, match
  the pre-refactor implementation exactly, with no rounding tolerance between
  old and new cases. Maximum difference from the published CSV remains
  1.1546319456101628e-14, below its fixed 1e-12 tolerance.
- Direct script execution, module execution, legacy imports and execution from
  another working directory pass. Changed inputs and existing receipt paths
  are rejected; frozen input hashes are unchanged.
- Receipts now include hashes for every implementation module, because hashing
  only the smaller compatibility wrapper would no longer identify the engine.

See supporting_evidence/refactor_validation_20261027.json. The original
replay_run_20261027.json and package_validation.json remain historical receipts;
their old script hashes are not silently relabeled as new checks.

## Remaining limits

This remains a hypothetical cost experiment on derived inputs. It does not
repair the ADI crossed quote, establish real execution costs, recover missing
contributor records, perform the historical SOX test or supply new human
verification. The annual cash-start cases cannot be compounded. No group or
private Trading file is accessed or changed. The broader upstream scaffold and
frozen compressed historical code were not refactored in this small cleanup.
