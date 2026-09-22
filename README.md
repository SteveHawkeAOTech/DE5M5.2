# Library Quality Analysis Automation

## Project Overview

This project has been developed as part of the QA Data Engineering Product Development course.

The aim is to automate a library's quality analysis process by extracting, cleaning, transforming, and preparing data for reporting. The solution uses Python for data processing, GitHub for source control, Azure DevOps for Agile planning and CI/CD automation, and Power BI for visualisation.

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
- Develop a CI/CD pipeline using Azure DevOps
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
├── pipelines/
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
| Azure DevOps | Agile planning and CI/CD |
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

Testing will cover:

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

The current test suite contains eight tests covering the cleaning, validation, summary, record-removal, and output-writing functions.

---

## CI/CD Pipeline

The Azure DevOps pipeline will:

1. Retrieve source code from GitHub
2. Install project dependencies
3. Execute automated tests
4. Run the data transformation process
5. Publish results

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
- Azure DevOps CI/CD Pipeline
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
