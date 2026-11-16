# Data dictionary

## Historical results: `powerbi_cross_industry_20_gross_2022_2025.csv`

These are derived results from the existing WRDS/CRSP daily analysis. They do not include raw prices. Each row describes a period and an individual stock or group. Years are segments of the same continuous 2022–2025 portfolio.

| Field | Meaning |
| --- | --- |
| `period` | `2022`–`2025` or `All` for the entire period |
| `level` | Sample or stock grouping |
| `item` | Name of the group or stock |
| `rule_return_pct` | Rule gross return, in percent |
| `buy_hold_return_pct` | Buy-and-hold gross return, in percent |
| `difference_pp` | Rule minus buy-and-hold return, in percentage points |

The main result is the `All`, `Sample`, `All 20` row. The HTML also shows two fixed full-period maximum drawdowns; see [RISK_METHOD.md](RISK_METHOD.md).

## Optional local quotes: `twelvedata_quotes_latest.csv`

Generated locally by the Twelve Data collector; this file is not part of the repository.

| Field | Meaning |
| --- | --- |
| `symbol`, `exchange`, `currency` | Provider-reported symbol, exchange and currency |
| `quote_date` | Provider's reported quote/bar date |
| `bar_open_unix`, `last_quote_unix` | Provider timestamps retained as received |
| `close` | Provider's close value, in the stated currency; not necessarily a live trade |
| `is_market_open` | Provider-reported market status |
| `source` | `Twelve Data` |
| `retrieved_at_utc` | UTC time at which this row was retrieved; not necessarily the quote time |

The collector saves a snapshot only after all 20 symbols succeed. If collection fails, an older file may remain. The quote feed is separate from the fixed historical analysis.

## Risk: average invested stock sleeves

`average_invested_sleeve_share` is the mean of the fraction of 20 stock sleeves held in stock in each of 1,003 holding intervals, excluding the initial base row. The rule is 10,443 / 20,060 = 52.06%; buy and hold is 100.00%. This is an equal-count metric, not dollar-weighted portfolio exposure. See [RISK_METHOD.md](RISK_METHOD.md) and [the verification receipt](repro20/INVESTED_SHARE_RECEIPT.json).
