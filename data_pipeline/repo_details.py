import requests
from data_pipeline.logger_code import get_logger

# Create separate loggers for each ETL process
gitrepo_logger = get_logger("git_repo", "git_repo.log")

def get_lang_perc(owner, repo):
    
    # Replace with your repository details
    owner = "pratikkanade"
    repo = "ML_project_h1b_visa_approval_predictions"
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"

    #https://github.com/pratikkanade/ML_project_h1b_visa_approval_predictions

    # Fetch language data
    response = requests.get(url)
    languages = response.json()

    # Calculate total bytes
    total_bytes = sum(languages.values())

    # Calculate percentages
    language_percentages = {lang: (bytes / total_bytes) * 100 for lang, bytes in languages.items()}

    gitrepo_logger.info(owner)
    gitrepo_logger.info(repo)
    gitrepo_logger.info(language_percentages)

    if language_percentages['Python'] >= 90:
        python_project = True
    else:
        python_project = False
        
    return python_project
    
    

def get_repo_latest_commit(owner, repo):

    # GitHub API endpoint
    owner = "pratikkanade"
    repo = "SECFinancialStatementsSnowflake"
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"


    # Fetch commits (latest first)
    response = requests.get(url, params={"per_page": 1})

    if response.status_code == 200:
        latest_commit = response.json()[0]["sha"]

        gitrepo_logger.info(owner)
        gitrepo_logger.info(repo)
        gitrepo_logger.info(f"Latest commit: {latest_commit}")

        return latest_commit
    
    else:
        gitrepo_logger.error(f"Error: {response.status_code} - {response.text}")



def affected_git_files(owner, repo, base_commit, head_commit):

    # Replace with your repository details and personal access token
    owner = "pratikkanade"
    repo = "SECFinancialStatementsSnowflake"
    base_commit = "ae89c45b16282b9277337225db09301e24c554d8"  # Base commit SHA
    head_commit = "9c1964cfbfd85f8ad4dd7fc0859f6c1f2b76ceb0"  # Head commit SHA


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

        gitrepo_logger.info(owner)
        gitrepo_logger.info(repo)
        gitrepo_logger.info(head_state_files)

    else:
        gitrepo_logger.error(f"Error: {response.status_code} - {response.text}")

    return head_state_files
