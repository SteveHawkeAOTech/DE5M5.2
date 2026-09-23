# Library Quality Analysis Architecture

## Purpose

This project loads library transaction and customer data from CSV files, cleans and validates it, and writes presentable CSV outputs for reporting.

## Components

- `data/raw/library.csv`: source library loan data.
- `data/raw/library_customers.csv`: source customer reference data.
- `src/main.py`: cleaning, validation, summary, and output process.
- `tests/test_main.py`: pytest unit tests.
- `data/processed/`: generated cleaned data and quality report.
- `.github/workflows/library-data.yml`: GitHub Actions test, data-processing, and artifact workflow.
- `.github/workflows/docker-image.yml`: GitHub Actions Docker build and run workflow.
- `Dockerfile`: container definition for the application.

## Processing Flow

```text
Raw CSV files
	|
	v
clean_books() / clean_customers()
	|
	v
validate_data()
	|
	+--> library_quality_issues.csv
	|
	v
remove_invalid_records()
	|
	v
Validated CSV files
```

`clean_books()` and `clean_customers()` remove fully blank rows and exact duplicates, remove unnecessary quotation marks and whitespace, convert IDs to nullable integers, and convert dates to datetime values. Loan periods such as `2 weeks` are converted into an `Allowed days` column.

`validate_data()` reports missing titles, missing customer IDs, invalid checkout dates, checkout dates after the allowed maximum, returns before checkout, and customer IDs missing from the customer reference data.

`remove_invalid_records()` keeps only complete and logically valid book transactions. It does not invent replacement values. Rejected records are described in `library_quality_issues.csv`.

## Outputs

The script writes:

- `data/processed/library_cleaned.csv`
- `data/processed/library_customers_cleaned.csv`
- `data/processed/library_quality_issues.csv`

Raw files are not overwritten.

## CI/CD Architecture

The GitHub Actions workflow uses an `ubuntu-latest` hosted runner and Python 3.13. It runs the tests, executes `src/main.py`, and uploads the processed directory as the `processed-library-data` artifact.

The current delivery target is a GitHub Actions artifact. A database or data lake destination has not yet been implemented.

## Docker Architecture

The Docker image is based on Python 3.13, installs the dependencies from `requirements.txt`, and runs as a non-root `app` user. It copies the source code, tests, and raw data into the image. The container command runs `pytest` first and runs `src/main.py` only when the tests pass.

