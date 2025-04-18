import os
import subprocess
from github import Github
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load GitHub credentials from .env
load_dotenv(r'environment\access.env')

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
g = Github(GITHUB_TOKEN)

# Extracts 'owner/repo' from URL
def extract_repo_name(repo_url: str) -> str:
    parsed = urlparse(repo_url)
    return parsed.path.lstrip("/").replace(".git", "")

# Safely commits a file: update if exists, else create
def safe_commit_file(repo, path, content, message, branch="main"):
    try:
        existing = repo.get_contents(path, ref=branch)
        repo.update_file(path, message, content, existing.sha, branch=branch)
        print(f"✅ {path} updated.")
    except Exception as e:
        if "Not Found" not in str(e):
            raise e
        try:
            repo.create_file(path, message, content, branch=branch)
            print(f"✅ {path} created.")
        except Exception as create_err:
            print(f"❌ Failed to create {path}: {create_err}")
            raise create_err

# Detects claat export folder based on the 'id:' field in the markdown file
def detect_export_folder(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.lower().startswith("id:"):
                folder_name = line.strip().split(":", 1)[1].strip()
                break
        else:
            raise ValueError("No 'id:' field found in markdown frontmatter.")

    # Detect directory relative to the .md file location
    base_dir = os.path.dirname(os.path.abspath(md_path))
    expected_path = os.path.join(base_dir, folder_name)

    print(f"🔎 Looking for export folder at: {expected_path}")
    print(f"📁 Contents of parent dir: {os.listdir(base_dir)}")

    if os.path.isdir(expected_path):
        return expected_path
    else:
        raise FileNotFoundError(f"❌ Folder '{folder_name}' not found at {expected_path}. Claat export likely succeeded but script is looking in the wrong place.")

# Main pipeline
def fork_commit_generated_files(file_type, file, repo_url: str):

    repo_name = extract_repo_name(repo_url)
    print(f"🔍 Resolved repository: {repo_name}")

    original_repo = g.get_repo(repo_name)
    user = g.get_user()

    # Step 1: Fork
    print(f"🔁 Forking {repo_name} ...")
    fork = original_repo.create_fork()
    branch = "main"

    if file_type == 'codelab':
    # Step 2: Run claat export
        print("🛠️ Exporting with claat ...")
        codelab_md_path = "codelab.md"
        try:
            subprocess.run(["claat", "export", codelab_md_path], check=True)
            output_dir = detect_export_folder(codelab_md_path)
        except Exception as e:
            raise RuntimeError(f"❌ Claat export failed: {e}")

        # Step 3: Read all generated content
        def read_file(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        codelab_md = read_file(codelab_md_path)
        index_html = read_file(os.path.join(output_dir, "index.html"))
        json_data = read_file(os.path.join(output_dir, "codelab.json"))

        # Step 4: Commit files
        safe_commit_file(fork, "codelab.md", codelab_md, "AutoDoc AI: Add Codelab Markdown", branch)
        safe_commit_file(fork, "index.html", index_html, "AutoDoc AI: Add Generated index.html", branch)
        safe_commit_file(fork, "codelab.json", json_data, "AutoDoc AI: Add Generated codelab.json", branch)

    elif file_type == 'readme':
        readme_content = 'README.md'
        safe_commit_file(fork, "README.md", readme_content, "AutoDoc AI: Add or Update README", branch)

    # Step 5: Create PR
    existing_prs = original_repo.get_pulls(state="open", head=f"{user.login}:{branch}")
    if existing_prs.totalCount > 0:
        pr = existing_prs[0]
        print("⚠️ PR already exists. Returning existing PR link.")
    else:
        pr = original_repo.create_pull(
            title="📄 AutoDoc AI: Add Codelab, README, and Generated Files",
            body="Auto-committed README.md, codelab.md, and claat-exported index.html + codelab.json.",
            head=f"{user.login}:{branch}",
            base="main"
        )
        print("✅ Pull Request created.")

    live_link = f"https://{GITHUB_USERNAME}.github.io/"
    return pr.html_url, live_link

# ==== Run script ====
#if __name__ == "__main__":
#    repo_url = "https://github.com/Jaiminsorathiya/Temp.git"
#    codelab_md_path = "codelab.md"
#    readme_path = "README.md"
#
#    pr_link, codelab_link = fork_commit_generated_files(repo_url, codelab_md_path, readme_path)
#
#    print("\n=== ✅ DONE ===")
#    print(f"📬 Pull Request: {pr_link}")
#    print(f"🌐 Live Codelab (GitHub Pages root): {codelab_link}")
