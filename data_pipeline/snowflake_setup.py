import os
from dotenv import load_dotenv
from snowflake.snowpark import Session
from data_pipeline.logger_code import get_logger

# Create separate loggers for each ETL process
snowflake_setup_logger = get_logger("snowflake_setup", "snowflake_setup.log")

load_dotenv(r'C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Project\environment\access.env')

connection_params = {
    "account": os.getenv('SNOWFLAKE_ACCOUNT'),
    "user": os.getenv('SNOWFLAKE_USER'),
    "password": os.getenv('SNOWFLAKE_PASSWORD'),
    "warehouse": os.getenv('SNOWFLAKE_WAREHOUSE'),
    "database": os.getenv('SNOWFLAKE_DATABASE'),
    "schema": os.getenv('SNOWFLAKE_SCHEMA')
}


# Create Snowflake session
session = Session.builder.configs(connection_params).create()

# Ensure schema exists
session.sql(f"CREATE SCHEMA IF NOT EXISTS {connection_params['schema']}").collect()
print(f"Schema '{connection_params['schema']}' is ready.")

# SQL statement to create the table if it does not exist
create_repo_table = """
CREATE TABLE IF NOT EXISTS REPO_INFO (
    id INT PRIMARY KEY IDENTITY(1,1),
    repo_name STRING,
    latest_commit_id STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

session.sql(create_repo_table).collect()


create_file_table = """
CREATE TABLE IF NOT EXISTS FILE_INFO (
    id INT PRIMARY KEY IDENTITY(1,1),
    repo_id INT NOT NULL,
    file_name STRING,
    latest_commit_id STRING,
    code_doc VARIANT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (repo_id) REFERENCES create_repo_table(id)
)
"""

session.sql(create_file_table).collect()

# Verify that the table was created (optional)
tables = session.sql("SHOW TABLES").collect()
snowflake_setup_logger.info([table.name for table in tables])  