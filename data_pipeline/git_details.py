import requests
from data_pipeline.logger_code import get_logger
#from snowflake.snowpark import Session



git_logger = get_logger("git_logger", "git_logger.log")


def get_repo_latest_commit(repo):

    # GitHub API endpoint
    #url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    git_logger.info('Started get_repo_latest_commit step')

    git_logger.info(f"Repo link in get_repo_latest_commit is '{repo}'")

    repo_name = repo.split("/")[-1]
    owner_name = repo.split("/")[-2]

    repo_link = f"https://api.github.com/repos/{owner_name}/{repo_name}/commits"

    # Fetch commits (latest first)
    response = requests.get(repo_link, params={"per_page": 1})

    if response.status_code == 200:
        latest_commit = response.json()[0]["sha"]

        git_logger.info(f"Latest commit id of the repo:{repo_name} is {latest_commit}")

        git_logger.info('Finished get_repo_latest_commit step')

        return latest_commit
    
    else:
        git_logger.error(f"Error: {response.status_code} - {response.text}")



def affected_git_files(owner, repo, base_commit, head_commit):

    # Replace with your repository details and personal access token
    #owner = "pratikkanade"
    #repo = "SECFinancialStatementsSnowflake"
    #base_commit = "ae89c45b16282b9277337225db09301e24c554d8"  # Base commit SHA
    #head_commit = "9c1964cfbfd85f8ad4dd7fc0859f6c1f2b76ceb0"  # Head commit SHA

    git_logger.info('Started affected_git_files step')


    # GitHub API URL for comparing commits
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base_commit}...{head_commit}"


    # Send request to GitHub API
    response = requests.get(url)

    head_state_files = {}
    added = []
    modified = []
    deleted = []

    if response.status_code == 200:

        # Extract file names from the response
        for file in response.json()["files"]:

            if file['status'] == 'added':
                added.append(file['filename'])
            elif file['status'] == 'modified':
                modified.append(file['filename'])
            elif file['status'] == 'deleted':
                deleted.append(file['filename'])

        head_state_files['added'] = added
        head_state_files['modified'] = modified
        head_state_files['deleted'] = deleted

        git_logger.info(owner)
        git_logger.info(repo)
        git_logger.info(head_state_files)

    else:
        git_logger.error(f"Error: {response.status_code} - {response.text}")

    git_logger.info('Finished affected_git_files step')

    return head_state_files