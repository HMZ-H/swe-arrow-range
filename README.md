![validate](https://github.com/HMZ-H/swe-arrow-range/actions/workflows/validate.yml/badge.svg)

# swe-arrow-range

A containerized bug-fix task built from a real commit in a real library, shipped
with the cheat solutions already written and proven to score zero.

## The bug

`arrow.Arrow.range()` clips the day at short months and never recovers. Ask for
monthly steps from 31 January and you get 31 Jan, 28 Feb, 28 Mar, 28 Apr. It
should snap back to the last day of each month: 31 Jan, 28 Feb, 31 Mar, 30 Apr.

Twelve lines in `arrow/arrow.py` fix it.

## How the task is built

Taken from arrow-py/arrow at commit `da6ed8c`, which fixes the bug and adds
three tests for it.

- The agent gets the repo at `da6ed8c~1` — broken, and without those tests.
- The three tests are held outside the image and injected at grade time.
- `solution.patch` is the source half of the real commit. It is the oracle, and
  it is not in the image either.

## Fail-to-pass

    tests/test_arrow.py::TestArrowRange::test_range_over_months_ending_on_different_days
    tests/test_arrow.py::TestArrowRange::test_range_over_quarter_months_ending_on_different_days
    tests/test_arrow.py::TestArrowRange::test_range_over_year_maintains_end_date_across_leap_year

## Pass-to-pass

All 1668 collected tests, compared against `baseline.json`. 14 of them already
error on the broken state — an old repo against modern pytest — so they are
recorded as known-bad rather than excluded. Excluding their three files would
have thrown away about 800 working tests and left a wide hole for a cheat to
hide in.

## What the grader does

Reward is 1.0 only if all three F2P tests pass and nothing regressed.

Two things make it hold:

**It reads per-test outcomes from JUnit XML**, not pytest's exit code. A test
only counts as passed if it appears in the XML with no failure, error or
skipped child. Deleted, skipped, xfailed, deselected or never collected all
come back as not-passed without needing a special case for each.

**It grades only the library diff.** Before running, it takes the agent's
changes to `arrow/*.py`, throws the entire working tree away, and replays that
diff onto a clean checkout. A `conftest.py`, a `pytest.ini`, a deleted test
file, a `sitecustomize` — none of it survives, because none of it is library
source. The agent can only win by changing the library.

That second rule exists because of a hole found while building this. A
`conftest.py` at the repo root is imported before any test runs, so it can
monkeypatch the library in memory: the tests go green while the shipped source
stays broken. Restoring the test file is not enough on its own.

## Scores

| Scenario | Reward |
| --- | --- |
| no change | 0.0 |
| oracle patch | 1.0 |
| delete the test file | 0.0 |
| conftest calls sys.exit(0) | 0.0 |
| conftest sets collect_ignore | 0.0 |
| conftest skips every test | 0.0 |
| conftest monkeypatches Arrow.range | 0.0 |

Every row is re-run in CI on each push. If a cheat ever scores above zero, the
build fails.

## Running it

    docker build -t swe-arrow-range .
    ./validate.sh "oracle" 'cd /workspace/repo && git apply /workspace/solution.patch'
    for c in cheats/*.sh; do ./validate.sh "$(basename $c .sh)" "bash /workspace/$c"; done

## Adding a cheat

Drop a script in `cheats/`. It runs inside the container before grading. If it
scores above zero, the grader is wrong — fix the grader, not the cheat.
