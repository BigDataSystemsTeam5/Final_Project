import streamlit as st
import requests

# Backend FastAPI URL
API_URL = "http://localhost:8000"

st.set_page_config(page_title="AutoDoc AI", layout="wide")
st.title("🧠 AutoDoc AI — Automated Documentation Assistant")
st.markdown("Generate README.md and Codelab tutorials for any public GitHub repository using AI.")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Pages", ["📂 Repo Input", "📄 Generated Docs", "✅ Approve & Commit"])

# Shared session state
if 'repo_url' not in st.session_state:
    st.session_state.repo_url = ""
if 'readme_content' not in st.session_state:
    st.session_state.readme_content = ""
if 'codelab_link' not in st.session_state:
    st.session_state.codelab_link = ""

# PAGE 1 — GitHub Repo Input
if page == "📂 Repo Input":
    st.subheader("Step 1: Enter a GitHub Repository URL")

    repo_input = st.text_input("GitHub Repo URL (e.g. https://github.com/your-org/project)", st.session_state.repo_url)

    if st.button("Generate Documentation"):
        with st.spinner("Generating README and Codelab using AI agents..."):
            response = requests.post(f"{API_URL}/generate_docs", json={"repo_url": repo_input})
            if response.status_code == 200:
                data = response.json()
                st.session_state.repo_url = repo_input
                st.session_state.readme_content = data.get("readme_md", "")
                st.session_state.codelab_link = data.get("codelab_url", "")
                st.success("Documentation generated successfully!")
            else:
                st.error("Failed to generate documentation. Please check the repo URL or server logs.")

# PAGE 2 — View Generated Docs
elif page == "📄 Generated Docs":
    st.subheader("Step 2: Review Auto-Generated Documentation")

    if st.session_state.readme_content:
        st.markdown("### 📘 README.md Preview")
        st.code(st.session_state.readme_content, language="markdown")

        if st.session_state.codelab_link:
            st.markdown(f"### 🧪 Codelab Tutorial\n[Codelab Live Link]({st.session_state.codelab_link})")
    else:
        st.info("No documentation generated yet. Go to 'Repo Input' and start from there.")

# PAGE 3 — Approval and GitHub Commit
elif page == "✅ Approve & Commit":
    st.subheader("Step 3: Approve and Commit to GitHub")

    if st.session_state.readme_content:
        approve = st.checkbox("✅ I approve this documentation for commit")
        if st.button("Commit to GitHub", disabled=not approve):
            with st.spinner("Committing README.md to GitHub..."):
                payload = {
                    "repo_url": st.session_state.repo_url,
                    "readme_md": st.session_state.readme_content
                }
                response = requests.post(f"{API_URL}/commit_docs", json=payload)
                if response.status_code == 200:
                    st.success("Documentation committed to GitHub successfully!")
                else:
                    st.error("Failed to commit documentation. Check backend logs.")
    else:
        st.warning("Please generate documentation first before committing.")
