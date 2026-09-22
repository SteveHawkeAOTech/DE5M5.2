# This script loads and cleans library transaction and customer reference data from CSV files.
# It follows Data Quality principles looking for:
# - Missing values
# - Invalid values
# - Duplicates

from pathlib import Path

import pandas as pd

# Define the columns that should be treated as dates in the books DataFrame
DATE_COLUMNS = ['Book checkout', 'Book Returned']
QUALITY_COLUMNS = ['Issue', 'Book IDs']

# Functions to clean the books and customers DataFrames, as well as a function to load and clean both datasets. 
# The cleaning functions remove blank rows, duplicates, normalize date formats, and convert ID columns to numeric types. 
# The main block loads the data from the specified directory and prints information about the cleaned DataFrames.

def clean_books(books: pd.DataFrame) -> pd.DataFrame:
	"""Return a cleaned copy of the library transactions."""
	print(f'Cleaning {len(books)} rows of library transactions...')
	cleaned = books.dropna(how='all').drop_duplicates().copy() # Drop rows that are completely blank and remove duplicate rows, then create a copy of the DataFrame to avoid modifying the original.

	cleaned['Books'] = (
		cleaned['Books']
		.astype('string') # Convert the 'Books' column to string type
		.str.replace('"', '', regex=False) # Remove any double quotes from the 'Books' column
		.str.strip() # Remove leading and trailing whitespace from the 'Books' column
	)

	for column in DATE_COLUMNS:
		values = (
			cleaned[column] # Select the column from the cleaned DataFrame
			.astype('string') # Convert the column to string type
			.str.replace('"', '', regex=False) # Remove any double quotes from the column
			.str.strip() # Remove leading and trailing whitespace from the column
		)
		cleaned[column] = pd.to_datetime(
			values,
			format='%d/%m/%Y', # Specify the expected date format for parsing
			dayfirst=True, # Indicate that the day comes first in the date format
			errors='coerce', # Convert invalid date strings to NaT (Not a Time) instead of raising an error
		)

	for column in ['Id', 'Customer ID']:
		cleaned[column] = pd.to_numeric(cleaned[column], errors='coerce').astype('Int64') # Convert the specified columns to numeric type, coercing errors to NaN, and then convert to nullable integer type 'Int64'.

	cleaned['Allowed days'] = pd.to_numeric(
		cleaned['Days allowed to borrow'].astype('string').str.extract(r'(\d+)')[0],
		errors='coerce',
	).mul(7).astype('Int64')

	return cleaned.reset_index(drop=True) # Reset the index of the cleaned DataFrame, dropping the old index and returning a new DataFrame with a default integer index.

# Function to validate the cleaned data for quality issues, returning a DataFrame of observed issues without modifying the cleaned data.

def validate_data(
	books: pd.DataFrame, # The cleaned books DataFrame containing library transaction data.
	customers: pd.DataFrame, # The cleaned customers DataFrame containing customer reference data.
	maximum_date: pd.Timestamp, # The maximum allowed date for book checkouts, used to identify any transactions that exceed this limit.
) -> pd.DataFrame:
	"""Return data-quality issues without changing the cleaned data."""
	issues: list[dict[str, object]] = []

	# Helper function to add quality issues to the issues list based on specific conditions in the books DataFrame. 
	# It checks for missing values, invalid dates, and other data quality problems, appending relevant information to the issues list.
	def add_issue(issue: str, rows: pd.Series) -> None:
		for book_id in books.loc[rows, 'Id'].dropna().tolist(): # Iterate over the 'Id' values of the books DataFrame where the specified condition (rows) is True, dropping any NaN values and converting the result to a list.
			issues.append({'Issue': issue, 'Book IDs': int(book_id)}) # Append a dictionary to the issues list containing the issue description and the corresponding book ID, converting the book ID to an integer.

	add_issue('Missing book title', books['Books'].isna()) # Check for missing book titles in the 'Books' column of the books DataFrame and add an issue for each occurrence.
	add_issue('Missing customer ID', books['Customer ID'].isna()) # Check for missing customer IDs in the 'Customer ID' column of the books DataFrame and add an issue for each occurrence.
	add_issue('Invalid checkout date', books['Book checkout'].isna()) # Check for invalid checkout dates in the 'Book checkout' column of the books DataFrame and add an issue for each occurrence.
	add_issue('Checkout date is after the allowed maximum', books['Book checkout'] > maximum_date) # Check for checkout dates that exceed the specified maximum date in the 'Book checkout' column of the books DataFrame and add an issue for each occurrence.
	add_issue(
		'Return date is before checkout date',
		books['Book Returned'].notna() # Check for return dates that are not null in the 'Book Returned' column of the books DataFrame
		& books['Book checkout'].notna() # Check for checkout dates that are not null in the 'Book checkout' column of the books DataFrame
		& (books['Book Returned'] < books['Book checkout']), # Check for return dates that are earlier than the corresponding checkout dates in the books DataFrame, indicating a data quality issue.
	)

	known_customer_ids = customers['Customer ID'].dropna()
	add_issue(
		'Customer ID is not in customer reference data',
		books['Customer ID'].notna() & ~books['Customer ID'].isin(known_customer_ids), # Check for customer IDs in the 'Customer ID' column of the books DataFrame that are not null and not present in the known customer IDs from the customers DataFrame, indicating a data quality issue.
	)

	return pd.DataFrame(issues, columns=QUALITY_COLUMNS)

# Function to clean the customer reference data
# Follows a similar approach to clean_books, removing blank rows and duplicates, 
# normalizing the 'Customer Name' column, and converting 'Customer ID' to numeric type.

def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
	"""Return a cleaned copy of the customer reference data."""
	print(f'Cleaning {len(customers)} rows of customer data...')
	cleaned = customers.dropna(how='all').drop_duplicates().copy() # Drop rows that are completely blank and remove duplicate rows, then create a copy of the DataFrame to avoid modifying the original.
	cleaned['Customer Name'] = (
		cleaned['Customer Name']
		.astype('string')
		.str.replace('"', '', regex=False)
		.str.strip()
	)
	cleaned['Customer ID'] = pd.to_numeric(
		cleaned['Customer ID'], errors='coerce').astype('Int64') # Convert the 'Customer ID' column to numeric type, coercing errors to NaN, and then convert to nullable integer type 'Int64'.
	
	return cleaned.reset_index(drop=True) # Reset the index of the cleaned DataFrame, dropping the old index and returning a new DataFrame with a default integer index.

# Function to load and clean both the books and customers datasets from the specified data directory.

def load_and_clean_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
	"""Load both source files and apply the cleaning rules."""
	books = pd.read_csv(data_dir / 'library.csv') # Read the library transactions CSV file into a DataFrame named 'books' from the specified data directory.
	customers = pd.read_csv(data_dir / 'library_customers.csv') # Read the customer reference CSV file into a DataFrame named 'customers' from the specified data directory.
	return clean_books(books), clean_customers(customers)

# Main block to load and clean the data when the script is run directly. It prints information about the cleaned DataFrames.

if __name__ == '__main__':
	data_directory = Path(__file__).resolve().parents[1] / 'data' / 'raw' # Determine the path to the raw data directory relative to the script's location.
	books, customers = load_and_clean_data(data_directory) # Load and clean the books and customers datasets from the specified data directory.
	quality_issues = validate_data(
		books,
		customers,
		maximum_date=pd.Timestamp('2026-12-31'),
	)
	print(books.info())
	print(customers.info())
	print(quality_issues.to_string(index=False))