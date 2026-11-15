# Audible capstone: 20-stock HTML dashboard

This folder is the current capstone handoff for the presentation. The earlier semiconductor-only v10 files are preserved elsewhere in this repository. Do not combine their results with the 20-stock results below: the samples, test periods and benchmarks differ.

## Start with the conclusion

Keep the rule in research. In our 20-stock 2022–2025 historical test, the rule returned **46.99% gross**, versus **92.65% gross** for buy and hold, a difference of **−45.66 percentage points**. The rule can hold cash while buy and hold remains invested, so this is not a risk-adjusted comparison. Neither return includes transaction costs.

The full-period maximum drawdown was **−21.27%** for the rule and **−25.36%** for buy and hold. The troughs occurred on different dates; a smaller past drawdown does not prove the rule will always be safer. See [method and scope](RISK_METHOD.md).

## The sample and rule

The 20 stocks were selected in 2026, after the 2022–2025 test period. Ten are semiconductor or equipment names; the other ten cover several other areas. This is an exploratory convenience sample, not a representative or survivorship-free universe. [The sample and methodology](SAMPLE_AND_METHOD.md) lists all 20 names.

The rule holds a stock from close to close when its prior session return is positive; otherwise that stock's sleeve holds cash. Stocks have equal initial allocations, with no cross-sleeve rebalancing. Buy and hold stays invested. Annual returns segment the continuous portfolio; they are not independent, annually reset experiments.

## Run the HTML dashboard

Python 3, network access, and `TWELVE_DATA_API_KEY` provisioned in the environment are required for the live demo. From this folder, run:

```sh
sh run_demo.sh
```

This command starts in strict live mode: it fetches all 20 symbols before opening the dashboard, and exits with an error if the key is missing or the initial fetch fails. First collection takes several minutes. A successfully retrieved quote can still be delayed or be from an earlier market session; check its timestamps.

An equivalent command, including on Windows without Git Bash, is:

```text
python html_dashboard.py --require-live
```

The dashboard opens locally at `http://127.0.0.1:8765/`. Keep the terminal open and press Ctrl+C to stop it. It has Executive, Risk, Compliance and Quote Monitor views. Select a year in Executive to see that segment's returns; drawdown remains a fixed full-period result.

Only derived historical results are included. **No Twelve Data quotes or API keys are included.** Do not commit or share the key. The Python collector fetches 20 symbols about 12 seconds apart, then waits an hour before its next cycle. It saves a new snapshot only if all 20 succeed. Quotes can be delayed or stale; check both quote date and retrieval time. The quote feed does not rerun the historical backtest.

For an offline historical-only preview, use `sh run_demo.sh --no-refresh` or `python html_dashboard.py --no-refresh`. Without a saved snapshot, Quote Monitor clearly indicates that quotes are unavailable. This preview is not a live-data test. See [data dictionary](DATA_DICTIONARY.md) and [presentation handoff](PRESENTATION_HANDOFF.md).

## Limits and remaining work

- This is a fixed historical output from WRDS/CRSP data, not proof of future or after-cost performance. The documented quote-based cost policy blocks a net result because three required strategy events have crossed quotes.
- Raw licensed WRDS records, provider quote snapshots, and the WRDS analysis environment are not included. The original 20-stock analysis must be made accessible and independently rerun before claiming full reproduction.
- The dashboard has not passed a clean-machine, no-manual-steps cold-start test. A fresh quote feed requires a separately provisioned key and network access.
- The course also refers to a Phase 2 risk console and to three output formats. The scope of those requirements and their integration still needs confirmation. The HTML Tufte review and final package review are not complete.

This folder is a team handoff, not a claim that the final capstone has been submitted or every rubric item satisfied.
