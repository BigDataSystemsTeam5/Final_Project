import requests

# GitHub API endpoint
owner = "pratikkanade"
repo_name = "SECFinancialStatementsSnowflake"
url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"


# Fetch commits (latest first)
response = requests.get(url, params={"per_page": 1})

if response.status_code == 200:
    latest_commit = response.json()[0]["sha"]
    print(f"Latest commit: {latest_commit}")
else:
    print(f"Error: {response.status_code} - {response.text}")
