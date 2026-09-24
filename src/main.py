"""Load, clean, validate, and export the library data."""

from pathlib import Path

import pandas as pd

DATE_COLUMNS = ['Book checkout', 'Book Returned']
QUALITY_COLUMNS = ['Issue', 'Book IDs']
SUMMARY_COLUMNS = ['Dataset', 'Metric', 'Before', 'After', 'Change']
MAX_CHECKOUT_DATE = pd.Timestamp('2023-12-31')

# Function to clean the library transactions data
def clean_books(books: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the library transactions."""
    print(f'Cleaning {len(books)} rows of library transactions...')
    cleaned = books.dropna(how='all').drop_duplicates().copy()

    cleaned['Books'] = (
        cleaned['Books']
        .astype('string') # Convert the 'Books' column to string type
        .str.replace('"', '', regex=False)
        .str.strip() # Remove leading and trailing whitespace from the 'Books' column
    )

    for column in DATE_COLUMNS:
        values = (
            cleaned[column]
            .astype('string')
            .str.replace('"', '', regex=False)
            .str.strip()
        )
        cleaned[column] = pd.to_datetime(
            values,
            format='%d/%m/%Y',
            errors='coerce',
        )


    for column in ['Id', 'Customer ID']:
        cleaned[column] = pd.to_numeric(
            cleaned[column], errors='coerce'
        ).astype('Int64')

    cleaned['Allowed days'] = pd.to_numeric(
        cleaned['Days allowed to borrow'].astype('string').str.extract(r'(\d+)')[0],
        errors='coerce',
    ).mul(7).astype('Int64')

    return cleaned.reset_index(drop=True)

# Function to validate the cleaned data and identify quality issues
def validate_data(
    books: pd.DataFrame,
    customers: pd.DataFrame,
    maximum_date: pd.Timestamp,
) -> pd.DataFrame:
    """Return data-quality issues without changing the cleaned data."""
    issues: list[dict[str, object]] = []

    def add_issue(issue: str, rows: pd.Series) -> None:
        for book_id in books.loc[rows, 'Id'].dropna().tolist():
            issues.append({'Issue': issue, 'Book IDs': int(book_id)})

    add_issue('Missing book title', books['Books'].isna())
    add_issue('Missing customer ID', books['Customer ID'].isna())
    add_issue('Invalid checkout date', books['Book checkout'].isna())
    add_issue(
        'Checkout date is after the allowed maximum',
        books['Book checkout'] > maximum_date,
    )
    add_issue(
        'Return date is before checkout date',
        books['Book Returned'].notna()
        & books['Book checkout'].notna()
        & (books['Book Returned'] < books['Book checkout']),
    )

    known_customer_ids = customers['Customer ID'].dropna()
    add_issue(
        'Customer ID is not in customer reference data',
        books['Customer ID'].notna()
        & ~books['Customer ID'].isin(known_customer_ids),
    )

    return pd.DataFrame(issues, columns=QUALITY_COLUMNS)

# Function to remove records that cannot be safely corrected from the source data
def remove_invalid_records(
    books: pd.DataFrame,
    customers: pd.DataFrame,
    maximum_date: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Remove records that cannot be safely corrected from the source data."""
    known_customer_ids = customers['Customer ID'].dropna()
    valid_books = (
        books['Id'].notna()
        & books['Books'].notna()
        & books['Customer ID'].notna()
        & books['Book checkout'].notna()
        & books['Book Returned'].notna()
        & (books['Book checkout'] <= maximum_date)
        & (books['Book Returned'] >= books['Book checkout'])
        & books['Customer ID'].isin(known_customer_ids)
    )
    return books.loc[valid_books].reset_index(drop=True), customers.copy()

# Function to build a summary of the cleaning impact
def build_cleaning_summary(
    raw_books: pd.DataFrame,
    cleaned_books: pd.DataFrame,
    raw_customers: pd.DataFrame,
    cleaned_customers: pd.DataFrame,
) -> pd.DataFrame:
    """Build a before-and-after summary of the cleaning impact."""
    def invalid_date_count(data: pd.DataFrame, column: str) -> int:
        values = (
            data[column]
            .astype('string')
            .str.replace('"', '', regex=False)
            .str.strip()
        )
        nonblank_values = values[values.notna() & values.ne('')]
        parsed_dates = pd.to_datetime(
            nonblank_values,
            format='%d/%m/%Y',
            errors='coerce',
        )
        return int(parsed_dates.isna().sum())

    def add_metric(
        rows: list[dict[str, object]],
        dataset: str,
        metric: str,
        before: int,
        after: int,
    ) -> None:
        rows.append({
            'Dataset': dataset,
            'Metric': metric,
            'Before': before,
            'After': after,
            'Change': after - before,
        })

    rows: list[dict[str, object]] = []
    for dataset, raw, cleaned in [
        ('Books', raw_books, cleaned_books),
        ('Customers', raw_customers, cleaned_customers),
    ]:
        add_metric(rows, dataset, 'Rows', len(raw), len(cleaned))
        add_metric(
            rows,
            dataset,
            'Fully blank rows',
            int(raw.isna().all(axis=1).sum()),
            0,
        )
        add_metric(
            rows,
            dataset,
            'Duplicate rows',
            int(raw.duplicated().sum()),
            int(cleaned.duplicated().sum()),
        )
        add_metric(
            rows,
            dataset,
            'Missing cells',
            int(raw.isna().sum().sum()),
            int(cleaned.isna().sum().sum()),
        )

    add_metric(
        rows,
        'Books',
        'Invalid checkout dates',
        invalid_date_count(raw_books, 'Book checkout'),
        int(cleaned_books['Book checkout'].isna().sum()),
    )
    add_metric(
        rows,
        'Books',
        'Invalid return dates',
        invalid_date_count(raw_books, 'Book Returned'),
        int(cleaned_books['Book Returned'].isna().sum()),
    )
    add_metric(
        rows,
        'Books',
        'Rejected invalid rows',
        0,
        len(raw_books) - len(cleaned_books),
    )
    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)

# Function to print the cleaning summary in a compact table
def print_cleaning_summary(summary: pd.DataFrame) -> None:
    """Print the cleaning impact in a compact table."""
    print('\nCleaning impact summary:')
    print(summary.to_string(index=False))

# Function to clean the customer reference data
def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the customer reference data."""
    print(f'Cleaning {len(customers)} rows of customer data...')
    cleaned = customers.dropna(how='all').drop_duplicates().copy()
    cleaned['Customer Name'] = (
        cleaned['Customer Name']
        .astype('string')
        .str.replace('"', '', regex=False)
        .str.strip()
    )
    cleaned['Customer ID'] = pd.to_numeric(
        cleaned['Customer ID'], errors='coerce'
    ).astype('Int64')

    return cleaned.reset_index(drop=True)

# Function to load and clean both source files
def load_and_clean_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load both source files and apply the cleaning rules."""
    books = pd.read_csv(data_dir / 'library.csv')
    customers = pd.read_csv(data_dir / 'library_customers.csv')
    return clean_books(books), clean_customers(customers)

# Function to write the cleaned data and quality report to the processed folder
def output_cleaned_csv(
    books: pd.DataFrame,
    customers: pd.DataFrame,
    quality_issues: pd.DataFrame,
    data_dir: Path,
) -> None:
    """Write cleaned data and the quality report to the processed folder."""
    processed_dir = data_dir.parent / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)
    books.to_csv(processed_dir / 'library_cleaned.csv', index=False)
    customers.to_csv(processed_dir / 'library_customers_cleaned.csv', index=False)
    quality_issues.to_csv(processed_dir / 'library_quality_issues.csv', index=False)

if __name__ == '__main__':
    data_directory = Path(__file__).resolve().parents[1] / 'data' / 'raw'
    raw_books = pd.read_csv(data_directory / 'library.csv')
    raw_customers = pd.read_csv(data_directory / 'library_customers.csv')
    cleaned_books = clean_books(raw_books)
    cleaned_customers = clean_customers(raw_customers)
    quality_issues = validate_data(
        cleaned_books,
        cleaned_customers,
        MAX_CHECKOUT_DATE,
    )
    validated_books, validated_customers = remove_invalid_records(
        cleaned_books,
        cleaned_customers,
        MAX_CHECKOUT_DATE,
    )
    output_cleaned_csv(
        validated_books,
        validated_customers,
        quality_issues,
        data_directory,
    )
    validated_books.info()
    validated_customers.info()
    print_cleaning_summary(
        build_cleaning_summary(
            raw_books,
            validated_books,
            raw_customers,
            validated_customers,
        )
    )
    print('\nData quality issues:')
    print(quality_issues.to_string(index=False))
    print(f'\nCleaned files written to {data_directory.parent / "processed"}')
