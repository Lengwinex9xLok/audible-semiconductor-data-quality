"""Replay the frozen v10 annual cost scenarios; no database or network access.

Run from repository/package root:
    python supporting_evidence/replay_v10_costs.py extracted_v09

The cash/share implementation was first added on 2026-10-27. This modular cleanup
preserves its accounting and CLI; it does not recover the contributor's missing
original script or original receipt. The public functions remain importable here.
"""

import argparse
import json
from pathlib import Path

# Support both direct execution and import as supporting_evidence.replay_v10_costs.
if __package__:
    from .cost_replay import (
        EXPECTED, PASSIVE, PUBLIC, TOL, digest, load_sleeves, read_csv, replay,
        require_close, sleeve_wealth,
    )
else:
    from cost_replay import (
        EXPECTED, PASSIVE, PUBLIC, TOL, digest, load_sleeves, read_csv, replay,
        require_close, sleeve_wealth,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('extracted_v09', type=Path)
    parser.add_argument(
        '--expected', type=Path,
        default=Path(__file__).with_name('cost_sensitivity_2025_v10.csv'),
    )
    parser.add_argument(
        '--receipt', type=Path,
        help='Optional NEW output file; existing files are rejected',
    )
    args = parser.parse_args()
    result = replay(args.extracted_v09, args.expected)
    text = json.dumps(result, indent=2)
    if args.receipt:
        with args.receipt.open('x', encoding='utf-8') as stream:
            stream.write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
