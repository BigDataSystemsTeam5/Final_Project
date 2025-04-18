import requests
from urllib.parse import urlparse

def extract_owner_repo(repo_url: str) -> tuple[str, str]:
    """
    Extracts the owner and repository name from a GitHub URL.
    
    Example:
        Input: "https://github.com/openai/gpt-4"
        Output: ("openai", "gpt-4")
    """
    parsed = urlparse(repo_url)
    path_parts = parsed.path.strip("/").split("/")
    
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL format. Expecting https://github.com/<owner>/<repo>")
    
    owner, repo = path_parts[0], path_parts[1]
    return owner, repo


def get_latest_commit_id(repo_url: str, branch: str = "main") -> str:
    """
    Fetches the latest commit SHA for the specified branch of a GitHub repository.
    
    Requires public repo or GitHub token if rate limited.
    """
    owner, repo = extract_owner_repo(repo_url)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
    
    headers = {
        "Accept": "application/vnd.github+json"
        # You can add a token here if needed: "Authorization": "Bearer YOUR_GITHUB_TOKEN"
    }
    
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch latest commit. GitHub API responded with status {response.status_code}: {response.text}")
    
    commit_data = response.json()
    return commit_data["sha"]
