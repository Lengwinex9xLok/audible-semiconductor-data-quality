"""Read and validate the frozen derived inputs for the 2025 annual experiment."""

from collections import defaultdict
import csv
import hashlib
import math
from pathlib import Path

from .accounting import Sleeve, require_close, sleeve_wealth

PUBLIC = 'lagged_positive_return'
PASSIVE = 'always_long'
PERIOD = '2025'
CONVENTION = 'annual_matched_cash_start'
SCENARIO_BPS = frozenset({0.0, 0.5, 1.0, 2.0})
EXPECTED = {
    'stock_daily_summary.csv': '7f4d65b8e170f3416f9b5feb3e0923d5426e160a356bced223ce9096bc57c8ea',
    'stock_performance_summary.csv': '64ee06912a73ec52621b0b9bfcffccd9d5bffd2af5dd9db8ffb1a78e6646c8c2',
}
RETURN_FIELDS = ('net_public', 'net_matched_passive', 'net_gap', 'extra_drag')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def input_hashes(inputs: Path) -> dict[str, str]:
    return {name: digest(inputs / name) for name in EXPECTED}


def load_reference_cases(path: Path) -> list[dict]:
    """Validate the four published cases; these are references, not fitted targets."""
    rows = read_csv(path)
    if len(rows) != 4 or {float(row['one_way_bps']) for row in rows} != SCENARIO_BPS:
        raise ValueError('Expected four distinct published cases')
    if any(row['period'] != PERIOD or row['convention'] != CONVENTION for row in rows):
        raise ValueError('Unexpected experiment convention')
    for row in rows:
        if any(not math.isfinite(float(row[field])) for field in RETURN_FIELDS):
            raise ValueError('Published reference returns must be finite')
    return sorted(rows, key=lambda row: float(row['one_way_bps']))


def _index_summaries(rows: list[dict]) -> dict[tuple[str, str], dict]:
    indexed = {}
    for row in rows:
        key = (row['ticker'], row['strategy'])
        if key in indexed:
            raise ValueError('Duplicate/missing stock summary')
        indexed[key] = row
    return indexed


def _index_paths(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    indexed = defaultdict(list)
    for row in rows:
        indexed[(row['ticker'], row['strategy'])].append(row)
    return indexed


def _validate_path(block: list[dict], calendar: list[str]) -> None:
    dates = [row['date'] for row in block]
    if len(dates) < 2 or len(set(dates)) != len(dates):
        raise ValueError('Invalid dates')
    if dates != calendar:
        raise ValueError('Calendar mismatch')
    if [int(row['is_initial']) for row in block] != [1] + [0] * (len(block) - 1):
        raise ValueError('Invalid baseline markers')
    if any(
        not math.isfinite(float(row['wealth'])) or float(row['wealth']) <= 0
        for row in block
    ):
        raise ValueError('Invalid saved wealth')
    require_close(float(block[0]['wealth']), 1.0, 'Initial wealth')


def load_sleeves(inputs: Path) -> tuple[list[Sleeve], list[str]]:
    """Check dates, saved gross paths, summaries and weights before any cost replay."""
    summaries = [
        row for row in read_csv(inputs / 'stock_performance_summary.csv')
        if row['period'] == PERIOD
    ]
    paths = [
        row for row in read_csv(inputs / 'stock_daily_summary.csv')
        if row['period'] == PERIOD
    ]
    if not summaries or any(
        row['cost_case'] != 'gross_zero_cost' or float(row['spread_multiplier']) != 0
        for row in summaries + paths
    ):
        raise ValueError('Expected saved gross 2025 inputs')
    strategies = {PUBLIC, PASSIVE}
    if {row['strategy'] for row in summaries} != strategies:
        raise ValueError('Expected both strategies')
    if {row['strategy'] for row in paths} != strategies:
        raise ValueError('Expected both strategies')
    tickers = sorted({row['ticker'] for row in summaries})
    if len(tickers) != 10 or {row['ticker'] for row in paths} != set(tickers):
        raise ValueError('Expected the frozen ten-stock sample')

    summary_index = _index_summaries(summaries)
    path_index = _index_paths(paths)
    sleeves = []
    calendar = None

    for ticker in tickers:
        blocks = {}
        summary = {}
        for strategy in (PUBLIC, PASSIVE):
            key = (ticker, strategy)
            if key not in summary_index:
                raise ValueError('Duplicate/missing stock summary')
            summary[strategy] = summary_index[key]
            block = sorted(path_index[key], key=lambda row: row['date'])
            if calendar is None:
                calendar = [row['date'] for row in block]
            _validate_path(block, calendar)
            blocks[strategy] = block

        # Baseline position may be blank; only actual intervals require a position.
        positions = [float(row['position']) for row in blocks[PUBLIC][1:]]
        prices = [float(row['wealth']) for row in blocks[PASSIVE]]
        gross, _, _ = sleeve_wealth(prices, positions, 0)
        for actual, row in zip(gross, blocks[PUBLIC]):
            require_close(actual, float(row['wealth']), 'Gross public path')
        require_close(gross[-1] - 1, float(summary[PUBLIC]['cumulative_return']), 'Public summary')
        require_close(prices[-1] - 1, float(summary[PASSIVE]['cumulative_return']), 'Passive summary')
        weight = float(summary[PUBLIC]['initial_portfolio_weight'])
        if not math.isfinite(weight) or weight < 0:
            raise ValueError('Invalid sleeve weight')
        sleeves.append(Sleeve(weight, prices, positions))

    require_close(sum(sleeve.weight for sleeve in sleeves), 1, 'Weight sum')
    return sleeves, calendar
