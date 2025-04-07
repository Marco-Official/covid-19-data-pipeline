# Coding Assignment: Data Processing and Analysis System

## Objective

Design and implement a system that ingests, processes, and analyzes a dataset to provide insights into its contents. Your solution should demonstrate your ability to work with data pipelines, databases, and analytical queries.

## Dataset

Use the **COVID-19 Data Repository** by **Johns Hopkins University**.

## Requirements

1. **Data Ingestion**:

   - Write a script to ingest data from the provided source into a database.
   - Account for potential inconsistencies and errors in the data.

2. **Data Processing**:

   - Implement a process to clean and transform the data.
   - This could involve handling missing values, deduplicating records, or transforming data formats.

3. **Data Storage**:

   - Store the processed data in a relational or NoSQL database.
   - Design the schema to support efficient querying and analysis.

4. **Data Analysis**:

   - Write queries or scripts to answer three specific questions about the dataset.
   - These questions should demonstrate your ability to perform complex data analysis.
   - Example questions include:
     - **What are the top 5 most common values in a particular column, and what is their frequency?**
     - **How does a particular metric change over time within the dataset?**
     - **Is there a correlation between two specific columns? Explain your findings.**

5. **Documentation**:
   - Provide a `README.md` file that includes:
     - Instructions on how to set up and run your solution.
     - A brief explanation of your design decisions and the technologies used.
     - Answers to the data analysis questions, including any assumptions made.

## Technology Constraints

- You should use a modern **data orchestration tool** such as **Mage.ai** or **Dagster**.
- For **data transformation**, it is recommended to use **dbt**.
- For **database storage**, you may choose between:
  - PostgreSQL
  - MySQL
  - SQLite
  - DuckDB
- **Python** is recommended for scripting.
- If applicable, you are encouraged to use **Docker** to containerize your solution.

## Submission Guidelines

- Submit your solution **within 1 week** of receiving the assignment as a link to a **GitHub repository**.
- Ensure your code is well-commented and follows best practices for readability and maintainability.

## Evaluation Criteria

- **Correctness and efficiency** of data ingestion and processing.
- **Database schema design** and the efficiency of queries.
- **Quality of analysis** and insights provided.
- **Code quality**, including readability, organization, and documentation.
