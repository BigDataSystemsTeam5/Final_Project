import os
from dotenv import load_dotenv
from snowflake.snowpark import Session
from agent_state import AgentState
from logger_code import get_logger


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

def fetch_repo(state: AgentState):

    langgraph_logger.info('Started fetch_repo step')
    
    repo = state["repo"]
    langgraph_logger.info(f"Working repo name in fetch_repo is '{repo}'")

    # Create Snowflake session
    session = Session.builder.configs(connection_params).create()

    get_repo_name = f"""
    SELECT REPO_LINK FROM REPO_INFO WHERE REPO_LINK = '{repo}';
    """

    snowflake_repo = session.sql(get_repo_name).collect()
    snowflake_repo_value = snowflake_repo[0]["REPO_LINK"]
   
    langgraph_logger.info(f"Repo name fetched from Snowflake in fetch_repo is '{snowflake_repo_value}'")

    langgraph_logger.info('Finished fetch_repo step')

    return {"snowflake_repo": snowflake_repo_value}


def decide_repo(state: AgentState):

    returned_repo = state['snowflake_repo']
    repo = state['repo']

    if returned_repo == repo:
        return "end"
    else:
        return "continue"

