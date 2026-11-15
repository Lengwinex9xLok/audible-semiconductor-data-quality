# Full-period maximum drawdown

For each of the two continuous 20-stock portfolio wealth paths, daily-close drawdown is `100 × (wealth / running peak wealth − 1)`. The running peak includes initial wealth of 1 on December 31, 2021. The maximum drawdown is the most negative daily value during the 2022–2025 holding interval.

| Portfolio | Maximum drawdown | Trough date |
| --- | ---: | --- |
| Rule | −21.27% | October 12, 2022 |
| Buy and hold | −25.36% | September 30, 2022 |

These are fixed, gross, full-period results. The individual troughs occurred on different dates. The calculation used the project's existing WRDS/CRSP daily inputs, a 20-stock equal-initial-capital portfolio, and no cross-sleeve rebalancing. The rule can hold cash; buy and hold stays invested. The sample was chosen after the test period. A smaller historical maximum drawdown is not proof of lower future risk.

The calculation was checked against an independent NumPy running-maximum calculation in its original environment. The daily wealth path and licensed inputs are not in this repository handoff, so readers cannot independently rerun it from this folder alone.
