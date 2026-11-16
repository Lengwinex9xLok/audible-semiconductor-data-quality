# Full-period maximum drawdown

For each of the two continuous 20-stock portfolio wealth paths, daily-close drawdown is `100 × (wealth / running peak wealth − 1)`. The running peak includes initial wealth of 1 on December 31, 2021. The maximum drawdown is the most negative daily value during the 2022–2025 holding interval.

| Portfolio | Maximum drawdown | Trough date |
| --- | ---: | --- |
| Rule | −21.27% | October 12, 2022 |
| Buy and hold | −25.36% | September 30, 2022 |

These are fixed, gross, full-period results. The individual troughs occurred on different dates. The calculation used the project's existing WRDS/CRSP daily inputs, a 20-stock equal-initial-capital portfolio, and no cross-sleeve rebalancing. The rule can hold cash; buy and hold stays invested. The sample was chosen after the test period. A smaller historical maximum drawdown is not proof of lower future risk.

The calculation was checked against an independent NumPy running-maximum calculation in its original environment. The daily wealth path and licensed inputs are not in this repository handoff, so readers cannot independently rerun it from this folder alone.

## Average invested stock sleeves

For each of the 1,003 close-to-close holding intervals, count how many of the 20 stock sleeves hold stock and divide by 20. Average these fractions across intervals; exclude the initial wealth base row. The rule has 10,443 invested sleeve-intervals out of 20,060, or **52.06%** on average. Buy and hold is **100.00%**.

This is an equal-count measure, not the fraction of portfolio dollars invested: initial sleeve weights drift over time. It describes the historical sample, does not isolate the cause of the drawdown difference, and does not establish future risk. The universe was selected in 2026.

The result was checked on WRDS against signals independently recomputed from the saved CRSP inputs. The same replay matched all 140 historical result rows. See [verification code](repro20/check_invested_share.py) and the [verification receipt](repro20/INVESTED_SHARE_RECEIPT.json). Reproduction requires the licensed inputs and environment described in [repro20/README.md](repro20/README.md).
