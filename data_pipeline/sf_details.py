import os
from dotenv import load_dotenv
from data_pipeline.logger_code import get_logger
from snowflake.snowpark import Session



load_dotenv(r'C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Project\environment\access.env')

connection_params = {
    "account": os.getenv('SNOWFLAKE_ACCOUNT'),
    "user": os.getenv('SNOWFLAKE_USER'),
    "password": os.getenv('SNOWFLAKE_PASSWORD'),
    "warehouse": os.getenv('SNOWFLAKE_WAREHOUSE'),
    "database": os.getenv('SNOWFLAKE_DATABASE'),
    "schema": os.getenv('SNOWFLAKE_SCHEMA')
}

snowflake_logger = get_logger("snowflake_logger", "snowflake_logger.log")


def fetch_sf_repo(repo):

    snowflake_logger.info('Started fetch_repo step')
    
    snowflake_logger.info(f"Working repo name in fetch_repo is '{repo}'")

    # Create Snowflake session
    session = Session.builder.configs(connection_params).create()

    get_repo_name = f"""
    SELECT REPO_LINK FROM REPO_INFO WHERE REPO_LINK = '{repo}';
    """

    snowflake_repo = session.sql(get_repo_name).collect()
    if snowflake_repo:
        snowflake_repo_value = snowflake_repo[0]["REPO_LINK"]
    else:
        # Handle the empty case appropriately
        snowflake_repo_value = None 

   
    snowflake_logger.info(f"Repo name fetched from Snowflake in fetch_repo is '{snowflake_repo_value}'")

    snowflake_logger.info('Finished fetch_repo step')

    return snowflake_repo_value


def fetch_sf_latest_commit(repo):

    snowflake_logger.info('Started fetch_repo_latest_commit step')
    
    snowflake_logger.info(f"Working repo name in fetch_repo_latest_commit is '{repo}'")

    # Create Snowflake session
    session = Session.builder.configs(connection_params).create()

    get_repo_latest_commmit = f"""
    SELECT LATEST_COMMIT_ID FROM REPO_INFO WHERE REPO_LINK = '{repo}';
    """

    snowflake_repo_latest_commit = session.sql(get_repo_latest_commmit).collect()
    snowflake_repo_commit_value = snowflake_repo_latest_commit[0]["REPO_LINK"]
   
    snowflake_logger.info(f"Repo name fetched from Snowflake in fetch_repo is '{snowflake_repo_commit_value}'")

    snowflake_logger.info('Finished fetch_repo_latest_commit step')

    return snowflake_repo_commit_value


def fetch_sf_readme(repo):

    snowflake_logger.info('Started fetch_repo_latest_commit step')
    
    snowflake_logger.info(f"Working repo name in fetch_repo_latest_commit is '{repo}'")

    # Create Snowflake session
    session = Session.builder.configs(connection_params).create()

    get_repo_latest_commmit = f"""
    SELECT LATEST_COMMIT_ID FROM REPO_INFO WHERE REPO_LINK = '{repo}';
    """

    snowflake_repo_latest_commit = session.sql(get_repo_latest_commmit).collect()
    snowflake_repo_commit_value = snowflake_repo_latest_commit[0]["REPO_LINK"]
   
    snowflake_logger.info(f"Repo name fetched from Snowflake in fetch_repo is '{snowflake_repo_commit_value}'")

    snowflake_logger.info('Finished fetch_repo_latest_commit step')

    return snowflake_repo_commit_value



def store_sf_readme(repo, file, latest_commit_id):

    snowflake_logger.info('Started store_sf_readme step')

    snowflake_logger.info(f"Repo link in store_sf_readme is '{repo}'")

    # Create Snowflake session
    session = Session.builder.configs(connection_params).create()

    repo_name = repo.split("/")[-1]
    owner_name = repo.split("/")[-2]

    insert_repo_table = f"""
    INSERT INTO REPO_INFO (REPO_LINK, OWNER_NAME, REPO_NAME, LATEST_COMMIT_ID, README, CODELAB, CREATED_AT, UPDATED_AT)
    VALUES ('{repo}', '{owner_name}', '{repo_name}', '{latest_commit_id}', '{file}', '', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
    """

    session.sql(insert_repo_table).collect()

    snowflake_logger.info('Finished store_sf_readme step')




def store_sf_codelab(repo, file, latest_commit_id):

    snowflake_logger.info('Started store_sf_codelab step')

    snowflake_logger.info(f"Repo link in store_sf_codelab is '{repo}'")

    # Create Snowflake session
    session = Session.builder.configs(connection_params).create()

    repo_name = repo.split("/")[-1]
    owner_name = repo.split("/")[-2]

    insert_repo_table = f"""
    INSERT INTO REPO_INFO (REPO_LINK, OWNER_NAME, REPO_NAME, LATEST_COMMIT_ID, README, CODELAB, CREATED_AT, UPDATED_AT)
    VALUES ('{repo}', '{owner_name}', '{repo_name}', '{latest_commit_id}', '', '{file}', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
    """

    session.sql(insert_repo_table).collect()

    snowflake_logger.info('Finished store_sf_codelab step')