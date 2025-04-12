import os
from dotenv import load_dotenv
#from langchain_openai import ChatOpenAI
from agent_state import AgentState
from langchain_deepseek.chat_models import ChatDeepSeek
from langchain.prompts import PromptTemplate


#llm = ChatOpenAI(
#    model="gpt-4o",
#    openai_api_key=os.environ["OPENAI_API_KEY"],
#    temperature=0
#)

load_dotenv(r'C:\Users\Admin\Desktop\MS Data Architecture and Management\DAMG 7245 - Big Data Systems and Intelligence Analytics\Project\environment\access.env')

llm = ChatDeepSeek(
    model="deepseek-chat",  
    temperature=0.7,       
    max_tokens=8000,       
    api_key=os.environ["DEEPSEEK_API_KEY"]        
)

def generate_summary(state: AgentState):

    response_list = []
    processed_filename_list = []

    prompt = PromptTemplate(template="""{Code} is a code file. {Name} is the name of this file. {Tree} is the 
                            structure of the entire project repository for reference on the file with respect to
                            the other files in the project repository.
                            Analyze and summarize this code file. Give a comprehensive
                            summary of the file that can be used to understand the code. 
                            State all the important points. Do not miss any key details. It should be detailed
                            document which can be used to understand the entire code file.""", 
                            input_variables=["Code", "Name", "Tree"])


    formatted_prompt = prompt.format(
        Name = state["current_filename"],
        Code = state["current_file"],
        Tree = state["structure"]
    )

    response = llm.invoke(formatted_prompt)

    processed_filename = state["current_filename"]
    processed_filename_list.append(processed_filename)

    response_list.append(str(response.content))
    #print(response_list)

    #print("----------------------------------------------------------")

    return {"summaries": response_list, "processed_filenames": processed_filename_list}

# Summary generation node
#def generate_summary(state: AgentState):
#    summary = llm.invoke({
#        "context": {state["current_filename"], 
#                    state["current_file"]},
#        "prompt": "Analyze this code file's purpose, key components, and dependencies:"
#    })
#    return {"summaries": [summary]}


