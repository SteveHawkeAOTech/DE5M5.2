# Library Quality Analysis Architecture

## Purpose

This project loads library transaction and customer data from CSV files, cleans and validates it, and writes presentable CSV outputs for reporting.

## Components

- `data/raw/library.csv`: source library loan data.
- `data/raw/library_customers.csv`: source customer reference data.
- `src/main.py`: cleaning, validation, summary, and output process.
- `tests/test_main.py`: pytest unit tests.
- `data/processed/`: generated cleaned data and quality report.
- `pipeline/continuous_integration.yaml`: test and data-processing pipeline.
- `pipeline/continuous_delivery.yaml`: test, data-build, and artifact-deployment pipeline.

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

Both Azure DevOps pipelines use an `ubuntu-latest` Microsoft-hosted agent and Python 3.13.

The continuous integration pipeline runs tests, executes `src/main.py`, and publishes the processed directory as an artifact.

The continuous delivery pipeline runs a test stage, builds the processed data, publishes the artifact, and then uses a `deployment` job with the `Library-Production` environment and a `runOnce` strategy to download and confirm the artifact.

The current deployment target is an Azure DevOps pipeline artifact. A database or data lake destination has not yet been implemented.

