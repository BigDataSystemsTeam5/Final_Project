from agent_state import AgentState
import os
from dotenv import load_dotenv
from snowflake.snowpark import Session
from logger_code import get_logger
from repo_details import get_repo_latest_commit
from agent_state import AgentState


load_dotenv(r'C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Project\environment\access.env')

connection_params = {
    "account": os.getenv('SNOWFLAKE_ACCOUNT'),
    "user": os.getenv('SNOWFLAKE_USER'),
    "password": os.getenv('SNOWFLAKE_PASSWORD'),
    "warehouse": os.getenv('SNOWFLAKE_WAREHOUSE'),
    "database": os.getenv('SNOWFLAKE_DATABASE'),
    "schema": os.getenv('SNOWFLAKE_SCHEMA')
}

langgraph_logger = get_logger("langgraph_logger", "langgraph_logger.log")

# Create Snowflake session
session = Session.builder.configs(connection_params).create()


def snowflake_store_repo(state: AgentState):

    langgraph_logger.info('Started snowflake_store_repo step')

    repo = state["repo"]
    langgraph_logger.info(f"Repo link in snowflake_store_repo is '{repo}'")

    repo_name = repo.split("/")[-1]
    owner_name = repo.split("/")[-2]

    latest_commit_id = get_repo_latest_commit(state)
    #created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    #updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 


    insert_repo_table = f"""
    INSERT INTO REPO_INFO (REPO_LINK, OWNER_NAME, REPO_NAME, LATEST_COMMIT_ID, CREATED_AT, UPDATED_AT)
    VALUES ('{repo}', '{owner_name}', '{repo_name}', '{latest_commit_id}', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
    """

    session.sql(insert_repo_table).collect()

    langgraph_logger.info('Finished snowflake_store_repo step')



def snowflake_store_file(state: AgentState):

    langgraph_logger.info('Started snowflake_store_file step')

    repo = state["repo"]
    langgraph_logger.info(f"Repo link in snowflake_store_file is '{repo}'")

    repo_name = repo.split("/")[-1]
    owner_name = repo.split("/")[-2]

    get_repo_id = f"""
    SELECT ID FROM REPO_INFO WHERE REPO_NAME = '{repo_name}' AND OWNER_NAME = '{owner_name}';
    """

    repo_id = session.sql(get_repo_id).collect()
    repo_id_value = repo_id[0]["ID"]

    langgraph_logger.info(f"Repo ID fetched from REPO_INFO table in snowflake: '{repo_id_value}'")

    file_name = state['current_filename']
    file_meaning = state['current_file']
    escaped_text = f"$$\n{file_meaning}\n$$"

    insert_file_table = f"""
    INSERT INTO FILE_INFO (REPO_ID, FILE_NAME, FILE_MEANING, CREATED_AT, UPDATED_AT)
    VALUES ({repo_id_value}, '{file_name}', {escaped_text}, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
    """

    session.sql(insert_file_table).collect()

    langgraph_logger.info('Finished snowflake_store_file step')
