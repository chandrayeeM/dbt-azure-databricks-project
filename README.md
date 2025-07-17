# DBT Azure Databricks Project

This project integrates DBT (Data Build Tool) with Azure DevOps for seamless deployment and management of data transformations in Databricks.

## Project Structure

- **models/**: Contains SQL files defining DBT models for transforming raw data.
  - `example_model.sql`: An example model demonstrating data transformation.

- **data/**: Holds YAML files defining data sources.
  - `sources.yml`: Configuration for data sources used in the project.

- **macros/**: Includes reusable SQL macros.
  - `example_macro.sql`: An example macro for use in models.

- **tests/**: Contains SQL files for testing DBT models.
  - `example_test.sql`: Tests to validate data transformations.

- **scripts/**: Shell scripts for automation.
  - `databricks_job.sh`: Script to automate DBT model deployment to Databricks.

- **.azure-pipelines/**: Azure DevOps pipeline configuration.
  - `pipeline.yml`: Defines the CI/CD pipeline for the project.

- **dbt_project.yml**: Main configuration file for the DBT project.

- **profiles.yml**: Connection profiles for the DBT project.

## Setup Instructions

1. **Clone the Repository**: Clone this repository to your local machine.
   
2. **Install DBT**: Ensure you have DBT installed. You can install it using pip:
   ```
   pip install dbt
   ```

3. **Configure Profiles**: Update the `profiles.yml` file with your Databricks connection details.

4. **Run DBT Commands**: Use the following commands to run your DBT models:
   ```
   dbt run
   ```

5. **Automate with Azure DevOps**: Set up the Azure DevOps pipeline defined in `.azure-pipelines/pipeline.yml` to automate testing and deployment.

## Usage Guidelines

- Modify the SQL files in the `models/` directory to create your own data transformations.
- Use the `macros/` directory to define reusable SQL snippets.
- Ensure to write tests in the `tests/` directory to validate your models.
- Use the `scripts/` directory for any automation scripts needed for deployment.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.


# Local Development

1. Create and source a virtual enviroment:
   - With venv:
      1. `python3 -m venv ./venv`
      2. `source ./venv/bin/activate`
   - With conda:
      1. `conda create -n dbt-lake python=3.9`
      2. `conda activate dbt-lake`
2. Install requirements: `pip install -r requirements.txt`
4. Create a work cluster in the `udev` Databricks workspace
5. Export the following environment variables. See
   [dbt-spark](https://github.com/fishtown-analytics/dbt-spark) for more details:
   ``` bash
   export DATABRICKS_SCHEMA="<your name>""
   export DATABRICKS_HOST="adb-<databricks organization ID>.<random number>.azuredatabricks.net"
   export DATABRICKS_TOKEN="<databricks token>"
   export DATABRICKS_ORGANIZATION="<databricks organization ID>"
   export DATABRICKS_HTTP_PATH="<find this in your cluster -> JDBC/ODBC -> HTTP Path>"
   export ENV="udev"
   export EXT_LANDING_PATH="abfss://extlanding@stifdperpinudev.dfs.core.windows.net"
   export LANDING_PATH="abfss://landing@stifdpingesudev.dfs.core.windows.net"
   ```
6. Copy `profiles.yml` to ~/.dbt/ (on Macbook)
7. Import dbt dependency modules: `dbt deps`
8. Test your connection: `dbt debug --profiles-dir ~/.dbt/`

Note that if a larger cluster than `small` is needed for dev dbt work and a larger cluster is created, ensure the
cluster's Spark Config configuration contains:

```
spark.mart.serverName {{secrets/mart/serverName}}
spark.mart.adminUsername {{secrets/mart/sqlAdministratorUsername}}
spark.mart.adminPassword {{secrets/mart/sqlAdministratorPassword}}
```

Else the cluster will not be able to connect to the SQL Server instance.