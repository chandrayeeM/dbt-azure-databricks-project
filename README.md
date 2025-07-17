# DBT Azure Databricks Project

This project builds a robust data pipeline using **dbt** on **Databricks**, with full **CI/CD** automation through **GitHub Actions**. The pipeline ingests, transforms, and analyzes aviation data from:

- `airports.csv`
- `countries.csv`
- `runways.csv`

### Key Features

- Data ingestion via `dbt seed`
-  Transformations using modular `dbt` models
-  Automated job deployment on Databricks
-  GitHub Actions CI/CD pipeline
-  Secure secrets management
-  RBAC roles for development and production environments

## Project Structure

├── .github/workflows/
│ └── deploy.yml            # CI/CD pipeline
├── jobs/
│ └── airport_pipeline.json # Databricks job definition
├── macros/
├── models/
│ ├── staging/
│ └── intermediate/
│ └── marts/
├── scripts/
│ └── deploy_jobs.py        # Python script to deploy Databricks jobs
├── seeds/
│ ├── airports.csv
│ ├── countries.csv
│ └── runways.csv
├── dbt_project.yml
├── profiles.yml
├── packages.yml
├── requirements.txt
└── README.md

## Approach

This project was implemented following a modular and scalable data engineering workflow, optimized for automation and CI/CD.

### 1. Data Ingestion
- Used `dbt seed` to ingest raw CSV files: `airports.csv`, `countries.csv`, and `runways.csv`.
- These files are stored in the `seeds/` directory and managed by dbt.

### 2. Data Modeling
- Applied the layered dbt modeling approach:
  - `staging/`: Initial staging and standardization of seed data.
  - `intermediate/`: Enriched and joined datasets for analytical modeling.
  - `marts/`: Final data marts answering the assignment questions.

### 3. Transformation Logic
- SQL-based transformation logic defined in `models/`.
- Key models:
  - `fct_country_airport_rankings.sql`: Ranks countries by number of airports.
  - `fct_longest_shortest_runways.sql`: Identifies countries with longest and shortest runways.

### 4. Job Deployment
- A reusable Python script `deploy_jobs.py` was created to deploy the dbt job using the Databricks Jobs API.
- The job is defined in `jobs/airport_pipeline.json`.

### 5. 🔁



# Local Development Set up

1. Create and source a virtual enviroment:
   - With venv:
      1. `python3 -m venv ./venv`
      2. `source ./venv/bin/activate`
   - With conda:
      1. `conda create -n dbt-lake python=3.9`
      2. `conda activate dbt-lake`
2. Install requirements: `pip install -r requirements.txt`
4. Create a work cluster in the Databricks workspace
5. Export the following environment variables. 
   ``` bash
   export DATABRICKS_SCHEMA="<your name>""
   export DATABRICKS_HOST="adb-<databricks organization ID>.<random number>.azuredatabricks.net"
   export DATABRICKS_TOKEN="<databricks token>"
   export DATABRICKS_ORGANIZATION="<databricks organization ID>"
   export DATABRICKS_HTTP_PATH="<find this in your cluster -> JDBC/ODBC -> HTTP Path>"
   export ENV="dev/prod"
   ```
6. Copy `profiles.yml` to ~/.dbt/ (on Macbook)
7. Import dbt dependency modules: `dbt deps`
8. Test your connection: `dbt debug --profiles-dir ~/.dbt/`

##  CI/CD Pipeline

- Defined in `.github/workflows/deploy.yml`
- Automatically runs on push to `main`
- Can be manually triggered from other branches
- Deploys job to Databricks using `deploy_jobs.py`
- Uses GitHub secrets for secure credentials

###  Example Secrets

| Secret Name               | Description                      |
|---------------------------|----------------------------------|
| `DATABRICKS_HOST`         | Databricks workspace URL         |
| `DATABRICKS_TOKEN`        | Personal Access Token            |
| `DATABRICKS_HTTP_PATH`    | Cluster SQL warehouse path       |
| `DATABRICKS_SCHEMA`       | Target schema name               |
| `DATABRICKS_ORGANIZATION` | Org ID if required               |
| `ENV`                     | dev / prod                       |

##  Databricks Job Configuration

The job is defined in the `jobs/airport_pipeline.json` file and deployed using the `scripts/deploy_jobs.py` script.

###  Example Configuration (airport_pipeline.json)

```json
{
  "name": "airports_pipeline",
  "commands": [
    "dbt deps",
    "dbt seed",
    "dbt build -s +fct_country_airport_rankings +fct_longest_shortest_runways"
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 2 ? * MON-FRI",
    "timezone_id": "UTC"
  },
  "max_retries": 0
}

```

## Usage Guidelines

- Modify the SQL files in the `models/` directory to create your own data transformations.
- Ensure to write tests in the `tests/` directory to validate your models.
- Use the `scripts/` directory for any automation scripts needed for deployment.

## Role-Based Access Control (RBAC)

The project includes an environment-aware setup for managing access between different types of users and deployment stages (development vs production). While Databricks native RBAC is not fully configured here, this section outlines how access would be structured in a scalable production environment.

###  User Roles

| Role            | Description                                                | Permissions                                                      |
|-----------------|------------------------------------------------------------|------------------------------------------------------------------|
| **Data Engineer** | Builds dbt models, owns deployment pipeline               | Read/Write access to `dev` and `prod` schemas, cluster admin     |
| **Data Analyst**  | Consumes transformed data, runs ad-hoc queries            | Read access to `prod` schema only                                |                    |
| **Admin**         | Manages secrets, clusters, and job permissions            | Full access across all environments and GitHub secrets           |

### Schema Isolation

- **dev**: Used for iterative development and testing.
- **prod**: Used for stable production-grade models.
- Schema names are dynamically injected using environment variables (`ENV`, `DATABRICKS_SCHEMA`).

###  Secrets Access

Secrets like Databricks tokens and host URLs are stored securely in [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets). 

##  LLM Usage
This documentation is  created with the assistance of ChatGPT-4o (OpenAI) for 

Markdown generation

dbt YAML configuration examples

Job definition templates

### ⚠️ Challenges

Several challenges were encountered while completing this assignment:

- Azure DevOps free-tier accounts have limited capabilities, for some reasons, it didn't work for me this time.

- The free (community) edition of Databricks does not allow creation of standard compute clusters. It only supports **Serverless SQL Warehouses**, which restricted the ability to run Python-based dbt tasks requiring a full cluster runtime.

###  Areas for Improvement

While the solution meets the core requirements, several enhancements could be made in a production-grade setup:

- Automate Source Ingestion*
  Currently, the source data (`airports.csv`, `countries.csv`, `runways.csv`) is manually placed in the `seeds/` folder and loaded using `dbt seed`.  
  In a production setup:
  - Automate ingestion from external sources (e.g., S3, Azure Blob Storage, API) using ADF etc. 

- ** Secret Management via Azure Key Vault**  
  Currently, secrets (e.g., Databricks token, host, HTTP path) are stored in GitHub Actions secrets. A more secure and scalable approach would be to integrate with **Azure Key Vault**, allowing centralized secret rotation and RBAC.

- ** Use of Production-Grade Clusters  
  This particular activity is designed to run with a Databricks Personal Compute where the cluster name is 
  hardcoded in deploy_jobs.py
  In a production-grade setup:
  - Cluster configuration should be externalized (e.g., stored in `JSON` or `YAML`)
  - Support for `new_cluster` should be added for job isolation


-  dbt Artifacts and Docs Hosting  
  DBT docs are not generated which can be added in production set up

-  Data Validation and Quality Monitoring  
  Incorporating tools like **Great Expectations** or **Soda Core** can add a layer of **data quality checks** before model promotion.

-  Logging and Monitoring 
  Implement logging and alerts for job failures using Databricks  job monitoring. 








