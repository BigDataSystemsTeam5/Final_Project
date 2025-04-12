import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from agent_state import AgentState
from langchain.prompts import PromptTemplate

load_dotenv(r'C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Project\environment\access.env')


llm = ChatDeepSeek(
    model="deepseek-chat",  
    temperature=0.7,       
    max_tokens=8000,       
    api_key=os.environ["DEEPSEEK_API_KEY"]        
)

def generate_project_overview(state: AgentState):
    #combined = "\n\n".join([
    #    f"File: {file}\nSummary: {summary}"
    #    for file, summary in zip(state["processed_filenames"], state["summaries"])
    #])
    
    prompt = PromptTemplate(template=
    """{Repo} is the project repository. {Files} is a list of file names in the project repository. {Tree} is the 
    repository structure of the entire project repository for reference.
    {Summaries} is a list of summaries of each of the file in the project repository. Create a comprehensive README file 
    for the entire project repository. Below is the structure of README file. You can include any or all 
    of the points from the below structure depending on the project files. Each section from the below structure
    should have detailed information. The information shouldn't be just one liners. The information in the 
    sections should not be generic or vague. 

        # Title

        This is an example file with maximal choices selected.

        This is a long description.

        ## Table of Contents

        - [Security](#security)
        - [Background](#background)
        - [Repository Structure](#Repository Structure)
        - [Install](#install)
        - [Usage](#usage)
        - [API](#api)
        - [Contributing](#contributing)
        - [License](#license)

        ## Security

        ### Any optional sections

        ## Background

        ### Any optional sections

        ## Repository Structure

        ## Install

        This module depends upon a knowledge of [Markdown]().

        ```
        ```

        ### Any optional sections

        ## Usage

        ```
        ```

        Note: The `license` badge image link at the top of this file should be updated with the correct `:user` and `:repo`.

        ### Any optional sections

        ## API

        ### Any optional sections

        ## More optional sections

        ## Contributing

        PRs accepted.

        ### Any optional sections

        ## License
    """, 
    input_variables=["Repo","Files", "Summaries", "Tree"])
    

    formatted_prompt = prompt.format(
        Repo = state["repo"],
        Files = state["processed_filenames"],
        Summaries = state["summaries"],
        Tree = state["structure"]
    )

    response = llm.invoke(formatted_prompt)

    bytes_obj = response.content.encode('utf-8')

    with open('output.md', 'wb') as f:
        f.write(bytes_obj)

    #print(response.content)

    return

