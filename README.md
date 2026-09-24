# Library Quality Analysis Automation

## Project Overview

This project has been developed as part of the QA Data Engineering Product Development course.

The aim is to automate a library's quality analysis process by extracting, cleaning, transforming, and preparing data for reporting. The solution uses Python for data processing, GitHub for source control and CI/CD automation, and Power BI for visualisation.

## Business Problem

The library currently performs quality analysis manually. This approach:

- Takes significant staff time
- Is prone to human error
- Produces inconsistent results
- Does not scale efficiently

The objective of this project is to create an automated, repeatable process that improves data quality and reduces manual effort.

---

## Project Objectives

- Create and manage work using an Agile Kanban board
- Store source code in a GitHub repository
- Clean and transform raw data using Python
- Implement automated unit testing
- Develop a CI/CD workflow using GitHub Actions
- Document architecture, testing, and security practices
- Prepare transformed data for reporting and visualisation

---

## Solution Architecture

```text
Raw Data
    |
    v
Python ETL Process
    |
    v
Data Cleaning & Validation
    |
    v
Processed Data Output
    |
    v
Power BI Dashboard
```

---

## Repository Structure

```text
library-quality-analysis/
│
├── data/
│   ├── raw/
│   │   ├── library.csv
│   │   └── library_customers.csv
│   └── processed/
│       ├── library_cleaned.csv
│       ├── library_customers_cleaned.csv
│       └── library_quality_issues.csv
│
├── src/
│   └── main.py
│
├── tests/
│   └── test_main.py
│
├── docs/
│   ├── architecture.md
│   ├── testing_plan.md
│   ├── security.md
│   └── kanban_screenshots/
│
├── .github/
│   └── workflows/
│       ├── library-data.yml
│       └── docker-image.yml
│
├── Dockerfile
│
├── requirements.txt
│
└── README.md
```

---

## Technologies Used

| Technology | Purpose |
|------------|----------|
| Python | Data processing and transformation |
| Pandas | Data manipulation |
| Pytest | Unit testing |
| GitHub | Version control |
| GitHub Actions | Continuous integration and delivery |
| Power BI | Reporting and visualisation |

---

## Data Processing Workflow

The application is implemented in `src/main.py` and performs the following steps:

1. Load the two CSV files from `data/raw/`.
2. Remove fully blank rows and duplicate records.
3. Strip unnecessary quotation marks and whitespace from text values.
4. Convert IDs to nullable integer values.
5. Convert dates from `DD/MM/YYYY` text to datetime values.
6. Convert loan periods such as `2 weeks` into an `Allowed days` value.
7. Detect missing titles, missing customer IDs, invalid dates, future checkout dates, incorrect date order, and unknown customers.
8. Remove book records that cannot be safely corrected without inventing data.
9. Write the validated data and quality report to `data/processed/`.

The main functions are:

- `clean_books()` and `clean_customers()` normalise the source data.
- `validate_data()` creates a report of data-quality issues.
- `remove_invalid_records()` creates the final presentable datasets.
- `build_cleaning_summary()` compares the data before and after cleaning.
- `output_cleaned_csv()` writes the processed CSV files.

The raw files are preserved. Records that are rejected are documented in `library_quality_issues.csv` rather than silently changed.

To run the cleaning script from the project root:

```bash
python src/main.py
```

The script creates or updates:

- `data/processed/library_cleaned.csv`
- `data/processed/library_customers_cleaned.csv`
- `data/processed/library_quality_issues.csv`

---

## Testing

Unit tests are implemented using Pytest in `tests/test_main.py`.

The nine tests are:

1. `test_clean_books_removes_blank_and_duplicate_rows()` removes blank and duplicate book rows and converts book IDs to nullable integers.
2. `test_clean_books_removes_duplicate_loan_records()` removes duplicate loan records.
3. `test_clean_books_normalizes_dates_and_invalid_values()` converts dates and loan periods and handles invalid dates.
4. `test_clean_customers_removes_blank_rows_and_converts_ids()` removes blank customer rows and converts customer IDs to nullable integers.
5. `test_validate_data_reports_observed_quality_issues()` reports the expected data-quality issues and affected book IDs.
6. `test_build_cleaning_summary_shows_cleaning_impact()` verifies the before-and-after cleaning summary.
7. `test_remove_invalid_records_produces_presentable_books_data()` verifies that final book data has no missing values or duplicates.
8. `test_remove_invalid_records_removes_invalid_books()` excludes book records that fail validation.
9. `test_output_cleaned_csv_writes_quality_report()` verifies that all expected processed CSV files are created.

The test coverage includes:

- Removal of empty rows and duplicates
- Date and loan-period format conversion
- Detection of data-quality issues
- Removal of invalid book records
- Missing-value checks on final data
- Creation of processed output files

To execute tests:

```bash
python -m pytest -q
```

The current test suite contains nine tests covering the cleaning, validation, summary, record-removal, duplicate-handling, and output-writing functions.

---

## GitHub Actions CI/CD

The workflow is defined in `.github/workflows/library-data.yml`. GitHub runs it when code is pushed to `main`, when a pull request targets `main`, or when it is started manually from the Actions tab.

The workflow uses an Ubuntu runner, installs Python 3.13 and the dependencies in `requirements.txt`, runs the nine pytest tests, executes `src/main.py`, and uploads `data/processed/` as the `processed-library-data` artifact.

The workflow provides continuous integration by testing every change and continuous delivery by publishing the processed data artifact after the tests and cleaning process succeed.

The project does not currently load data into a database or data lake. That would require a selected service, credentials, and an additional upload step.

### Docker

The `Dockerfile` uses Python 3.13, installs the packages in `requirements.txt` (`pandas` and `pytest`), copies the application, tests, and raw data, and runs the tests before the application:

```text
pytest -> src/main.py
```

Build and run the image from the project root:

```bash
docker build . --file Dockerfile --tag library-quality-analysis:local
docker run --rm library-quality-analysis:local
```

The Docker workflow in `.github/workflows/docker-image.yml` performs the same steps in GitHub Actions. On pushes to `main`, it publishes the image to GitHub Container Registry with both the commit SHA and `latest` tags. Pull requests build and test the image but do not publish it. The application currently requires no secrets or environment variables; the workflow uses GitHub's built-in `GITHUB_TOKEN` for registry authentication.

After the workflow completes, pull the latest published image with:

```bash
docker pull ghcr.io/<github-owner>/<repository>:latest
docker run --rm ghcr.io/<github-owner>/<repository>:latest
```

Replace `<github-owner>/<repository>` with the GitHub repository path, for example `octocat/library-quality-analysis`.

---

## Security Considerations

The following security practices are applied:

- No credentials stored in source code
- Input validation on source data
- Principle of least privilege
- Secure repository access
- Protected main branch
- Regular dependency updates

---

## Project Deliverables

- Agile Kanban Board
- GitHub Repository
- Python Data Transformation Application
- Unit Testing Suite
- GitHub Actions CI/CD Workflow
- Architecture Documentation
- Security Review
- Power BI Dashboard
- Final Presentation

---

## Future Enhancements

Potential improvements include:

- Automated data ingestion from external sources
- Data quality scoring
- Automated email reporting
- Cloud-based storage
- Advanced data validation rules

---

## Author

**Stephen Hawke**  
Academic and Operations Technologist

Developed as part of the QA Data Engineering Product Development programme.
