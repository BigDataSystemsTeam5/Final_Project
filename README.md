# Final_Project

# 🧠 AutoDoc AI – Automated Documentation Generator for GitHub Repositories

AutoDoc AI is an intelligent documentation automation tool designed to generate structured and high-quality documentation for GitHub projects using LLMs and agentic workflows.

It automatically produces:
- 📘 `README.md` summarizing your project
- 🧭 Architecture diagrams (Mermaid & Mingrammer)
- 🧪 Interactive tutorials via [Google Claat](https://github.com/googlecodelabs/tools)
- 🔁 CI/CD-ready documentation updates through GitHub Actions

---

## 🚀 Live Tutorial

🎓 **Explore the interactive Codelab**:  
[https://BigDataSystemsTeam5.github.io/Final_Project](https://BigDataSystemsTeam5.github.io/Final_Project)

---

## 📦 Features

✅ Automatically generates:
- `README.md` based on code structure and purpose  
- Architecture diagrams using Mermaid & Mingrammer  
- Interactive Google Codelab tutorials  
- GitHub integration for commit/push of generated files  

💡 Uses:
- **LLMs** (GPT-4o mini via LangGraph agents)
- **Airflow** for pipeline orchestration
- **Claat** for tutorials
- **Streamlit + FastAPI** for user interface
- **S3, Pinecone, Snowflake** for storage and vector retrieval

---

## 🛠️ Tech Stack

| Component        | Technology Used          |
|------------------|--------------------------|
| Frontend         | Streamlit                |
| Backend          | FastAPI                  |
| LLM Framework    | LangGraph + GPT-4o mini  |
| Orchestration    | Apache Airflow           |
| Embeddings       | all-MiniLM-L6-v2         |
| Storage          | AWS S3, PineconeDB       |
| DB & Analytics   | Snowflake                |
| Docs Generation  | Google Claat, Mermaid, Mingrammer |
| CI/CD            | GitHub Actions           |

---

## 📁 Folder Structure

```bash
Final_Project/
├── docs/                      # Public Codelab (GitHub Pages)
├── pipeline/                  # Airflow DAGs and data flow
├── fastapi_app/               # Backend APIs
├── streamlit_app/             # User interface
├── diagrams/                  # Mermaid / Mingrammer diagrams
├── scripts/                   # Utility and code parsers
├── autodoc-ai-codelab.md      # Source tutorial file
├── README.md
