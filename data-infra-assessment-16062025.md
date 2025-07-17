Design and implement a data pipeline to ingest, transform and analyze data in a data warehouse. Automate the pipeline to run daily, set up CI/CD and document your work. The assignment should take approximately 3 hours to complete.

## Datasets

- [airports.csv](https://sacodeassessment.blob.core.windows.net/public/airports.csv)
- [countries.csv](https://sacodeassessment.blob.core.windows.net/public/countries.csv)
- [runways.csv](https://sacodeassessment.blob.core.windows.net/public/runways.csv)

## Questions

- For each country with airports, list the details (width, length, airport name) of its longest and shortest runways.
- Calculate the number of airports per country, identifying the top 3 and bottom 10 countries.

## Tasks

1. **Data Ingestion**: Load datasets into a data warehouse.
2. **Data Transformation**: Transform the data and answer the questions.
3. **Workflow Orchestration**: Automate the pipeline to run daily.
4. **Design RBAC**: Define user groups and identify what types of users are intended for each group.
5. **CI/CD**: Set up a CI/CD to run tests and deploy the code.
6. **Documentation**: Create a README with setup instructions, approach, assumptions, challenges and improvement ideas. Specify if any LLMs were used in the process.

## Deliverables

- All processes (ingestion, transformation, scheduling) must be automated.
- Git repository containing the code, CI/CD pipeline, README file. Archive and send it over email.

## Platform choice

We are looking for candidates with experience in **Snowflake** or **Databricks**, please use either of these platforms as your data warehouse solution.

- Databricks Free Edition: [link](https://www.databricks.com/learn/free-edition)
- Snowflake Trial: [link](https://signup.snowflake.com/)