# Independent version validation

Checked on October 25, 2026. The offline suite passed **44 tests** on Python
3.11.9, pandas 2.2.3, numpy 2.4.6 and pytest 9.1.1. It used the already installed
local environment; no environment or package was copied into this project.

Inherited tests exercise dated identity resolution, quote/return semantics,
raw preservation, calendar gaps, replay and notebook startup/overwrite guards.
Six added tests cover data-root isolation, ten-label identity checking,
connection closure on ambiguous identity, refusing another stock sample,
summary-only handoff with tamper detection, and refusing external group paths.
All data used by these tests were fictional.

The first test invocation used an incorrect output path and a temporary directory
whose parent did not exist. Those paths and the README test command were corrected;
the complete suite then passed. This was a test setup issue, not live data evidence.

All notebook code cells and source modules parse. The notebook has no execution
counts or outputs. The plan command opens no data connection. The 54 tracked
files checked in the original group project retained identical SHA-256 hashes.
The independent directory contains no copied Git history, real data or credentials.

Not verified: live CRSP schemas/access for this run, the ten actual permnos,
2004-2024 coverage, new quote/return/membership counts, dashboard rendering or
presentation, and final memos. No semiconductor result is borrowed from the old
sample. No account session, paid data request, push or publication was performed.
