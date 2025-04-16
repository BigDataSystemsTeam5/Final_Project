import re
from gitingest import ingest
from agent_state import AgentState
from logger_code import get_logger

#repo = "https://github.com/pratikkanade/ML_project_h1b_visa_approval_predictions"

langgraph_logger = get_logger("langgraph_logger", "langgraph_logger.log")

def repo_file_details(state: AgentState):
#def repo_file_details(repo):

    langgraph_logger.info('Started repo_file_details step')

    repo = state["repo"]
    langgraph_logger.info(f"Current repo name in repo_file_details is '{repo}'")

    summary, tree, content = ingest(repo)

    #repo_name = repo.split("/")[-1]
    #owner_name = repo.split("/")[-2]

    # Define the delimiter pattern (escape special characters)
    #file_pattern = r"\n=+\nFile: .+\n=+\n"
    file_pattern = r"(?=\n=+\nFile: .+\n=+\n)"

    # Split the content based on the delimiter
    files = re.split(file_pattern, content)

    # Define the regex pattern to match the filename
    filename_pattern = r"File: ([^\n]+)"

    # Find all filenames that match the pattern
    filenames = re.findall(filename_pattern, content)
    #print(filenames)

    for filename in filenames:
        if not filename.endswith(('.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.sh', '.bat', '.sql', '.db', '.sqlite', '.ipynb')):
            file_index = filenames.index(filename)
            files.pop(file_index)
            filenames.pop(file_index)

    #print(files)
    #print(filenames)
    langgraph_logger.info('Finished repo_file_details step')

    return {"structure":tree, "files": files, "filenames": filenames}

#repo_file_details(repo)