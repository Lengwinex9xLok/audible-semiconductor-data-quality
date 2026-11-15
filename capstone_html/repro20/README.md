# Replaying the 20-stock analysis

This is a read-only replay of the saved 2022–2025 research run. It compares all 140 sample/stock result rows and both full-period drawdowns against the saved results. It checks the input manifests, code hashes and calendar hash before calculation. It does not query WRDS, create files, modify the original run, or calculate a net return.

## What was checked on WRDS

On 15 November 2026, the saved 20-stock script, the 14-stock and six-stock inputs and identity files, cohort and selection specifications, the earlier 14-stock comparison, model code and trading calendar were all present. Both input manifests, the model code and the calendar passed their saved SHA-256 checks. The saved 20-stock output's SHA-256 was `86463bd682eaaccab45aa1c160bb6f05abfba19b65b513c68f9969dae044f383`, matching the dashboard's CSV.

The original 20-stock calculation script is `run_twenty.py` (SHA-256 `dcc9852c3801a1018b06d0962ac4486786e8328dcd2824bacb4a96de7fe88684`). The 14-stock manifest records the daily and identity SQL, and the six-stock manifest records identity, history and daily queries. No separate acquisition `.py`, `.sql` or notebook file was found at the top level of either saved run directory; a complete standalone query-to-output pipeline has not been identified. The recorded queries and saved snapshots are not proof that a fresh extraction will produce identical data.

We independently executed the calculation in a WRDS Jupyter console without writing files. All 140 rows matched the saved result to absolute tolerance `1e-8` percentage points; the maximum observed difference was about `2.84e-14`. The two maximum drawdowns were −21.2746747828% and −25.3552334896%, with troughs on 2022-10-12 and 2022-09-30. There were three required crossed-quote and 23 required locked-quote strategy events. The net result remains blocked under the original policy.

That check uses the saved WRDS inputs and existing engine; it is a replay of the same source snapshot, not an independent audit of the CRSP vendor data. `replay_wrds.py` was then executed as a standalone script on WRDS on 15 November 2026 and exited successfully. Its SHA-256 was verified before execution; see [the run receipt](WRDS_REPLAY_RECEIPT.json).

## Inputs and paths

The default paths match the original WRDS account:

- `~/audible_cross_industry_20261115/run_20261115T101618Z_07eb6156/`: prior 14-stock data, identities and manifest.
- `~/audible_cross_industry_20261115/twenty_stock_20261115T183448Z_35a432fa/`: six-stock additions, identities, manifest, cohort specification and saved 20-stock reference.
- `~/audible_semiconductors_20261025/Audible-Semiconductor/`: original financial engine, aggregation code, prior manifest and calendar.

Use `--base` and `--project` if these directories have been placed elsewhere. The original `run_twenty.py` is present in the 20-stock run directory, but its outputs use exclusive creation in that directory. Do not rerun it directly there. `replay_wrds.py` avoids writing anything and includes the reference comparison.

The source files are licensed WRDS/CRSP data and are not part of GitHub. A reviewer must have appropriate WRDS access and these saved inputs; access to GitHub alone does not reproduce the data. Do not upload raw prices, quotes, credentials, or the original inputs.

## Environment and execution

WRDS Jupyter reported Python 3.14.5, NumPy 2.4.6 and pandas 2.2.3 during the read-only replay. Check the preinstalled environment before installing anything; do not modify WRDS-managed packages.

The separate `environment-analysis.yml` specifies Python 3.11, NumPy 1.26.4 and pandas 2.2.3. The existing 12 financial-engine tests passed with these versions in an isolated Windows virtual environment using fictional data. This does not prove that Conda can solve that file on every platform, or that the WRDS source replay works on a different machine. The HTML demo itself uses Python's standard library and does not require this analysis environment.

Once the files in this folder are available in your authorized WRDS workspace, run:

```sh
python replay_wrds.py
```

No arguments are necessary for the original account layout. A successful run prints `PASS`, the number of rows compared, maximum difference, drawdowns and quote-event counts. A missing file, changed hash, or mismatched result should stop the run; do not treat a partial result as a pass.

## Limits

The 20-stock selection was made in 2026, after the test period, and is not survivorship-free. The rule can hold cash, while buy and hold remains invested. Results are gross and not risk-adjusted; a lower historical drawdown does not prove lower future risk. Live Twelve Data quotes are separate and do not recalculate these historical results.
