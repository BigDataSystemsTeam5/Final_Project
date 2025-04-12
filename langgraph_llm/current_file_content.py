from agent_state import AgentState


def file_content(state: AgentState):
    
    file_name = state["current_filename"]
    print(file_name)
    file_index = state["filenames"].index(file_name)
    file_content = state["files"][file_index]
    return {"current_file": file_content}