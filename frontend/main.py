import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AutoDoc AI", layout="wide")

# Sidebar Navigation
st.title("AutoDoc Navigation")

st.divider()

page = st.sidebar.radio("Select File Type", ["Readme", "Codelab"])

# GitHub Repository URL Input
st.sidebar.markdown("---")
repo = st.sidebar.text_input("GitHub Repository URL")
generate_clicked = st.sidebar.button(" Generate Documentation")

# Results Display
#generated_readme = ""
#generated_codelab = ""

# Page-specific views
if page == "Readme":
    st.subheader("Generated Readme File")
    #st.text_area("README Output", generated_readme, height=300, key="readme_output")

    if generate_clicked:
        if not repo:
            st.sidebar.warning("Please enter the GitHub repository URL.")
        else:
            with st.spinner("Generating documentation using AutoDoc agent..."):
                try:
                    params = {"repo": repo, "file_type": 'readme'}
                    response = requests.get(f"{API_BASE_URL}/final-file", params=params)

                    if response.status_code == 200:
                        generated_readme = response.json()['choices'][0]['message']['content']
                        st.write(generated_readme)
                        #data = response.json()
                        #generated_readme = data.get("readme", "No README generated.")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Approve & Push to GitHub"):
                                st.success("Approval received. Sending to backend...")

                                try:
                                    params = {"repo_url": repo, "file_type": 'readme', "file": generated_readme}
                                    response = requests.get(f"{API_BASE_URL}/final-file", params=params)
    
                                    if response.status_code == 200:
                                        result = response.json()
                                        st.success("Successfully pushed to GitHub!")
                                        st.markdown(f"[View Pull Request]({result['pull_request']})")
                                        st.markdown(f"[View Codelab Preview]({result['codelab_url']})")
                                    else:
                                        st.error(f"Failed: {response.status_code}")
                                        st.error(response.text)

                                except Exception as e:
                                    st.error(f"Exception occurred: {e}")

                        with col2:
                            if st.button(" Not Approved - Needs Changes"):
                                st.warning("Feedback noted. Please make necessary changes before pushing to GitHub.")


                    else:
                        st.error("Agent failed to process the request.")
                except Exception as e:
                    st.error(f"Error: {e}")

    

elif page == "Codelab":
    st.subheader("Generated Codelab File")
    #st.text_area("Codelab Output", generated_codelab, height=300, key="codelab_output")


    if generate_clicked:
        if not repo:
            st.sidebar.warning("Please enter the GitHub repository URL.")
        else:
            with st.spinner("Generating documentation using AutoDoc agent..."):
                try:
                    params = {"repo_url": repo, "file_type": 'codelab'}
                    response = requests.get(f"{API_BASE_URL}/final-file", params=params)

                    if response.status_code == 200:
                        generated_codelab = response.json()['choices'][0]['message']['content']
                        st.write(generated_codelab)

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Approve & Push to GitHub"):
                                st.success("Approval received. Sending to backend...")

                                try:
                                    params = {"repo": repo, "file_type": 'codelab', "file": generated_codelab}
                                    response = requests.get(f"{API_BASE_URL}/final-file", params=params)
                                

                                    if response.status_code == 200:
                                        result = response.json()
                                        st.success("Successfully pushed to GitHub!")
                                        st.markdown(f"[View Pull Request]({result['pull_request']})")
                                        st.markdown(f"[View Codelab Preview]({result['codelab_url']})")
                                    else:
                                        st.error(f"Failed: {response.status_code}")
                                        st.error(response.text)

                                except Exception as e:
                                    st.error(f"Exception occurred: {e}")

                        with col2:
                            if st.button(" Not Approved - Needs Changes"):
                                st.warning("Feedback noted. Please make necessary changes before pushing to GitHub.")


                    else:
                        st.error("Agent failed to process the request.")
                except Exception as e:
                    st.error(f"Error: {e}")





    #col1, col2 = st.columns(2)
    #with col1:
    #    if st.button("Approve & Push to GitHub (Codelab)"):
    #        st.success("Approval received. Sending to backend...")
#
    #        try:
    #            response = requests.post(
    #                url="http://localhost:8000/approve",
    #                json={
    #                    "repo_url": repo_url,
    #                    #"generated_readme": generated_readme,
    #                    "generated_codelab": generated_codelab
    #                },
    #                timeout=60
    #            )
#
    #            if response.status_code == 200:
    #                result = response.json()
    #                st.success("Successfully pushed to GitHub!")
    #                st.markdown(f"📂 [View Pull Request]({result['pull_request']})")
    #                st.markdown(f"🎓 [View Codelab Preview]({result['codelab_url']})")
    #            else:
    #                st.error(f"Failed: {response.status_code}")
    #                st.error(response.text)
#
    #        except Exception as e:
    #            st.error(f"Exception occurred: {e}")
#
    #with col2:
    #    if st.button(" Not Approved - Needs Changes (Codelab)"):
    #        st.warning("Feedback noted. Please make necessary changes before pushing to GitHub.")
            