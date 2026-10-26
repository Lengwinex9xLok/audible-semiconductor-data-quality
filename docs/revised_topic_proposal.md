# Revised Project Audible Proposal

Status: working proposal; benchmark selection and final empirical results are pending.

## 1. The question

Does a transparent short-horizon trading benchmark remain profitable after estimated trading costs?

A rule may predict price changes without providing a tradable advantage. I will test one fully disclosed benchmark and compare its performance before and after estimated costs. The conclusion will apply to that benchmark and sample, rather than to all short-term trading strategies.

## 2. The data

I have built a June 2024 pilot covering ten semiconductor stocks using CRSP data retrieved programmatically through WRDS. The course analysis will use a separate, documented sample and a benchmark rule that can be fully disclosed.

Bid and ask prices will provide a proxy for spread costs, not actual fills or a direct measure of execution delays. I will confirm that the source meets the project requirements and assess whether a longer sample is needed.

## 3. My position

My working hypothesis is that estimated trading costs eliminate the benchmark's apparent advantage. This remains to be tested in the independent course version.

I will show the strongest evidence against this position, including any positive net performance under defensible assumptions. My private strategy, parameters and research results will remain outside the project.

## Decisions before the final analysis

- Fix and document the public benchmark rule, stock selection, holding period and sample dates before evaluating performance.
- Specify when the signal becomes available and the earliest execution time supported by the data. Daily closing quotes cannot establish intraday execution latency.
- State entry and exit spread-cost assumptions, any other costs modeled, and any omitted costs. Report estimated net returns rather than actual trading profit.
- Treat the existing June sample as a pipeline pilot. Its 190 stock-date observations cover 19 trading dates; they do not establish robust profitability.
- Verify the course's primary-source requirement before relying on WRDS/CRSP as the final source.
- Keep the working hypothesis separate from the eventual finding. Do not select a rule or cost assumption merely to obtain a negative result.
- Keep private signals, strategy-selected samples, account records, orders and private performance results outside the course repository.

The existing extraction, identity resolution, data-quality checks and dashboard components can be reused. A new benchmark analysis and its conclusions still need to be developed and verified.
