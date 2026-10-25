# Semiconductor sample selection

Selected on October 25, 2026 for data-quality coursework. The sample prioritizes
established U.S.-listed chip/equipment businesses, manageable scope, and the
existing ordinary-common-stock resolver. It is not ranked by returns, model
outcomes or anomaly counts. Business labels describe broad current activities.

| Ticker | Company | Broad segment |
| --- | --- | --- |
| NVDA | NVIDIA | Compute and chip design |
| AMD | Advanced Micro Devices | Compute and chip design |
| INTC | Intel | Processors and manufacturing |
| MU | Micron Technology | Memory |
| QCOM | QUALCOMM | Connectivity and chip design |
| TXN | Texas Instruments | Analog and embedded |
| ADI | Analog Devices | Analog and mixed signal |
| AMAT | Applied Materials | Semiconductor equipment |
| LRCX | Lam Research | Semiconductor equipment |
| KLAC | KLA | Semiconductor process control |

The identifier anchor is 2024-12-31; subsequent history follows each resolved
permno. Do not splice different IDs to make a longer history. The live check must
return exactly one active common-stock ID per label. Intended ordinary-share
candidates still require actual shrcd 10/11 and name-interval verification.
The chosen firms need not cover every requested date; preserve any coverage gaps.

Selection uses present knowledge. It does not include every semiconductor firm
that existed historically and cannot establish sector-wide performance. S&P
membership remains descriptive context, not an automatic sample filter.

## Primary sources checked on October 25, 2026

* [Nasdaq PHLX Semiconductor data](https://www.nasdaq.com/docs/2023/11/06/SOX%5B1%5D.pdf).
  The document displays data as of May 1, 2026, regardless of its URL directory.
* [iShares Semiconductor ETF](https://www.ishares.com/us/products/239705/ishares-phlx-semiconductor-etf):
  sector context. No current fund weights are used to construct a historical portfolio.
* [NVIDIA](https://www.nvidia.com/en-us/about-nvidia/),
  [AMD](https://www.amd.com/en/corporate.html),
  [Micron](https://www.micron.com/about),
  [Qualcomm](https://www.qualcomm.com/company): chip-business descriptions.
* [Texas Instruments 2024 10-K](https://www.sec.gov/Archives/edgar/data/97476/000009747625000007/txn-20241231.htm),
  [Analog Devices 2024 10-K](https://www.sec.gov/Archives/edgar/data/6281/000000628124000204/adi-20241102.htm):
  company/security descriptions and analog/embedded context.
* [Applied Materials](https://www.appliedmaterials.com/us/en/about.html),
  [Lam Research](https://www.lamresearch.com/company/),
  [KLA](https://www.kla.com/company): equipment/process-control descriptions.

These sources do not establish CRSP identifiers, complete 2004-2024 coverage,
or historical S&P membership. Record actual tables, extraction dates and runtime
after the new WRDS run. Never reuse the old ten-stock sample's result counts.
