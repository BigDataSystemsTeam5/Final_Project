import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mcp.server.fastmcp import FastMCP
from typing import Optional
from services.github_tracker import get_latest_commit_id, extract_owner_repo
from services.generator import generate_readme, generate_codelab
from services.validator import validate_documentation

mcp = FastMCP("AutoDoc")

@mcp.tool()
def generate_repo_docs(repo_url: str, branch: Optional[str] = "main") -> dict:
    """Generate README and Codelab markdowns for a GitHub repository."""
    commit_id = get_latest_commit_id(repo_url, branch)
    readme = generate_readme(repo_url, commit_id)
    codelab = generate_codelab(repo_url, commit_id)
    validation = validate_documentation(repo_url, readme, codelab)

    return {
        "commit_id": commit_id,
        "readme": readme,
        "codelab": codelab,
        "validation": validation,
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
