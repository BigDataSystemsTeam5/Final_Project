from fastapi import FastAPI, HTTPException
import os
from github_handler import fork_commit_generated_files
from project_main import main_func

app = FastAPI()


@app.get("/")
async def read_root():
    return {"status": "AutoDoc API is live"}


# NEW: Fetch basic repo info
@app.get("/final-file")
async def get_final_file(repo, file_type):
    try:
        final_file = await main_func(repo, file_type)
        return final_file
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



#  POST: approve
@app.post("/approve")
async def approve_and_push(file_type, file, repo_url):
    try:
        result = fork_commit_generated_files(file_type, file, repo_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
