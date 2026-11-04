"""
Filename: airac.py
Description: AIRAC (Aeronautical Information Regulation And Control) cycle calculation.

AIRAC cycles are 28 days long and start on a Thursday (ICAO Annex 15).
Cycle 2001 became effective on 2020-01-02; every cycle since is a whole
number of 28-day periods after that date. A cycle is identified as YYNN,
where YY is the year of its effective date and NN its ordinal within that year
(some years, e.g. 2020, have 14 cycles).

Run as a script to print the current cycle, and, when running in GitHub
Actions, export it as step outputs (ident, effective, next_effective).
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
from dataclasses import dataclass

AIRAC_EPOCH = dt.date(2020, 1, 2)  # Effective date of AIRAC 2001
CYCLE_DAYS = 28


@dataclass(frozen=True)
class AiracCycle:
    """An AIRAC cycle, identified by its effective date."""

    effective: dt.date

    @property
    def ident(self) -> str:
        """Cycle identifier in YYNN format (e.g. '2611')."""
        number = (self.effective.timetuple().tm_yday - 1) // CYCLE_DAYS + 1
        return f"{self.effective.year % 100:02d}{number:02d}"

    @property
    def next_effective(self) -> dt.date:
        """Effective date of the following cycle."""
        return self.effective + dt.timedelta(days=CYCLE_DAYS)


def cycle_for(date: dt.date) -> AiracCycle:
    """Return the AIRAC cycle in force on the given date."""
    periods = (date - AIRAC_EPOCH).days // CYCLE_DAYS
    return AiracCycle(AIRAC_EPOCH + dt.timedelta(days=periods * CYCLE_DAYS))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the AIRAC cycle in force on a date.")
    parser.add_argument('--date', type=dt.date.fromisoformat, default=None,
                        help='ISO date (YYYY-MM-DD). Defaults to today (UTC).')
    args = parser.parse_args()

    date = args.date or dt.datetime.now(dt.timezone.utc).date()
    cycle = cycle_for(date)
    values = {
        'ident': cycle.ident,
        'effective': cycle.effective.isoformat(),
        'next_effective': cycle.next_effective.isoformat(),
    }
    for key, value in values.items():
        print(f"{key}={value}")

    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as file:
            for key, value in values.items():
                file.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()
