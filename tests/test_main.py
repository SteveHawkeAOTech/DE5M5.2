# This script contains unit tests for the data cleaning and validation functions defined in src/main.py. 
# It uses the pytest framework to run the tests, which check that the cleaning functions correctly:
# - remove blank and duplicate rows
# - normalize date formats 
# - convert ID columns to numeric types
# - the validation function accurately identifies data quality issues in the cleaned datasets.

import sys
from pathlib import Path

import pandas as pd

# Add the src directory to the system path to allow importing the main module for testing.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

# Import the cleaning and validation functions from the main module for testing.
from main import (
	MAX_CHECKOUT_DATE,
	build_cleaning_summary,
	clean_books,
	clean_customers,
	output_cleaned_csv,
	remove_invalid_records,
	validate_data,
)

# Define the path to the raw data directory, which contains the CSV files used for testing the cleaning and validation functions.
DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'raw'

# Test functions to verify the behavior of the cleaning and validation functions. 
# Each test function loads the relevant CSV file, applies the cleaning or validation function, and asserts that the output meets the expected conditions.
def test_clean_books_removes_blank_and_duplicate_rows():
	books = pd.read_csv(DATA_DIR / 'library.csv')
	duplicate_count_before = int(books.duplicated().sum())

	cleaned = clean_books(books)

	assert len(cleaned) == 21 # Check that the cleaned DataFrame has the expected number of rows after removing blank and duplicate rows.
	assert duplicate_count_before > 0 # Check that the source data contains duplicates to clean.
	assert cleaned.duplicated().sum() == 0 # Check that duplicate rows have been removed.
	assert cleaned['Id'].dtype == 'Int64' # Check that the 'Id' column in the cleaned DataFrame is of the expected numeric type 'Int64'.

# Test function to verify that the clean_books function correctly normalizes date formats and handles invalid values in the 'Book checkout' and 'Book Returned' columns.
def test_clean_books_normalizes_dates_and_invalid_values():
	books = pd.read_csv(DATA_DIR / 'library.csv')

	cleaned = clean_books(books)

	assert cleaned.loc[0, 'Book checkout'] == pd.Timestamp('2023-02-20') # Check that the first row's 'Book checkout' date is correctly normalized to a Timestamp object.
	assert pd.isna(cleaned.loc[16, 'Book checkout']) # Check that the 17th row's 'Book checkout' date is NaN, indicating that invalid values were correctly handled.
	assert pd.api.types.is_datetime64_any_dtype(cleaned['Book Returned']) # Check that the 'Book Returned' column in the cleaned DataFrame is of a datetime type, indicating that date normalization was successful.
	assert cleaned.loc[0, 'Allowed days'] == 14 # Check that the 'Allowed days' column in the first row is correctly calculated based on the 'Days allowed to borrow' column, confirming that the conversion to numeric and multiplication by 7 was successful.

# Test function to verify that the clean_customers function correctly removes blank rows and converts the 'Customer ID' column to a numeric type.
def test_clean_customers_removes_blank_rows_and_converts_ids():
	customers = pd.read_csv(DATA_DIR / 'library_customers.csv')

	cleaned = clean_customers(customers)

	assert len(cleaned) == 8 # Check that the cleaned DataFrame has the expected number of rows after removing blank rows.
	assert cleaned['Customer ID'].dtype == 'Int64' # Check that the 'Customer ID' column in the cleaned DataFrame is of the expected numeric type 'Int64'.
	assert cleaned.loc[0, 'Customer Name'] == 'Jane Doe' # Check that the first row's 'Customer Name' is correctly set.

# Test function to verify that the validate_data function correctly identifies and reports observed data quality issues in the cleaned books and customers DataFrames.
def test_validate_data_reports_observed_quality_issues():
	books = clean_books(pd.read_csv(DATA_DIR / 'library.csv'))
	customers = clean_customers(pd.read_csv(DATA_DIR / 'library_customers.csv'))

	issues = validate_data(books, customers, pd.Timestamp('2026-12-31'))

	assert set(issues.loc[issues['Issue'] == 'Invalid checkout date', 'Book IDs']) == {17} # Check that the 'Invalid checkout date' issue is correctly reported for the book with ID 17.
	assert set(issues.loc[issues['Issue'] == 'Missing book title', 'Book IDs']) == {21} # Check that the 'Missing book title' issue is correctly reported for the book with ID 21.
	assert set(issues.loc[issues['Issue'] == 'Missing customer ID', 'Book IDs']) == {21} # Check that the 'Missing customer ID' issue is correctly reported for the book with ID 21.
	assert set(issues.loc[issues['Issue'] == 'Checkout date is after the allowed maximum', 'Book IDs']) == {7} # Check that the 'Checkout date is after the allowed maximum' issue is correctly reported for the book with ID 7.
	assert set(issues.loc[issues['Issue'] == 'Customer ID is not in customer reference data', 'Book IDs']) == {4, 19} # Check that the 'Customer ID is not in customer reference data' issue is correctly reported for the books with IDs 4 and 19.
	assert set(issues.loc[issues['Issue'] == 'Return date is before checkout date', 'Book IDs']) == {2, 3, 4, 5, 7, 8} # Check that the 'Return date is before checkout date' issue is correctly reported for the books with IDs 2, 3, 4, 5, 7, and 8.

# Test function to verify that the build_cleaning_summary function correctly summarizes the impact of the cleaning process on both the books and customers DataFrames, including counts before and after cleaning and the change in counts for each metric.
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

