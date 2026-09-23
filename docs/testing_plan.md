# Testing Plan

## Purpose

Testing verifies that the library cleaning functions remove bad data, preserve valid data, report anomalies, and create the expected output files.

## Test Tool

Tests are written with `pytest` in `tests/test_main.py`.

Run the tests from the project root with:

```bash
python -m pytest -q
```

## Test Coverage

The test suite contains nine tests covering:

| Area | What is checked |
| --- | --- |
| Empty rows | Fully blank book and customer rows are removed. |
| Exact duplicates | Duplicate book rows are removed. |
| Date formats | Checkout and return dates become datetime values. |
| Loan format | `2 weeks` becomes 14 allowed days. |
| ID formats | IDs become nullable integer values. |
| Issue detection | Known missing, invalid, chronological, and unmatched-customer issues are reported. |
| Invalid-record removal | Invalid book IDs are excluded from the final dataset. |
| Final data quality | Validated data has no missing values or duplicates. |
| File output | Cleaned data and the quality report are written to the processed directory. |

## Test Types

### Unit Tests

The tests call individual functions with pandas DataFrames and assert their results. A duplicate loan row is added within a test to prove that duplicate removal works for a nonblank record, not only for the blank padding rows in the source file.

### Pipeline Tests

The GitHub Actions workflow installs the dependencies and runs:

```bash
python -m pytest -q
```

The data-cleaning stage then runs:

```bash
python src/main.py
```

## Expected Result

All tests should pass before processed data is published. If a test fails, the cleaning or delivery stage should not be treated as successful.

## Limitations

The tests currently use the example CSV files and temporary directories for output testing. They do not test a real database upload because the project does not yet have a database destination.

