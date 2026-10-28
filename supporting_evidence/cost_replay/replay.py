"""Compare calculated annual cost cases with published values and report evidence."""

from datetime import datetime, timezone
from pathlib import Path

from .accounting import TOL, portfolio_return, require_close
from .inputs import (
    CONVENTION, EXPECTED, PERIOD, RETURN_FIELDS, digest, input_hashes,
    load_reference_cases, load_sleeves,
)


def implementation_hashes() -> dict[str, str]:
    """Hash every source module, since the legacy entrypoint is now a thin wrapper."""
    package = Path(__file__).resolve().parent
    wrapper = package.parent / 'replay_v10_costs.py'
    sources = [wrapper, *sorted(package.glob('*.py'))]
    return {
        path.relative_to(package.parent).as_posix(): digest(path)
        for path in sources
    }


def replay(bundle: Path, expected_csv: Path) -> dict:
    """Replay fixed 2025 scenarios without writing files or contacting a data service."""
    inputs = bundle / 'inputs'
    before = input_hashes(inputs)
    if before != EXPECTED:
        raise ValueError('Frozen input hashes differ')
    expected_digest = digest(expected_csv)
    expected_rows = load_reference_cases(expected_csv)
    sleeves, calendar = load_sleeves(inputs)

    gross_public = portfolio_return(sleeves, 0, active=True)[0]
    gross_passive = portfolio_return(sleeves, 0, active=False)[0]
    results = []
    max_error = 0.0

    for reference in expected_rows:
        bps = float(reference['one_way_bps'])
        public, entries, exits = portfolio_return(sleeves, bps, active=True)
        passive, _, _ = portfolio_return(sleeves, bps, active=False)
        gap = public - passive
        extra = (gross_public - public) - (gross_passive - passive)
        row = dict(
            one_way_bps=bps,
            net_public=public,
            net_matched_passive=passive,
            net_gap=gap,
            extra_drag=extra,
        )
        for field in RETURN_FIELDS:
            expected = float(reference[field])
            max_error = max(max_error, abs(row[field] - expected))
            require_close(row[field], expected, field)
        require_close(gap, (gross_public - gross_passive) - extra, 'Relative drag identity')
        row.update(public_entries=entries, public_exits=exits)
        results.append(row)

    if before != input_hashes(inputs) or expected_digest != digest(expected_csv):
        raise ValueError('Input files changed')

    sources = implementation_hashes()
    return dict(
        status='PASS',
        implementation='new_cash_and_share_replay_20261027',
        implementation_revision='modular_cleanup_20261027',
        provenance='New reconstruction after 5e622d6; not the missing contributor M11 source or original receipt',
        executed_at_utc=datetime.now(timezone.utc).isoformat(),
        period=PERIOD,
        convention=CONVENTION,
        inputs_sha256=before,
        expected_csv_sha256=expected_digest,
        script_sha256=sources['replay_v10_costs.py'],
        implementation_files_sha256=sources,
        securities=len(sleeves),
        intervals_per_security=len(calendar) - 1,
        tolerance=TOL,
        max_absolute_error=max_error,
        cases=results,
        inputs_unchanged=True,
        raw_wrds_queried=False,
        continuous_four_year_replayed=False,
        independent_human_verification=False,
    )
