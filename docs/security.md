# Security Considerations

## Current Data Flow

The application reads CSV files from `data/raw/`, processes them locally or on a GitHub Actions runner, and writes outputs to `data/processed/`. The raw files are preserved and are not overwritten by the script.

## Implemented Controls

- No passwords, tokens, or connection strings are stored in the Python script or workflow.
- Source data is validated before invalid records are included in the final outputs.
- Records with missing required values or impossible dates are rejected rather than silently corrected.
- Quality issues are written to a separate report for review.
- Dependencies are declared in `requirements.txt` and installed by the workflow.
- The GitHub Actions workflow runs tests before cleaning and publishing data.
- Raw input files are kept separate from generated processed files.

## GitHub

The workflow uses GitHub Actions with the minimum permissions needed to read the repository and upload its artifact. Repository Actions settings should restrict who can change workflows and secrets.

The workflow uses a GitHub-hosted Ubuntu runner. If a self-hosted runner is used in future, it should run under a restricted service account and be kept updated.

## Sensitive Data

The example data contains customer names. In a real deployment, access to the repository and workflow artifacts should be restricted. Customer data should not be exposed through public artifacts or unrestricted logs.

## Future Database Deployment

The current workflow publishes processed CSV files as a GitHub Actions artifact and does not connect to a database. If a database or data lake is added, credentials must be stored in GitHub Actions secrets or a secure external secret manager. They must not be committed to YAML, Python files, or CSV files.

The future deployment should also use a restricted service identity, encrypted connections, and least-privilege database permissions.
