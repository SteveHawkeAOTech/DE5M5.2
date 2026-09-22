"""Tests for the library data-cleaning pipeline."""

import sys
from pathlib import Path

import pandas as pd

# Allow the tests to import the application module from src.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from main import (
	MAX_CHECKOUT_DATE,
	build_cleaning_summary,
	clean_books,
	clean_customers,
	output_cleaned_csv,
	remove_invalid_records,
	validate_data,
)

DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'raw'

# Check that blank rows are removed from the book data.
def test_clean_books_removes_blank_and_duplicate_rows():
	books = pd.read_csv(DATA_DIR / 'library.csv')

	cleaned = clean_books(books)

	assert len(cleaned) == 21
	assert cleaned.duplicated().sum() == 0
	assert cleaned['Id'].dtype == 'Int64'

# Check that a duplicate nonblank loan record is removed.
def test_clean_books_removes_duplicate_loan_records():
	books = pd.read_csv(DATA_DIR / 'library.csv')
	books_with_duplicate = pd.concat([books, books.iloc[[0]]], ignore_index=True)

	cleaned = clean_books(books_with_duplicate)

	assert len(cleaned) == 21
	assert cleaned['Id'].duplicated().sum() == 0

# Check that book dates and loan duration are converted to the expected formats.
def test_clean_books_normalizes_dates_and_invalid_values():
	books = pd.read_csv(DATA_DIR / 'library.csv')

	cleaned = clean_books(books)

	assert cleaned.loc[0, 'Book checkout'] == pd.Timestamp('2023-02-20')
	assert pd.isna(cleaned.loc[16, 'Book checkout'])
	assert pd.api.types.is_datetime64_any_dtype(cleaned['Book Returned'])
	assert cleaned.loc[0, 'Allowed days'] == 14

# Check that blank customer rows are removed and customer IDs are numeric.
def test_clean_customers_removes_blank_rows_and_converts_ids():
	customers = pd.read_csv(DATA_DIR / 'library_customers.csv')

	cleaned = clean_customers(customers)

	assert len(cleaned) == 8
	assert cleaned['Customer ID'].dtype == 'Int64'
	assert cleaned.loc[0, 'Customer Name'] == 'Jane Doe'

# Check that known data-quality problems are reported with the correct book IDs.
def test_validate_data_reports_observed_quality_issues():
	books = clean_books(pd.read_csv(DATA_DIR / 'library.csv'))
	customers = clean_customers(pd.read_csv(DATA_DIR / 'library_customers.csv'))

	issues = validate_data(books, customers, MAX_CHECKOUT_DATE)

	assert set(issues.loc[issues['Issue'] == 'Invalid checkout date', 'Book IDs']) == {17}
	assert set(issues.loc[issues['Issue'] == 'Missing book title', 'Book IDs']) == {21}
	assert set(issues.loc[issues['Issue'] == 'Missing customer ID', 'Book IDs']) == {21}
	assert set(issues.loc[issues['Issue'] == 'Checkout date is after the allowed maximum', 'Book IDs']) == {7}
	assert set(issues.loc[issues['Issue'] == 'Customer ID is not in customer reference data', 'Book IDs']) == {4, 19}
	assert set(issues.loc[issues['Issue'] == 'Return date is before checkout date', 'Book IDs']) == {2, 3, 4, 5, 7, 8}

# Check that the summary shows how the data changed during cleaning.
def test_build_cleaning_summary_shows_cleaning_impact():
	raw_books = pd.read_csv(DATA_DIR / 'library.csv')
	raw_customers = pd.read_csv(DATA_DIR / 'library_customers.csv')
	cleaned_books = clean_books(raw_books)
	cleaned_customers = clean_customers(raw_customers)

	summary = build_cleaning_summary(
		raw_books,
		cleaned_books,
		raw_customers,
		cleaned_customers,
	)

	rows = summary.set_index(['Dataset', 'Metric'])
	assert tuple(rows.loc[('Books', 'Rows'), ['Before', 'After', 'Change']]) == (114, 21, -93)
	assert tuple(rows.loc[('Books', 'Fully blank rows'), ['Before', 'After', 'Change']]) == (93, 0, -93)
	assert tuple(rows.loc[('Books', 'Invalid checkout dates'), ['Before', 'After', 'Change']]) == (1, 1, 0)
	assert tuple(rows.loc[('Books', 'Rejected invalid rows'), ['Before', 'After', 'Change']]) == (0, 93, 93)

# Check that the final book and customer data contains no missing values or duplicates.
def test_remove_invalid_records_produces_presentable_books_data():
	books = clean_books(pd.read_csv(DATA_DIR / 'library.csv'))
	customers = clean_customers(pd.read_csv(DATA_DIR / 'library_customers.csv'))

	cleaned_books, cleaned_customers = remove_invalid_records(
		books,
		customers,
		MAX_CHECKOUT_DATE,
	)

	assert len(cleaned_books) == 12
	assert cleaned_books.isna().sum().sum() == 0
	assert not cleaned_books.duplicated().any()
	assert cleaned_customers.isna().sum().sum() == 0

# Check that specific invalid book records are excluded from the final data.
def test_remove_invalid_records_removes_invalid_books():
	books = clean_books(pd.read_csv(DATA_DIR / 'library.csv'))
	customers = clean_customers(pd.read_csv(DATA_DIR / 'library_customers.csv'))

	cleaned_books, _ = remove_invalid_records(
		books,
		customers,
		MAX_CHECKOUT_DATE,
	)

	book_ids = set(cleaned_books['Id'])
	assert 17 not in book_ids  # Invalid checkout date.
	assert 21 not in book_ids  # Missing title and customer ID.
	assert 7 not in book_ids  # Checkout date exceeds the allowed maximum.

# Check that all expected cleaned CSV files are written to the processed folder.
def test_output_cleaned_csv_writes_quality_report(tmp_path):
	books = clean_books(pd.read_csv(DATA_DIR / 'library.csv'))
	customers = clean_customers(pd.read_csv(DATA_DIR / 'library_customers.csv'))
	quality_issues = validate_data(books, customers, MAX_CHECKOUT_DATE)
	validated_books, validated_customers = remove_invalid_records(
		books,
		customers,
		MAX_CHECKOUT_DATE,
	)

	output_cleaned_csv(
		validated_books,
		validated_customers,
		quality_issues,
		tmp_path / 'raw',
	)

	processed_dir = tmp_path / 'processed'
	assert (processed_dir / 'library_cleaned.csv').exists()
	assert (processed_dir / 'library_customers_cleaned.csv').exists()
	assert (processed_dir / 'library_quality_issues.csv').exists()

