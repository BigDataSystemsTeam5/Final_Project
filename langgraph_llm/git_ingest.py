# Synchronous usage
import re
from gitingest import ingest
from agent_state import AgentState

#repo = "https://github.com/pratikkanade/SECFinancialStatementsSnowflake"



def repo_file_details(state: AgentState):

    repo = state["repo"]
    summary, tree, content = ingest(repo)

    #repo_name = repo.split("/")[-1]
    #owner_name = repo.split("/")[-2]

    # Define the delimiter pattern (escape special characters)
    file_pattern = r"\n=+\nFile: .+\n=+\n"

    # Split the content based on the delimiter
    files = re.split(file_pattern, content)

    #print(files[0])

    # Define the regex pattern to match the filename
    filename_pattern = r"File: ([^\n]+)"

    # Find all filenames that match the pattern
    filenames = re.findall(filename_pattern, content)
    #print(filenames)

    return {"structure":tree, "files": files, "filenames": filenames}