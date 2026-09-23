# Security Considerations

## Current Data Flow

The application reads CSV files from `data/raw/`, processes them locally or on an Azure DevOps build agent, and writes outputs to `data/processed/`. The raw files are preserved and are not overwritten by the script.

## Implemented Controls

- No passwords, tokens, or connection strings are stored in the Python script or YAML files.
- Source data is validated before invalid records are included in the final outputs.
- Records with missing required values or impossible dates are rejected rather than silently corrected.
- Quality issues are written to a separate report for review.
- Dependencies are declared in `requirements.txt` and installed by the pipeline.
- The pipelines run tests before cleaning and publishing data.
- The continuous delivery pipeline uses an Azure DevOps environment named `Library-Production`, which can support approvals and checks.
- The raw input files are kept separate from generated processed files.

## Azure DevOps and GitHub

The repository connection and Azure Pipelines GitHub app should be configured through Azure DevOps and GitHub rather than by placing credentials in the repository. The pipeline should use the minimum permissions needed to read the repository and publish its artifact.

If a self-hosted agent is used, it should run under a restricted service account and be kept updated. The current YAML uses Microsoft-hosted Ubuntu agents, so the local Windows agent is not required by the committed pipeline files.

## Sensitive Data

The example data contains customer names. In a real deployment, access to the repository, pipeline artifacts, and `Library-Production` environment should be restricted. Customer data should not be exposed through public artifacts or unrestricted logs.

## Future Database Deployment

The current pipeline publishes processed CSV files as an Azure DevOps artifact and does not connect to a database. If a database or data lake is added, credentials must be stored in Azure Key Vault, secret pipeline variables, or a service connection. They must not be committed to YAML, Python files, or CSV files.

The future deployment should also use a restricted service identity, encrypted connections, least-privilege database permissions, and an approval check for the production environment.

