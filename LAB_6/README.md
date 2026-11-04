# L6_L7_10 — Bus Transit Fare

Lab 6: Code and Branch Coverage

## About

A small Python module that calculates bus transit fares by route type, zone traversals, and passenger concession categories, and checks contactless smartcard turnstile failure rates.

## Files

| File | Description |
|------|-------------|
| `bus_transit_fare.py` | The module under test |
| `test_bus_transit.py` | Starter test file |

Keep all your Lab 6 work in this `LAB6` folder. Lab 7 will be added to this repo later.

Refer to the lab handout for instructions.

## Lab 6 Submission (PES1UG25CS824)

| File | Description |
|------|-------------|
| `CodeCoverageTest_bus_transit_fare.py` | Test cases for code (line) coverage |
| `BranchCoverageTest_bus_transit_fare.py` | Test cases for branch coverage |
| `screenshots/code_coverage.png` | Terminal output: line coverage **100%** |
| `screenshots/branch_coverage.png` | Terminal output: branch coverage **100%** (40/40 branches) |

### Commands

```bash
pip install coverage pytest

# Code (line) coverage
coverage run -m pytest -v CodeCoverageTest_bus_transit_fare.py
coverage report -m

# Branch coverage
coverage run --branch -m pytest -v BranchCoverageTest_bus_transit_fare.py
coverage report -m
```

`.coveragerc` leaves system packages out of the report.
