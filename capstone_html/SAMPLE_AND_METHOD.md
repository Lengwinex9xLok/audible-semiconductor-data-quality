# Twenty-stock sample and method

The 20-stock extension is a 2026-selected convenience sample, added to the earlier semiconductor-only project. Half the names are semiconductor or equipment companies; pairs of other companies are not representative of entire industries.

| Group | Symbols |
| --- | --- |
| Semiconductor / equipment | ADI, AMAT, AMD, INTC, KLAC, LRCX, MU, NVDA, QCOM, TXN |
| Other selected companies | AAPL, MSFT, BAC, JPM, CVX, XOM, JNJ, UNH, PG, WMT |

The analysis uses WRDS/CRSP daily data for the 2022–2025 holding period and an earlier observation for the first signal. Each stock gets an equal initial allocation; there is no rebalancing across sleeves. The rule holds a stock from close to close when its prior session return is positive and otherwise holds cash. The comparator remains invested. Annual values are segments of the continuous portfolio rather than annually reset experiments.

The 20-stock rule returned 46.99% gross against 92.65% gross for buy and hold, a difference of −45.66 percentage points. These values exclude transaction costs and are not risk-adjusted. The sample was selected after the test period, which limits what can be inferred about future performance.

Three required strategy events have crossed quotes, so the original quote-based cost policy blocks a net estimate. Locked quotes also occur; neither condition proves a zero execution cost. The derived CSV is included; the restricted source records and the WRDS scripts used to produce the 20-stock extension are not included in this handoff. The result has not been independently reproduced from raw data as part of this package.
