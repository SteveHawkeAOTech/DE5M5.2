import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from main import clean_books, clean_customers


DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'raw'


def test_clean_books_removes_blank_and_duplicate_rows():
	books = pd.read_csv(DATA_DIR / 'library.csv')

	cleaned = clean_books(books)

	assert len(cleaned) == 21
	assert not cleaned.duplicated().any()
	assert cleaned['Id'].dtype == 'Int64'


def test_clean_books_normalizes_dates_and_invalid_values():
	books = pd.read_csv(DATA_DIR / 'library.csv')

	cleaned = clean_books(books)

	assert cleaned.loc[0, 'Book checkout'] == pd.Timestamp('2023-02-20')
	assert pd.isna(cleaned.loc[16, 'Book checkout'])
	assert pd.api.types.is_datetime64_any_dtype(cleaned['Book Returned'])


def test_clean_customers_removes_blank_rows_and_converts_ids():
	customers = pd.read_csv(DATA_DIR / 'library_customers.csv')

	cleaned = clean_customers(customers)

	assert len(cleaned) == 8
	assert cleaned['Customer ID'].dtype == 'Int64'
	assert cleaned.loc[0, 'Customer Name'] == 'Jane Doe'

