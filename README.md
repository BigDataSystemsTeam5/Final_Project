# Final_Project

# 🧠 AutoDoc AI – Automated Documentation Generator for GitHub Repositories

AutoDoc AI is an intelligent documentation automation tool designed to generate structured and high-quality documentation for GitHub projects using LLMs and agentic workflows.

It automatically produces:
- 📘 `README.md` summarizing your project
- 🧪 Interactive Codelab tutorials via [Google Claat](https://github.com/googlecodelabs/tools)
- 🔁 CI/CD-ready documentation updates through GitHub Actions

Streamlit access link: http://3.130.104.76:8501/  
FastAPI access link: http://3.130.104.76:8000/docs
Codelabs link: https://bigdatasystemsteam5.github.io/Final_Project/#0
Deployed application on AWS EC2 link: http://3.130.104.76:8501/  
 

---

## 🧭 Architecture Diagram
![image](https://github.com/user-attachments/assets/e630cd0d-c96e-4fe0-8b86-33f34a14f72f)

*AutoDoc AI – Full Architecture*

---

## 📦 Features

✅ Automatically generates:
- README.md based on code structure and purpose  
- Interactive Google Codelab tutorials  
- GitHub integration for commit/push of generated files  

---

## 🛠️ Tech Stack

| Component        | Technology Used          |
|------------------|--------------------------|
| Frontend         | Streamlit                |
| Backend          | FastAPI                  |
| LLM Framework    | CrewAI + GPT-4o mini  |
| Database         | Snowflake                |
| Docs Generation  | Google Claat             |
| Context Retrieval|CrewAI Code Analyzer Agent |

---
Prerequisites
Python 3.8+
GitHub personal access token
VS Code (or similar IDE)
Basic knowledge of Python and REST APIs

2. Setup
Step 1: Clone the repository
git clone https://github.com/BigDataSystemsTeam5/Final_Project.git
cd Final_Project
Step 2: Set up the environment
python3 -m venv venv
source venv/bin/activate  # Use `venv\Scripts\activate` on Windows

pip install -r requirements.txt
Also, create a .env file in the root with the following:

OPENAI_API_KEY=your_openai_key
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username

3. Backend: FastAPI
Step 3: Run the backend API
uvicorn app:app --reload
This exposes endpoints like:

/final-file – Generate final README or Codelab
/approve – Commit changes back to GitHub

4. Frontend: Streamlit
Step 4: Launch the frontend UI
cd frontend
streamlit run main.py
This provides a clean interface for:

Selecting file type (README, Codelab)
Entering GitHub repo URL
Generating and pushing docs

5. GitHub Integration
Step 5: Understand how GitHub commits work
The github_handler.py contains logic for:

Extracting owner/repo from URL
Forking repos if needed
Creating/committing README and Codelab files
Opening a Pull Request
To test commit logic:

python new_github_handler.py
Ensure your GitHub PAT has repo and workflow scopes.

6. GitHub Actions
Step 6: Automate using GitHub Actions
Edit or create .github/workflows/autodoc.yml:

name: AutoDoc Deploy

on:
  push:
    branches: [ main ]

jobs:
  autodoc:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run AutoDoc
        run: python project_main.py
This runs your generation logic on every push.

7. Summary
You've successfully:

✅ Set up AutoDoc AI locally
✅ Connected it to GitHub
✅ Built a FastAPI + Streamlit interface
✅ Automated PRs and commits with GitHub Actions


## 📁 AI USE DISCLOSURE:

```bash
-Required Attestation and Contribution Declaration WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK. 

-Contribution:

Hishita Thakkar: 33 1/3%

Asavari Shejwal: 33 1/3%

Pratik Kanade: 33 1/3%
