import requests

# Replace with your repository details and personal access token
owner = "pratikkanade"
repo = "SECFinancialStatementsSnowflake"
commit1 = "ae89c45b16282b9277337225db09301e24c554d8"  # Base commit SHA
commit2 = "9c1964cfbfd85f8ad4dd7fc0859f6c1f2b76ceb0"  # Head commit SHA


# GitHub API URL for comparing commits
url = f"https://api.github.com/repos/{owner}/{repo}/compare/{commit1}...{commit2}"


# Send request to GitHub API
response = requests.get(url)

head_state = {}
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
    
    head_state['added'] = added
    head_state['modified'] = modified
    head_state['deleted'] = deleted

    print(head_state)

else:
    print(f"Error: {response.status_code} - {response.text}")
