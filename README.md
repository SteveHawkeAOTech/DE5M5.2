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
│   └── processed/
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

The application performs the following steps:

1. Load source data
2. Validate data quality
3. Remove duplicate records
4. Handle missing values
5. Standardise formats and text values
6. Export cleaned data
7. Make output available for reporting

---

## Testing

Unit tests will be implemented using Pytest.

Testing will cover:

- Data loading
- Duplicate removal
- Null value handling
- Data transformation functions
- Output file creation

To execute tests:

```bash
pytest
```

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
