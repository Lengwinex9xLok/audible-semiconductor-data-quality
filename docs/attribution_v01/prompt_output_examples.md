# Selected prompt and output excerpts

Date: October 26, 2026. Tool: Codex. Exact backend model/version was not captured.

User: "行，那就先不动我自己的Trading数据，你按这个思路把公平对照和收益归因补上吧，组里的别动。但是这样足够符合教授指定的这个project的规则吗？"

Design used: freeze an accounting comparator with the public rule's actual period-start
stock weights; preserve the original passive comparator; decompose its return gap into
holding-path and initial-allocation terms. Use gross summary paths only. Calculate
stock contributions, monthly telescoping increments, prior-wealth dollar exposure and
daily-close drawdowns. Do not fit leverage or call the residual alpha.

Output used: 2025 public +76.3489%, matched passive +74.4191%, holding-path gap +1.9298 pp,
initial-allocation term +8.6655 pp. See result CSVs for full precision. Public maximum
drawdown -18.2063%; matched -29.7584%. These are automated checks, not human verification.

Validation: ten fictional-data tests; exact decomposition/stock/month reconciliations;
active factors reconstructed from passive intervals and holding positions; input hashes;
fresh-directory replay; five rendered memo pages; native Power BI checks recorded separately.

Corrections: fictional fixtures originally lacked All but the period loop assumed it;
fixed to process only supplied periods. The monthly horizontal chart initially required
scrolling and hid November/December; changed to columns. Enabled comparison legends and
reduced numeric precision to two decimals. Added portable summary inputs and a new-output
replay argument without changing economic rules. No raw/quote repair or net result fabricated.

Human ownership: Loki chose privacy boundaries, approved the benchmark/attribution direction
and asked for the course check. AI authored code, DAX, prose and verification. Student final
position, professor acceptance and new independent human numeric validation remain pending.
