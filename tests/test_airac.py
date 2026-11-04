import datetime as dt

import pytest

from airac import AIRAC_EPOCH, CYCLE_DAYS, cycle_for

D = dt.date


@pytest.mark.parametrize("date, ident, effective", [
    (D(2020, 1, 2), "2001", D(2020, 1, 2)),     # epoch
    (D(2020, 1, 29), "2001", D(2020, 1, 2)),    # last day of a cycle
    (D(2020, 1, 30), "2002", D(2020, 1, 30)),   # first day of the next one
    (D(2020, 12, 31), "2014", D(2020, 12, 31)), # 2020 has 14 cycles
    (D(2021, 1, 27), "2014", D(2020, 12, 31)),  # cycle 2014 runs into 2021
    (D(2021, 1, 28), "2101", D(2021, 1, 28)),
    (D(2024, 1, 25), "2401", D(2024, 1, 25)),
    (D(2026, 1, 22), "2601", D(2026, 1, 22)),
    (D(2026, 11, 4), "2611", D(2026, 10, 29)),
    (D(2026, 11, 26), "2612", D(2026, 11, 26)),
    (D(2019, 12, 31), "1913", D(2019, 12, 5)),  # before the epoch
])
def test_cycle_for(date, ident, effective):
    cycle = cycle_for(date)
    assert cycle.ident == ident
    assert cycle.effective == effective
    assert cycle.next_effective == effective + dt.timedelta(days=CYCLE_DAYS)


def test_cycles_start_on_thursday_and_are_contiguous():
    date = AIRAC_EPOCH
    previous = None
    for _ in range(200):
        cycle = cycle_for(date)
        assert cycle.effective.weekday() == 3  # Thursday
        if previous:
            assert cycle.effective == previous.next_effective
            year_changed = cycle.effective.year != previous.effective.year
            expected = 1 if year_changed else int(previous.ident[2:]) + 1
            assert int(cycle.ident[2:]) == expected
        previous = cycle
        date = cycle.next_effective
