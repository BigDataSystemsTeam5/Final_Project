from diagrams import Diagram, Cluster
from diagrams.onprem.client import Users
from diagrams.programming.language import Python
from diagrams.saas.analytics import Snowflake
from diagrams.onprem.client import Client
from diagrams.onprem.vcs import Github
from diagrams.generic.compute import Rack
from diagrams.onprem.compute import Server

with Diagram("AutoDoc AI Architecture", show=False):

    users = Users("End Users")

    with Cluster("GitHub"):
        github = Github("Push to GitHub")

    with Cluster("GitHub Commit"):
        github2 = Github("Push to GitHub")

    with Cluster("Snowflake History"):
        snowflake_db = Snowflake("Snowflake DB")
    
    with Cluster("EC2 Instance"):    
        fastapi = Python("FastAPI")
        streamlit = Client("Streamlit UI")
        gitingest = Python("GitIngest")
        gitpython = Python("GitPython")
        snowflake_db1 = Snowflake("Snowflake DB")
        #langgraph = Server("LangGraph")
        langgraph = Server("AutoDoc AI")

    with Cluster("MCP Server"):
        mcp = Rack("MCP Server")

    with Cluster("Snowflake"):
        snowflake_db2 = Snowflake("Snowflake DB")


    users >> streamlit >> fastapi >> snowflake_db1 >> gitingest >> langgraph >> mcp >> [snowflake_db2, github]
    users << streamlit << fastapi

    snowflake_db2 >> mcp
    langgraph << mcp

    streamlit << langgraph
    langgraph >> [github2, snowflake_db]
    
        



